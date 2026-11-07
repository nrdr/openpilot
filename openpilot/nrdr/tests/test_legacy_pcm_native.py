"""Native legacy planner -> feedback -> opendbc helper acceptance, Linux only.

Run in the parent's private staging overlay with its existing acados build.
Uses actual planner/solver/controller classes and Cap'n Proto actuator messages;
only advisory alerts and settings readers are patched. No sockets, CAN sends,
processes, model loading, or physical-vehicle simulation are used by this test.
The measurements below are scripted inputs, not claims about vehicle response.
"""
import math
import sys
from types import SimpleNamespace as NS

import numpy as np
import pytest

if sys.platform == "win32":
  pytest.skip("Native legacy acados acceptance runs in isolated Linux staging", allow_module_level=True)

from opendbc.car.honda.interface import CarInterface
from opendbc.car.honda.legacy_pcm import LegacyPCMCommand, LegacyPCMController
from opendbc.car.honda.pcm_test_modes import FIXED_CRUISE_MPS
from opendbc.car.honda.values import CAR, HondaFlags
from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.features.longitudinal.long_tune import LongTune
from openpilot.nrdr.params import get_live_params, read_bool, read_float
from openpilot.nrdr.tests.test_mvl_host_native import lead
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import AcadosOcpSolverCython, LongitudinalPlanSource
from openpilot.sunnypilot.selfdrive.controls.lib import longitudinal_planner as sp_planner


def forbidden_settings(*_args, **_kwargs):
  raise AssertionError("Legacy native sequence attempted to read persisted settings/tuning")


@pytest.fixture
def isolated_settings(monkeypatch):
  monkeypatch.setattr(sp_planner, "E2EAlertsHelper", lambda: NS(update=lambda *_: None))
  # Patch already-bound reader imports too, not just their defining module.
  # Do not replace a planner, solver, controller, tune class, or command law.
  readers = {"Params": Params, "get_live_params": get_live_params, "read_bool": read_bool, "read_float": read_float}
  for name, module in tuple(sys.modules.items()):
    if module is not None and name.startswith("openpilot."):
      for attribute, reader in readers.items():
        if vars(module).get(attribute) is reader:
          monkeypatch.setattr(module, attribute, forbidden_settings)
  monkeypatch.setattr(LongTune, "refresh", forbidden_settings)
  # This directly constructed logger can retain an enabled-level cache even
  # after logging.disable(). Disable just its IPC output during this test.
  monkeypatch.setattr(cloudlog, "disabled", True)


def civic_params(fixed):
  flags = HondaFlags.NIDEC | HondaFlags.NIDEC_PCM_LEGACY
  if fixed:
    flags |= HondaFlags.NIDEC_PCM_FIXED_CRUISE
  cp = car.CarParams.new_message(
    brand="honda", carFingerprint=CAR.HONDA_CIVIC, flags=int(flags),
    openpilotLongitudinalControl=True, pcmCruise=True, passive=False, dashcamOnly=False,
    longitudinalActuatorDelay=.3, stopAccel=-.5, steerRatio=15.38, wheelbase=2.7,
  )
  # Real schema fields; legacy must ignore even this deliberately unsuitable
  # acceleration-loop tune in favor of its fixed historical speed PI.
  cp.longitudinalTuning.kiBP = [0.]
  cp.longitudinalTuning.kiV = [1000.]
  cp.longitudinalTuning.deprecated.kpBP = [0.]
  cp.longitudinalTuning.deprecated.kpV = [1000.]
  return cp, custom.CarParamsSP.new_message(enableGasInterceptor=False, pcmCruiseSpeed=not fixed)


class NativeSequence:
  """In-memory input/transport harness; all longitudinal math is production."""
  def __init__(self, fixed, experimental):
    self.cp, self.cp_sp = civic_params(fixed)
    self.controller = LongControl(self.cp, self.cp_sp)
    self.planner = LongitudinalPlanner(self.cp, self.cp_sp, init_v=10.)
    self.helper = LegacyPCMController()
    assert self.controller.legacy_controller is not None and self.controller.nrdr_controller is None
    assert self.planner.legacy_pcm and self.planner.fixed_pcm_cruise == fixed
    assert not self.planner.mvl_enabled and not self.planner.mpc.mvl_enabled
    assert self.planner.nrdr is self.planner.mpc.nrdr is self.planner.mpc.tune is None
    assert self.planner.scc is self.planner.sla is self.planner.resolver is self.planner.accel_boost_sp is None
    assert isinstance(self.planner.mpc.solver, AcadosOcpSolverCython)

    self.cs = car.CarState.new_message(
      vEgo=10., aEgo=0., vCruise=80., vCruiseCluster=80., canValid=True,
      cruiseState={"available": True, "enabled": True, "standstill": False,
                   "speed": FIXED_CRUISE_MPS if fixed else 80. / 3.6},
    )
    self.sm = {
      "carState": self.cs,
      "carControl": car.CarControl.new_message(enabled=True, longActive=True),
      "controlsState": NS(forceDecel=False, longControlState=LongCtrlState.off),
      "selfdriveState": NS(enabled=True, personality=1, experimentalMode=experimental),
      "vehicleParameters": NS(angleOffsetDeg=0.),
      "modelV2": NS(meta=NS(disengagePredictions=NS(gasPressProbs=[0., 1.])),
                    action=NS(desiredAcceleration=1., shouldStop=False)),
      "radarState": NS(leadOne=lead(present=False), leadTwo=lead(present=False)),
    }
    self.frame = 0
    self.last_actuators = None
    self.last_command = LegacyPCMCommand()

  def feedback_ticks(self, *, fresh=True):
    """Five real 100 Hz controller updates per unchanged 20 Hz selected plan."""
    limits = CarInterface.get_pid_accel_limits(self.cp, self.cp_sp, self.cs.vEgo, self.cs.vCruise / 3.6)
    selected = float(self.planner.output_a_target)
    expected_accel = float(np.clip(selected, *limits))
    for _ in range(5):
      legacy = self.controller.legacy_controller
      previous_reference = legacy.reference.speed
      cc = car.CarControl.new_message(enabled=True, longActive=True)
      cc.actuators.accel = self.controller.update(
        True, self.cs, selected, self.planner.output_should_stop, limits, reference_valid=fresh,
      )
      # Same four-channel contract as controlsd, without starting its process.
      cc.actuators.speed = legacy.v_pid
      cc.actuators.brake = legacy.brake
      cc.actuators.gas = 0.
      cc.actuators.longControlState = self.controller.long_control_state
      expected_active = fresh and not (self.cs.gasPressed or self.cs.brakePressed)
      if expected_active:
        assert cc.actuators.accel == pytest.approx(expected_accel, abs=1e-6)
        if self.controller.long_control_state == LongCtrlState.pid:
          # Independently check that the speed handoff integrates FINAL aTarget,
          # not MPC speeds/accels or the PI's normalized braking output.
          previous = self.cs.vEgo if previous_reference is None else previous_reference
          expected_speed = max(0., previous + .01 / 2.01 * (self.cs.vEgo - previous) + expected_accel * .01)
          expected_speed = min(expected_speed, max(self.cs.vEgo, self.cs.vCruise / 3.6))
          assert cc.actuators.speed == pytest.approx(expected_speed, abs=2e-6)
          assert self.controller.pid.f == pytest.approx(expected_accel)
      else:
        assert self.controller.long_control_state == LongCtrlState.off
        assert legacy.reference.speed is None
        assert self.controller.pid.p == self.controller.pid.i == self.controller.pid.f == 0.
        assert cc.actuators.accel == cc.actuators.speed == cc.actuators.brake == 0.

      # Exercise the native schema across the exact host-to-opendbc boundary.
      with car.CarControl.from_bytes(cc.to_bytes()) as received:
        a = received.actuators
        command = self.helper.update(
          active=received.longActive and a.longControlState != LongCtrlState.off,
          v_ego=self.cs.vEgo, a_ego=self.cs.aEgo, v_target=a.speed, a_target=a.accel, brake=a.brake,
          send_brake=self.frame % 2 == 0, gas_pressed=self.cs.gasPressed, brake_pressed=self.cs.brakePressed,
        )
        assert all(math.isfinite(value) for value in (a.accel, a.speed, a.brake, a.gas,
                                                      command.pcm_speed, command.brake_fraction))
        assert limits[0] - 1e-6 <= a.accel <= limits[1] + 1e-6  # Float32 transport rounding
        assert 0. <= a.brake <= 1. and a.gas == 0.
        assert 0. <= command.pcm_speed <= 100.
        assert 0 <= command.pcm_accel <= 198 and 0 <= command.apply_brake <= 255
        if command.apply_brake > 0 or self.helper.apply_brake_last > 0:
          assert command.pcm_speed == command.pcm_accel == 0
        if not expected_active:
          assert command == LegacyPCMCommand()
      self.last_actuators = cc.actuators.as_reader()
      self.last_command = command
      self.frame += 1
    return self.last_command

  def model_tick(self):
    self.sm["controlsState"].longControlState = self.controller.long_control_state
    self.planner.update(self.sm)
    assert self.planner.mpc.solution_status == 0
    assert np.isfinite(self.planner.mpc.x_sol).all() and np.isfinite(self.planner.mpc.u_sol).all()
    assert math.isfinite(self.planner.output_a_target)
    assert not self.planner.fcw  # These bounded scenarios are not imminent-crash tests.
    return self.feedback_ticks()


@pytest.mark.parametrize("fixed", [False, True])
@pytest.mark.parametrize("experimental", [False, True])
def test_native_legacy_selected_plan_feedback_and_command_sequence(isolated_settings, monkeypatch, fixed, experimental):
  sequence = NativeSequence(fixed, experimental)
  def failed_solver_reset():
    raise AssertionError("Native MPC attempted to reset after a solve failure")
  # A failed solve calls reset(), which otherwise restores solution_status=0.
  # Fail the test at that boundary rather than accepting reset trajectories.
  monkeypatch.setattr(sequence.planner.mpc, "reset", failed_solver_reset)
  positive_commands = []
  for _ in range(30):
    positive_commands.append(sequence.model_tick().pcm_accel)
  assert sequence.planner.output_a_target > 0.
  assert any(value > 0 for value in positive_commands)
  assert sequence.controller.legacy_controller.brake == 0.

  # Fresh -> stale with the previous positive plan still in memory.
  assert sequence.feedback_ticks(fresh=False) == LegacyPCMCommand()
  assert sequence.planner.output_a_target > 0.
  for _ in range(5):
    sequence.model_tick()
  assert sequence.last_command.pcm_accel > 0

  # Challenge the feedback guard even with caller-active still true.
  for pedal in ("gasPressed", "brakePressed"):
    setattr(sequence.cs, pedal, True)
    assert sequence.feedback_ticks() == LegacyPCMCommand()
    setattr(sequence.cs, pedal, False)
    for _ in range(5):
      sequence.model_tick()
    assert sequence.last_command.pcm_accel > 0

  sequence.sm["modelV2"].action.desiredAcceleration = -1.
  for _ in range(10):
    sequence.model_tick()
  if experimental:
    assert sequence.planner.output_a_target <= -1.
    assert sequence.planner.mpc.source == LongitudinalPlanSource.e2e
    assert sequence.last_actuators.brake > 0.
  else:
    assert sequence.planner.output_a_target > 0.
    assert sequence.planner.mpc.source != LongitudinalPlanSource.e2e

  # Now request lower acceleration from a real lead-MPC solution in both modes.
  sequence.sm["modelV2"].action.desiredAcceleration = 2.
  sequence.sm["radarState"].leadOne = lead(distance=30., speed=6., accel=-.3)
  lead_brakes = []
  for _ in range(60):
    sequence.model_tick()
    lead_brakes.append(sequence.last_actuators.brake)
  assert sequence.planner.output_a_target < 0.
  assert sequence.planner.mpc.source == LongitudinalPlanSource.lead0
  assert any(value > 0. for value in lead_brakes)

  # Script a descent to standstill; never integrate command output as a plant.
  sequence.cs.vCruise = sequence.cs.vCruiseCluster = 0.
  sequence.sm["radarState"].leadOne = lead(present=False)
  sequence.sm["modelV2"].action.desiredAcceleration = 0.
  for step in range(1, 101):
    sequence.cs.vEgo = max(0., 10. - step * .1)
    sequence.cs.aEgo = -2. if sequence.cs.vEgo > 0. else 0.
    sequence.cs.standstill = sequence.cs.vEgo == 0.
    sequence.model_tick()
  for _ in range(60):
    sequence.model_tick()
  assert sequence.planner.output_should_stop
  assert sequence.controller.long_control_state == LongCtrlState.stopping
  assert sequence.last_actuators.speed == 0.
  assert sequence.last_actuators.brake >= .25
  assert sequence.last_command.apply_brake > 0
  assert sequence.last_command.pcm_accel == sequence.last_command.pcm_speed == 0
