import ast
from importlib import import_module
from pathlib import Path
import unittest


UI_MODULES = {
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


if __name__ == "__main__":
  unittest.main()
