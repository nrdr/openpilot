#!/usr/bin/env python3
"""Compatibility facade for the canonical NRDR lateral-stiction shadow tool."""

from openpilot.nrdr.tools.lateral.stiction_shadow import (
  CONTROL_DT,
  MAX_INPUT_AGE_S,
  ZERO_CROSSING_WINDOW_S,
  LatStiction,
  ShadowFrame,
  ShadowResult,
  ShadowSummary,
  TriggerScore,
  build_parser,
  expand_sources,
  iter_local_events,
  iter_shadow_frames,
  main,
  replay_shadow,
  route_segment,
  score_triggers,
  summarize,
)


__all__ = (
  "CONTROL_DT",
  "MAX_INPUT_AGE_S",
  "ZERO_CROSSING_WINDOW_S",
  "LatStiction",
  "ShadowFrame",
  "ShadowResult",
  "ShadowSummary",
  "TriggerScore",
  "build_parser",
  "expand_sources",
  "iter_local_events",
  "iter_shadow_frames",
  "main",
  "replay_shadow",
  "route_segment",
  "score_triggers",
  "summarize",
)


if __name__ == "__main__":
  raise SystemExit(main())
