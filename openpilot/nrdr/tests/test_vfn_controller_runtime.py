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


@pytest.fixture(autouse=True)
def world_model(monkeypatch):
  monkeypatch.setattr("openpilot.nrdr.features.lateral.lane_change_tuning.active_model_supports_optimized_lane_changes", lambda: True)


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


def tick(control, *, active=True, state=0, angle=20., speed=15., desired=20., pressed=False, torque=0., limited=False):
  control.update_model_v2(SimpleNamespace(meta=SimpleNamespace(laneChangeState=SimpleNamespace(raw=state))))
  cs = SimpleNamespace(vEgo=speed, steeringAngleDeg=angle, steeringRateDeg=0.,
                       steeringPressed=pressed, steeringTorque=torque)
  vm = vehicle_model()
  curvature = control.steer_ratio_selection.measured_curvature(vm, desired, speed, 0.)
  return control.update(active, cs, vm, SimpleNamespace(roll=0., angleOffsetDeg=0.),
                        limited, curvature, None, False, .2)


def recovery_controller(duration):
  live = SimpleNamespace(override_fade_up_s=duration)
  reads = []

  def get_live_tuning(*, refresh_if_uninitialized):
    assert refresh_if_uninitialized is False  # never poll Params from the lateral update
    reads.append(live.override_fade_up_s)
    return live

  ci = SimpleNamespace(interface_config=SimpleNamespace(honda=SimpleNamespace(
    provider=SimpleNamespace(get_live_tuning=get_live_tuning))))
  cp, sp = car()
  control = LatControlFirmware(cp, sp, ci, .01)
  control.core.output_lpf_enabled = False
  control.core.pid.i = control.core.output = .2
  return control, live, reads


@pytest.mark.parametrize("duration", [.01, .5, 1.5])
def test_override_decay_uses_existing_press_detector_and_live_honda_recovery(duration):
  control, live, reads = recovery_controller(duration)
  # A short co-direction press is still filtered out, so it cannot arm decay.
  tick(control, angle=0., desired=0., pressed=True, torque=1., limited=True)
  assert not control.pressed_prev and math.isinf(control.core.since_press_s)
  tick(control, angle=0., desired=0., limited=True)
  assert control.core.pid.i == .2
  # An opposing press qualifies immediately, but freezes rather than decays while held.
  tick(control, angle=0., desired=0., pressed=True, torque=-1., limited=True)
  assert control.pressed_prev and control.core.pid.i == .2
  tick(control, angle=0., desired=0., limited=True)
  held = .2 * math.exp(-.01 / .5)
  assert control.core.pid.i == pytest.approx(held)
  live.override_fade_up_s = 0.
  tick(control, angle=0., desired=0., limited=True)
  assert control.core.pid.i == pytest.approx(held)
  assert reads == [duration] * 4 + [0.]


def test_override_decay_respects_a_short_configured_window_and_disengagement():
  control, _, _ = recovery_controller(.01)
  tick(control, angle=0., desired=0., pressed=True, torque=-1., limited=True)
  for _ in range(2):  # configured 10 ms plus the delayed limiter feedback frame
    tick(control, angle=0., desired=0., limited=True)
  held = control.core.pid.i
  tick(control, angle=0., desired=0., limited=True)
  assert held == pytest.approx(.2 * math.exp(-.02 / .5))
  assert control.core.pid.i == held
  tick(control, active=False, angle=0., desired=0.)
  assert math.isinf(control.core.since_press_s) and not control.pressed_prev
  control.core.pid.i = .2
  tick(control, angle=0., desired=0., limited=True)
  assert control.core.pid.i == .2


def test_no_honda_provider_keeps_existing_freeze_behavior():
  control = controller()
  control.core.pid.i = .2
  tick(control, angle=0., desired=0., pressed=True, torque=-1., limited=True)
  tick(control, angle=0., desired=0., limited=True)
  assert control.core.pid.i == .2


@pytest.mark.parametrize("changes", [{"fingerprint": "HONDA_CIVIC"}, {"firmware": b"39990-TRW-A010"}, {"modified": False}])
def test_wrong_platform_or_eps_cannot_select_vfn(changes):
  with pytest.raises(ValueError):
    controller(**changes)


SUPPORTED_CIVICS = [
  {"fingerprint": "HONDA_CIVIC_BOSCH", "firmware": b"39990-TBA-C020"},
  {"fingerprint": "HONDA_CIVIC", "firmware": b"39990-TEG-A010"},
]


@pytest.mark.parametrize("changes", SUPPORTED_CIVICS)
def test_civic_wrapper_uses_its_own_calibration_and_the_c020_trims_without_mutating_carparams(changes):
  from openpilot.nrdr.features.lateral.vfn_eps_core import (CIVIC_BOSCH_C020, CIVIC_EPS_LOAD, CIVIC_P_SCALE,
                                                            CIVIC_I_SCALE, CIVIC_TEG_A010, CIVIC_TEG_EPS_LOAD)
  cp, sp = car(**changes)
  before = repr(cp)
  control = LatControlFirmware(cp, sp, None, .01)
  assert repr(cp) == before
  teg = changes["fingerprint"] == "HONDA_CIVIC"
  assert control.core.ff.cal is (CIVIC_TEG_A010 if teg else CIVIC_BOSCH_C020)
  assert control.core.ff.load_coefficients == (CIVIC_TEG_EPS_LOAD if teg else CIVIC_EPS_LOAD)
  assert control.core.p_scale == CIVIC_P_SCALE and control.core.i_scale == CIVIC_I_SCALE
  assert control.delay_schedule[1] == ((.20,) * 5 if teg else (.28, .28, .28, .26, .26))  # its own measured lag
  assert not control.firmware_profile.provisional
  # User PIF/yaw settings cannot leak into either firmware profile.
  control.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrDeviceYawCorrection": True, "LatFScaleHighway": 500,
                                                   "NrdrLatRateDampingHighway": 300}))
  for state in (0, 2, 3):
    for _ in range(100):
      output, _, logged = tick(control, state=state)
      assert math.isfinite(output) and abs(output) <= control.steer_max
      assert logged.commandDelay == pytest.approx(.175)  # held flat above 15 m/s
      if state in (2, 3):
        assert logged.f == 0. and logged.epsFfWeight == 0.


def test_insight_wrapper_uses_its_own_calibration_the_c020_trims_and_the_clarity_schedule():
  from openpilot.nrdr.features.lateral.vfn_eps_core import (CIVIC_I_SCALE, CIVIC_P_SCALE, INSIGHT_TXM_A040,
                                                            INSIGHT_TXM_EPS_LOAD)
  cp, sp = car(fingerprint="HONDA_INSIGHT", firmware=b"39990-TXM,A040")
  before = repr(cp)
  control = LatControlFirmware(cp, sp, None, .01)
  assert repr(cp) == before
  assert control.core.ff.cal is INSIGHT_TXM_A040 and control.core.ff.load_coefficients == INSIGHT_TXM_EPS_LOAD
  assert control.core.p_scale == CIVIC_P_SCALE and control.core.i_scale == CIVIC_I_SCALE
  assert control.delay_schedule is not None and not control.firmware_profile.provisional
  for _ in range(60):
    tick(control, active=False, speed=5., desired=15.)
  _, _, logged = tick(control, speed=5., desired=60.)
  assert logged.commandDelay == pytest.approx(.175)


@pytest.mark.parametrize("changes", SUPPORTED_CIVICS)
@pytest.mark.parametrize("speed,delay", [(5., .175), (12.5, .175), (20., .175)])
def test_civic_wrapper_uses_its_command_delay_and_preserves_shared_steer_ratio(changes, speed, delay):
  control = controller(**changes)
  cp, _ = car(**changes)
  selection = resolve_steer_ratio_selection(cp, {"NrdrSteerRatioMode": 3})
  control.set_steer_ratio_selection(selection)
  for _ in range(60):
    tick(control, active=False, speed=speed, desired=15.)
  _, target, logged = tick(control, speed=speed, desired=60.)
  assert target == pytest.approx(15.)
  assert logged.commandDelay == pytest.approx(delay)
  assert selection.firmware_profile is not None


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


def test_ineligible_model_matches_toggle_off_through_complete_lane_change(monkeypatch):
  monkeypatch.setattr("openpilot.nrdr.features.lateral.lane_change_tuning.active_model_supports_optimized_lane_changes", lambda: False)
  enabled, baseline = controller(), controller()
  enabled.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrOptimizedLaneChanges": True}))
  baseline.set_live_tuning_snapshot(ParamSnapshot(1, {"NrdrOptimizedLaneChanges": False}))
  for state in [0, 1, 2, 3, 0]:
    for _ in range(30):
      assert tick(enabled, state=state)[0] == tick(baseline, state=state)[0]
      assert enabled.core.ff_weight == baseline.core.ff_weight
  assert enabled.core.ff_weight == 1.


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


def test_confirmed_rdx_does_not_ride_through_a_one_frame_dropout(monkeypatch):
  from openpilot.nrdr.tests.test_rdx_route_a import MODIFIED, rdx, simulate_receipt
  cp = rdx()
  simulate_receipt(monkeypatch, cp)
  control = LatControlFirmware(cp, MODIFIED, None, .01)
  assert control.core.p_scale == (1., 1., .7) and control.core.i_scale == (1., 1., 1.)
  assert control.steer_ratio_selection.rack_map is None
  assert control.delay_schedule is None  # no forced Clarity schedule on an RDX
  for _ in range(200):
    output, _, _ = tick(control, angle=17., desired=20.)
  assert output != 0. and control.core.ff_weight > 0.
  output, previous, log = tick(control, active=False)
  assert output == log.output == 0. and not log.active
  assert control.core.ff_weight == control.core.output == control.core.pid.i == 0.
  assert control.core.ff.prev_angle is None
  _, requested, _ = tick(control, desired=100.)
  assert requested - previous <= 3.0001


@pytest.mark.parametrize("fingerprint,stock_limit", [("ACURA_RDX_3G", 4095), ("ACURA_RDX_3G_MMR", 4076)])
def test_rdx_requires_real_carparams_identity_and_the_exact_transport(monkeypatch, fingerprint, stock_limit):
  from openpilot.nrdr.tests.test_rdx_route_a import MODIFIED, simulate_receipt
  from openpilot.nrdr.features.lateral.controller_selection import RDX_PROFILE, firmware_controller_profile
  cp = car_structs.CarParams.new_message(
    brand="honda", carFingerprint=fingerprint, carVin="TEST1234567890123", fingerprintSource="fw",
    carFw=[{"ecu": "eps", "address": 0x18DA30F1, "fwVersion": b"39990-TJB,A220\0\0"}])
  cp.lateralTuning.init("pid")
  simulate_receipt(monkeypatch, cp)
  cp.lateralParams.torqueBP = cp.lateralParams.torqueV = [0, stock_limit]
  assert firmware_controller_profile(cp, MODIFIED) is None
  cp.lateralParams.torqueBP = cp.lateralParams.torqueV = [0, 4096]
  assert firmware_controller_profile(cp, MODIFIED) is RDX_PROFILE
  cp.carFw[0].fwVersion = b"39990-TJB-A220\0\0"
  assert firmware_controller_profile(cp, MODIFIED) is None


@pytest.mark.parametrize("curvature", [-.01, -.001, .001, .01])
def test_lane_change_shaping_reduces_request_without_reversing_it(curvature):
  control = controller()
  shaped = shape_lane_change_curvature(control.steer_ratio_selection, vehicle_model(), 15., 15., .01, curvature, 5.)
  assert min(0., curvature) <= shaped <= max(0., curvature)
  assert abs(shaped) < abs(curvature)


@pytest.mark.parametrize("speed, delay", [(5., .145), (12.5, .135), (20., .125)])
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


@pytest.mark.parametrize("firmware", (b"39990-TLA-A040", b"39990-TLA-A220"))
@pytest.mark.parametrize("steer_max", (1., .5))
def test_crv_saturation_uses_the_lower_of_the_row_ceiling_and_host_limit(firmware, steer_max):
  control = controller(fingerprint="HONDA_CRV_5G", firmware=firmware)
  control.steer_max = steer_max
  limit = min(steer_max, 3841 / 4096)
  for _ in range(200):
    output, _, logged = tick(control, angle=0., speed=20., desired=100.)
    assert abs(output) <= limit
  assert output == pytest.approx(limit, abs=1e-6)
  assert logged.saturated
