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

  samples = np.linspace(10.0, 12.0, 101)
  factors = np.array([_center_boost(angle, 0.0, 1.0, 1.0, 10.0, 0.0, 2.0) for angle in samples])
  assert factors[0] == 2.0
  assert factors[50] == pytest.approx(1.5)
  assert factors[-1] == 1.0
  assert np.all(np.diff(factors) <= 0.0)


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
  for linear_angle in (0.0, 4.25, 23.75, 90.0, last_linear_knot * 0.9, last_linear_knot * 1.25):
    physical_angle = profile.linear_to_physical(linear_angle)
    assert profile.linear_to_physical(-linear_angle) == pytest.approx(-physical_angle)
    assert profile.physical_to_linear(physical_angle) == pytest.approx(linear_angle, abs=1e-8)
    assert profile.physical_to_linear(-physical_angle) == pytest.approx(-linear_angle, abs=1e-8)

  tail_linear = last_linear_knot * 1.25
  assert profile.linear_to_physical(tail_linear) == pytest.approx(tail_linear * profile.tail_scale)


@pytest.mark.parametrize("profile", HONDA_VGR_PROFILES, ids=lambda profile: profile.name)
def test_forward_map_slope_matches_finite_difference(profile):
  linear_angle = profile.physical_to_linear(70.0)
  step = 1e-3
  finite_difference = (
    profile.linear_to_physical(linear_angle + step) - profile.linear_to_physical(linear_angle - step)
  ) / (2.0 * step)
  assert profile.linear_to_physical_slope(linear_angle) == pytest.approx(finite_difference, rel=1e-6)
