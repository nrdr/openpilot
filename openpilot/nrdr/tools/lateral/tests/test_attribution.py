import json
from types import SimpleNamespace

import pytest

from openpilot.nrdr.tools.lateral.attribution import (
  ControlSample,
  classify_attribution,
  extract_controller_reading,
  is_fresh,
  lane_observation,
  logged_steer_ratio_model_policy,
  summarize_controls,
)
from openpilot.nrdr.features.lateral.model_policy import SteerRatioModelPolicy


def _lateral_state(which: str, state):
  return SimpleNamespace(which=lambda: which, **{which: state})


def _curve_model(path_offset: float, lane_prob: float = 0.9):
  x = [0.0, 10.0, 20.0, 30.0]
  center = [0.0, 0.3, 1.0, 2.0]
  left = SimpleNamespace(x=x, y=[value - 1.75 for value in center])
  right = SimpleNamespace(x=x, y=[value + 1.75 for value in center])
  unused = SimpleNamespace(x=x, y=center)
  position = SimpleNamespace(x=x, y=[value + path_offset for value in center], yStd=[0.1] * len(x))
  return SimpleNamespace(
    laneLines=[unused, left, right, unused],
    laneLineProbs=[0.0, lane_prob, lane_prob, 0.0],
    laneLineStds=[1.0, 0.1, 0.1, 1.0],
    position=position,
  )


def test_extracts_clarity_pid_compatibility_wrapper():
  torque = SimpleNamespace(active=True, error=2.0, p=0.2, i=0.1, f=0.3, output=0.6, saturated=False)
  reading = extract_controller_reading(_lateral_state("torqueState", torque), "HONDA_CLARITY", 10.0, 12.0)

  assert reading is not None
  assert reading.kind == "clarityPidWrappedInTorqueState"
  assert reading.desired_angle_deg == 12.0
  assert reading.angle_error_deg == 2.0


def test_does_not_mislabel_native_torque_state_as_pid():
  torque = SimpleNamespace(active=True, error=0.2, p=0.2, i=0.1, f=0.3, output=0.6, saturated=False)
  assert extract_controller_reading(_lateral_state("torqueState", torque), "HONDA_CIVIC", 10.0, 12.0) is None
  assert extract_controller_reading(_lateral_state("torqueState", torque), "HONDA_CLARITY", 10.0, 12.0, True) is None


def test_clarity_exact_firmware_vgr_remains_pid_when_nnlc_toggle_is_on():
  torque = SimpleNamespace(active=True, error=2.0, p=0.2, i=0.1, f=0.3, output=0.6, saturated=False)
  reading = extract_controller_reading(_lateral_state("torqueState", torque), "HONDA_CLARITY", 10.0, 12.0, True, True)
  assert reading is not None
  assert reading.kind == "clarityPidWrappedInTorqueState"


@pytest.mark.parametrize(("artifact_sha256", "expected"), (
  ("c48899574c1303e47ca2a6f80113876ca5eb749c4a75c89b53cc8029bb3bb710",
   SteerRatioModelPolicy.LEGACY_DUAL_BP),
  ("92d06467e4de97c40ffdc366e385a4f5897f36fc8ea632bd9bed113a3083fea8",
   SteerRatioModelPolicy.PURE_FIRMWARE_VGR),
))
def test_logged_bundle_uses_exact_artifact_policy(artifact_sha256, expected):
  raw_bundle = json.dumps({
    "models": [{"artifact": {"downloadUri": {"sha256": artifact_sha256}}}],
  })
  assert logged_steer_ratio_model_policy(raw_bundle) is expected


@pytest.mark.parametrize("raw_bundle", (None, "", "{malformed", json.dumps({"models": []})))
def test_logged_missing_or_malformed_bundle_is_unknown(raw_bundle):
  assert logged_steer_ratio_model_policy(raw_bundle) is SteerRatioModelPolicy.UNKNOWN


def test_freshness_rejects_future_and_stale_timestamps():
  assert is_fresh(10.0, 9.8, 0.25)
  assert not is_fresh(10.0, 10.01, 0.25)
  assert not is_fresh(10.0, 9.7, 0.25)


@pytest.mark.parametrize(("curvature", "path_offset"), ((0.002, 0.25), (-0.002, -0.25)))
def test_lane_offset_is_positive_toward_inside_for_both_turn_directions(curvature, path_offset):
  observation, rejection = lane_observation(_curve_model(path_offset), curvature, 20.0)

  assert rejection is None
  assert observation is not None
  assert observation.inside_offset_m == pytest.approx(0.25)
  assert observation.confidence == "high"


def test_lane_confidence_gate_rejects_weak_lines():
  observation, rejection = lane_observation(_curve_model(0.25, lane_prob=0.4), 0.002, 20.0)
  assert observation is None
  assert rejection == "lane confidence"


def _control_sample(phase: str, yaw_ratio: float = 0.98) -> ControlSample:
  desired_angle = 15.0
  steering_rate = {"turn-in": 3.0, "steady": 0.0, "unwind": -3.0}[phase]
  return ControlSample(
    "route", "cohort", 1.0, "clarityPidWrappedInTorqueState", 25.0,
    desired_angle, 14.0, steering_rate, 0.002, 0.002, yaw_ratio * 0.002,
    0.10, 0.03, 0.04, 0.17, False, True,
  )


def test_summary_reports_tracking_and_p_i_feedforward_contributions():
  overall, bins = summarize_controls(
    [_control_sample("turn-in") for _ in range(40)],
    30,
    (5.0, 65.0),
    (3.0, 45.0),
  )

  assert overall["yaw_to_desired_median"] == pytest.approx(0.98)
  assert overall["angle_error_aligned_median_deg"] == pytest.approx(1.0)
  assert overall["p_abs_share"] == pytest.approx(0.10 / 0.17)
  assert overall["output_minus_raw_p_i_f_aligned_median"] == pytest.approx(0.0)
  assert "before_nrdr_scaling" in overall["term_scope"]
  assert bins[0]["phase"] == "turn-in"


def test_verdict_attributes_inside_path_when_yaw_tracks_and_angle_is_under_target():
  overall = {
    "yaw_to_desired_median": 0.98,
    "yaw_overtrack_fraction": 0.05,
    "angle_error_aligned_median_deg": 1.0,
    "actual_under_target_fraction": 0.80,
    "vehicle_model_to_yaw_median": 1.0,
    "p_aligned_median": 0.1,
    "p_abs_share": 0.60,
    "i_abs_share": 0.15,
    "feedforward_abs_share": 0.25,
  }
  lanes = [
    {"lookahead_m": distance, "accepted_frames": 100, "accepted_fraction": 0.80,
     "inside_offset_median_m": 0.25, "inside_fraction": 0.85, "high_confidence_fraction": 0.75}
    for distance in (10.0, 20.0, 30.0)
  ]
  delay = {"effective_min_s": 0.15, "effective_max_s": 0.15}
  matched = {"both_directions": True, "matched_directions": ["left", "right"],
             "matched_speed_angle_bands": [{"speed_mph": [35, 50], "angle_deg": [10, 20]}]}

  verdict = classify_attribution(overall, [], lanes, delay, mixed_cohorts=False, matched=matched)

  assert verdict["primary"] == "model_path_inside_detected_lane"
  assert verdict["confidence"] == "high"
  assert verdict["p_i_feedforward"]["tracking_evidence"] == "P_is_correcting_remaining_error_not_driving_angle_overshoot"
  assert verdict["causal_comparison"] is False
  assert "cannot_separate_planner" in verdict["model_path_source_ambiguity"]


@pytest.mark.parametrize(("mixed", "matched", "delay"), (
  (True, {"both_directions": True, "matched_directions": ["left", "right"], "matched_speed_angle_bands": []}, (0.15, 0.15)),
  (False, {"both_directions": False, "matched_directions": ["left"], "matched_speed_angle_bands": []}, (0.15, 0.15)),
  (False, {"both_directions": True, "matched_directions": ["left", "right"], "matched_speed_angle_bands": []}, (0.15, 0.60)),
))
def test_confounded_path_evidence_is_never_high(mixed, matched, delay):
  overall = {
    "yaw_to_desired_median": 0.98, "yaw_overtrack_fraction": 0.0,
    "angle_error_aligned_median_deg": 1.0, "actual_under_target_fraction": 0.8,
    "vehicle_model_to_yaw_median": 1.0, "p_aligned_median": 0.1,
    "p_abs_share": 0.6, "i_abs_share": 0.2, "feedforward_abs_share": 0.2,
  }
  lanes = [{"lookahead_m": distance, "accepted_frames": 100, "accepted_fraction": 0.8,
            "inside_offset_median_m": 0.25, "inside_fraction": 0.85, "high_confidence_fraction": 0.75}
           for distance in (10.0, 20.0)]
  verdict = classify_attribution(overall, [], lanes, {"effective_min_s": delay[0], "effective_max_s": delay[1]}, mixed, matched)
  assert verdict["primary"] == "model_path_inside_detected_lane"
  assert verdict["confidence"] != "high"
  assert "bilateral" not in verdict["steer_ratio"]


def test_phase_lag_is_not_claimed_as_a_unique_live_delay_cause():
  overall = {
    "yaw_to_desired_median": 0.90,
    "yaw_overtrack_fraction": 0.0,
    "angle_error_aligned_median_deg": 1.0,
    "actual_under_target_fraction": 0.8,
    "vehicle_model_to_yaw_median": 1.0,
    "p_aligned_median": 0.1,
    "p_abs_share": 0.6,
    "i_abs_share": 0.2,
    "feedforward_abs_share": 0.2,
  }
  bins = [
    {"phase": "turn-in", "angle_deg": [10.0, 20.0], "yaw_to_desired_median": 0.70},
    {"phase": "steady", "angle_deg": [10.0, 20.0], "yaw_to_desired_median": 0.98},
  ]
  delay = {"effective_min_s": 0.15, "effective_max_s": 0.15}

  verdict = classify_attribution(overall, bins, [], delay, mixed_cohorts=False)

  assert verdict["primary"] == "dynamic_phase_lag_observed"
  assert verdict["live_delay"] == "phase_lag_present_but_live_delay_not_isolated"
