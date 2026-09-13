"""Thin, lazily loaded adapters between openpilot processes and NRDR."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.hooks.controlsd import (
    apply_hud_lead,
    initialize_live_parameter_settings,
    refresh_live_parameter_settings,
    stopping_inputs,
    vehicle_model_params,
    vehicle_model_state,
  )
  from openpilot.nrdr.hooks.driver_monitoring import apply_driver_monitoring_policy
  from openpilot.nrdr.hooks.events import allow_longitudinal, filter_car_events, is_drivable_gear, keep_lateral_active
  from openpilot.nrdr.hooks.events_sp import apply_events, speed_limit_pre_active_alert
  from openpilot.nrdr.hooks.selfdrived import NrdrSelfdrive


__all__ = (
  "NrdrSelfdrive",
  "allow_longitudinal",
  "apply_driver_monitoring_policy",
  "apply_events",
  "apply_hud_lead",
  "filter_car_events",
  "initialize_live_parameter_settings",
  "is_drivable_gear",
  "keep_lateral_active",
  "refresh_live_parameter_settings",
  "speed_limit_pre_active_alert",
  "stopping_inputs",
  "vehicle_model_params",
  "vehicle_model_state",
)
_EXPORT_MODULES = {
  "apply_hud_lead": "openpilot.nrdr.hooks.controlsd",
  "initialize_live_parameter_settings": "openpilot.nrdr.hooks.controlsd",
  "refresh_live_parameter_settings": "openpilot.nrdr.hooks.controlsd",
  "stopping_inputs": "openpilot.nrdr.hooks.controlsd",
  "vehicle_model_params": "openpilot.nrdr.hooks.controlsd",
  "vehicle_model_state": "openpilot.nrdr.hooks.controlsd",
  "apply_driver_monitoring_policy": "openpilot.nrdr.hooks.driver_monitoring",
  "allow_longitudinal": "openpilot.nrdr.hooks.events",
  "filter_car_events": "openpilot.nrdr.hooks.events",
  "is_drivable_gear": "openpilot.nrdr.hooks.events",
  "keep_lateral_active": "openpilot.nrdr.hooks.events",
  "apply_events": "openpilot.nrdr.hooks.events_sp",
  "speed_limit_pre_active_alert": "openpilot.nrdr.hooks.events_sp",
  "NrdrSelfdrive": "openpilot.nrdr.hooks.selfdrived",
}


def __getattr__(name: str):
  module_name = _EXPORT_MODULES.get(name)
  if module_name is None:
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

  value = getattr(import_module(module_name), name)
  globals()[name] = value
  return value


def __dir__() -> list[str]:
  return sorted((*globals(), *_EXPORT_MODULES))
