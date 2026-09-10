import pytest

from openpilot.nrdr.features.lateral.steer_ratio_tuning import (
  STEER_RATIO_METADATA,
  SteerRatioMode,
  SteerRatioModeLatch,
  get_steer_ratio_metadata,
  resolve_steer_ratio_selection,
)


@pytest.mark.parametrize("profile", STEER_RATIO_METADATA)
def test_profiles_are_monotonic(profile):
  assert profile.outer_angle > 0.0


@pytest.mark.parametrize("profile", STEER_RATIO_METADATA)
def test_fingerprint_lookup(profile):
  for fingerprint in profile.fingerprints:
    assert get_steer_ratio_metadata(fingerprint) is profile


def test_unknown_fingerprint_has_no_profile():
  assert get_steer_ratio_metadata("UNKNOWN") is None


def test_mode_latch_replaces_retired_lane_change_geometry_fade():
  CP = type("CP", (), {"brand": "honda", "carFingerprint": "HONDA_CLARITY", "steerRatio": 16.5, "carFw": []})()
  manual = resolve_steer_ratio_selection(CP, {
    "NrdrSteerRatioMode": 0,
    "NrdrSteerRatioManualCenter": 15.38,
    "NrdrSteerRatioManualFinal": 10.93,
  })
  comma = resolve_steer_ratio_selection(CP, {
    "NrdrSteerRatioMode": 1,
    "NrdrSteerRatioManualCenter": 15.38,
    "NrdrSteerRatioManualFinal": 10.93,
  })
  latch = SteerRatioModeLatch(manual)

  assert latch.update(comma, active=True) is manual
  assert latch.pending is comma
  assert latch.update(comma, active=False).effective_mode is SteerRatioMode.COMMA
