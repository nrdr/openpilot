from collections import deque
from types import SimpleNamespace

from openpilot.cereal import log
from openpilot.nrdr.features.lateral.interpolated_torque_pif import InterpolatedTorquePifSettings
from openpilot.nrdr.features.lateral.latcontrol_clarity_hybrid import LatControlClarityHybrid
from openpilot.nrdr.features.lateral.latcontrol_pid import NrdrLatControlPID


class StubPidController:
  def __init__(self, blend_enabled):
    self.nrdr_controller = SimpleNamespace(
      firmware_vgr_selected=False,
      interpolated_torque_pif_enabled=blend_enabled,
    )
    self.pid = SimpleNamespace(i=0.25)

  @staticmethod
  def update(*args):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.active = True
    pid_log.angleError = 0.1
    pid_log.p = 0.2
    pid_log.i = 0.3
    pid_log.f = 0.4
    pid_log.output = 0.5
    pid_log.saturated = False
    return 0.5, 12.0, pid_log


class StubTorqueController:
  def __init__(self):
    self.update_calls = 0
    self.sat_time = 1.0
    self.pid = Resettable(i=0.6)
    self.previous_measurement = 0.4
    self.measurement_rate_filter = SimpleNamespace(x=0.3, initialized=False)
    self.lat_accel_request_buffer = deque((0.1, 0.2, 0.3), maxlen=3)
    self.nrdr_updates = 0
    nrdr = SimpleNamespace(previous_curvature=0.4)
    nrdr.update = lambda: setattr(self, "nrdr_updates", self.nrdr_updates + 1)
    self.extension = SimpleNamespace(
      nrdr=nrdr,
      _pid=Resettable(i=0.75),
      _nnlc_enabled=True,
      _pid_log=object(),
      _steer_limited_by_safety=True,
      pitch=SimpleNamespace(x=0.2, initialized=False),
      pitch_last=0.1,
      lat_accel_friction_factor=1.0,
      lateral_accel_desired_deque=deque((1.0,), maxlen=30),
      roll_deque=deque((2.0,), maxlen=30),
      error_deque=deque((3.0,), maxlen=30),
    )

  def reset(self):
    self.sat_time = 0.0

  def update(self, *args):
    self.update_calls += 1
    raise AssertionError("outer NNLC/JATC controller must not run while interpolated blend is effective")


class Resettable:
  def __init__(self, i):
    self.i = i
    self.reset_calls = 0

  def reset(self):
    self.i = 0.0
    self.reset_calls += 1


def test_clarity_hybrid_bypasses_and_resets_outer_controller_when_blend_is_effective():
  controller = LatControlClarityHybrid.__new__(LatControlClarityHybrid)
  controller.pid_controller = StubPidController(blend_enabled=True)
  controller.torque_controller = StubTorqueController()
  controller.nnlc_blend = 0.8

  output, angle, torque_log = controller.update(
    True,
    SimpleNamespace(vEgo=20.0),
    object(),
    object(),
    False,
    0.01,
    object(),
    False,
    0.2,
  )

  assert output == 0.5
  assert angle == 12.0
  assert torque_log.output == 0.5
  assert controller.torque_controller.update_calls == 0
  assert controller.torque_controller.nrdr_updates == 0
  assert controller.nnlc_blend == 0.0
  assert controller.torque_controller.sat_time == 0.0
  assert controller.torque_controller.pid.reset_calls == 1
  assert controller.torque_controller.previous_measurement == 0.0
  assert controller.torque_controller.measurement_rate_filter.x == 0.0
  assert list(controller.torque_controller.lat_accel_request_buffer) == [0.0, 0.0, 0.0]
  assert controller.torque_controller.extension._pid.i == 0.0
  assert controller.torque_controller.extension._pid_log is None
  assert not controller.torque_controller.extension._steer_limited_by_safety
  assert controller.torque_controller.extension.nrdr.previous_curvature == 0.0
  assert not controller.torque_controller.extension.lateral_accel_desired_deque
  assert not controller.torque_controller.extension.roll_deque
  assert not controller.torque_controller.extension.error_deque
  assert controller.torque_controller.extension.pitch.x == 0.0
  assert controller.torque_controller.extension.pitch_last == 0.0
  assert controller.torque_controller.extension.lat_accel_friction_factor == 0.7


def test_blend_pauses_learner_samples_but_keeps_learner_maintenance_running():
  class LearnerSpy:
    def __init__(self):
      self.calls = []

    def learn(self, *args):
      self.calls.append(args)

  controller = NrdrLatControlPID.__new__(NrdrLatControlPID)
  controller.is_eps_modified = True
  controller.interpolated_torque_pif_latch = SimpleNamespace(
    settings=InterpolatedTorquePifSettings(enabled=True),
  )
  controller.stiction_enabled = False
  controller.stiction = SimpleNamespace(freeze_integrator=False)
  controller.tune_learner = LearnerSpy()
  controller.frame = 123
  CS = SimpleNamespace(vEgo=10.0, steeringRateDeg=0.5)

  controller._update_tune_learner(
    CS, desired_angle=2.0, error=0.1, steering_pressed=False,
    params_valid=True, lane_change=False, stiction_limited=False,
  )
  assert len(controller.tune_learner.calls) == 1
  assert controller.tune_learner.calls[-1][5] is False

  controller.interpolated_torque_pif_latch.settings = InterpolatedTorquePifSettings(enabled=False)
  controller._update_tune_learner(
    CS, desired_angle=2.0, error=0.1, steering_pressed=False,
    params_valid=True, lane_change=False, stiction_limited=False,
  )
  assert len(controller.tune_learner.calls) == 2
  assert controller.tune_learner.calls[-1][5] is True
