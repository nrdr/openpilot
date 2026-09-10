#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR lateral tune-trace tool."""

import sys

from openpilot.nrdr.tools.lateral import tune_trace as _implementation
from openpilot.nrdr.tools.lateral.tune_trace import (
  GAP_S,
  MAX_MPH,
  MAX_ROWS,
  MIN_ABS_DES,
  MIN_EVENT_S,
  MS_TO_MPH,
  TOP_EVENTS,
  collect,
  event_stats,
  find_events,
  main,
)


__all__ = (
  "GAP_S",
  "MAX_MPH",
  "MAX_ROWS",
  "MIN_ABS_DES",
  "MIN_EVENT_S",
  "MS_TO_MPH",
  "TOP_EVENTS",
  "collect",
  "event_stats",
  "find_events",
  "main",
)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(_implementation.__doc__)
    raise SystemExit(1)
  main(sys.argv[1:])
