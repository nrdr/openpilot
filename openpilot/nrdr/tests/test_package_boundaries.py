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


class TestPackageBoundaries(unittest.TestCase):
  def test_package_is_first_class_under_openpilot(self):
    package_path = Path(openpilot.nrdr.__file__).resolve().parent
    self.assertEqual(package_path.name, "nrdr")
    self.assertEqual(package_path.parent.name, "openpilot")
    self.assertIsNotNone(import_module("openpilot.nrdr.features"))
    self.assertIsNotNone(import_module("openpilot.nrdr.hooks"))
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
