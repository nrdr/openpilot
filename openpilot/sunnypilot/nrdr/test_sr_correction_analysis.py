import math
from dataclasses import replace

import pytest

from openpilot.sunnypilot.nrdr.sr_correction_analysis import (
  CommandSample,
  CorrectionSample,
  GateConfig,
  MappingSample,
  VehicleSample,
  aggregate_bin,
  aggregate_mapping_bin,
  apply_center_bias,
  correction_factor,
  estimate_center_bias,
  make_bin_key,
  mapping_rejection_reason,
  model_effective_ratio,
  nearest_sample,
  phase_from_steering,
  rejection_reason,
  stable_dwell_samples,
)


def command(**overrides) -> CommandSample:
  values = {
    "timestamp": 10.0,
    "desired_curvature": 0.01,
    # openpilot's steering-angle sign is opposite its curvature sign. The
    # analyzer must compare signs within each signal family, not across them.
    "desired_angle_deg": -20.0,
    "lat_active": True,
  }
  values.update(overrides)
  return CommandSample(**values)


def vehicle(**overrides) -> VehicleSample:
  values = {
    "timestamp": 10.2,
    "speed_mps": 10.0,
    "actual_angle_deg": -20.0,
    "steering_rate_deg_s": 0.0,
    "steering_pressed": False,
    "yaw_rate_rad_s": 0.1,
    "yaw_rate_std_rad_s": 0.01,
  }
  values.update(overrides)
  return VehicleSample(**values)


def correction_sample(**overrides) -> CorrectionSample:
  values = {
    "route_id": "route-a",
    "timestamp": 0.1,
    "speed_mps": 10.0,
    "angle_deg": 20.0,
    "direction": "left",
    "phase": "steady",
    "desired_curvature": 0.01,
    "achieved_curvature": 0.01,
    "desired_angle_deg": -20.0,
    "actual_angle_deg": -20.0,
    "correction_factor": 1.0,
    "tracking_ratio": 1.0,
  }
  values.update(overrides)
  return CorrectionSample(**values)


def mapping_sample(**overrides) -> MappingSample:
  values = {
    "route_id": "route-a",
    "timestamp": 0.0,
    "speed_mps": 10.0,
    "signed_angle_deg": -10.0,
    "direction": "left",
    "effective_ratio": 18.0,
    "ratio_per_degree": 1.8,
    "bias_corrected_angle_deg": -10.0,
    "bias_corrected_effective_ratio": 18.0,
    "fingerprint": "HONDA_CLARITY",
  }
  values.update(overrides)
  return MappingSample(**values)


@pytest.mark.parametrize(
  ("achieved_curvature", "actual_angle_deg", "expected"),
  [
    (0.01, -20.0, 1.0),       # perfect response and tracking
    (0.008, -16.0, 1.0),      # tracking miss only: do not blame steer ratio
    (0.008, -20.0, 1.25),     # mapping under-response only
    (0.0064, -16.0, 1.25),    # mapping under-response plus a tracking miss
    (0.012, -20.0, 5.0 / 6.0),
  ],
)
def test_correction_factor_cancels_angle_tracking(achieved_curvature, actual_angle_deg, expected):
  result = correction_factor(0.01, achieved_curvature, -20.0, actual_angle_deg)
  assert result == pytest.approx(expected)


def test_correction_factor_is_symmetric_for_mirrored_turns():
  left = correction_factor(0.01, 0.008, -20.0, -20.0)
  right = correction_factor(-0.01, -0.008, 20.0, 20.0)
  assert left == pytest.approx(1.25)
  assert right == pytest.approx(left)


def test_correction_factor_removes_roll_curvature_intercept():
  desired_curvature = 0.010
  roll_curvature = 0.002
  tracking_ratio = 0.8
  achieved_curvature = roll_curvature + tracking_ratio * (desired_curvature - roll_curvature)

  # Treating roll-induced curvature as steering response invents a correction.
  naive = correction_factor(desired_curvature, achieved_curvature, -20.0, -16.0)
  corrected = correction_factor(
    desired_curvature,
    achieved_curvature,
    -20.0,
    -16.0,
    curvature_offset=roll_curvature,
  )
  assert naive == pytest.approx(20.0 / 21.0)
  assert corrected == pytest.approx(1.0)


def test_model_effective_ratio_removes_speed_and_roll_dynamics():
  wheelbase = 2.75
  mass = 1600.0
  center_to_front = 1.2
  stiffness_front = 100_000.0
  stiffness_rear = 100_000.0
  stiffness_factor = 1.0
  speed = 15.0
  roll = 0.02
  steering_angle = -20.0
  expected_ratio = 18.0

  center_to_rear = wheelbase - center_to_front
  slip_factor = mass * (
    stiffness_front * center_to_front - stiffness_rear * center_to_rear
  ) / (wheelbase ** 2 * stiffness_front * stiffness_rear)
  curvature_factor = 1.0 / ((1.0 - slip_factor * speed ** 2) * wheelbase)
  roll_curvature = 9.81 * roll / (1.0 / slip_factor - speed ** 2)
  measured_curvature = curvature_factor * math.radians(steering_angle) / expected_ratio + roll_curvature
  yaw_rate = -measured_curvature * speed

  result = model_effective_ratio(
    steering_angle,
    yaw_rate,
    speed,
    roll,
    stiffness_factor,
    wheelbase,
    mass,
    center_to_front,
    stiffness_front,
    stiffness_rear,
  )
  assert result == pytest.approx(expected_ratio)


@pytest.mark.parametrize(
  ("speed", "stiffness_factor", "yaw_rate"),
  [
    (0.0, 1.0, 0.1),
    (10.0, 0.0, 0.1),
    (10.0, 1.0, -0.1),
    (10.0, 1.0, math.nan),
  ],
)
def test_model_effective_ratio_rejects_invalid_geometry(speed, stiffness_factor, yaw_rate):
  assert model_effective_ratio(
    -20.0,
    yaw_rate,
    speed,
    0.0,
    stiffness_factor,
    2.75,
    1600.0,
    1.2,
    100_000.0,
    100_000.0,
  ) is None


@pytest.mark.parametrize(
  ("desired_curvature", "achieved_curvature", "desired_angle_deg", "actual_angle_deg"),
  [
    (0.0, 0.01, -20.0, -20.0),
    (0.01, 0.0, -20.0, -20.0),
    (0.01, 0.01, 0.0, -20.0),
    (0.01, 0.01, -20.0, 0.0),
    (0.01, -0.01, -20.0, -20.0),
    (0.01, 0.01, -20.0, 20.0),
    (math.nan, 0.01, -20.0, -20.0),
    (0.01, math.inf, -20.0, -20.0),
  ],
)
def test_correction_factor_rejects_undefined_or_wrong_way_inputs(
  desired_curvature, achieved_curvature, desired_angle_deg, actual_angle_deg,
):
  assert correction_factor(desired_curvature, achieved_curvature, desired_angle_deg, actual_angle_deg) is None


def test_nearest_sample_applies_delay_target_and_freshness():
  samples = [command(timestamp=10.00), command(timestamp=10.05), command(timestamp=10.10)]
  yaw_timestamp = 10.26
  yaw_delay = 0.20

  assert nearest_sample(samples, yaw_timestamp - yaw_delay, 0.02) == samples[1]
  assert nearest_sample(samples, 9.90, 0.05) is None
  assert nearest_sample(samples, 10.15, 0.05) == samples[-1]
  assert nearest_sample(samples, 10.05, -1.0) is None
  assert nearest_sample(samples, math.nan, 1.0) is None


@pytest.mark.parametrize(
  ("command_updates", "vehicle_updates", "expected"),
  [
    ({"desired_curvature": math.nan}, {}, "nonfinite"),
    ({"lat_active": False}, {}, "lateral inactive"),
    ({"saturated": True}, {}, "steering saturated"),
    ({"lane_change_active": True}, {}, "lane change"),
    ({}, {"steering_pressed": True}, "driver steering"),
    ({}, {"pose_valid": False}, "invalid pose"),
    ({}, {"speed_mps": 2.0}, "speed gate"),
    ({"desired_angle_deg": -1.0}, {}, "angle gate"),
    ({"desired_curvature": 0.00001}, {}, "desired curvature gate"),
    ({}, {"yaw_rate_rad_s": 0.005}, "yaw gate"),
    ({}, {"yaw_rate_std_rad_s": 0.051}, "yaw uncertainty"),
    ({}, {"yaw_accel_rad_s2": 0.101}, "yaw-accel gate"),
    ({}, {"steering_rate_deg_s": 5.01}, "steering-rate gate"),
    ({}, {"longitudinal_accel_mps2": 1.01}, "longitudinal-accel gate"),
    ({}, {"road_roll_rad": 0.081}, "road-roll gate"),
    ({}, {"yaw_rate_rad_s": -0.1}, "curvature direction mismatch"),
    ({}, {"actual_angle_deg": 20.0}, "angle direction mismatch"),
    ({}, {"actual_angle_deg": -10.0}, "angle tracking gate"),
    ({}, {"yaw_rate_rad_s": 0.06}, "correction bounds"),
  ],
)
def test_each_quality_gate_has_an_explicit_rejection_reason(command_updates, vehicle_updates, expected):
  assert rejection_reason(command(**command_updates), vehicle(**vehicle_updates)) == expected


def test_valid_sample_and_allowed_lane_change_pass_gates():
  assert rejection_reason(command(), vehicle()) is None
  config = replace(GateConfig(), allow_lane_changes=True)
  assert rejection_reason(command(lane_change_active=True), vehicle(), config) is None


def test_mapping_gate_admits_manual_geometry_without_controller_state():
  manual = vehicle(steering_pressed=True)

  assert mapping_rejection_reason(
    manual,
    18.0,
    geometry_valid=True,
    average_offset_valid=True,
    stiffness_valid=True,
  ) is None
  assert rejection_reason(command(lat_active=False), manual) == "lateral inactive"


@pytest.mark.parametrize(
  ("vehicle_updates", "effective_ratio", "validity", "expected"),
  [
    ({"pose_valid": False}, 18.0, {}, "invalid pose"),
    ({"forward_gear": False}, 18.0, {}, "not forward gear"),
    ({"steering_rate_deg_s": 1.51}, 18.0, {}, "steering-rate gate"),
    ({"yaw_accel_rad_s2": 0.031}, 18.0, {}, "yaw-accel gate"),
    ({"longitudinal_accel_mps2": 0.51}, 18.0, {}, "longitudinal-accel gate"),
    ({}, 18.0, {"geometry_valid": False}, "unknown geometry"),
    ({}, 18.0, {"average_offset_valid": False}, "invalid average angle offset"),
    ({}, 18.0, {"stiffness_valid": False}, "invalid stiffness"),
    ({}, None, {}, "curvature direction mismatch"),
  ],
)
def test_mapping_gate_rejects_invalid_geometry_or_nonsteady_motion(
  vehicle_updates, effective_ratio, validity, expected,
):
  flags = {
    "geometry_valid": True,
    "average_offset_valid": True,
    "stiffness_valid": True,
    **validity,
  }
  assert mapping_rejection_reason(vehicle(**vehicle_updates), effective_ratio, **flags) == expected


def test_mapping_dwell_requires_continuous_stable_geometry():
  stable = [mapping_sample(timestamp=index / 10.0) for index in range(9)]
  short = stable[:-1]

  assert stable_dwell_samples(short) == []
  selected = stable_dwell_samples(stable)
  assert len(selected) == len(stable)
  assert {sample.dwell_id for sample in selected} == {0}
  assert all(sample.dwell_duration_s == pytest.approx(0.8) for sample in selected)

  interrupted = [*stable[:4], *[replace(sample, timestamp=sample.timestamp + 0.2) for sample in stable[4:]]]
  assert stable_dwell_samples(interrupted) == []


def test_mapping_confidence_requires_bilateral_agreement():
  mirrored = []
  for route_number in range(5):
    for second in range(6):
      for direction, angle in (("left", -10.0), ("right", 10.0)):
        mirrored.append(mapping_sample(
          route_id=f"route-{route_number}",
          timestamp=float(second),
          signed_angle_deg=angle,
          direction=direction,
        ))

  bilateral = aggregate_mapping_bin(mirrored)
  one_sided = aggregate_mapping_bin([sample for sample in mirrored if sample.direction == "left"])
  asymmetric = aggregate_mapping_bin([
    replace(sample, bias_corrected_effective_ratio=18.0 if sample.direction == "left" else 16.0)
    for sample in mirrored
  ])

  assert bilateral is not None and one_sided is not None and asymmetric is not None
  assert bilateral.confidence == "high"
  assert bilateral.bilateral_gap_percent == pytest.approx(0.0)
  assert one_sided.confidence == "low"
  assert math.isinf(one_sided.bilateral_gap_percent)
  assert asymmetric.confidence == "low"
  assert asymmetric.bilateral_gap_percent == pytest.approx(200.0 / 17.0)


def test_mapping_confidence_requires_both_directions_on_the_same_routes():
  disjoint_routes = []
  for route_number in range(6):
    direction = "left" if route_number < 3 else "right"
    angle = -10.0 if direction == "left" else 10.0
    for second in range(10):
      disjoint_routes.append(mapping_sample(
        route_id=f"route-{route_number}",
        timestamp=float(second),
        signed_angle_deg=angle,
        direction=direction,
      ))

  stats = aggregate_mapping_bin(disjoint_routes)

  assert stats is not None
  assert stats.seconds == 60
  assert stats.left_seconds == stats.right_seconds == 30
  assert stats.route_directions == stats.routes
  assert stats.confidence == "low"


def test_residual_center_bias_fit_recovers_signed_intercept_and_ratio():
  true_ratio = 18.0
  true_bias = 1.5
  samples = []
  for bin_index, magnitude in enumerate((7.5, 12.5, 17.5)):
    for second in range(7):
      for direction, true_angle in (("left", -magnitude), ("right", magnitude)):
        signed_angle = true_angle + true_bias
        samples.append(mapping_sample(
          timestamp=float(bin_index * 10 + second),
          signed_angle_deg=signed_angle,
          direction=direction,
          effective_ratio=true_ratio / magnitude * abs(signed_angle),
          ratio_per_degree=true_ratio / magnitude,
          bias_corrected_angle_deg=math.nan,
          bias_corrected_effective_ratio=math.nan,
        ))

  estimate = estimate_center_bias(samples, max_abs_bias_deg=2.0)

  assert estimate is not None
  assert estimate.bias_deg == pytest.approx(true_bias, abs=0.01)
  assert estimate.paired_bins == 3
  assert estimate.left_seconds == estimate.right_seconds == 21
  assert estimate.objective_after < estimate.objective_before
  assert estimate.objective_after == pytest.approx(0.0, abs=1e-12)
  assert estimate.confidence == "high"

  adjusted = apply_center_bias(samples, estimate.bias_deg)
  assert all(sample.bias_corrected_effective_ratio == pytest.approx(true_ratio) for sample in adjusted)


def test_center_bias_fit_at_search_boundary_is_not_high_confidence():
  samples = []
  for bin_index, magnitude in enumerate((7.5, 12.5, 17.5)):
    for second in range(7):
      for direction, true_angle in (("left", -magnitude), ("right", magnitude)):
        signed_angle = true_angle + 1.0
        samples.append(mapping_sample(
          timestamp=float(bin_index * 10 + second),
          signed_angle_deg=signed_angle,
          direction=direction,
          effective_ratio=18.0 / magnitude * abs(signed_angle),
          ratio_per_degree=18.0 / magnitude,
        ))

  estimate = estimate_center_bias(samples, max_abs_bias_deg=1.0)

  assert estimate is not None
  assert estimate.bias_deg == pytest.approx(1.0)
  assert estimate.confidence != "high"


def test_center_bias_fit_cannot_explain_a_left_right_speed_confound_as_offset():
  samples = []
  for bin_index, magnitude in enumerate((7.5, 12.5, 17.5)):
    for second in range(7):
      samples.append(mapping_sample(
        timestamp=float(bin_index * 10 + second),
        speed_mps=4.0,
        signed_angle_deg=-magnitude,
        direction="left",
        effective_ratio=18.0,
        ratio_per_degree=18.0 / magnitude,
      ))
      samples.append(mapping_sample(
        timestamp=float(bin_index * 10 + second),
        speed_mps=10.0,
        signed_angle_deg=magnitude,
        direction="right",
        effective_ratio=16.0,
        ratio_per_degree=16.0 / magnitude,
      ))

  estimate = estimate_center_bias(samples)

  assert estimate is None or estimate.confidence == "low"


def test_gate_uses_offset_corrected_angles_for_tracking_cancellation():
  # Physical desired/actual are -20/-16 degrees. Both logged values carry the
  # same +2 degree sensor-center offset and must therefore still yield 80%.
  cfg = replace(GateConfig(), min_tracking_ratio=0.79, max_tracking_ratio=0.81)
  cmd = command(desired_angle_deg=-18.0, angle_offset_deg=2.0)
  state = vehicle(actual_angle_deg=-14.0, angle_offset_deg=2.0, yaw_rate_rad_s=0.08)
  assert rejection_reason(cmd, state, cfg) is None


@pytest.mark.parametrize(
  ("angle", "rate", "expected"),
  [
    (20.0, 2.0, "turn-in"),
    (-20.0, -2.0, "turn-in"),
    (20.0, -2.0, "unwind"),
    (-20.0, 2.0, "unwind"),
    (20.0, 1.5, "steady"),
    (-20.0, -1.5, "steady"),
  ],
)
def test_phase_classification_is_direction_normalized(angle, rate, expected):
  assert phase_from_steering(angle, rate) == expected


def test_bin_key_preserves_angle_speed_direction_and_phase():
  key = make_bin_key(correction_sample(
    angle_deg=-7.5,
    speed_mps=12.0,
    direction="right",
    phase="unwind",
  ), angle_width_deg=2.5)

  assert key.angle_start_deg == 7.5
  assert key.angle_end_deg == 10.0
  assert key.speed_start_mps == 12.0
  assert key.speed_end_mps == 18.0
  assert key.direction == "right"
  assert key.phase == "unwind"


def test_bin_key_rejects_invalid_grid_geometry():
  sample = correction_sample()
  with pytest.raises(ValueError, match="angle_width_deg"):
    make_bin_key(sample, angle_width_deg=0.0)
  with pytest.raises(ValueError, match="speed_edges_mps"):
    make_bin_key(sample, speed_edges_mps=(0.0, 10.0, 10.0))


def test_aggregation_is_route_balanced_not_frame_or_duration_weighted():
  samples = []
  # Route A contributes far more frames and seconds than route B, but each
  # route/direction contributes one value to the final robust median.
  for second in range(100):
    for frame in range(5):
      samples.append(correction_sample(
        route_id="route-a",
        timestamp=second + frame / 10.0,
        correction_factor=1.0,
      ))
  samples.append(correction_sample(route_id="route-b", correction_factor=1.2))

  stats = aggregate_bin(samples)
  assert stats is not None
  assert stats.seconds == 101
  assert stats.routes == 2
  assert stats.route_directions == 2
  assert stats.median_factor == pytest.approx(1.1)


def test_aggregation_uses_per_second_medians_to_reject_frame_outlier():
  samples = [
    correction_sample(timestamp=3.01, correction_factor=1.0),
    correction_sample(timestamp=3.02, correction_factor=1.0),
    correction_sample(timestamp=3.03, correction_factor=1.0),
    correction_sample(timestamp=3.04, correction_factor=1.5),
  ]

  stats = aggregate_bin(samples)
  assert stats is not None
  assert stats.seconds == 1
  assert stats.median_factor == pytest.approx(1.0)


def test_bilateral_coverage_can_be_high_confidence_only_when_combined():
  left = []
  right = []
  for route_number in range(5):
    for second in range(6):
      common = {
        "route_id": f"route-{route_number}",
        "timestamp": float(second),
        "correction_factor": 1.0 + route_number * 0.005,
      }
      left.append(correction_sample(direction="left", **common))
      right.append(correction_sample(direction="right", **common))

  left_stats = aggregate_bin(left)
  combined_stats = aggregate_bin(left + right)
  assert left_stats is not None and combined_stats is not None
  assert left_stats.confidence == "low"
  assert combined_stats.seconds == 60
  assert combined_stats.routes == 5
  assert combined_stats.left_seconds == 30
  assert combined_stats.right_seconds == 30
  assert combined_stats.confidence == "high"


def test_empty_or_neutral_aggregation_is_a_safe_noop():
  assert aggregate_bin([]) is None

  stats = aggregate_bin([
    correction_sample(route_id="route-a", correction_factor=1.0),
    correction_sample(route_id="route-b", correction_factor=1.0),
  ])
  assert stats is not None
  assert stats.median_factor == pytest.approx(1.0)
  assert stats.confidence == "low"
  assert math.isnan(stats.median_required_angle_deg)
  assert math.isnan(stats.median_effective_ratio)
