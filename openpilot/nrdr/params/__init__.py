"""Public parameter access and metadata for NRDR.

Runtime readers are loaded lazily so build tools can import the standard-library
only parameter catalog before native Params dependencies have been compiled.
"""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from openpilot.nrdr.params.generated.keys import NrdrParamKey
  from openpilot.nrdr.params.defaults import BOOL_DEFAULTS, VALUE_DEFAULTS, apply_defaults
  from openpilot.nrdr.params.profiles import (
    CLARITY_ROAD_TESTED_2026_08_21,
    HANDCRAFTED_EXTERNAL_PARAM_KEYS,
    HANDCRAFTED_LATERAL_PROFILES,
    HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS,
    HONDA_TORQUE_MOD_HANDCRAFTED_VALUES,
    HandcraftedLateralProfile,
    ProfileParamStore,
    ProfileValue,
    apply_handcrafted_lateral_profile,
    get_handcrafted_lateral_profile,
    is_handcrafted_lateral_enabled,
    restore_handcrafted_lateral_profile,
  )
  from openpilot.nrdr.params.snapshots import (
    CONTROL_GROUPS,
    PLANNER_GROUPS,
    REFRESH_PERIOD,
    LiveParams,
    ParamGroup,
    ParamSnapshot,
    get_live_params,
    reset_live_params_for_tests,
  )
  from openpilot.nrdr.params.store import ParamReader, ParamValue, read_bool, read_float
  from openpilot.nrdr.params.ui_metadata import (
    NRDR_UI_METADATA,
    NRDR_UI_METADATA_BY_KEY,
    NumericUiMetadata,
    ParamUiMetadata,
    UiDescriptionSource,
    UiEditPolicy,
    UiRemoteWritePolicy,
    UiWidget,
    get_ui_metadata,
    validate_ui_metadata,
  )


__all__ = (
  "BOOL_DEFAULTS",
  "CLARITY_ROAD_TESTED_2026_08_21",
  "CONTROL_GROUPS",
  "HANDCRAFTED_EXTERNAL_PARAM_KEYS",
  "HANDCRAFTED_LATERAL_PROFILES",
  "HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS",
  "HONDA_TORQUE_MOD_HANDCRAFTED_VALUES",
  "LiveParams",
  "NRDR_UI_METADATA",
  "NRDR_UI_METADATA_BY_KEY",
  "NrdrParamKey",
  "NumericUiMetadata",
  "PLANNER_GROUPS",
  "ParamGroup",
  "ParamReader",
  "ParamSnapshot",
  "ParamUiMetadata",
  "ParamValue",
  "ProfileParamStore",
  "ProfileValue",
  "REFRESH_PERIOD",
  "HandcraftedLateralProfile",
  "UiDescriptionSource",
  "UiEditPolicy",
  "UiRemoteWritePolicy",
  "UiWidget",
  "VALUE_DEFAULTS",
  "apply_defaults",
  "apply_handcrafted_lateral_profile",
  "get_handcrafted_lateral_profile",
  "get_live_params",
  "get_ui_metadata",
  "is_handcrafted_lateral_enabled",
  "read_bool",
  "read_float",
  "reset_live_params_for_tests",
  "restore_handcrafted_lateral_profile",
  "validate_ui_metadata",
)
_EXPORT_MODULES = {
  "BOOL_DEFAULTS": "openpilot.nrdr.params.defaults",
  "VALUE_DEFAULTS": "openpilot.nrdr.params.defaults",
  "apply_defaults": "openpilot.nrdr.params.defaults",
  "CLARITY_ROAD_TESTED_2026_08_21": "openpilot.nrdr.params.profiles",
  "HANDCRAFTED_EXTERNAL_PARAM_KEYS": "openpilot.nrdr.params.profiles",
  "HANDCRAFTED_LATERAL_PROFILES": "openpilot.nrdr.params.profiles",
  "HONDA_TORQUE_MOD_HANDCRAFTED_FINGERPRINTS": "openpilot.nrdr.params.profiles",
  "HONDA_TORQUE_MOD_HANDCRAFTED_VALUES": "openpilot.nrdr.params.profiles",
  "HandcraftedLateralProfile": "openpilot.nrdr.params.profiles",
  "ProfileParamStore": "openpilot.nrdr.params.profiles",
  "ProfileValue": "openpilot.nrdr.params.profiles",
  "apply_handcrafted_lateral_profile": "openpilot.nrdr.params.profiles",
  "get_handcrafted_lateral_profile": "openpilot.nrdr.params.profiles",
  "is_handcrafted_lateral_enabled": "openpilot.nrdr.params.profiles",
  "restore_handcrafted_lateral_profile": "openpilot.nrdr.params.profiles",
  "NRDR_UI_METADATA": "openpilot.nrdr.params.ui_metadata",
  "NRDR_UI_METADATA_BY_KEY": "openpilot.nrdr.params.ui_metadata",
  "NumericUiMetadata": "openpilot.nrdr.params.ui_metadata",
  "ParamUiMetadata": "openpilot.nrdr.params.ui_metadata",
  "UiDescriptionSource": "openpilot.nrdr.params.ui_metadata",
  "UiEditPolicy": "openpilot.nrdr.params.ui_metadata",
  "UiRemoteWritePolicy": "openpilot.nrdr.params.ui_metadata",
  "UiWidget": "openpilot.nrdr.params.ui_metadata",
  "get_ui_metadata": "openpilot.nrdr.params.ui_metadata",
  "validate_ui_metadata": "openpilot.nrdr.params.ui_metadata",
  "CONTROL_GROUPS": "openpilot.nrdr.params.snapshots",
  "PLANNER_GROUPS": "openpilot.nrdr.params.snapshots",
  "REFRESH_PERIOD": "openpilot.nrdr.params.snapshots",
  "LiveParams": "openpilot.nrdr.params.snapshots",
  "ParamGroup": "openpilot.nrdr.params.snapshots",
  "ParamSnapshot": "openpilot.nrdr.params.snapshots",
  "get_live_params": "openpilot.nrdr.params.snapshots",
  "reset_live_params_for_tests": "openpilot.nrdr.params.snapshots",
  "NrdrParamKey": "openpilot.nrdr.params.generated.keys",
  "ParamReader": "openpilot.nrdr.params.store",
  "ParamValue": "openpilot.nrdr.params.store",
  "read_bool": "openpilot.nrdr.params.store",
  "read_float": "openpilot.nrdr.params.store",
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
