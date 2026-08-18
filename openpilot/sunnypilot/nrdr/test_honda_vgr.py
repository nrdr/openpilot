from types import SimpleNamespace
import sys

import numpy as np
import pytest

from openpilot.sunnypilot.nrdr.honda_vgr import (
  HONDA_VGR_PROFILES,
  Q14,
  RAW_UNITS_PER_DEGREE,
  get_honda_vgr_profile,
  normalize_honda_eps_firmware,
)
from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  FIRMWARE_LEGACY_BLEND_END_DEG,
  FIRMWARE_LEGACY_BLEND_START_DEG,
  FirmwareLegacySteerRatioCurve,
  dual_bp_desired_angle,
  dual_bp_ratio,
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
  from openpilot.sunnypilot.nrdr.latcontrol_pid import _center_boost_angle_fade

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
  from openpilot.sunnypilot.nrdr.latcontrol_pid import _center_boost

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
  from openpilot.sunnypilot.nrdr.latcontrol_pid import _center_boost

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


def _endpoint_profile(vgr_profile):
  return get_steer_ratio_endpoint_profile(vgr_profile.fingerprints[0])


def _firmware_legacy_curve(vgr_profile):
  endpoint = _endpoint_profile(vgr_profile)
  return FirmwareLegacySteerRatioCurve(
    vgr_profile, endpoint.center_default, endpoint.outer_default, endpoint.outer_angle,
  )


@pytest.mark.parametrize("vgr_profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_firmware_legacy_curve_is_valid_symmetric_and_monotonic(vgr_profile):
  curve = _firmware_legacy_curve(vgr_profile)
  endpoint = _endpoint_profile(vgr_profile)
  assert curve.valid

  final_linear = endpoint.center_default * (endpoint.outer_angle + 50.0) / endpoint.outer_default
  linear_samples = np.linspace(0.0, final_linear, 4001)
  desired = np.array([curve.desired_angle(value) for value in linear_samples])
  assert np.all(np.diff(desired) > 0.0)
  assert np.array([curve.desired_angle(-value) for value in linear_samples]) == pytest.approx(-desired)


@pytest.mark.parametrize("vgr_profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_firmware_curve_is_exact_through_70_degrees(vgr_profile):
  curve = _firmware_legacy_curve(vgr_profile)
  for physical_angle in (0.0, 35.0, 69.999, FIRMWARE_LEGACY_BLEND_START_DEG):
    linear_angle = vgr_profile.physical_to_linear(physical_angle)
    for signed_linear in (linear_angle, -linear_angle):
      expected = vgr_profile.linear_to_physical(signed_linear)
      assert curve.desired_angle(signed_linear) == expected


@pytest.mark.parametrize("vgr_profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_presolved_legacy_curve_is_exact_from_90_degrees(vgr_profile):
  curve = _firmware_legacy_curve(vgr_profile)
  endpoint = _endpoint_profile(vgr_profile)
  for desired_angle in (FIRMWARE_LEGACY_BLEND_END_DEG, 120.0, endpoint.outer_angle, endpoint.outer_angle + 50.0):
    ratio = dual_bp_ratio(desired_angle, endpoint.center_default, endpoint.outer_default, endpoint.outer_angle)
    linear_angle = endpoint.center_default * desired_angle / ratio
    assert curve.desired_angle(linear_angle) == pytest.approx(desired_angle, abs=1e-10)
    assert dual_bp_desired_angle(
      linear_angle, endpoint.center_default, endpoint.outer_default, endpoint.outer_angle,
    ) == pytest.approx(desired_angle, abs=1e-10)


@pytest.mark.parametrize("vgr_profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_firmware_legacy_handoff_is_c1(vgr_profile):
  curve = _firmware_legacy_curve(vgr_profile)
  step = 1e-3
  for boundary in (curve.transition_start_linear, curve.transition_end_linear):
    value = curve.desired_angle(boundary)
    left_slope = (value - curve.desired_angle(boundary - step)) / step
    right_slope = (curve.desired_angle(boundary + step) - value) / step
    assert left_slope == pytest.approx(right_slope, rel=2e-4, abs=2e-4)


def test_invalid_or_nonmonotonic_handoff_falls_back_to_raw_firmware():
  vgr_profile = HONDA_VGR_PROFILES[0]
  curve = FirmwareLegacySteerRatioCurve(vgr_profile, center_ratio=8.0, outer_ratio=25.0, outer_angle=250.0)
  assert not curve.valid
  for linear_angle in (50.0, 80.0, 150.0, -150.0):
    assert curve.desired_angle(linear_angle) == pytest.approx(vgr_profile.linear_to_physical(linear_angle))


@pytest.mark.parametrize("vgr_profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
@pytest.mark.parametrize(("center_ratio", "outer_ratio"), (
  (8.0, 8.0), (18.5, 8.0), (18.5, 18.5), (25.0, 12.0), (8.0, 25.0), (25.0, 25.0),
))
def test_configured_endpoint_range_is_monotonic_or_uses_exact_fallback(vgr_profile, center_ratio, outer_ratio):
  endpoint = _endpoint_profile(vgr_profile)
  curve = FirmwareLegacySteerRatioCurve(vgr_profile, center_ratio, outer_ratio, endpoint.outer_angle)
  linear_samples = np.linspace(0.0, 500.0, 1001)
  desired = np.array([curve.desired_angle(value) for value in linear_samples])
  if curve.valid:
    assert np.all(np.diff(desired) > 0.0)
  else:
    expected = np.array([vgr_profile.linear_to_physical(value) for value in linear_samples])
    assert desired == pytest.approx(expected)


class _VehicleModel:
  def __init__(self):
    self.sR = 0.0

  def get_steer_from_curvature(self, curvature, _speed, _roll):
    return curvature * self.sR


def _pid_controller(*, legacy: bool, lane_change: bool = False):
  from openpilot.sunnypilot.nrdr.latcontrol_pid import NrdrLatControlPID

  controller = NrdrLatControlPID.__new__(NrdrLatControlPID)
  controller.sr_profile = get_steer_ratio_endpoint_profile("HONDA_CLARITY")
  controller.sr_values = list(controller.sr_profile.default_values)
  controller.vgr_profile = next(profile for profile in HONDA_VGR_PROFILES if profile.name == "Clarity TRW-A020")
  controller.firmware_legacy_sr_curve = FirmwareLegacySteerRatioCurve(
    controller.vgr_profile, controller.sr_values[0], controller.sr_values[-1], controller.sr_profile.outer_angle,
  )
  controller.legacy_dual_bp_sr = legacy
  controller.lane_change_endpoint_sr = True
  controller._lane_change_active = lambda: lane_change
  return controller


@pytest.mark.parametrize("measured_angle", (0.0, 175.0))
@requires_controller
def test_firmware_desired_angle_does_not_depend_on_measured_steering(measured_angle):
  controller = _pid_controller(legacy=False)
  VM = _VehicleModel()
  CS = SimpleNamespace(steeringAngleDeg=measured_angle, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=1.25)

  result = controller._desired_angles(VM, CS, params, desired_curvature=0.10)
  reference = controller._desired_angles(
    _VehicleModel(), SimpleNamespace(steeringAngleDeg=0.0, vEgo=20.0), params, desired_curvature=0.10,
  )
  assert result == pytest.approx(reference)


@requires_controller
def test_firmware_controller_uses_presolved_legacy_curve_above_handoff():
  controller = _pid_controller(legacy=False)
  endpoint = controller.sr_profile
  expected_angle = 120.0
  ratio = dual_bp_ratio(expected_angle, endpoint.center_default, endpoint.outer_default, endpoint.outer_angle)
  linear_angle = endpoint.center_default * expected_angle / ratio
  desired_curvature = -np.radians(linear_angle) / endpoint.center_default

  desired_no_offset, desired_with_offset = controller._desired_angles(
    _VehicleModel(),
    SimpleNamespace(steeringAngleDeg=0.0, vEgo=20.0),
    SimpleNamespace(roll=0.0, angleOffsetDeg=1.25),
    desired_curvature,
  )
  assert desired_no_offset == pytest.approx(expected_angle)
  assert desired_with_offset == pytest.approx(expected_angle + 1.25)


@requires_controller
def test_legacy_desired_angle_retains_measured_angle_ratio_lookup():
  controller = _pid_controller(legacy=True)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)

  centered = controller._desired_angles(
    _VehicleModel(), SimpleNamespace(steeringAngleDeg=0.0, vEgo=20.0), params, desired_curvature=0.01,
  )
  off_center = controller._desired_angles(
    _VehicleModel(), SimpleNamespace(steeringAngleDeg=250.0, vEgo=20.0), params, desired_curvature=0.01,
  )
  assert centered != pytest.approx(off_center)


@requires_controller
def test_unknown_firmware_profile_falls_back_to_legacy_ratio_lookup():
  firmware_controller = _pid_controller(legacy=False)
  firmware_controller.vgr_profile = None
  legacy_controller = _pid_controller(legacy=True)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.75)
  CS = SimpleNamespace(steeringAngleDeg=175.0, vEgo=20.0)

  fallback = firmware_controller._desired_angles(_VehicleModel(), CS, params, desired_curvature=0.01)
  legacy = legacy_controller._desired_angles(_VehicleModel(), CS, params, desired_curvature=0.01)
  assert fallback == legacy


@requires_controller
def test_clarity_hybrid_preserves_trw_firmware_and_enters_firmware_mode():
  from opendbc.car.car_helpers import interfaces
  from opendbc.car.structs import CarParams
  from opendbc.car.honda.values import CAR as HONDA
  from openpilot.common.params import Params
  from openpilot.common.realtime import DT_CTRL
  from openpilot.selfdrive.car.helpers import convert_to_capnp
  from openpilot.sunnypilot.nrdr.latcontrol_clarity_hybrid import LatControlClarityHybrid
  from openpilot.sunnypilot.nrdr.live_params import reset_live_params_for_tests
  from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
  from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt

  settings = Params()
  keys = ("NrdrHandcraftedLateralTune", "NrdrLegacyDualBpSteerRatio")
  previous = {key: settings.get(key) for key in keys}
  try:
    settings.put_bool("NrdrHandcraftedLateralTune", False, block=True)
    settings.put_bool("NrdrLegacyDualBpSteerRatio", False, block=True)
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
    assert not controller.legacy_dual_bp_sr

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


@requires_controller
def test_lane_change_endpoint_bypasses_firmware_map():
  controller = _pid_controller(legacy=False, lane_change=True)
  VM = _VehicleModel()
  CS = SimpleNamespace(steeringAngleDeg=80.0, vEgo=20.0)
  params = SimpleNamespace(roll=0.0, angleOffsetDeg=0.0)
  desired_no_offset, _ = controller._desired_angles(VM, CS, params, desired_curvature=0.01)

  assert VM.sR == controller.sr_values[-1]
  assert desired_no_offset == pytest.approx(np.degrees(-0.01 * controller.sr_values[-1]))
