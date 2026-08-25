import ast
from importlib import import_module
from pathlib import Path
import unittest

import openpilot.nrdr
from openpilot.nrdr.params import NrdrParamKey, ParamReader, ParamValue, read_bool, read_float


MIGRATED_CONSUMERS = (
  "latcontrol_pid.py",
  "longcontrol.py",
  "longitudinal_planner.py",
  "nnlc.py",
  "tune_learner.py",
)

PHASE_TWO_CONSUMERS = (
  "openpilot/selfdrive/car/card.py",
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/lateral_tuning.py",
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/override_tuning.py",
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/pidf_ground.py",
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/steer_filters.py",
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/vehicle_model_learning.py",
  "openpilot/sunnypilot/nrdr/car_tune_report.py",
  "openpilot/sunnypilot/nrdr/controlsd.py",
  "openpilot/sunnypilot/nrdr/latcontrol_pid.py",
  "openpilot/sunnypilot/nrdr/longcontrol.py",
  "openpilot/sunnypilot/nrdr/longitudinal_planner.py",
  "openpilot/sunnypilot/nrdr/nnlc.py",
  "openpilot/sunnypilot/nrdr/settings.py",
  "openpilot/sunnypilot/nrdr/tune_learner.py",
  "openpilot/sunnypilot/sunnylink/capabilities.py",
  "openpilot/system/manager/manager.py",
)


class TestPackageBoundaries(unittest.TestCase):
  def test_package_is_first_class_under_openpilot(self):
    package_path = Path(openpilot.nrdr.__file__).resolve().parent
    self.assertEqual(package_path.name, "nrdr")
    self.assertEqual(package_path.parent.name, "openpilot")
    self.assertIsNotNone(import_module("openpilot.nrdr.features"))
    self.assertIsNotNone(import_module("openpilot.nrdr.features.lateral"))
    self.assertIsNotNone(import_module("openpilot.nrdr.hooks"))
    self.assertIsNotNone(import_module("openpilot.nrdr.tools"))
    self.assertIsNotNone(import_module("openpilot.nrdr.ui"))

  def test_legacy_parameter_module_forwards_public_objects(self):
    legacy = import_module("openpilot.sunnypilot.nrdr.params")
    self.assertIs(legacy.NrdrParamKey, NrdrParamKey)
    self.assertIs(legacy.ParamReader, ParamReader)
    self.assertIs(legacy.ParamValue, ParamValue)
    self.assertIs(legacy.read_bool, read_bool)
    self.assertIs(legacy.read_float, read_float)
    self.assertEqual(legacy.__all__, ("NrdrParamKey", "ParamReader", "ParamValue", "read_bool", "read_float"))

  def test_first_consumers_use_public_parameter_api(self):
    legacy_dir = Path(__file__).resolve().parents[2] / "sunnypilot" / "nrdr"
    for filename in MIGRATED_CONSUMERS:
      with self.subTest(filename=filename):
        source = (legacy_dir / filename).read_text()
        self.assertIn("from openpilot.nrdr.params import", source)
        self.assertNotIn("from openpilot.sunnypilot.nrdr.params import", source)

  def test_migrated_readers_do_not_use_static_string_keys(self):
    legacy_dir = Path(__file__).resolve().parents[2] / "sunnypilot" / "nrdr"
    failures: list[str] = []
    for filename in MIGRATED_CONSUMERS:
      tree = ast.parse((legacy_dir / filename).read_text(), filename=filename)
      for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
          continue
        if node.func.id not in ("read_bool", "read_float") or len(node.args) < 2:
          continue
        key = node.args[1]
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
          failures.append(f"{filename}:{node.lineno}: {key.value}")
    self.assertEqual(failures, [], "static parameter keys must use NrdrParamKey")

  def test_phase_two_consumers_use_the_public_facade(self):
    repository_root = Path(__file__).resolve().parents[3]
    forbidden = (
      "from openpilot.nrdr.params.defaults import",
      "from openpilot.nrdr.params.profiles import",
      "from openpilot.nrdr.params.snapshots import",
      "from openpilot.sunnypilot.nrdr.handcrafted_lateral import",
      "from openpilot.sunnypilot.nrdr.live_params import",
      "from openpilot.sunnypilot.nrdr.manager import",
    )
    for relative_path in PHASE_TWO_CONSUMERS:
      with self.subTest(path=relative_path):
        source = (repository_root / relative_path).read_text()
        self.assertIn("from openpilot.nrdr.params import", source)
        self.assertFalse(any(import_line in source for import_line in forbidden))

  def test_public_parameter_exports_are_lazy_and_complete(self):
    params_package = import_module("openpilot.nrdr.params")
    self.assertEqual(set(params_package.__all__), set(params_package._EXPORT_MODULES))
    self.assertEqual(len(params_package.__all__), len(set(params_package.__all__)))

  def test_ui_metadata_keeps_params_dependency_direction(self):
    params_dir = Path(__file__).resolve().parent.parent / "params"
    tree = ast.parse((params_dir / "ui_metadata.py").read_text(), filename="ui_metadata.py")
    forbidden_prefixes = (
      "openpilot.common",
      "openpilot.nrdr.features",
      "openpilot.nrdr.hooks",
      "openpilot.nrdr.ui",
      "openpilot.selfdrive",
      "openpilot.system.ui",
      "openpilot.sunnypilot",
    )
    imported: list[str] = []
    for node in ast.walk(tree):
      if isinstance(node, ast.Import):
        imported.extend(alias.name for alias in node.names)
      elif isinstance(node, ast.ImportFrom) and node.module is not None:
        imported.append(node.module)
    self.assertFalse(any(name.startswith(forbidden_prefixes) for name in imported), imported)

  def test_legacy_steer_ratio_analysis_preserves_all_public_object_identities(self):
    canonical = import_module("openpilot.nrdr.tools.sr_correction_analysis")
    legacy = import_module("openpilot.sunnypilot.nrdr.sr_correction_analysis")
    canonical_path = Path(canonical.__file__).resolve()
    tree = ast.parse(canonical_path.read_text(), filename=canonical_path.name)
    module_defined: set[str] = set()
    for node in tree.body:
      if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        if not node.name.startswith("_"):
          module_defined.add(node.name)
      elif isinstance(node, ast.Assign):
        for target in node.targets:
          if isinstance(target, ast.Name) and not target.id.startswith("_"):
            module_defined.add(target.id)
      elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and not node.target.id.startswith("_"):
        module_defined.add(node.target.id)

    self.assertIn("T", module_defined)
    self.assertEqual(set(legacy.__all__), module_defined)
    self.assertEqual(len(legacy.__all__), len(module_defined))
    for name in legacy.__all__:
      with self.subTest(name=name):
        self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_root_steer_ratio_cli_imports_the_canonical_analysis_module(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (repository_root / "steerratio_correction.py").read_text()
    self.assertIn("from openpilot.nrdr.tools.sr_correction_analysis import", source)
    self.assertNotIn("from openpilot.sunnypilot.nrdr.sr_correction_analysis import", source)

  def test_legacy_phase_detector_preserves_public_object_identities(self):
    canonical = import_module("openpilot.nrdr.features.lateral.phase_detector")
    legacy = import_module("openpilot.sunnypilot.nrdr.phase_detector")
    self.assertEqual(legacy.__all__, ("PHASE_SWITCH_MIN_SPEED", "phase_with_latch"))
    for name in legacy.__all__:
      with self.subTest(name=name):
        self.assertIs(getattr(legacy, name), getattr(canonical, name))

  def test_legacy_latcontrol_pid_imports_the_canonical_phase_detector(self):
    repository_root = Path(__file__).resolve().parents[3]
    source = (repository_root / "openpilot/sunnypilot/nrdr/latcontrol_pid.py").read_text()
    self.assertIn("from openpilot.nrdr.features.lateral.phase_detector import phase_with_latch", source)
    self.assertNotIn("from openpilot.sunnypilot.nrdr.phase_detector import", source)
