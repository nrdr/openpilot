"""Compatibility exports for canonical NRDR cruise-button submode policy."""

from openpilot.nrdr.features.driver_policy.hud_submode import (
  SUBMODE_WINDOW_DEFAULT_S,
  SUBMODE_WINDOW_MAX_S,
  SUBMODE_WINDOW_MIN_S,
  consume_button_press,
)


__all__ = (
  "SUBMODE_WINDOW_DEFAULT_S",
  "SUBMODE_WINDOW_MAX_S",
  "SUBMODE_WINDOW_MIN_S",
  "consume_button_press",
)
