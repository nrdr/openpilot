import pytest

from openpilot.sunnypilot.nrdr.steer_ratio_tuning import (
  LANE_CHANGE_SR_FADE_SECONDS,
  STEER_RATIO_ENDPOINT_PROFILES,
  LaneChangeSteerRatioFade,
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


def test_lane_change_fade_starts_at_outer_and_is_linear_for_exactly_1_5_seconds():
  fade = LaneChangeSteerRatioFade(dt=0.25)

  assert fade.update(False) == 0.0
  assert fade.update(True) == 1.0
  assert fade.update(True) == pytest.approx(1.0 - 0.25 / LANE_CHANGE_SR_FADE_SECONDS)
  assert fade.update(True) == pytest.approx(1.0 - 0.50 / LANE_CHANGE_SR_FADE_SECONDS)
  assert fade.update(True) == pytest.approx(1.0 - 0.75 / LANE_CHANGE_SR_FADE_SECONDS)
  assert fade.update(True) == pytest.approx(1.0 - 1.00 / LANE_CHANGE_SR_FADE_SECONDS)
  assert fade.update(True) == pytest.approx(1.0 - 1.25 / LANE_CHANGE_SR_FADE_SECONDS)
  assert fade.update(True) == 0.0
  assert fade.update(True) == 0.0


def test_pre_lane_change_wait_does_not_consume_fade():
  fade = LaneChangeSteerRatioFade(dt=0.25)

  assert all(fade.update(False) == 0.0 for _ in range(40))
  assert fade.update(True) == 1.0


def test_lane_change_fade_continues_after_lane_change_ends_and_does_not_jump_at_end():
  fade = LaneChangeSteerRatioFade(dt=0.5)

  assert fade.update(True) == 1.0
  assert fade.update(False) == pytest.approx(2.0 / 3.0)
  assert fade.update(False) == pytest.approx(1.0 / 3.0)
  assert fade.update(False) == 0.0


def test_lane_change_fade_reset_and_retrigger_start_from_outer():
  fade = LaneChangeSteerRatioFade(dt=0.5)

  assert fade.update(True) == 1.0
  assert fade.update(True) == pytest.approx(2.0 / 3.0)
  fade.reset()
  assert fade.update(False) == 0.0
  assert fade.update(True) == 1.0
  assert fade.update(False) == pytest.approx(2.0 / 3.0)
  assert fade.update(True) == 1.0
