"""Compatibility exports for the canonical NRDR Clarity hybrid controller."""

from openpilot.nrdr.features.lateral.latcontrol_clarity_hybrid import (
  BLEND_TO_NNLC_SECONDS,
  BLEND_TO_PID_SECONDS,
  NNLC_BLEND_HALF_WIDTH,
  NNLC_DEFAULT_ACTIVATION_SPEED,
  ClarityHybridExtension,
  LatControlClarityHybrid,
  clarity_nnlc_blend_target,
)


__all__ = (
  "BLEND_TO_NNLC_SECONDS",
  "BLEND_TO_PID_SECONDS",
  "NNLC_BLEND_HALF_WIDTH",
  "NNLC_DEFAULT_ACTIVATION_SPEED",
  "ClarityHybridExtension",
  "LatControlClarityHybrid",
  "clarity_nnlc_blend_target",
)
