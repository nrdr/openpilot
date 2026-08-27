from types import SimpleNamespace
import sys

import numpy as np
import pytest

from openpilot.nrdr.features.lateral.honda_vgr import (
  HONDA_VGR_PROFILES,
  Q14,
  RAW_UNITS_PER_DEGREE,
  get_honda_vgr_profile,
  normalize_honda_eps_firmware,
)
from openpilot.nrdr.features.lateral.model_policy import SteerRatioModelPolicy
from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  LaneChangeSteerRatioFade,
  get_steer_ratio_endpoint_profile,
)


requires_controller = pytest.mark.skipif(sys.platform == "win32", reason="latcontrol_pid requires openpilot's Linux runtime")


def _car_params(fingerprint: str, firmware, *, brand: str = "honda", ecu: str = "eps"):
  car_fw = [SimpleNamespace(ecu=ecu, fwVersion=firmware)]
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint, carFw=car_fw)


@pytest.mark.parametrize("profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_firmware_position_maps_are_monotonic(profile):
  assert profile.position_x[0] == 0
  assert len(profile.position_x) == len(profile.position_y) == len(profile.physical_knots)
  assert all(a < b for a, b in zip(profile.position_x, profile.position_x[1:], strict=False))
  assert all(divisor > 0 for divisor in profile.position_y)
  assert all(a < b for a, b in zip(profile.physical_knots, profile.physical_knots[1:], strict=False))


@pytest.mark.parametrize(
  ("raw", "normalized"),
  (
    (b"39990,TRW,A020\0ignored", "39990-TRW-A020"),
    ("39990,TBA,C120\0ignored", "39990-TBA-C120"),
    (b"39990-TXM-A040", "39990-TXM-A040"),
  ),
)
def test_firmware_normalization(raw, normalized):
  assert normalize_honda_eps_firmware(raw) == normalized


@pytest.mark.parametrize(
  ("fingerprint", "firmware", "profile_name"),
  (
    ("HONDA_CLARITY", b"39990,TRW,A020\0junk", "Clarity TRW-A020"),
    ("HONDA_CIVIC", b"39990-TBA-A030", "Civic C120/A030/TEG"),
    ("HONDA_CIVIC", b"39990-TEG-A010", "Civic C120/A030/TEG"),
    ("HONDA_CIVIC_BOSCH", b"39990-TBA-C120", "Civic C120/A030/TEG"),
    ("HONDA_CIVIC_BOSCH", b"39990-TBA-C020", "Civic C020/TGG-A120"),
    ("HONDA_CIVIC_BOSCH", b"39990-TGG-A120", "Civic C020/TGG-A120"),
    ("HONDA_CRV_5G", b"39990-TLA-A040", "CR-V TLA-A040"),
    ("HONDA_INSIGHT", b"39990-TXM-A040", "Insight TXM-A040"),
  ),
)
def test_exact_firmware_and_fingerprint_select_profile(fingerprint, firmware, profile_name):
  assert get_honda_vgr_profile(_car_params(fingerprint, firmware)).name == profile_name


@pytest.mark.parametrize(
  "CP",
  (
    _car_params("HONDA_CIVIC", b"39990-TBA-C020"),
    _car_params("HONDA_CIVIC", b"39990-TBA-C120"),
    _car_params("HONDA_CIVIC_BOSCH", b"39990-TBA-A030"),
    _car_params("HONDA_CLARITY", b"39990-TRW-UNKNOWN"),
    _car_params("HONDA_CLARITY", b"39990-TRW-A020", ecu="engine"),
    _car_params("HONDA_CLARITY", b"39990-TRW-A020", brand="toyota"),
  ),
)
def test_wrong_fingerprint_or_unknown_firmware_does_not_select_profile(CP):
  assert get_honda_vgr_profile(CP) is None


@requires_controller
def test_civic_teg_center_boost_fade_is_exactly_scoped():
  from openpilot.nrdr.features.lateral.latcontrol_pid import _center_boost_angle_fade

  assert _center_boost_angle_fade(_car_params("HONDA_CIVIC", b"39990-TEG-A010")) == 2.0
  for CP in (
    _car_params("HONDA_CIVIC", b"39990-TBA-A030"),
    _car_params("HONDA_CIVIC_BOSCH", b"39990-TBA-C120"),
    _car_params("HONDA_CIVIC_BOSCH", b"39990-TBA-C020"),
    _car_params("HONDA_CIVIC", b"39990-TEG-UNKNOWN"),
    _car_params("HONDA_CLARITY", b"39990-TRW-A020"),
  ):
    assert _center_boost_angle_fade(CP) == 1.0


@requires_controller
def test_civic_teg_center_boost_smooths_only_the_ten_to_twelve_degree_handoff():
  from openpilot.nrdr.features.lateral.latcontrol_pid import _center_boost

  values = {
    angle: _center_boost(angle, v_ego=0.0, fade=1.0, magnitude=1.0,
                         threshold=10.0, minimum_speed=0.0, angle_fade=2.0)
    for angle in (0.0, 10.0, 11.0, 12.0, 20.0, 70.0, 90.0, -12.0, -70.0, -90.0)
  }
  assert values == {
    0.0: 2.0, 10.0: 2.0, 11.0: 1.5, 12.0: 1.0, 20.0: 1.0, 70.0: 1.0, 90.0: 1.0,
    -12.0: 1.0, -70.0: 1.0, -90.0: 1.0,
  }
  assert _center_boost(-11.0, 0.0, 1.0, 1.0, 10.0, 0.0, 2.0) == values[11.0]
  assert _center_boost(4.0, 0.0, 1.0, 1.0, 3.0, 0.0, 2.0) == 1.5
  assert _center_boost(5.0, 0.0, 1.0, 1.0, 3.0, 0.0, 2.0) == 1.0

  samples = np.linspace(10.0, 12.0, 101)
  factors = np.array([_center_boost(angle, 0.0, 1.0, 1.0, 10.0, 0.0, 2.0) for angle in samples])
  assert np.all(np.diff(factors) <= 0.0)
  assert np.all((1.0 <= factors) & (factors <= 2.0))


@requires_controller
def test_non_teg_center_boost_retains_the_existing_one_degree_fade():
  from openpilot.nrdr.features.lateral.latcontrol_pid import _center_boost

  for angle in (0.0, 9.9, 10.0, 10.25, 10.5, 10.999, 11.0, 12.0, 70.0):
    expected = 1.0 + np.clip(11.0 - abs(angle), 0.0, 1.0)
    assert _center_boost(angle, 0.0, 1.0, 1.0, 10.0, 0.0) == expected


@pytest.mark.parametrize("profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_forward_map_matches_firmware_formula_inside_segment(profile):
  index = len(profile.position_x) // 2
  raw = (profile.position_x[index] + profile.position_x[index + 1]) / 2.0
  divisor = (profile.position_y[index] + profile.position_y[index + 1]) / 2.0
  linear_angle = raw * Q14 / (profile.center_divisor * RAW_UNITS_PER_DEGREE)
  expected_physical_angle = raw * Q14 / (divisor * RAW_UNITS_PER_DEGREE)

  assert profile.linear_to_physical(linear_angle) == pytest.approx(expected_physical_angle)


@pytest.mark.parametrize("profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_forward_inverse_roundtrip_sign_symmetry_and_tail_continuation(profile):
  last_linear_knot = profile.position_x[-1] * Q14 / (profile.center_divisor * RAW_UNITS_PER_DEGREE)
  samples = (0.0, 4.25, 23.75, 90.0, last_linear_knot * 0.9, last_linear_knot * 1.25)

  for linear_angle in samples:
    physical_angle = profile.linear_to_physical(linear_angle)
    assert profile.linear_to_physical(-linear_angle) == pytest.approx(-physical_angle)
    assert profile.physical_to_linear(physical_angle) == pytest.approx(linear_angle, abs=1e-8)
    assert profile.physical_to_linear(-physical_angle) == pytest.approx(-linear_angle, abs=1e-8)

  tail_linear = last_linear_knot * 1.25
  expected_tail = tail_linear * profile.center_divisor / profile.position_y[-1]
  assert profile.linear_to_physical(tail_linear) == pytest.approx(expected_tail)
  assert profile.linear_to_physical(tail_linear) > profile.physical_knots[-1]


@pytest.mark.parametrize("profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_forward_map_slope_matches_finite_difference(profile):
  linear_angle = profile.physical_to_linear(70.0)
  step = 1e-3
  finite_difference = (
    profile.linear_to_physical(linear_angle + step) - profile.linear_to_physical(linear_angle - step)
  ) / (2.0 * step)
  assert profile.linear_to_physical_slope(linear_angle) == pytest.approx(finite_difference, rel=1e-6)


class _VehicleModel:
  def __init__(self):
    self.sR = 0.0

  def get_steer_from_curvature(self, curvature, _speed, _roll):
    return curvature * self.sR


def _pid_controller(*, policy: SteerRatioModelPolicy, lane_change: bool = False):
  from openpilot.nrdr.features.lateral.latcontrol_pid import NrdrLatControlPID

  controller = NrdrLatControlPID.__new__(NrdrLatControlPID)
  controller.sr_profile = get_steer_ratio_endpoint_profile("HONDA_CLARITY")
  controller.sr_values = list(controller.sr_profile.default_values)
  controller.vgr_profile = next(profile for profile in HONDA_VGR_PROFILES if profile.name == "Clarity TRW-A020")
  controller.model_sr_policy = policy
  controller.lane_change_endpoint_sr = True
  controller.lane_change_sr_fade = LaneChangeSteerRatioFade(dt=0.5)
  controller._lane_change_active = lambda: lane_change
  controller._lane_change_starting_for_test = lane_change
  controller._lane_change_starting = lambda: controller._lane_change_starting_for_test
  return controller


@pytest.mark.parametrize("policy", (SteerRatioModelPolicy.PURE_FIRMWARE_VGR, SteerRatioModelPolicy.UNKNOWN))
@pytest.mark.parametrize("measured_angle", (0.0, 175.0))
@requires_controller
def test_firmware_desired_angle_does_not_depend_on_measured_steering(policy, measured_angle):
  controller = _pid_controller(policy=policy)
  VM = _VehicleModel()
  CS = SimpleNamespace(steeringAngleDeg=measured_angle, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=1.25)

  result = controller._desired_angles(VM, CS, params, desired_curvature=0.10)
  reference = controller._desired_angles(
    _VehicleModel(), SimpleNamespace(steeringAngleDeg=0.0, vEgo=20.0), params, desired_curvature=0.10,
  )
  assert result == pytest.approx(reference)


@requires_controller
@pytest.mark.parametrize("linear_angle", (35.0, 80.0, 120.0, 220.0, -220.0))
@pytest.mark.parametrize("policy", (SteerRatioModelPolicy.PURE_FIRMWARE_VGR, SteerRatioModelPolicy.UNKNOWN))
def test_firmware_controller_uses_raw_eps_map_at_every_angle(policy, linear_angle):
  controller = _pid_controller(policy=policy)
  desired_curvature = -np.radians(linear_angle) / controller.sr_values[0]
  VM = _VehicleModel()
  VM.sR = 13.75

  desired_no_offset, desired_with_offset = controller._desired_angles(
    VM, SimpleNamespace(steeringAngleDeg=175.0, vEgo=20.0),
    SimpleNamespace(roll=0.0, angleOffsetDeg=1.25), desired_curvature,
  )
  expected = controller.vgr_profile.linear_to_physical(linear_angle)
  assert desired_no_offset == pytest.approx(expected)
  assert desired_with_offset == pytest.approx(expected + 1.25)
  assert VM.sR == 13.75


@requires_controller
def test_legacy_desired_angle_retains_measured_angle_ratio_lookup():
  controller = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)

  centered = controller._desired_angles(
    _VehicleModel(), SimpleNamespace(steeringAngleDeg=0.0, vEgo=20.0), params, desired_curvature=0.01,
  )
  off_center = controller._desired_angles(
    _VehicleModel(), SimpleNamespace(steeringAngleDeg=250.0, vEgo=20.0), params, desired_curvature=0.01,
  )
  assert centered != pytest.approx(off_center)


@pytest.mark.parametrize("policy", (SteerRatioModelPolicy.PURE_FIRMWARE_VGR, SteerRatioModelPolicy.UNKNOWN))
@requires_controller
def test_pure_or_unknown_model_without_exact_firmware_leaves_stock_vehicle_model_untouched(policy):
  controller = _pid_controller(policy=policy)
  controller.vgr_profile = None
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.75)
  CS = SimpleNamespace(steeringAngleDeg=175.0, vEgo=20.0)
  VM = _VehicleModel()
  VM.sR = 14.25

  desired_no_offset, desired_with_offset = controller._desired_angles(VM, CS, params, desired_curvature=0.01)
  assert desired_no_offset == pytest.approx(np.degrees(-0.01 * 14.25))
  assert desired_with_offset == pytest.approx(desired_no_offset + 0.75)
  assert VM.sR == 14.25


@requires_controller
def test_legacy_model_uses_dual_bp_without_exact_firmware_map():
  controller = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP)
  controller.vgr_profile = None
  VM = _VehicleModel()
  CS = SimpleNamespace(steeringAngleDeg=250.0, vEgo=20.0)
  controller._desired_angles(VM, CS, SimpleNamespace(roll=0.0, angleOffsetDeg=0.0), desired_curvature=0.01)
  assert VM.sR == pytest.approx(controller.sr_values[-1])


@requires_controller
def test_clarity_hybrid_preserves_trw_firmware_and_enters_firmware_mode():
  from opendbc.car.car_helpers import interfaces
  from opendbc.car.structs import CarParams
  from opendbc.car.honda.values import CAR as HONDA
  from openpilot.common.params import Params
  from openpilot.common.realtime import DT_CTRL
  from openpilot.selfdrive.car.helpers import convert_to_capnp
  from openpilot.nrdr.features.lateral.latcontrol_clarity_hybrid import LatControlClarityHybrid
  from openpilot.nrdr.params import reset_live_params_for_tests
  from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
  from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt

  settings = Params()
  keys = ("NrdrHandcraftedLateralTune", "ModelManager_ActiveBundle")
  previous = {key: settings.get(key) for key in keys}
  try:
    settings.put_bool("NrdrHandcraftedLateralTune", False, block=True)
    settings.remove("ModelManager_ActiveBundle")
    reset_live_params_for_tests()

    CarInterface = interfaces[HONDA.HONDA_CLARITY]
    CP = CarInterface.get_non_essential_params(HONDA.HONDA_CLARITY)
    CP.carFw = [CarParams.CarFw(ecu=CarParams.Ecu.eps, fwVersion=b"39990-TRW-A020")]
    CP_SP = CarInterface.get_non_essential_params_sp(CP, HONDA.HONDA_CLARITY)
    CI = CarInterface(CP, CP_SP)
    sunnypilot_interfaces.setup_interfaces(CI, settings)

    controls_ext = ControlsExt.__new__(ControlsExt)
    controls_ext.CP = CP.as_reader()
    controls_ext.CP_SP = convert_to_capnp(CP_SP).as_reader()
    controls_ext.params = settings
    hybrid = controls_ext.initialize_lateral_control(object(), CI, DT_CTRL)

    assert isinstance(hybrid, LatControlClarityHybrid)
    controller = hybrid.pid_controller.nrdr_controller
    assert controller is not None
    assert controller.vgr_profile is not None
    assert controller.vgr_profile.name == "Clarity TRW-A020"
    assert controller.model_sr_policy is SteerRatioModelPolicy.UNKNOWN
    assert controller.firmware_vgr_selected

    VM = _VehicleModel()
    CS = SimpleNamespace(steeringAngleDeg=175.0, vEgo=20.0)
    live = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
    desired_no_offset, _ = controller._desired_angles(VM, CS, live, desired_curvature=0.01)
    linear_angle = np.degrees(-0.01 * controller.sr_values[0])
    assert desired_no_offset == pytest.approx(controller.vgr_profile.linear_to_physical(linear_angle))
  finally:
    for key, value in previous.items():
      if value is None:
        settings.remove(key)
      else:
        settings.put(key, value, block=True)
    reset_live_params_for_tests()


@pytest.mark.parametrize("policy", (SteerRatioModelPolicy.PURE_FIRMWARE_VGR, SteerRatioModelPolicy.UNKNOWN))
@requires_controller
def test_pure_and_unknown_firmware_modes_never_apply_lane_change_ratio_fade(policy):
  controller = _pid_controller(policy=policy, lane_change=True)
  VM = _VehicleModel()
  CS = SimpleNamespace(steeringAngleDeg=80.0, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  values = [controller._desired_angles(VM, CS, params, desired_curvature=0.01)[0] for _ in range(4)]
  linear_angle = np.degrees(-0.01 * controller.sr_values[0])
  expected = controller.vgr_profile.linear_to_physical(linear_angle)
  assert values == pytest.approx([expected] * 4)
  assert controller.lane_change_sr_fade._elapsed == controller.lane_change_sr_fade.duration


@requires_controller
def test_lane_change_fade_continues_through_finishing_and_rearms_only_for_a_new_start():
  controller = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP, lane_change=True)
  CS = SimpleNamespace(steeringAngleDeg=80.0, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  expected_endpoint = np.degrees(-0.01 * controller.sr_values[-1])

  first, _ = controller._desired_angles(_VehicleModel(), CS, params, desired_curvature=0.01)
  controller._lane_change_starting_for_test = False
  finishing, _ = controller._desired_angles(_VehicleModel(), CS, params, desired_curvature=0.01)
  after_finish, _ = controller._desired_angles(_VehicleModel(), CS, params, desired_curvature=0.01)
  controller._lane_change_starting_for_test = True
  retriggered, _ = controller._desired_angles(_VehicleModel(), CS, params, desired_curvature=0.01)

  normal_controller = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP)
  expected_normal, _ = normal_controller._desired_angles(
    _VehicleModel(), CS, params, desired_curvature=0.01,
  )
  assert first == pytest.approx(expected_endpoint)
  assert finishing == pytest.approx(expected_normal + (2.0 / 3.0) * (expected_endpoint - expected_normal))
  assert after_finish == pytest.approx(expected_normal + (1.0 / 3.0) * (expected_endpoint - expected_normal))
  assert retriggered == pytest.approx(expected_endpoint)


@requires_controller
def test_lane_change_fade_preserves_legacy_dual_bp_normal_ratio():
  controller = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP, lane_change=True)
  VM = _VehicleModel()
  CS = SimpleNamespace(steeringAngleDeg=80.0, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  normal_ratio = float(np.interp(abs(CS.steeringAngleDeg), controller.sr_profile.breakpoints, controller.sr_values))

  endpoint, _ = controller._desired_angles(VM, CS, params, desired_curvature=0.01)
  fading, _ = controller._desired_angles(VM, CS, params, desired_curvature=0.01)
  controller._desired_angles(VM, CS, params, desired_curvature=0.01)
  normal, _ = controller._desired_angles(VM, CS, params, desired_curvature=0.01)

  assert endpoint == pytest.approx(np.degrees(-0.01 * controller.sr_values[-1]))
  assert fading == pytest.approx(np.degrees(-0.01 * (normal_ratio + (2.0 / 3.0) * (controller.sr_values[-1] - normal_ratio))))
  assert normal == pytest.approx(np.degrees(-0.01 * normal_ratio))
  assert VM.sR == pytest.approx(normal_ratio)


@requires_controller
def test_lane_change_endpoint_disabled_and_unknown_profile_are_noops():
  CS = SimpleNamespace(steeringAngleDeg=80.0, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)

  disabled = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP, lane_change=True)
  disabled.lane_change_endpoint_sr = False
  disabled_vm = _VehicleModel()
  disabled_angle, _ = disabled._desired_angles(disabled_vm, CS, params, desired_curvature=0.01)
  normal_ratio = float(np.interp(abs(CS.steeringAngleDeg), disabled.sr_profile.breakpoints, disabled.sr_values))
  assert disabled_angle == pytest.approx(np.degrees(-0.01 * normal_ratio))

  unknown = _pid_controller(policy=SteerRatioModelPolicy.LEGACY_DUAL_BP, lane_change=True)
  unknown.sr_profile = None
  unknown_vm = _VehicleModel()
  unknown_vm.sR = 14.0
  unknown_angle, _ = unknown._desired_angles(unknown_vm, CS, params, desired_curvature=0.01)
  assert unknown_angle == pytest.approx(np.degrees(-0.01 * 14.0))
