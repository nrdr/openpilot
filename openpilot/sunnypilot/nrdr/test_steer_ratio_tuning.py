import pytest

from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  STEER_RATIO_ENDPOINT_PROFILES,
  get_steer_ratio_endpoint_profile,
)


@pytest.mark.parametrize("profile", STEER_RATIO_ENDPOINT_PROFILES)
def test_profiles_are_monotonic(profile):
  assert profile.breakpoints[0] == 0.0
  assert profile.breakpoints[1] > 0.0
  assert profile.center_default > profile.outer_default > 0.0


@pytest.mark.parametrize("profile", STEER_RATIO_ENDPOINT_PROFILES)
def test_fingerprint_lookup(profile):
  for fingerprint in profile.fingerprints:
    assert get_steer_ratio_endpoint_profile(fingerprint) is profile


def test_unknown_fingerprint_has_no_profile():
  assert get_steer_ratio_endpoint_profile("UNKNOWN") is None
