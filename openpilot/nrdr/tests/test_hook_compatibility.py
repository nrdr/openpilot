import ast
from importlib import import_module
from pathlib import Path

import pytest


LEGACY_HOOK_EXPORTS = {
  "controlsd": (
    "openpilot.nrdr.hooks.controlsd",
    (
      "initialize_live_parameter_settings",
      "refresh_live_parameter_settings",
      "vehicle_model_params",
      "stopping_inputs",
      "apply_hud_lead",
    ),
  ),
  "driver_monitoring": (
    "openpilot.nrdr.hooks.driver_monitoring",
    ("apply_driver_monitoring_policy",),
  ),
  "events": (
    "openpilot.nrdr.hooks.events",
    ("EventName", "GearShifter", "filter_car_events", "keep_lateral_active", "is_drivable_gear", "allow_longitudinal"),
  ),
  "events_sp": (
    "openpilot.nrdr.hooks.events_sp",
    ("speed_limit_pre_active_alert", "apply_events"),
  ),
  "selfdrived": (
    "openpilot.nrdr.hooks.selfdrived",
    ("ButtonType", "NrdrSelfdrive"),
  ),
  "settings": (
    "openpilot.nrdr.ui.settings_policy",
    (
      "CRUISE_PARAMS",
      "UI_CONSTRAINT_PARAMS",
      "snapshot_params",
      "restore_params",
      "apply_cruise_preferences",
      "apply_speed_limit_preferences",
      "apply_chevron_preference",
      "apply_handcrafted_delay_controls",
      "hide_global_controller_settings",
    ),
  ),
}

PURE_MODULES = ("controlsd", "driver_monitoring")
RUNTIME_MODULES = ("events", "events_sp", "selfdrived")


def _assert_module_identity(legacy_name: str) -> None:
  canonical_name, expected_exports = LEGACY_HOOK_EXPORTS[legacy_name]
  canonical = import_module(canonical_name)
  legacy = import_module(f"openpilot.sunnypilot.nrdr.{legacy_name}")
  assert legacy.__all__ == expected_exports
  for name in expected_exports:
    assert getattr(legacy, name) is getattr(canonical, name), f"{legacy_name}.{name}"


@pytest.mark.parametrize("legacy_name", PURE_MODULES)
def test_pure_legacy_hook_modules_preserve_object_identity(legacy_name):
  _assert_module_identity(legacy_name)


@pytest.mark.parametrize("legacy_name", RUNTIME_MODULES)
def test_runtime_legacy_hook_modules_preserve_object_identity(legacy_name):
  pytest.importorskip("numpy")
  pytest.importorskip("opendbc")
  pytest.importorskip("capnp")
  _assert_module_identity(legacy_name)


def test_ui_policy_legacy_module_preserves_object_identity():
  pytest.importorskip("zmq")
  _assert_module_identity("settings")


def test_legacy_hook_modules_are_explicit_forwarders_only():
  repository_root = Path(__file__).resolve().parents[3]
  for legacy_name, (canonical_name, expected_exports) in LEGACY_HOOK_EXPORTS.items():
    path = repository_root / "openpilot" / "sunnypilot" / "nrdr" / f"{legacy_name}.py"
    tree = ast.parse(path.read_text(), filename=path.name)
    definitions = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    assert not definitions, legacy_name
    assert len(imports) == 1, legacy_name
    assert imports[0].module == canonical_name, legacy_name
    assert tuple(alias.name for alias in imports[0].names) == expected_exports, legacy_name
