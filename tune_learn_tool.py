#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR tune-learner companion tool."""

import sys

from openpilot.nrdr.tools.lateral.tune_learn import (
  HEATMAP_PNG,
  PARAM_KEY,
  SEED_CAP,
  SEED_GAIN,
  SEED_MIN_SPEED_BIN,
  STEER_MAX,
  cmd_seed,
  cmd_view,
  load_map,
  main,
  make_heatmap,
  print_map,
  save_map,
)


__all__ = (
  "HEATMAP_PNG",
  "PARAM_KEY",
  "SEED_CAP",
  "SEED_GAIN",
  "SEED_MIN_SPEED_BIN",
  "STEER_MAX",
  "cmd_seed",
  "cmd_view",
  "load_map",
  "main",
  "make_heatmap",
  "print_map",
  "save_map",
)


if __name__ == "__main__":
  main(sys.argv[1:])
