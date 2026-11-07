#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR tune-attribution tool."""

import sys

from openpilot.nrdr.tools.lateral import tune_attribute as _implementation
from openpilot.nrdr.tools.lateral.tune_attribute import (
  ANGLE_BIN_DEG,
  DT,
  FF_DOMINATED,
  GUIDE,
  I_HEAVY,
  MIN_ABS_DES,
  MIN_SAMPLES,
  MS_TO_MPH,
  RATE_PRESENT,
  RATE_SIG,
  RESID_REPORT,
  SPEED_BIN_MPH,
  TOP_N,
  analyze,
  collect,
  main,
  offset_flag,
  paramsd_context,
  print_cells,
)


__all__ = (
  "ANGLE_BIN_DEG",
  "DT",
  "FF_DOMINATED",
  "GUIDE",
  "I_HEAVY",
  "MIN_ABS_DES",
  "MIN_SAMPLES",
  "MS_TO_MPH",
  "RATE_PRESENT",
  "RATE_SIG",
  "RESID_REPORT",
  "SPEED_BIN_MPH",
  "TOP_N",
  "analyze",
  "collect",
  "main",
  "offset_flag",
  "paramsd_context",
  "print_cells",
)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(_implementation.__doc__)
    raise SystemExit(1)
  main(sys.argv[1:])
