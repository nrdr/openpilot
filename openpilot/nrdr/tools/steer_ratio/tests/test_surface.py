from dataclasses import replace
import math
from bisect import bisect_left
from collections import deque

import pytest

from openpilot.nrdr.tools.sr_correction_analysis import (
  CorrectionSample, MappingSample, model_effective_ratio, nearest_sample, stable_dwell_samples,
)
from openpilot.nrdr.tools.steer_ratio.surface import (
  SurfaceConfig, mapping_surface, matched_speed_comparisons, tracking_surface,
)


def mapping(**kwargs):
  values = {"route_id": "a", "timestamp": 0.0, "speed_mps": 10.0, "signed_angle_deg": -10.1,
                "direction": "left", "effective_ratio": 15.0, "ratio_per_degree": 15 / 10.1,
                "bias_corrected_angle_deg": -10.1, "bias_corrected_effective_ratio": 15.0,
                "zero_roll_effective_ratio": 15.0, "unit_stiffness_effective_ratio": 15.0,
                "geometric_effective_ratio": 15.0, "fingerprint": "GENERIC", "eps_firmware": "eps-a",
                "software_id": "build-a", "vehicle_model_id": "model-a"}
  values.update(kwargs)
  return MappingSample(**values)


def speed_data(high_ratio=18.0):
  return [mapping(route_id=route, timestamp=float(second + 10 * band), speed_mps=speed,
                  direction=direction, signed_angle_deg=angle, bias_corrected_angle_deg=angle,
                  effective_ratio=ratio, bias_corrected_effective_ratio=ratio,
                  zero_roll_effective_ratio=ratio, unit_stiffness_effective_ratio=ratio,
                  geometric_effective_ratio=ratio, ratio_per_degree=ratio / abs(angle))
          for route in ("a", "b") for direction, angle in (("left", -10.1), ("right", 10.1))
          for band, speed, ratio in ((0, 12.0, 15.0), (1, 27.0, high_ratio)) for second in range(4)]


def command(**kwargs):
  values = {"route_id": "a", "timestamp": 0.0, "speed_mps": 27.0, "angle_deg": 10.0, "direction": "left",
                "phase": "steady", "desired_curvature": 0.01, "achieved_curvature": 0.008,
                "desired_angle_deg": -10.0, "actual_angle_deg": -10.0, "correction_factor": 1.25,
                "tracking_ratio": 1.0, "quality": "strict", "factor_delay_minus_100ms": 1.25,
                "factor_delay_plus_100ms": 1.25}
  values.update(kwargs)
  return CorrectionSample(**values)


def test_matched_speed_signal_and_unchanged_mapping():
  row = matched_speed_comparisons(speed_data(), SurfaceConfig())[0]
  assert row["normalized_change_percent"] == pytest.approx(20.0)
  assert row["bilateral_routes"] == 2
  assert row["status"].startswith("repeatable speed-associated")
  row = matched_speed_comparisons(speed_data(15), SurfaceConfig())[0]
  assert row["status"].startswith("no resolved speed residual")


@pytest.mark.parametrize("field", ["eps_firmware", "fingerprint", "vehicle_model_id", "software_id"])
def test_no_cross_cohort_speed_pairing(field):
  samples = [replace(s, **{field: "other"}) if s.speed_mps > 20 else s for s in speed_data()]
  assert matched_speed_comparisons(samples, SurfaceConfig()) == []
  assert len({r["cohort"] for r in mapping_surface(samples, SurfaceConfig())}) == 2


def test_angle_speed_confound_does_not_form_a_match():
  for angle in (14.0, 10.8):
    samples = [replace(s, signed_angle_deg=math.copysign(angle, s.signed_angle_deg),
                       bias_corrected_angle_deg=math.copysign(angle, s.signed_angle_deg))
               if s.speed_mps > 20 else s for s in speed_data()]
    assert matched_speed_comparisons(samples, SurfaceConfig()) == []


def test_opposing_route_residuals_do_not_cancel_into_speed_independence():
  samples = [replace(s, effective_ratio=12, bias_corrected_effective_ratio=12,
                     zero_roll_effective_ratio=12, unit_stiffness_effective_ratio=12)
             if s.route_id == "b" and s.speed_mps > 20 else s for s in speed_data()]
  row = matched_speed_comparisons(samples, SurfaceConfig())[0]
  assert row["normalized_change_percent"] == pytest.approx(0)
  assert row["status"] == "inconsistent route/direction residual"


@pytest.mark.parametrize("field", ["zero_roll_effective_ratio", "unit_stiffness_effective_ratio", "effective_ratio"])
def test_model_or_center_bias_sensitive_residual_is_not_isolated(field):
  samples = [replace(s, **{field: 15.0}) if s.speed_mps > 20 else s for s in speed_data()]
  assert matched_speed_comparisons(samples, SurfaceConfig())[0]["status"].startswith("model/offset-sensitive")


def test_one_sided_one_route_and_dense_frames_cannot_create_support():
  for samples in ([s for s in speed_data() if s.direction == "left"],
                  [s for s in speed_data() if s.route_id == "a"]):
    assert matched_speed_comparisons(samples * 100, SurfaceConfig())[0]["status"].startswith("insufficient")
  samples = [replace(s, timestamp=0.01) for s in speed_data()]
  assert matched_speed_comparisons(samples * 100, SurfaceConfig()) == []


def test_equal_second_then_route_weight_not_frames():
  samples = [mapping(timestamp=0.0), mapping(timestamp=1.0)]
  dense = mapping(route_id="b", effective_ratio=25, bias_corrected_effective_ratio=25)
  rows = mapping_surface(samples + [dense] * 1000, SurfaceConfig())
  assert rows[0]["model_normalized_sr"] == 20
  assert rows[0]["occupied_seconds"] == 3


def test_tracking_vs_mapping_and_lag_are_separate():
  samples = [command(route_id=route, timestamp=float(second)) for route in ("a", "b") for second in range(4)]
  row = tracking_surface(samples, SurfaceConfig())[0]
  assert row["status"].startswith("angle tracks but curvature undershoots")
  assert row["timing_status"].startswith("low")
  row = tracking_surface([replace(s, tracking_ratio=0.8, correction_factor=1.0) for s in samples], SurfaceConfig())[0]
  assert row["status"].startswith("angle undershoot")
  row = tracking_surface([replace(s, factor_delay_plus_100ms=1.5) for s in samples], SurfaceConfig())[0]
  assert row["timing_status"].startswith("lag-sensitive")
  assert tracking_surface([replace(s, safety_limited=True) for s in samples], SurfaceConfig()) == []
  assert tracking_surface([replace(s, quality="relaxed") for s in samples], SurfaceConfig()) == []


def test_dwell_breaks_on_rejected_frame_or_cohort_change():
  samples = [mapping(timestamp=i / 10) for i in range(9)]
  assert len(stable_dwell_samples(samples)) == 9
  for field, value in (("continuity_id", 1), ("eps_firmware", "eps-b"), ("software_id", "other")):
    split = [replace(s, **{field: value}) if s.timestamp >= 0.4 else s for s in samples]
    assert stable_dwell_samples(split) == []


@pytest.mark.parametrize("fingerprint,wheelbase,mass,front", [
  ("HONDA_CIVIC", 2.70, 1450, 1.05), ("LEXUS_ES", 2.82, 1650, 1.2), ("GENERIC_SUV", 3.0, 2250, 1.4),
])
def test_dynamic_model_speed_effect_is_not_fitted_as_sr(fingerprint, wheelbase, mass, front):
  # Synthetic yaw generated with a fixed 16:1 ratio and speed-dependent tire slip.
  cf, cr, ratio = 100000.0, 120000.0, 16.0
  slip = mass * (cf * front - cr * (wheelbase - front)) / (wheelbase ** 2 * cf * cr)
  for speed in (4, 12, 27, 32):
    angle = -10.1
    yaw = -speed * math.radians(angle) / (ratio * wheelbase * (1 - slip * speed ** 2))
    recovered = model_effective_ratio(angle, yaw, speed, 0, 1, wheelbase, mass, front, cf, cr)
    assert recovered == pytest.approx(ratio), fingerprint


@pytest.mark.parametrize("kwargs", [{"speed_width_mps": 0}, {"angle_width_deg": math.nan},
                                    {"min_paired_routes": 1}, {"match_angle_width_deg": 6}])
def test_bad_config_rejected(kwargs):
  with pytest.raises(ValueError):
    SurfaceConfig(**kwargs)


@pytest.mark.parametrize("container", [list, tuple, deque])
def test_fast_pairing_matches_original_including_ties_and_duplicates(container):
  samples = container(mapping(timestamp=i // 2 / 100) for i in range(1000))
  for target in (-1, 0, 0.004, 0.005, 0.006, 1.231, 2.505, 4.99, 5, 99):
    for age in (0, 0.005, 0.03, 10):
      times = [s.timestamp for s in samples]
      index = bisect_left(times, target)
      candidates = ([samples[index]] if index < len(samples) else []) + ([samples[index - 1]] if index else [])
      closest = min(candidates, key=lambda s: abs(s.timestamp - target))
      expected = closest if abs(closest.timestamp - target) <= age + 1e-9 else None
      assert nearest_sample(samples, target, age) is expected
