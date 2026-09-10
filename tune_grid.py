#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR tune-grid tool."""

import sys

from openpilot.nrdr.tools.lateral import tune_grid as _implementation
from openpilot.nrdr.tools.lateral.tune_grid import (
  ANGLE_BIN_DEG,
  ANGLE_MAX_DEG,
  HEATMAP_PNG,
  MIN_ABS_DES,
  MIN_CELL,
  MS_TO_MPH,
  N_ANGLE,
  N_SPEED,
  SPEED_BIN_MPH,
  SPEED_MAX_MPH,
  build_grid,
  cell_stats,
  collect,
  main,
  make_heatmap,
  max_used_angle_bin,
  print_counts,
  print_grid,
)


__all__ = (
  "ANGLE_BIN_DEG",
  "ANGLE_MAX_DEG",
  "HEATMAP_PNG",
  "MIN_ABS_DES",
  "MIN_CELL",
  "MS_TO_MPH",
  "N_ANGLE",
  "N_SPEED",
  "SPEED_BIN_MPH",
  "SPEED_MAX_MPH",
  "build_grid",
  "cell_stats",
  "collect",
  "main",
  "make_heatmap",
  "max_used_angle_bin",
  "print_counts",
  "print_grid",
)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(_implementation.__doc__)
    raise SystemExit(1)
  main(sys.argv[1:])
