"""Public API for NRDR cruise, speed-limit, and driving-policy features."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.features.driver_policy.cruise import NrdrCruise
  from openpilot.nrdr.features.driver_policy.dec import enforce_mode_dwell, slow_down_threshold
  from openpilot.nrdr.features.driver_policy.hud_submode import consume_button_press
  from openpilot.nrdr.features.driver_policy.lane_change import driver_nudging, torque_controller_active, torque_from_lateral_accel
  from openpilot.nrdr.features.driver_policy.mads import AutoLkas
  from openpilot.nrdr.features.driver_policy.speed_limit import (
    SpeedLimitConfirmation,
    apply_map_limit,
    compare_cluster_target,
    pre_active_icon,
    quantize_set_speed,
  )
  from openpilot.nrdr.features.driver_policy.speed_limit_assist import NrdrSpeedLimitAssist


__all__ = (
  "AutoLkas",
  "NrdrCruise",
  "NrdrSpeedLimitAssist",
  "SpeedLimitConfirmation",
  "apply_map_limit",
  "compare_cluster_target",
  "consume_button_press",
  "driver_nudging",
  "enforce_mode_dwell",
  "pre_active_icon",
  "quantize_set_speed",
  "slow_down_threshold",
  "torque_controller_active",
  "torque_from_lateral_accel",
)
_EXPORT_MODULES = {
  "AutoLkas": "openpilot.nrdr.features.driver_policy.mads",
  "NrdrCruise": "openpilot.nrdr.features.driver_policy.cruise",
  "enforce_mode_dwell": "openpilot.nrdr.features.driver_policy.dec",
  "slow_down_threshold": "openpilot.nrdr.features.driver_policy.dec",
  "consume_button_press": "openpilot.nrdr.features.driver_policy.hud_submode",
  "driver_nudging": "openpilot.nrdr.features.driver_policy.lane_change",
  "SpeedLimitConfirmation": "openpilot.nrdr.features.driver_policy.speed_limit",
  "apply_map_limit": "openpilot.nrdr.features.driver_policy.speed_limit",
  "compare_cluster_target": "openpilot.nrdr.features.driver_policy.speed_limit",
  "pre_active_icon": "openpilot.nrdr.features.driver_policy.speed_limit",
  "quantize_set_speed": "openpilot.nrdr.features.driver_policy.speed_limit",
  "NrdrSpeedLimitAssist": "openpilot.nrdr.features.driver_policy.speed_limit_assist",
  "torque_controller_active": "openpilot.nrdr.features.driver_policy.lane_change",
  "torque_from_lateral_accel": "openpilot.nrdr.features.driver_policy.lane_change",
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
