"""Vehicle-independent, observational angle/speed diagnostics. Never writes tuning.

No extrapolation or pooled speed regression: compare the same route, direction,
vehicle/configuration and one-degree angle cell at two observed speed bands.
Model-normalized SR is compared with raw kinematic SR, roll and stiffness variants.
"""
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
import math
from statistics import median

from openpilot.nrdr.tools.sr_correction_analysis import CorrectionSample, MappingSample, sample_cohort


@dataclass(frozen=True)
class SurfaceConfig:
  angle_width_deg: float = 5.0
  speed_width_mps: float = 5.0
  match_angle_width_deg: float = 1.0
  min_cell_seconds: int = 3
  min_paired_routes: int = 2
  effect_threshold_percent: float = 5.0
  max_matched_angle_gap_deg: float = 0.25

  def __post_init__(self):
    values = (self.angle_width_deg, self.speed_width_mps, self.match_angle_width_deg,
              self.effect_threshold_percent, self.max_matched_angle_gap_deg)
    if any(not math.isfinite(value) or value <= 0 for value in values):
      raise ValueError("surface widths and effect threshold must be finite and positive")
    if self.min_cell_seconds < 1 or self.min_paired_routes < 2:
      raise ValueError("require positive coverage and at least two paired routes")
    if self.match_angle_width_deg > self.angle_width_deg:
      raise ValueError("matched-angle cells must not exceed reporting cells")


def _bin(value: float, width: float) -> float:
  return math.floor(value / width) * width


def _finite_median(values):
  values = [value for value in values if math.isfinite(value)]
  return median(values) if values else math.nan


def _balanced(samples, value):
  """Equal seconds, then equal route/direction weight; not frame-count weight."""
  seconds = defaultdict(list)
  for sample in samples:
    number = value(sample)
    if math.isfinite(number):
      seconds[(sample.route_id, sample.direction, math.floor(sample.timestamp))].append(number)
  routes = defaultdict(list)
  for (route, direction, _second), values in seconds.items():
    routes[(route, direction)].append(median(values))
  return _finite_median(median(values) for values in routes.values())


def _variant(sample, field):
  value = getattr(sample, field)
  return (value * abs(sample.bias_corrected_angle_deg / sample.signed_angle_deg)
          if sample.signed_angle_deg else math.nan)


def _valid_mapping(sample):
  return (math.isfinite(sample.bias_corrected_angle_deg)
          and math.isfinite(sample.speed_mps) and sample.speed_mps > 0
          and math.isfinite(sample.bias_corrected_effective_ratio)
          and sample.bias_corrected_effective_ratio > 0)


def mapping_surface(samples: list[MappingSample], config: SurfaceConfig) -> list[dict]:
  groups = defaultdict(list)
  for sample in samples:
    if _valid_mapping(sample):
      key = (sample_cohort(sample), _bin(abs(sample.bias_corrected_angle_deg), config.angle_width_deg),
             _bin(sample.speed_mps, config.speed_width_mps), sample.direction)
      groups[key].append(sample)
  rows = []
  for (cohort, angle, speed, direction), group in sorted(groups.items()):
    ratio = _balanced(group, lambda sample: sample.bias_corrected_effective_ratio)
    rows.append({
      "cohort": cohort, "fingerprint": group[0].fingerprint, "eps_firmware": group[0].eps_firmware,
      "steering_fault": group[0].steering_fault,
      "angle_start_deg": angle, "angle_end_deg": angle + config.angle_width_deg,
      "speed_start_mps": speed, "speed_end_mps": speed + config.speed_width_mps, "direction": direction,
      "occupied_seconds": len({(s.route_id, math.floor(s.timestamp)) for s in group}),
      "routes": len({s.route_id for s in group}),
      "dwells": len({(s.route_id, s.dwell_id) for s in group}),
      "model_normalized_sr": ratio,
      "geometric_sr": _balanced(group, lambda s: _variant(s, "geometric_effective_ratio")),
      "zero_roll_sr": _balanced(group, lambda s: _variant(s, "zero_roll_effective_ratio")),
      "unit_stiffness_sr": _balanced(group, lambda s: _variant(s, "unit_stiffness_effective_ratio")),
      "uncorrected_sr": _balanced(group, lambda s: s.effective_ratio),
      "median_angle_deg": _balanced(group, lambda s: abs(s.bias_corrected_angle_deg)),
      "median_speed_mps": _balanced(group, lambda s: s.speed_mps),
      "status": "observational cell; not a deployable ratio",
    })
  return rows


def matched_speed_comparisons(samples: list[MappingSample], config: SurfaceConfig) -> list[dict]:
  cells = defaultdict(lambda: defaultdict(list))
  for sample in samples:
    if _valid_mapping(sample):
      angle = abs(sample.bias_corrected_angle_deg)
      key = (sample_cohort(sample), _bin(angle, config.angle_width_deg),
             _bin(angle, config.match_angle_width_deg), sample.route_id, sample.direction)
      cells[key][_bin(sample.speed_mps, config.speed_width_mps)].append(sample)
  comparisons = defaultdict(list)
  for (cohort, angle, _fine_angle, route, direction), speeds in cells.items():
    usable = {speed: group for speed, group in speeds.items()
              if len({math.floor(s.timestamp) for s in group}) >= config.min_cell_seconds}
    for low, high in combinations(sorted(usable), 2):
      first, second = usable[low], usable[high]
      angle_gap = abs(_balanced(first, lambda s: abs(s.bias_corrected_angle_deg)) -
                      _balanced(second, lambda s: abs(s.bias_corrected_angle_deg)))
      if angle_gap > config.max_matched_angle_gap_deg:
        continue
      row = {"route": route, "direction": direction, "angle_gap": angle_gap}
      metrics = {
        "normalized": lambda s: s.bias_corrected_effective_ratio,
        "geometric": lambda s: _variant(s, "geometric_effective_ratio"),
        "zero_roll": lambda s: _variant(s, "zero_roll_effective_ratio"),
        "unit_stiffness": lambda s: _variant(s, "unit_stiffness_effective_ratio"),
        "uncorrected": lambda s: s.effective_ratio,
      }
      for name, metric in metrics.items():
        a, b = _balanced(first, metric), _balanced(second, metric)
        row[name] = 100 * (b / a - 1) if math.isfinite(a) and a > 0 else math.nan
      comparisons[(cohort, angle, low, high)].append(row)
  rows = []
  for (cohort, angle, low, high), pairs in sorted(comparisons.items()):
    by_route_direction = defaultdict(list)
    for pair in pairs:
      by_route_direction[(pair["route"], pair["direction"])].append(pair)
    balanced = [{"route": route, "direction": direction,
                 **{name: _finite_median(p[name] for p in group)
                    for name in ("normalized", "geometric", "zero_roll", "unit_stiffness", "uncorrected")}}
                for (route, direction), group in by_route_direction.items()]
    shifts = {name: _finite_median(p[name] for p in balanced)
              for name in ("normalized", "geometric", "zero_roll", "unit_stiffness", "uncorrected")}
    bilateral_routes = {p["route"] for p in balanced if p["direction"] == "left"} & {
      p["route"] for p in balanced if p["direction"] == "right"}
    supported = len(bilateral_routes) >= config.min_paired_routes
    sensitivity = max((abs(shifts[name] - shifts["normalized"])
                       for name in ("zero_roll", "unit_stiffness", "uncorrected")
                       if math.isfinite(shifts[name])), default=math.inf)
    agreement = sum(p["normalized"] * shifts["normalized"] > 0 for p in balanced) / len(balanced)
    variants_complete = all(math.isfinite(pair[name]) for pair in pairs
                            for name in ("zero_roll", "unit_stiffness", "uncorrected"))
    if cohort.endswith("|faulted=1"):
      status = "steering-fault-tagged observations; diagnostic only"
    elif not supported:
      status = "insufficient matched bilateral route coverage"
    elif not variants_complete or sensitivity > config.effect_threshold_percent:
      status = "model/offset-sensitive; speed correction not isolated"
    elif agreement < 0.8 and max(abs(p["normalized"]) for p in balanced) > config.effect_threshold_percent:
      status = "inconsistent route/direction residual"
    elif abs(shifts["normalized"]) <= config.effect_threshold_percent:
      status = "no resolved speed residual in observed cells"
    elif agreement < 0.8:
      status = "inconsistent route/direction residual"
    else:
      status = "repeatable speed-associated residual; cause not identified"
    rows.append({
      "cohort": cohort, "angle_start_deg": angle, "angle_end_deg": angle + config.angle_width_deg,
      "low_speed_start_mps": low, "high_speed_start_mps": high, "speed_width_mps": config.speed_width_mps,
      "matched_angle_width_deg": config.match_angle_width_deg,
      "matched_cells": len(pairs), "paired_route_directions": len(balanced),
      "max_median_angle_gap_deg": max(p["angle_gap"] for p in pairs),
      "bilateral_routes": len(bilateral_routes),
      **{name + "_change_percent": value for name, value in shifts.items()},
      "model_offset_sensitivity_points": sensitivity, "direction_agreement_fraction": agreement,
      "route_direction_spread_points": max(p["normalized"] for p in balanced) - min(p["normalized"] for p in balanced),
      "status": status,
    })
  return rows


def tracking_surface(samples: list[CorrectionSample], config: SurfaceConfig) -> list[dict]:
  groups = defaultdict(list)
  for sample in samples:
    if (sample.quality == "strict" and sample.phase == "steady"
        and sample.command_output_available and not sample.safety_limited):
      key = (sample_cohort(sample), _bin(abs(sample.desired_angle_deg), config.angle_width_deg),
             _bin(sample.speed_mps, config.speed_width_mps), sample.direction)
      groups[key].append(sample)
  rows = []
  for (cohort, angle, speed, direction), group in sorted(groups.items()):
    tracking = _balanced(group, lambda s: s.tracking_ratio)
    mapping = _balanced(group, lambda s: s.correction_factor)
    seconds = len({(s.route_id, math.floor(s.timestamp)) for s in group})
    routes = len({s.route_id for s in group})
    lag_pairs = [s for s in group if math.isfinite(s.factor_delay_minus_100ms)
                 and math.isfinite(s.factor_delay_plus_100ms)]
    lag_span = _balanced(lag_pairs, lambda s: 100 * abs(s.factor_delay_plus_100ms - s.factor_delay_minus_100ms))
    lag_seconds = len({(s.route_id, math.floor(s.timestamp)) for s in lag_pairs})
    if seconds < config.min_cell_seconds or routes < config.min_paired_routes:
      status = "insufficient coverage"
    elif abs(tracking - 1) <= 0.05 and mapping > 1.05:
      status = "angle tracks but curvature undershoots; inspect mapping/model"
    elif tracking < 0.95 and mapping > 1.05:
      status = "both angle tracking and mapping/model mismatch"
    elif tracking < 0.95:
      status = "angle undershoot; SR alone does not explain tracking error"
    else:
      status = "no isolated undershoot signature"
    if lag_seconds < config.min_cell_seconds:
      timing_status = "insufficient +/-100 ms pairing; nominal result only"
    elif lag_span > config.effect_threshold_percent:
      timing_status = "lag-sensitive; resolve timing before interpreting mapping"
    else:
      timing_status = "low +/-100 ms sensitivity on available pairs"
    rows.append({
      "cohort": cohort, "requested_angle_start_deg": angle,
      "speed_start_mps": speed, "speed_end_mps": speed + config.speed_width_mps, "direction": direction,
      "occupied_seconds": seconds, "routes": routes,
      "actual_over_requested_angle": tracking, "tracking_cancelled_mapping_factor": mapping,
      "lag_paired_seconds": lag_seconds, "lag_sensitivity_points": lag_span, "timing_status": timing_status,
      "status": status, "caveat": "steady observations at selected command lag; not causal proof or an SR trim",
    })
  return rows
