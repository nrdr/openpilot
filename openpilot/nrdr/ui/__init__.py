"""Lazily loaded NRDR-owned user-interface policy and integration."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.ui.settings_policy import (
    CRUISE_PARAMS,
    UI_CONSTRAINT_PARAMS,
    apply_chevron_preference,
    apply_cruise_preferences,
    apply_speed_limit_preferences,
    hide_global_controller_settings,
    restore_params,
    snapshot_params,
  )


__all__ = (
  "CRUISE_PARAMS",
  "UI_CONSTRAINT_PARAMS",
  "apply_chevron_preference",
  "apply_cruise_preferences",
  "apply_speed_limit_preferences",
  "hide_global_controller_settings",
  "restore_params",
  "snapshot_params",
)
_EXPORT_MODULES = dict.fromkeys(__all__, "openpilot.nrdr.ui.settings_policy")


def __getattr__(name: str):
  module_name = _EXPORT_MODULES.get(name)
  if module_name is None:
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

  value = getattr(import_module(module_name), name)
  globals()[name] = value
  return value


def __dir__() -> list[str]:
  return sorted((*globals(), *_EXPORT_MODULES))
