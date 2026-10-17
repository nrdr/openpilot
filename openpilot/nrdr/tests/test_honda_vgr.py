from types import SimpleNamespace

import pytest

from openpilot.nrdr.features.lateral.honda_vgr import (
  HONDA_VGR_PROFILES,
  Q14,
  RAW_UNITS_PER_DEGREE,
  get_honda_vgr_profile,
  normalize_honda_eps_firmware,
)
from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode, resolve_steer_ratio_selection




def _car_params(fingerprint: str, firmware, *, brand: str = "honda", ecu: str = "eps", steer_ratio: float = 16.5):
  car_fw = [SimpleNamespace(ecu=ecu, fwVersion=firmware)]
  return SimpleNamespace(brand=brand, carFingerprint=fingerprint, carFw=car_fw, steerRatio=steer_ratio)


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


def test_brand_matching_is_case_normalized_but_not_spoofable():
  assert get_honda_vgr_profile(_car_params("HONDA_CLARITY", b"39990-TRW-A020", brand="HONDA")) is not None
  assert get_honda_vgr_profile(_car_params("HONDA_CLARITY", b"39990-TRW-A020", brand="toyota")) is None


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


def test_explicit_firmware_mode_uses_cp_anchor_and_never_manual_center():
  CP = _car_params("HONDA_CLARITY", b"39990-TRW-A020", steer_ratio=16.5)
  selection = resolve_steer_ratio_selection(CP, {
    "NrdrSteerRatioMode": 3,
    "NrdrSteerRatioManualCenter": 25.0,
    "NrdrSteerRatioManualFinal": 8.0,
  })

  assert selection.effective_mode is SteerRatioMode.FIRMWARE
  assert selection.ratio_at(0.0) == pytest.approx(16.5)
  assert selection.ratio_at(300.0) == pytest.approx(16.5)
  assert selection.physicalize_desired_angle(120.0) != pytest.approx(120.0)


def test_unrecognized_firmware_mode_is_whole_controller_cp_fallback():
  CP = _car_params("HONDA_CLARITY", b"39990-TRW-UNKNOWN", steer_ratio=16.5)
  selection = resolve_steer_ratio_selection(CP, {
    "NrdrSteerRatioMode": 3,
    "NrdrSteerRatioManualCenter": 15.38,
    "NrdrSteerRatioManualFinal": 10.93,
  })

  assert selection.effective_mode is None
  assert selection.ratio_at(0.0) == selection.ratio_at(450.0) == pytest.approx(16.5)
  assert "No exact recognized EPS firmware profile" in selection.unavailable_reason
