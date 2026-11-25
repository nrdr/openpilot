"""Compatibility exports for canonical NRDR speed-limit policy."""

from openpilot.nrdr.features.driver_policy.speed_limit import (
  HONDA_MPH_OFFSET,
  HONDA_MPH_PER_KPH,
  LIMIT_AHEAD_PREEMPTIVE_DISTANCE,
  SpeedLimitConfirmation,
  apply_map_limit,
  compare_cluster_target,
  honda_kph_to_mph,
  honda_mph_to_kph,
  is_honda,
  pre_active_icon,
  quantize_set_speed,
)


__all__ = (
  "HONDA_MPH_OFFSET",
  "HONDA_MPH_PER_KPH",
  "LIMIT_AHEAD_PREEMPTIVE_DISTANCE",
  "SpeedLimitConfirmation",
  "apply_map_limit",
  "compare_cluster_target",
  "honda_kph_to_mph",
  "honda_mph_to_kph",
  "is_honda",
  "pre_active_icon",
  "quantize_set_speed",
)
