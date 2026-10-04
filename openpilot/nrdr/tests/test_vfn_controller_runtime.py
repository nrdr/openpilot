"""Exercise the production VFN wrapper, without CAN or device settings writes."""
import math
from types import SimpleNamespace

import pytest

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP
from opendbc.car.structs import car as car_structs
from opendbc.car.vehicle_model import VehicleModel
from openpilot.nrdr.features.lateral.steer_ratio_tuning import resolve_steer_ratio_selection
from openpilot.nrdr.features.lateral.lane_change_tuning import shape_lane_change_curvature
from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
from openpilot.nrdr.params.snapshots import ParamSnapshot


def car(fingerprint="HONDA_CLARITY", firmware=b"39990-TRW-A020", modified=True):
  cp = SimpleNamespace(brand="honda", carFingerprint=fingerprint, steerRatio=16.5,
                       wheelbase=2.75, steerLimitTimer=.8,
                       carFw=[SimpleNamespace(ecu="eps", fwVersion=firmware)],
                       lateralTuning=SimpleNamespace(which=lambda: "pid"))
  return cp, SimpleNamespace(flags=HondaFlagsSP.EPS_MODIFIED.value if modified else 0)


def controller(**changes):
  cp, sp = car(**changes)
  return LatControlFirmware(cp, sp, None, .01)


def vehicle_model():
  return VehicleModel(car_structs.CarParams.new_message(
    mass=1840, rotationalInertia=3000, wheelbase=2.75, centerToFront=1.08,
    steerRatioRear=0, steerRatio=16.5, tireStiffnessFront=200000, tireStiffnessRear=200000))


def tick(control, *, active=True, state=0, angle=20., speed=15., desired=20.):
  control.update_model_v2(SimpleNamespace(meta=SimpleNamespace(laneChangeState=SimpleNamespace(raw=state))))
  cs = SimpleNamespace(vEgo=speed, steeringAngleDeg=angle, steeringRateDeg=0.,
                       steeringPressed=False, steeringTorque=0.)
  vm = vehicle_model()
  curvature = control.steer_ratio_selection.measured_curvature(vm, desired, speed, 0.)
  return control.update(active, cs, vm, SimpleNamespace(roll=0., angleOffsetDeg=0.),
                        False, curvature, None, False, .2)


@pytest.mark.parametrize("changes", [{"fingerprint": "HONDA_CIVIC"}, {"firmware": b"39990-TRW-A010"}, {"modified": False}])
def test_wrong_platform_or_eps_cannot_select_vfn(changes):
  with pytest.raises(ValueError):
    controller(**changes)


@pytest.mark.parametrize("state", [2, 3])
def test_lane_change_suppresses_wrapper_feedforward_and_rejoins(state):
  control = controller()
  for _ in range(100):
    tick(control)
  assert control.core.ff_weight == 1.
  for _ in range(60):
    output, _, logged = tick(control, state=state)
    assert control.core.ff_weight == 0.
    assert logged.f == 0.
    assert math.isfinite(output) and abs(output) <= 1.
  tick(control)
  assert 0. < control.core.ff_weight < .1


def test_disabled_optimization_and_waiting_for_nudge_keep_feedforward():
  control = controller()
  control.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrOptimizedLaneChanges": False}))
  for _ in range(100):
    tick(control, state=2)
  assert control.core.ff_weight == 1.
  control.set_live_tuning_snapshot(ParamSnapshot(2, {"NrdrOptimizedLaneChanges": True}))
  tick(control, state=1)
  assert control.core.ff_weight == 1.


def test_custom_pif_gains_and_filter_settings_do_not_retune_vfn():
  baseline, custom = controller(), controller()
  custom.set_live_tuning_snapshot(ParamSnapshot(1, {
    **{f"Lat{term}Scale{band}": value for term, value in (("P", 500), ("I", 0), ("F", 0))
       for band in ("LowSpeed", "Standard", "Highway")},
    "NrdrLatRateDampingStandard": 300, "HondaTorqueLowPassFilter": True,
    "HondaLpfTauLowSpeed": 1., "HondaLpfTauStandard": 1., "HondaLpfTauHighway": 1.,
  }))
  for frame in range(150):
    desired = 20. + math.sin(frame / 20.)
    assert tick(custom, desired=desired)[0] == pytest.approx(tick(baseline, desired=desired)[0])


NO_COMMAND_DELAY = ParamSnapshot(1, {"NrdrYawCommandDelayLow": 0.0, "NrdrYawCommandDelayHigh": 0.0})


def test_inactive_control_resets_and_reengagement_limits_requested_angle_rate():
  control = controller()
  control.set_live_tuning_snapshot(NO_COMMAND_DELAY)
  for _ in range(100):
    tick(control)
  output, previous, logged = tick(control, active=False)
  assert output == 0. and not logged.active
  assert control.core.pid.i == 0. and control.core.output == 0.
  _, requested, _ = tick(control, desired=100.)
  assert requested - previous == pytest.approx(3.)


@pytest.mark.parametrize("curvature", [-.01, -.001, .001, .01])
def test_lane_change_shaping_reduces_request_without_reversing_it(curvature):
  control = controller()
  shaped = shape_lane_change_curvature(control.steer_ratio_selection, vehicle_model(), 15., 15., .01, curvature, 5.)
  assert min(0., curvature) <= shaped <= max(0., curvature)
  assert abs(shaped) < abs(curvature)


@pytest.mark.parametrize("speed, delay", [(5., .145), (12.5, .085), (20., .025)])
def test_default_command_delay_holds_the_request_back_on_speed(speed, delay):
  control = controller()
  for _ in range(50):
    tick(control, speed=speed, desired=0.)
  frames = 0
  while tick(control, speed=speed, desired=10.)[1] < 9.999:
    frames += 1
  # The rate limit takes 4 frames to reach 10 deg; the rest is the delay line.
  assert frames - 3 == pytest.approx(delay / .01, abs=1.)
  assert control.update(True, SimpleNamespace(vEgo=speed, steeringAngleDeg=0., steeringRateDeg=0., steeringPressed=False,
                                              steeringTorque=0.), vehicle_model(), SimpleNamespace(roll=0., angleOffsetDeg=0.),
                        False, 0., None, False, .2)[2].commandDelay == pytest.approx(delay)


def test_command_delay_settings_are_live_and_zero_passes_through():
  delayed, direct = controller(), controller()
  direct.set_live_tuning_snapshot(NO_COMMAND_DELAY)
  for _ in range(50):
    tick(delayed, speed=5., desired=0.)
    tick(direct, speed=5., desired=0.)
  assert tick(direct, speed=5., desired=1.)[1] == pytest.approx(1.)
  assert tick(delayed, speed=5., desired=1.)[1] == pytest.approx(0.)


def test_controller_does_not_override_shared_geometry_feedback_or_model_delay():
  control = controller()
  assert not hasattr(control, "lateral_delay")
  assert not hasattr(control, "measured_curvature")
  assert not hasattr(control, "shape_lane_change_request")


def test_feedforward_telemetry_is_logged_on_the_pid_state():
  control = controller()
  for _ in range(100):
    _, _, logged = tick(control, angle=0.)
  assert logged.epsFfActive
  assert logged.epsFfWeight == pytest.approx(control.core.ff_weight)
  assert logged.epsFfFeedforward == pytest.approx(control.core.ff.output) and logged.epsFfFeedforward != 0.
  assert logged.epsFfR5 == pytest.approx(control.core.ff.r5)
  assert logged.epsFfLoad == pytest.approx(control.core.ff.load)
  assert logged.epsFfDesiredRate == pytest.approx(control.core.ff.rate)


def test_inactive_history_is_retained_without_commanding_torque():
  control = controller()
  for _ in range(50):
    output, _, logged = tick(control, active=False, speed=5., desired=20.)
    assert output == 0. and not logged.epsFfActive and logged.epsFfWeight == 0.
    assert logged.epsFfFeedforward == 0.
  # Re-engagement consumes the history, not a new undelayed target.
  _, angle, logged = tick(control, speed=5., desired=100.)
  assert angle == pytest.approx(20.)
  assert logged.commandDelay == pytest.approx(.145)


def test_lane_change_logs_zero_feedforward_weight_and_fades_back_in():
  control = controller()
  for _ in range(100):
    tick(control)
  for state in (2, 3):
    _, _, logged = tick(control, state=state)
    assert logged.epsFfWeight == 0. and logged.f == 0.
  _, _, logged = tick(control)
  assert 0. < logged.epsFfWeight < .1


def test_device_yaw_blend_toggle_does_not_change_the_separate_vfn_controller():
  enabled, disabled = controller(), controller()
  enabled.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrDeviceYawCorrection": True}))
  disabled.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrDeviceYawCorrection": False}))
  for frame in range(100):
    desired = 20. + math.sin(frame / 20.)
    assert tick(enabled, desired=desired)[0] == pytest.approx(tick(disabled, desired=desired)[0])


@pytest.mark.parametrize("mode,hybrid", [(0, False), (1, False), (2, False), (3, False), (2, True)])
@pytest.mark.parametrize("angle", [-90., -15., -12.5, -10., 0., 10., 12.5, 15., 90.])
@pytest.mark.parametrize("speed", [5., 15., 30.])
def test_shared_steer_ratio_controls_the_actual_yaw_target(mode, hybrid, angle, speed):
  control = controller()
  control.set_live_tuning_snapshot(NO_COMMAND_DELAY)
  selected = resolve_steer_ratio_selection(car()[0], {
    "NrdrSteerRatioMode": mode, "NrdrSteerRatioHybrid": hybrid,
    "NrdrSteerRatioSourceB": 3, "NrdrSteerRatioBlendStart": 10.,
    "NrdrSteerRatioManualCenter": 20., "NrdrSteerRatioManualFinal": 13.75,
  }, live_comma_ratio=18.)
  assert selected.available
  control.set_steer_ratio_selection(selected)
  vm = vehicle_model()
  vm.sR = 18. if mode == 1 else vm.sR
  cs = SimpleNamespace(vEgo=speed, steeringAngleDeg=angle, steeringRateDeg=0.,
                       steeringPressed=False, steeringTorque=0.)
  roll, offset, curvature = .02, .7, -.002
  expected = selected.desired_angle_no_offset(vm, angle, speed, roll, curvature) + offset
  # Inactive first primes the normal angle-rate limiter; next frame exercises the active core.
  control.update(False, cs, vm, SimpleNamespace(roll=roll, angleOffsetDeg=offset),
                 False, curvature, None, False, .3)
  output, target, logged = control.update(True, cs, vm, SimpleNamespace(roll=roll, angleOffsetDeg=offset),
                                         False, curvature, None, False, .3)
  assert target == pytest.approx(expected)
  assert logged.steeringAngleDesiredDeg == pytest.approx(expected)
  assert math.isfinite(output) and abs(output) <= 1.


def test_manual_ratio_changes_yaw_target_without_changing_fixed_gains():
  control = controller()
  control.set_live_tuning_snapshot(NO_COMMAND_DELAY)
  vm = vehicle_model()
  cs = SimpleNamespace(vEgo=10., steeringAngleDeg=0., steeringRateDeg=0.)
  targets = []
  gains = (control.core.pid.k_p, control.core.pid.k_i)
  for ratio in (12., 20.):
    control.set_steer_ratio_selection(resolve_steer_ratio_selection(car()[0], {
      "NrdrSteerRatioMode": 0, "NrdrSteerRatioManualCenter": ratio, "NrdrSteerRatioManualFinal": ratio,
    }))
    targets.append(control.update(False, cs, vm, SimpleNamespace(roll=0., angleOffsetDeg=0.),
                                  False, -.002, None, False, .3)[1])
    assert (control.core.pid.k_p, control.core.pid.k_i) == gains
  assert targets[1] / targets[0] == pytest.approx(20 / 12)
