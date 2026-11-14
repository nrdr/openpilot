import ast
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
import unittest


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
      "hide_global_controller_settings",
    ),
  ),
}

PURE_MODULES = ("controlsd", "driver_monitoring")
RUNTIME_MODULES = ("events", "events_sp", "selfdrived")


def _modules_available(*module_names: str) -> bool:
  return all(find_spec(module_name) is not None for module_name in module_names)


class TestHookCompatibility(unittest.TestCase):
  def assert_module_identity(self, legacy_name: str) -> None:
    canonical_name, expected_exports = LEGACY_HOOK_EXPORTS[legacy_name]
    canonical = import_module(canonical_name)
    legacy = import_module(f"openpilot.sunnypilot.nrdr.{legacy_name}")
    self.assertEqual(legacy.__all__, expected_exports)
    for name in expected_exports:
      self.assertIs(getattr(legacy, name), getattr(canonical, name), f"{legacy_name}.{name}")

  def test_pure_legacy_hook_modules_preserve_object_identity(self):
    for legacy_name in PURE_MODULES:
      with self.subTest(module=legacy_name):
        self.assert_module_identity(legacy_name)

  @unittest.skipUnless(_modules_available("numpy", "opendbc", "capnp"), "requires OpenPilot runtime dependencies")
  def test_runtime_legacy_hook_modules_preserve_object_identity(self):
    for legacy_name in RUNTIME_MODULES:
      with self.subTest(module=legacy_name):
        self.assert_module_identity(legacy_name)

  @unittest.skipUnless(_modules_available("zmq"), "requires zmq")
  def test_ui_policy_legacy_module_preserves_object_identity(self):
    self.assert_module_identity("settings")

  def test_legacy_hook_modules_are_explicit_forwarders_only(self):
    repository_root = Path(__file__).resolve().parents[3]
    for legacy_name, (canonical_name, expected_exports) in LEGACY_HOOK_EXPORTS.items():
      with self.subTest(module=legacy_name):
        path = repository_root / "openpilot" / "sunnypilot" / "nrdr" / f"{legacy_name}.py"
        tree = ast.parse(path.read_text(), filename=path.name)
        definitions = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
        imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
        self.assertFalse(definitions, legacy_name)
        self.assertEqual(len(imports), 1, legacy_name)
        self.assertEqual(imports[0].module, canonical_name, legacy_name)
        self.assertEqual(tuple(alias.name for alias in imports[0].names), expected_exports, legacy_name)
