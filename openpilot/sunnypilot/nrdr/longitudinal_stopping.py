"""Compatibility exports for canonical NRDR longitudinal stopping."""

from openpilot.nrdr.features.longitudinal.longitudinal_stopping import (
  ACCELERATION_DUE_TO_GRAVITY,
  CONTROL_DT,
  HARD_HOLD_FLOOR,
  compute_stopping_accel,
)


__all__ = (
  "ACCELERATION_DUE_TO_GRAVITY",
  "CONTROL_DT",
  "HARD_HOLD_FLOOR",
  "compute_stopping_accel",
)
