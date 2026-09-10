from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
import math
from statistics import median
from typing import TypeVar


DEFAULT_SPEED_EDGES_MPS = (0.0, 7.0, 12.0, 18.0, 25.0, 33.0, math.inf)
ACCELERATION_DUE_TO_GRAVITY = 9.81


@dataclass(frozen=True)
class CommandSample:
  timestamp: float
  desired_curvature: float
  desired_angle_deg: float
  angle_offset_deg: float = 0.0
  lat_active: bool = False
  saturated: bool = False
  lane_change_active: bool = False
  requested_torque: float = math.nan


@dataclass(frozen=True)
class VehicleSample:
  timestamp: float
  speed_mps: float
  actual_angle_deg: float
  steering_rate_deg_s: float
  steering_pressed: bool
  yaw_rate_rad_s: float
  yaw_rate_std_rad_s: float = 0.0
  yaw_accel_rad_s2: float = 0.0
  longitudinal_accel_mps2: float = 0.0
  road_roll_rad: float = 0.0
  stiffness_factor: float = 1.0
  pose_valid: bool = True
  angle_offset_deg: float = 0.0
  geometry_angle_offset_deg: float | None = None
  steering_torque: float = 0.0
  forward_gear: bool = True


@dataclass(frozen=True)
class GateConfig:
  min_speed_mps: float = 3.0
  max_speed_mps: float = 33.0
  min_angle_deg: float = 2.0
  min_curvature: float = 1e-4
  min_yaw_rate_rad_s: float = 0.01
  max_yaw_rate_std_rad_s: float = 0.05
  max_yaw_accel_rad_s2: float = 0.10
  max_steering_rate_deg_s: float = 5.0
  max_longitudinal_accel_mps2: float = 1.0
  max_road_roll_rad: float = 0.08
  min_tracking_ratio: float = 0.65
  max_tracking_ratio: float = 1.35
  min_correction_factor: float = 0.5
  max_correction_factor: float = 1.5
  allow_lane_changes: bool = False


DEFAULT_GATE_CONFIG = GateConfig()


@dataclass(frozen=True)
class MappingGateConfig:
  min_speed_mps: float = 2.0
  max_speed_mps: float = 15.0
  min_angle_deg: float = 2.0
  min_yaw_rate_rad_s: float = 0.005
  max_yaw_rate_std_rad_s: float = 0.05
  max_relative_yaw_rate_std: float = 0.50
  max_yaw_accel_rad_s2: float = 0.03
  max_steering_rate_deg_s: float = 1.5
  max_longitudinal_accel_mps2: float = 0.50
  max_lateral_accel_mps2: float = 1.50
  max_road_roll_rad: float = 0.08


DEFAULT_MAPPING_GATE_CONFIG = MappingGateConfig()


@dataclass(frozen=True)
class BinKey:
  angle_start_deg: float
  angle_end_deg: float
  speed_start_mps: float
  speed_end_mps: float
  direction: str
  phase: str


@dataclass(frozen=True)
class CorrectionSample:
  route_id: str
  timestamp: float
  speed_mps: float
  angle_deg: float
  direction: str
  phase: str
  desired_curvature: float
  achieved_curvature: float
  desired_angle_deg: float
  actual_angle_deg: float
  correction_factor: float
  tracking_ratio: float
  required_angle_deg: float = math.nan
  effective_ratio: float = math.nan
  software_id: str = "unknown"
  quality: str = "relaxed"
  factor_delay_minus_100ms: float = math.nan
  factor_delay_plus_100ms: float = math.nan
  fingerprint: str = "UNKNOWN"
  command_output_available: bool = True
  safety_limited: bool = False


@dataclass(frozen=True)
class MappingSample:
  route_id: str
  timestamp: float
  speed_mps: float
  signed_angle_deg: float
  direction: str
  effective_ratio: float
  ratio_per_degree: float
  steering_torque: float = 0.0
  dwell_id: int = -1
  dwell_duration_s: float = 0.0
  center_bias_deg: float = 0.0
  bias_source: str = "none"
  bias_corrected_angle_deg: float = math.nan
  bias_corrected_effective_ratio: float = math.nan
  fingerprint: str = "UNKNOWN"
  steering_rate_deg_s: float = math.nan
  yaw_rate_rad_s: float = math.nan
  yaw_rate_std_rad_s: float = math.nan
  road_roll_rad: float = math.nan
  stiffness_factor: float = math.nan
  longitudinal_accel_mps2: float = math.nan
  lateral_accel_mps2: float = math.nan
  zero_roll_effective_ratio: float = math.nan
  unit_stiffness_effective_ratio: float = math.nan


@dataclass(frozen=True)
class CenterBiasEstimate:
  route_id: str
  bias_deg: float
  paired_bins: int
  left_seconds: int
  right_seconds: int
  objective_before: float
  objective_after: float
  confidence: str


@dataclass(frozen=True)
class MappingBinStats:
  seconds: int
  routes: int
  route_directions: int
  paired_routes: int
  left_seconds: int
  right_seconds: int
  median_ratio: float
  p25_ratio: float
  p75_ratio: float
  left_median_ratio: float
  right_median_ratio: float
  bilateral_gap_percent: float
  confidence: str


@dataclass(frozen=True)
class BinStats:
  seconds: int
  routes: int
  route_directions: int
  left_seconds: int
  right_seconds: int
  median_factor: float
  p25_factor: float
  p75_factor: float
  median_tracking_ratio: float
  median_required_angle_deg: float
  median_effective_ratio: float
  confidence: str


T = TypeVar("T")


def _finite(*values: float) -> bool:
  return all(math.isfinite(value) for value in values)


def _percentile(values: Sequence[float], percentile: float) -> float:
  if not values:
    return math.nan
  ordered = sorted(values)
  position = (len(ordered) - 1) * percentile / 100.0
  lower = math.floor(position)
  upper = math.ceil(position)
  if lower == upper:
    return float(ordered[lower])
  weight = position - lower
  return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def nearest_sample(samples: Sequence[T], target_time: float, max_age: float) -> T | None:  # noqa: UP047
  if not samples or max_age < 0.0 or not math.isfinite(target_time):
    return None
  timestamps = [float(sample.timestamp) for sample in samples]
  index = bisect_left(timestamps, target_time)
  candidates = []
  if index < len(samples):
    candidates.append(samples[index])
  if index:
    candidates.append(samples[index - 1])
  closest = min(candidates, key=lambda sample: abs(float(sample.timestamp) - target_time))
  return closest if abs(float(closest.timestamp) - target_time) <= max_age + 1e-9 else None


def correction_factor(desired_curvature: float, achieved_curvature: float,
                      desired_angle_deg: float, actual_angle_deg: float,
                      *, min_abs_curvature: float = 1e-4,
                      min_abs_angle_deg: float = 1e-3,
                      curvature_offset: float = 0.0) -> float | None:
  values = (desired_curvature, achieved_curvature, desired_angle_deg, actual_angle_deg)
  if not _finite(*values, curvature_offset):
    return None
  desired_from_steer = desired_curvature - curvature_offset
  achieved_from_steer = achieved_curvature - curvature_offset
  if abs(desired_from_steer) < min_abs_curvature or abs(achieved_from_steer) < min_abs_curvature:
    return None
  if abs(desired_angle_deg) < min_abs_angle_deg or abs(actual_angle_deg) < min_abs_angle_deg:
    return None
  if desired_from_steer * achieved_from_steer <= 0.0 or desired_angle_deg * actual_angle_deg <= 0.0:
    return None
  return abs(actual_angle_deg / desired_angle_deg) * abs(desired_from_steer / achieved_from_steer)


def model_roll_compensation(speed_mps: float, road_roll_rad: float, stiffness_factor: float,
                            wheelbase_m: float, mass_kg: float, center_to_front_m: float,
                            tire_stiffness_front: float, tire_stiffness_rear: float) -> float | None:
  values = (
    speed_mps, road_roll_rad, stiffness_factor, wheelbase_m, mass_kg,
    center_to_front_m, tire_stiffness_front, tire_stiffness_rear,
  )
  if not _finite(*values) or speed_mps <= 0.0 or wheelbase_m <= 0.0 or stiffness_factor <= 0.0:
    return None
  stiffness_front = tire_stiffness_front * stiffness_factor
  stiffness_rear = tire_stiffness_rear * stiffness_factor
  center_to_rear = wheelbase_m - center_to_front_m
  denominator = wheelbase_m ** 2 * stiffness_front * stiffness_rear
  if denominator == 0.0:
    return None
  slip_factor = mass_kg * (stiffness_front * center_to_front_m - stiffness_rear * center_to_rear) / denominator
  if abs(slip_factor) < 1e-6:
    return 0.0
  roll_denominator = 1.0 / slip_factor - speed_mps ** 2
  if abs(roll_denominator) < 1e-9:
    return None
  return ACCELERATION_DUE_TO_GRAVITY * road_roll_rad / roll_denominator


def model_effective_ratio(steering_angle_deg: float, yaw_rate_rad_s: float, speed_mps: float,
                          road_roll_rad: float, stiffness_factor: float, wheelbase_m: float,
                          mass_kg: float, center_to_front_m: float,
                          tire_stiffness_front: float, tire_stiffness_rear: float) -> float | None:
  values = (
    steering_angle_deg, yaw_rate_rad_s, speed_mps, road_roll_rad, stiffness_factor,
    wheelbase_m, mass_kg, center_to_front_m, tire_stiffness_front, tire_stiffness_rear,
  )
  if not _finite(*values) or speed_mps <= 0.0 or wheelbase_m <= 0.0 or stiffness_factor <= 0.0:
    return None
  stiffness_front = tire_stiffness_front * stiffness_factor
  stiffness_rear = tire_stiffness_rear * stiffness_factor
  center_to_rear = wheelbase_m - center_to_front_m
  denominator = wheelbase_m ** 2 * stiffness_front * stiffness_rear
  if denominator == 0.0:
    return None
  slip_factor = mass_kg * (stiffness_front * center_to_front_m - stiffness_rear * center_to_rear) / denominator
  curvature_denominator = (1.0 - slip_factor * speed_mps ** 2) * wheelbase_m
  if abs(curvature_denominator) < 1e-9:
    return None
  curvature_factor = 1.0 / curvature_denominator
  roll_compensation = model_roll_compensation(
    speed_mps, road_roll_rad, stiffness_factor, wheelbase_m, mass_kg,
    center_to_front_m, tire_stiffness_front, tire_stiffness_rear,
  )
  if roll_compensation is None:
    return None
  measured_curvature = -yaw_rate_rad_s / speed_mps
  curvature_from_steer = measured_curvature - roll_compensation
  steering_angle_rad = math.radians(steering_angle_deg)
  if abs(curvature_from_steer) < 1e-6 or steering_angle_rad * curvature_from_steer <= 0.0:
    return None
  ratio = curvature_factor * steering_angle_rad / curvature_from_steer
  return ratio if math.isfinite(ratio) and 5.0 <= ratio <= 40.0 else None


def mapping_rejection_reason(vehicle: VehicleSample, effective_ratio: float | None, *,
                             geometry_valid: bool, average_offset_valid: bool,
                             stiffness_valid: bool,
                             config: MappingGateConfig = DEFAULT_MAPPING_GATE_CONFIG) -> str | None:
  geometry_offset = (vehicle.angle_offset_deg if vehicle.geometry_angle_offset_deg is None
                     else vehicle.geometry_angle_offset_deg)
  signed_angle = vehicle.actual_angle_deg - geometry_offset
  values = (
    vehicle.timestamp, vehicle.speed_mps, signed_angle, vehicle.steering_rate_deg_s,
    vehicle.yaw_rate_rad_s, vehicle.yaw_rate_std_rad_s, vehicle.yaw_accel_rad_s2,
    vehicle.longitudinal_accel_mps2, vehicle.road_roll_rad, vehicle.stiffness_factor,
  )
  if not _finite(*values):
    return "nonfinite"
  if not geometry_valid:
    return "unknown geometry"
  if not average_offset_valid:
    return "invalid average angle offset"
  if not stiffness_valid or not 0.2 <= vehicle.stiffness_factor <= 5.0:
    return "invalid stiffness"
  if not vehicle.pose_valid:
    return "invalid pose"
  if not vehicle.forward_gear:
    return "not forward gear"
  if not config.min_speed_mps <= vehicle.speed_mps <= config.max_speed_mps:
    return "speed gate"
  if abs(signed_angle) < config.min_angle_deg:
    return "angle gate"
  if abs(vehicle.yaw_rate_rad_s) < config.min_yaw_rate_rad_s:
    return "yaw gate"
  if vehicle.yaw_rate_std_rad_s < 0.0 or vehicle.yaw_rate_std_rad_s > config.max_yaw_rate_std_rad_s:
    return "yaw uncertainty"
  if vehicle.yaw_rate_std_rad_s / abs(vehicle.yaw_rate_rad_s) > config.max_relative_yaw_rate_std:
    return "yaw uncertainty"
  if abs(vehicle.yaw_accel_rad_s2) > config.max_yaw_accel_rad_s2:
    return "yaw-accel gate"
  if abs(vehicle.steering_rate_deg_s) > config.max_steering_rate_deg_s:
    return "steering-rate gate"
  if abs(vehicle.longitudinal_accel_mps2) > config.max_longitudinal_accel_mps2:
    return "longitudinal-accel gate"
  if abs(vehicle.yaw_rate_rad_s * vehicle.speed_mps) > config.max_lateral_accel_mps2:
    return "lateral-accel gate"
  if abs(vehicle.road_roll_rad) > config.max_road_roll_rad:
    return "road-roll gate"
  if effective_ratio is None or not math.isfinite(effective_ratio):
    return "curvature direction mismatch"
  return None


def stable_dwell_samples(samples: Sequence[MappingSample], min_duration_s: float = 0.75,
                         max_gap_s: float = 0.15,
                         max_angle_span_deg: float = 2.5) -> list[MappingSample]:
  if min_duration_s < 0.0 or max_gap_s <= 0.0 or max_angle_span_deg < 0.0:
    raise ValueError("invalid dwell thresholds")
  if not samples:
    return []

  ordered = sorted(samples, key=lambda sample: (sample.route_id, sample.timestamp))
  selected: list[MappingSample] = []
  run: list[MappingSample] = []
  run_min_angle = math.inf
  run_max_angle = -math.inf
  dwell_id = 0

  def flush() -> None:
    nonlocal dwell_id
    if run and run[-1].timestamp - run[0].timestamp + 1e-9 >= min_duration_s:
      duration = run[-1].timestamp - run[0].timestamp
      selected.extend(replace(sample, dwell_id=dwell_id, dwell_duration_s=duration) for sample in run)
      dwell_id += 1

  for sample in ordered:
    angle = sample.signed_angle_deg
    continues = bool(
      run
      and sample.route_id == run[-1].route_id
      and sample.direction == run[-1].direction
      and 0.0 <= sample.timestamp - run[-1].timestamp <= max_gap_s + 1e-9
      and max(run_max_angle, angle) - min(run_min_angle, angle) <= max_angle_span_deg + 1e-9
    )
    if not continues:
      flush()
      run = [sample]
      run_min_angle = angle
      run_max_angle = angle
    else:
      run.append(sample)
      run_min_angle = min(run_min_angle, angle)
      run_max_angle = max(run_max_angle, angle)
  flush()
  return selected


def _center_bias_objective(samples: Sequence[MappingSample], bias_deg: float,
                           angle_bin_width_deg: float, min_seconds_per_direction: int,
                           max_fit_angle_deg: float,
                           speed_bin_width_mps: float) -> tuple[float, int, int, int]:
  per_second: dict[tuple[int, int, str, int], list[float]] = {}
  for sample in samples:
    angle = abs(sample.signed_angle_deg)
    if not 2.0 <= angle <= max_fit_angle_deg:
      continue
    angle_bin = math.floor(angle / angle_bin_width_deg)
    speed_bin = math.floor(sample.speed_mps / speed_bin_width_mps)
    value = sample.ratio_per_degree * abs(sample.signed_angle_deg - bias_deg)
    per_second.setdefault((angle_bin, speed_bin, sample.direction, math.floor(sample.timestamp)), []).append(value)

  per_bin_direction: dict[tuple[int, int, str], list[float]] = {}
  for (angle_bin, speed_bin, direction, _second), values in per_second.items():
    per_bin_direction.setdefault((angle_bin, speed_bin, direction), []).append(median(values))

  discrepancies = []
  left_seconds = 0
  right_seconds = 0
  for angle_bin, speed_bin in {(key[0], key[1]) for key in per_bin_direction}:
    left = per_bin_direction.get((angle_bin, speed_bin, "left"), [])
    right = per_bin_direction.get((angle_bin, speed_bin, "right"), [])
    if len(left) < min_seconds_per_direction or len(right) < min_seconds_per_direction:
      continue
    left_ratio = median(left)
    right_ratio = median(right)
    if left_ratio <= 0.0 or right_ratio <= 0.0:
      continue
    discrepancies.append(abs(math.log(left_ratio / right_ratio)))
    left_seconds += len(left)
    right_seconds += len(right)
  objective = median(discrepancies) if discrepancies else math.inf
  return objective, len(discrepancies), left_seconds, right_seconds


def estimate_center_bias(samples: Sequence[MappingSample], *, max_abs_bias_deg: float = 1.0,
                         step_deg: float = 0.01, angle_bin_width_deg: float = 5.0,
                         speed_bin_width_mps: float = 3.0,
                         min_seconds_per_direction: int = 3,
                         max_fit_angle_deg: float = 20.0) -> CenterBiasEstimate | None:
  if (max_abs_bias_deg < 0.0 or step_deg <= 0.0 or angle_bin_width_deg <= 0.0
      or speed_bin_width_mps <= 0.0):
    raise ValueError("invalid center-bias fit thresholds")
  routes = {sample.route_id for sample in samples}
  if len(routes) != 1:
    raise ValueError("center-bias fit requires exactly one route")
  route_id = next(iter(routes))
  before, paired_bins, left_seconds, right_seconds = _center_bias_objective(
    samples, 0.0, angle_bin_width_deg, min_seconds_per_direction, max_fit_angle_deg, speed_bin_width_mps,
  )
  if not math.isfinite(before):
    return None

  count = round(2.0 * max_abs_bias_deg / step_deg)
  candidates = (-max_abs_bias_deg + index * step_deg for index in range(count + 1))
  scored = []
  for bias in candidates:
    objective, bins, left, right = _center_bias_objective(
      samples, bias, angle_bin_width_deg, min_seconds_per_direction, max_fit_angle_deg, speed_bin_width_mps,
    )
    if math.isfinite(objective):
      scored.append((objective, abs(bias), bias, bins, left, right))
  if not scored:
    return None
  after, _magnitude, bias, paired_bins, left_seconds, right_seconds = min(scored)
  if paired_bins >= 3 and min(left_seconds, right_seconds) >= 20 and after <= 0.03:
    confidence = "high"
  elif paired_bins >= 2 and min(left_seconds, right_seconds) >= 8 and after <= 0.05:
    confidence = "medium"
  else:
    confidence = "low"
  if abs(bias) >= max(0.0, max_abs_bias_deg - step_deg) - 1e-9:
    confidence = "low"
  return CenterBiasEstimate(
    route_id, bias, paired_bins, left_seconds, right_seconds,
    before, after, confidence,
  )


def apply_center_bias(samples: Sequence[MappingSample], bias_deg: float,
                      bias_source: str = "route-fit") -> list[MappingSample]:
  adjusted = []
  for sample in samples:
    angle = sample.signed_angle_deg - bias_deg
    adjusted.append(replace(
      sample,
      center_bias_deg=bias_deg,
      bias_source=bias_source,
      bias_corrected_angle_deg=angle,
      bias_corrected_effective_ratio=sample.ratio_per_degree * abs(angle),
    ))
  return adjusted


def aggregate_mapping_bin(samples: Iterable[MappingSample]) -> MappingBinStats | None:
  samples = [sample for sample in samples if math.isfinite(sample.bias_corrected_effective_ratio)]
  if not samples:
    return None
  per_second: dict[tuple[str, int, str], list[float]] = {}
  for sample in samples:
    key = sample.route_id, math.floor(sample.timestamp), sample.direction
    per_second.setdefault(key, []).append(sample.bias_corrected_effective_ratio)
  seconds = [(route, direction, median(values)) for (route, _second, direction), values in per_second.items()]
  by_route_direction: dict[tuple[str, str], list[float]] = {}
  for route, direction, value in seconds:
    by_route_direction.setdefault((route, direction), []).append(value)
  balanced = [(direction, median(values)) for (_route, direction), values in by_route_direction.items()]
  ratios = [value for _direction, value in balanced]
  left = [value for direction, value in balanced if direction == "left"]
  right = [value for direction, value in balanced if direction == "right"]
  ratio = median(ratios)
  p25 = _percentile(ratios, 25.0)
  p75 = _percentile(ratios, 75.0)
  left_ratio = median(left) if left else math.nan
  right_ratio = median(right) if right else math.nan
  route_directions: dict[str, dict[str, float]] = {}
  for (route, direction), values in by_route_direction.items():
    route_directions.setdefault(route, {})[direction] = median(values)
  paired = [values for values in route_directions.values() if "left" in values and "right" in values]
  paired_gaps = [
    100.0 * abs(values["left"] - values["right"]) / median((values["left"], values["right"]))
    for values in paired
    if median((values["left"], values["right"]))
  ]
  bilateral_gap = median(paired_gaps) if paired_gaps else math.inf
  left_seconds = sum(direction == "left" for _route, direction, _value in seconds)
  right_seconds = sum(direction == "right" for _route, direction, _value in seconds)
  relative_iqr = (p75 - p25) / abs(ratio) if ratio else math.inf
  route_count = len({route for route, _direction, _value in seconds})
  if (len(seconds) >= 60 and route_count >= 5 and len(paired) >= 3 and min(left_seconds, right_seconds) >= 20
      and relative_iqr <= 0.08 and bilateral_gap <= 3.0):
    confidence = "high"
  elif (len(seconds) >= 20 and route_count >= 3 and len(paired) >= 1 and min(left_seconds, right_seconds) >= 5
        and relative_iqr <= 0.15 and bilateral_gap <= 5.0):
    confidence = "medium"
  else:
    confidence = "low"
  return MappingBinStats(
    len(seconds), route_count, len(by_route_direction), len(paired), left_seconds, right_seconds,
    ratio, p25, p75, left_ratio, right_ratio, bilateral_gap, confidence,
  )


def rejection_reason(command: CommandSample, vehicle: VehicleSample,
                     config: GateConfig = DEFAULT_GATE_CONFIG,
                     curvature_offset: float = 0.0) -> str | None:
  desired_angle = command.desired_angle_deg - command.angle_offset_deg
  actual_angle = vehicle.actual_angle_deg - vehicle.angle_offset_deg
  achieved_curvature = vehicle.yaw_rate_rad_s / vehicle.speed_mps if vehicle.speed_mps else math.nan
  desired_from_steer = command.desired_curvature - curvature_offset
  achieved_from_steer = achieved_curvature - curvature_offset
  values = (
    command.timestamp, command.desired_curvature, desired_angle,
    vehicle.timestamp, vehicle.speed_mps, actual_angle, vehicle.steering_rate_deg_s,
    vehicle.yaw_rate_rad_s, vehicle.yaw_rate_std_rad_s,
    vehicle.yaw_accel_rad_s2, vehicle.longitudinal_accel_mps2, vehicle.road_roll_rad,
    vehicle.stiffness_factor,
  )
  if not _finite(*values):
    return "nonfinite"
  if not command.lat_active:
    return "lateral inactive"
  if command.saturated:
    return "steering saturated"
  if command.lane_change_active and not config.allow_lane_changes:
    return "lane change"
  if vehicle.steering_pressed:
    return "driver steering"
  if not vehicle.pose_valid:
    return "invalid pose"
  if not config.min_speed_mps <= vehicle.speed_mps <= config.max_speed_mps:
    return "speed gate"
  if abs(desired_angle) < config.min_angle_deg or abs(actual_angle) < config.min_angle_deg:
    return "angle gate"
  if abs(command.desired_curvature) < config.min_curvature:
    return "desired curvature gate"
  if abs(vehicle.yaw_rate_rad_s) < config.min_yaw_rate_rad_s:
    return "yaw gate"
  if vehicle.yaw_rate_std_rad_s < 0.0 or vehicle.yaw_rate_std_rad_s > config.max_yaw_rate_std_rad_s:
    return "yaw uncertainty"
  if abs(vehicle.yaw_accel_rad_s2) > config.max_yaw_accel_rad_s2:
    return "yaw-accel gate"
  if abs(vehicle.steering_rate_deg_s) > config.max_steering_rate_deg_s:
    return "steering-rate gate"
  if abs(vehicle.longitudinal_accel_mps2) > config.max_longitudinal_accel_mps2:
    return "longitudinal-accel gate"
  if abs(vehicle.road_roll_rad) > config.max_road_roll_rad:
    return "road-roll gate"
  if desired_from_steer * achieved_from_steer <= 0.0:
    return "curvature direction mismatch"
  if desired_angle * actual_angle <= 0.0:
    return "angle direction mismatch"
  tracking_ratio = abs(actual_angle / desired_angle)
  if not config.min_tracking_ratio <= tracking_ratio <= config.max_tracking_ratio:
    return "angle tracking gate"
  factor = correction_factor(command.desired_curvature, achieved_curvature, desired_angle, actual_angle,
                             min_abs_curvature=config.min_curvature, curvature_offset=curvature_offset)
  if factor is None or not config.min_correction_factor <= factor <= config.max_correction_factor:
    return "correction bounds"
  return None


def phase_from_steering(desired_angle_deg: float, steering_rate_deg_s: float,
                        steady_rate_deg_s: float = 1.5) -> str:
  if abs(steering_rate_deg_s) <= steady_rate_deg_s:
    return "steady"
  return "turn-in" if desired_angle_deg * steering_rate_deg_s > 0.0 else "unwind"


def make_bin_key(sample: CorrectionSample, angle_width_deg: float = 5.0,
                 speed_edges_mps: Sequence[float] = DEFAULT_SPEED_EDGES_MPS) -> BinKey:
  if angle_width_deg <= 0.0:
    raise ValueError("angle_width_deg must be positive")
  if len(speed_edges_mps) < 2 or any(b <= a for a, b in zip(speed_edges_mps, speed_edges_mps[1:], strict=False)):
    raise ValueError("speed_edges_mps must increase")
  angle_start = math.floor(abs(sample.angle_deg) / angle_width_deg) * angle_width_deg
  speed_index = bisect_right(speed_edges_mps, sample.speed_mps)
  if speed_index == 0:
    speed_index = 1
  if speed_index >= len(speed_edges_mps):
    speed_index = len(speed_edges_mps) - 1
  return BinKey(
    angle_start,
    angle_start + angle_width_deg,
    float(speed_edges_mps[speed_index - 1]),
    float(speed_edges_mps[speed_index]),
    sample.direction,
    sample.phase,
  )


def _confidence(seconds: int, routes: int, left_seconds: int, right_seconds: int,
                p25: float, p75: float) -> str:
  spread = p75 - p25
  if seconds >= 60 and routes >= 5 and min(left_seconds, right_seconds) >= 20 and spread <= 0.10:
    return "high"
  if seconds >= 20 and routes >= 3 and min(left_seconds, right_seconds) >= 5 and spread <= 0.20:
    return "medium"
  return "low"


def aggregate_bin(samples: Iterable[CorrectionSample]) -> BinStats | None:
  samples = list(samples)
  if not samples:
    return None

  per_second: dict[tuple[str, int, str], list[CorrectionSample]] = {}
  for sample in samples:
    key = sample.route_id, math.floor(sample.timestamp), sample.direction
    per_second.setdefault(key, []).append(sample)

  seconds = []
  for (route_id, second, direction), group in per_second.items():
    finite_required = [sample.required_angle_deg for sample in group if math.isfinite(sample.required_angle_deg)]
    finite_ratios = [sample.effective_ratio for sample in group if math.isfinite(sample.effective_ratio)]
    seconds.append((
      route_id,
      second,
      direction,
      median(sample.correction_factor for sample in group),
      median(sample.tracking_ratio for sample in group),
      median(finite_required) if finite_required else math.nan,
      median(finite_ratios) if finite_ratios else math.nan,
    ))

  route_direction: dict[tuple[str, str], list[tuple[float, float, float, float]]] = {}
  for route_id, _second, direction, factor, tracking, required, ratio in seconds:
    route_direction.setdefault((route_id, direction), []).append((factor, tracking, required, ratio))
  balanced = [median(value[0] for value in values) for values in route_direction.values()]
  balanced_tracking = [median(value[1] for value in values) for values in route_direction.values()]
  balanced_required = [median(value[2] for value in values if math.isfinite(value[2]))
                       for values in route_direction.values() if any(math.isfinite(value[2]) for value in values)]
  balanced_ratios = [median(value[3] for value in values if math.isfinite(value[3]))
                     for values in route_direction.values() if any(math.isfinite(value[3]) for value in values)]
  left_seconds = sum(value[2] == "left" for value in seconds)
  right_seconds = sum(value[2] == "right" for value in seconds)
  p25 = _percentile(balanced, 25.0)
  p75 = _percentile(balanced, 75.0)
  route_count = len({value[0] for value in seconds})
  return BinStats(
    seconds=len(seconds),
    routes=route_count,
    route_directions=len(route_direction),
    left_seconds=left_seconds,
    right_seconds=right_seconds,
    median_factor=float(median(balanced)),
    p25_factor=p25,
    p75_factor=p75,
    median_tracking_ratio=float(median(balanced_tracking)),
    median_required_angle_deg=float(median(balanced_required)) if balanced_required else math.nan,
    median_effective_ratio=float(median(balanced_ratios)) if balanced_ratios else math.nan,
    confidence=_confidence(len(seconds), route_count, left_seconds, right_seconds, p25, p75),
  )
