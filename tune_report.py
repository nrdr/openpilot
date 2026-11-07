#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR lateral tune-report tool."""

import sys

from openpilot.nrdr.tools.lateral import tune_report as _implementation
from openpilot.nrdr.tools.lateral.tune_report import (
  ANGLE_STRAIGHT_DEG,
  BAND_DEFS,
  MIN_SAMPLES,
  MS_TO_MPH,
  PHASE_WORD,
  SCORE_BIAS_FULL_DEG,
  SCORE_FLIP_FLOOR,
  SCORE_FLIP_FULL,
  SCORE_RMS_FULL_DEG,
  SCORE_SAT_FULL_PCT,
  SIDE_WORD,
  Bin,
  compute_score,
  diagnose,
  friendly_report,
  main,
)


__all__ = (
  "ANGLE_STRAIGHT_DEG",
  "BAND_DEFS",
  "MIN_SAMPLES",
  "MS_TO_MPH",
  "PHASE_WORD",
  "SCORE_BIAS_FULL_DEG",
  "SCORE_FLIP_FLOOR",
  "SCORE_FLIP_FULL",
  "SCORE_RMS_FULL_DEG",
  "SCORE_SAT_FULL_PCT",
  "SIDE_WORD",
  "Bin",
  "compute_score",
  "diagnose",
  "friendly_report",
  "main",
)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(_implementation.__doc__)
    raise SystemExit(1)
  main(sys.argv[1:])
