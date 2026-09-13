#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR steer-ratio-by-angle tool."""

from openpilot.nrdr.tools.steer_ratio.by_angle import (
  M_PER_MILE,
  MPS_TO_MPH,
  ROUTE_TIME_RE,
  SEGMENT_DIR_RE,
  AngleRatioSample,
  CarReportData,
  CarStateSample,
  SteerRatioReport,
  angle_bin_start,
  build_parser,
  effective_ratio,
  expand_sources,
  format_duration,
  format_number,
  main,
  nearest_state_sample,
  percentile,
  print_cached_params,
  source_sort_key,
  source_time,
)


__all__ = (
  "M_PER_MILE",
  "MPS_TO_MPH",
  "ROUTE_TIME_RE",
  "SEGMENT_DIR_RE",
  "AngleRatioSample",
  "CarReportData",
  "CarStateSample",
  "SteerRatioReport",
  "angle_bin_start",
  "build_parser",
  "effective_ratio",
  "expand_sources",
  "format_duration",
  "format_number",
  "main",
  "nearest_state_sample",
  "percentile",
  "print_cached_params",
  "source_sort_key",
  "source_time",
)


if __name__ == "__main__":
  raise SystemExit(main())
