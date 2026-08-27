import ast
from importlib import import_module
from pathlib import Path
import subprocess
import sys
import unittest


UI_MODULES = {
  "openpilot.sunnypilot.nrdr.circular_alerts": (
    "openpilot.nrdr.ui.onroad.circular_alerts", ("StandstillLatch",),
  ),
  "openpilot.sunnypilot.nrdr.home": (
    "openpilot.nrdr.ui.home.layout", ("REFRESH_INTERVAL", "FirstRunSetup", "NrdrForkWidget", "NrdrHomeLayout"),
  ),
  "openpilot.sunnypilot.nrdr.mici_home": (
    "openpilot.nrdr.ui.home.mici", ("NrdrMiciHome",),
  ),
  "openpilot.sunnypilot.nrdr.mici_hud": (
    "openpilot.nrdr.ui.onroad.mici_hud", ("NrdrHudRenderer",),
  ),
  "openpilot.sunnypilot.nrdr.mici_onroad": (
    "openpilot.nrdr.ui.onroad.mici_onroad",
    ("NrdrAugmentedRoadView", "NrdrConfidenceBall", "NrdrDriverStateRenderer", "StripDevUiRenderer"),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr": (
    "openpilot.nrdr.ui.settings.layout", ("NrdrLayout", "PanelType"),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.footage": (
    "openpilot.nrdr.ui.settings.footage",
    ("COPYPARTY_PORT", "MAX_ROUTES", "ROUTES_MOUNT", "SEGMENT_RE", "FootageLayout", "FootageQrDialog"),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.lateral_tuning": (
    "openpilot.nrdr.ui.settings.lateral_tuning",
    ("MEDIA_ROOT", "RLOG_GLOBS", "TUNE_REPORT_PATH", "TUNE_REPORT_TMP", "LateralPanel", "LateralTuningLayout"),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.longitudinal_tuning": (
    "openpilot.nrdr.ui.settings.longitudinal_tuning", ("LongitudinalTuningLayout",),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.override_tuning": (
    "openpilot.nrdr.ui.settings.override_tuning", ("OverrideTuningLayout",),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.party_tricks": (
    "openpilot.nrdr.ui.settings.party_tricks", ("PartyTricksLayout",),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.pidf_ground": (
    "openpilot.nrdr.ui.settings.pidf_ground", ("PidfGroundLayout",),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.steer_filters": (
    "openpilot.nrdr.ui.settings.steer_filters", ("SteerFiltersLayout",),
  ),
  "openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr_sub_layouts.vehicle_model_learning": (
    "openpilot.nrdr.ui.settings.vehicle_model_learning", ("VehicleModelLearningLayout",),
  ),
}

UI_PRODUCTION_IMPORTS = {
  "openpilot/selfdrive/ui/mici/layouts/main.py": ("openpilot.nrdr.ui.onroad.mici_onroad", "mici_onroad"),
  "openpilot/selfdrive/ui/sunnypilot/layouts/home.py": ("openpilot.nrdr.ui.home.layout", "home"),
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/device.py": ("openpilot.nrdr.ui.settings.device_power", "device_power"),
  "openpilot/selfdrive/ui/sunnypilot/mici/layouts/home.py": ("openpilot.nrdr.ui.home.mici", "mici_home"),
  "openpilot/selfdrive/ui/sunnypilot/mici/layouts/device.py": ("openpilot.nrdr.ui.settings.device_power", "device_power"),
  "openpilot/selfdrive/ui/sunnypilot/mici/onroad/hud_renderer.py": ("openpilot.nrdr.ui.onroad.mici_hud", "mici_hud"),
  "openpilot/selfdrive/ui/sunnypilot/onroad/circular_alerts.py": ("openpilot.nrdr.ui.onroad.circular_alerts", "circular_alerts"),
}


class TestUiOwnership(unittest.TestCase):
  def test_framework_settings_entrypoint_uses_canonical_layout(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (repository_root / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/settings.py").read_text(encoding="utf-8")
    self.assertIn("from openpilot.nrdr.ui.settings.layout import NrdrLayout", source)
    self.assertNotIn("layouts.settings.nrdr import NrdrLayout", source)

  def test_canonical_layouts_never_import_legacy_layouts(self):
    settings_dir = Path(__file__).resolve().parents[1] / "ui" / "settings"
    for path in settings_dir.glob("*.py"):
      with self.subTest(path=path.name):
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("openpilot.selfdrive.ui.sunnypilot.layouts.settings.nrdr", source)

  def test_canonical_native_ui_modules_never_import_legacy_nrdr_modules(self):
    ui_dir = Path(__file__).resolve().parents[1] / "ui"
    for package_name in ("home", "onroad"):
      for path in (ui_dir / package_name).glob("*.py"):
        with self.subTest(path=f"{package_name}/{path.name}"):
          source = path.read_text(encoding="utf-8")
          self.assertNotIn("openpilot.sunnypilot.nrdr", source)

  def test_framework_onroad_entrypoints_use_canonical_owners(self):
    repository_root = Path(__file__).resolve().parents[3]
    for relative_path, (canonical_module, legacy_module) in UI_PRODUCTION_IMPORTS.items():
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text(encoding="utf-8")
        self.assertIn(f"from {canonical_module} import", source)
        self.assertNotIn(f"from openpilot.sunnypilot.nrdr.{legacy_module} import", source)

  def test_native_ui_packages_import_lazily_without_native_dependencies(self):
    repository_root = Path(__file__).resolve().parents[3]
    script = """
import sys
sys.modules["pyray"] = None
import openpilot.nrdr.ui.home
import openpilot.nrdr.ui.onroad
assert "openpilot.nrdr.ui.onroad.circular_alerts" not in sys.modules
assert "openpilot.nrdr.ui.home.layout" not in sys.modules
assert "openpilot.nrdr.ui.home.mici" not in sys.modules
assert "openpilot.nrdr.ui.onroad.mici_hud" not in sys.modules
assert "openpilot.nrdr.ui.onroad.mici_onroad" not in sys.modules
"""
    subprocess.run([sys.executable, "-c", script], cwd=repository_root, check=True)

  def test_translation_extractor_scans_canonical_ui(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (repository_root / "openpilot/selfdrive/ui/translations/update_translations.py").read_text(encoding="utf-8")
    self.assertIn('NRDR_UI_DIR = os.path.join(BASEDIR, "openpilot", "nrdr", "ui")', source)
    self.assertIn("os.walk(NRDR_UI_DIR)", source)

  def test_legacy_layouts_are_explicit_facades(self):
    repository_root = Path(__file__).resolve().parents[3]
    for legacy_name, (canonical_name, expected_exports) in UI_MODULES.items():
      relative = Path(*legacy_name.split(".")).with_suffix(".py")
      tree = ast.parse((repository_root / relative).read_text(encoding="utf-8"), filename=str(relative))
      imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
      assignments = [node for node in tree.body if isinstance(node, ast.Assign)]
      self.assertEqual(len(imports), 1, legacy_name)
      self.assertEqual(imports[0].module, canonical_name)
      self.assertEqual(tuple(alias.name for alias in imports[0].names), expected_exports)
      self.assertEqual(len(assignments), 1, legacy_name)
      self.assertEqual(assignments[0].targets[0].id, "__all__")
      self.assertEqual(ast.literal_eval(assignments[0].value), expected_exports)

  def test_legacy_layouts_preserve_runtime_object_identity(self):
    try:
      import_module("pyray")
    except ModuleNotFoundError as error:
      self.skipTest(f"native UI dependencies unavailable: {error}")

    for legacy_name, (canonical_name, expected_exports) in UI_MODULES.items():
      with self.subTest(module=legacy_name):
        legacy = import_module(legacy_name)
        canonical = import_module(canonical_name)
        self.assertEqual(legacy.__all__, expected_exports)
        for name in expected_exports:
          self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_portable_onroad_facade_preserves_runtime_object_identity(self):
    legacy = import_module("openpilot.sunnypilot.nrdr.circular_alerts")
    canonical = import_module("openpilot.nrdr.ui.onroad.circular_alerts")
    self.assertEqual(legacy.__all__, ("StandstillLatch",))
    self.assertIs(legacy.StandstillLatch, canonical.StandstillLatch)


if __name__ == "__main__":
  unittest.main()
