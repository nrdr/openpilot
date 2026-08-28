import ast
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT_TOOL_FACADES = {
  "lateral_attribution.py": "openpilot.nrdr.tools.lateral.attribution",
  "lat_stiction_shadow.py": "openpilot.nrdr.tools.lateral.stiction_shadow",
  "steerratio_by_angle.py": "openpilot.nrdr.tools.steer_ratio.by_angle",
  "steerratio_correction.py": "openpilot.nrdr.tools.steer_ratio.correction",
  "tune_attribute.py": "openpilot.nrdr.tools.lateral.tune_attribute",
  "tune_grid.py": "openpilot.nrdr.tools.lateral.tune_grid",
  "tune_learn_tool.py": "openpilot.nrdr.tools.lateral.tune_learn",
  "tune_report.py": "openpilot.nrdr.tools.lateral.tune_report",
  "tune_trace.py": "openpilot.nrdr.tools.lateral.tune_trace",
}

RADAR_FACADE_MODULES = (
  "__init__",
  "cli",
  "enums",
  "gates",
  "ingest",
  "pairing",
  "report",
  "sweep",
)

CANONICAL_TOOL_DIRS = (
  "openpilot/nrdr/tools/lateral",
  "openpilot/nrdr/tools/steer_ratio",
  "openpilot/nrdr/tools/radar_re",
  "openpilot/nrdr/tools/eps",
)


def _literal_all(tree: ast.Module) -> tuple[str, ...]:
  assignments = [
    node for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
  ]
  if len(assignments) != 1:
    raise AssertionError(f"expected one __all__ assignment, found {len(assignments)}")
  return ast.literal_eval(assignments[0].value)


class TestToolBoundaries(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.repository_root = Path(__file__).resolve().parents[3]

  def assert_explicit_facade(self, path: Path, canonical_module: str):
    tree = ast.parse(path.read_text(), filename=str(path))
    exports = _literal_all(tree)
    canonical_imports = [
      node for node in tree.body
      if isinstance(node, ast.ImportFrom) and node.module == canonical_module
    ]
    self.assertEqual(len(canonical_imports), 1, path)
    self.assertEqual(tuple(alias.name for alias in canonical_imports[0].names), exports, path)
    self.assertEqual(len(exports), len(set(exports)), path)
    self.assertFalse(any(isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) for node in tree.body), path)

  def test_root_cli_files_are_explicit_canonical_facades(self):
    for relative_path, canonical_module in ROOT_TOOL_FACADES.items():
      with self.subTest(path=relative_path):
        self.assert_explicit_facade(self.repository_root / relative_path, canonical_module)

  def test_old_radar_package_is_an_explicit_canonical_facade(self):
    legacy_dir = self.repository_root / "openpilot" / "tools" / "nrdr_radar_re"
    for module_name in RADAR_FACADE_MODULES:
      canonical_module = "openpilot.nrdr.tools.radar_re"
      if module_name != "__init__":
        canonical_module = f"{canonical_module}.{module_name}"
      with self.subTest(module=module_name):
        self.assert_explicit_facade(legacy_dir / f"{module_name}.py", canonical_module)

  @unittest.skipUnless(importlib.util.find_spec("numpy") is not None, "requires numpy")
  def test_facades_preserve_every_exported_object_identity(self):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(self.repository_root), environment.get("PYTHONPATH"))))
    script = f"""
from importlib import import_module
import sys
from types import ModuleType

fake_logreader = ModuleType("openpilot.tools.lib.logreader")
fake_logreader.LogReader = object
sys.modules["openpilot.tools.lib.logreader"] = fake_logreader

fake_params = ModuleType("openpilot.common.params")
fake_params.Params = object
fake_params.UnknownKeyName = KeyError
sys.modules["openpilot.common.params"] = fake_params

root_facades = {ROOT_TOOL_FACADES!r}
for legacy_name, canonical_name in root_facades.items():
  legacy = import_module(legacy_name.removesuffix(".py"))
  canonical = import_module(canonical_name)
  assert legacy.__all__ == canonical.__all__, legacy_name
  for name in canonical.__all__:
    assert getattr(legacy, name) is getattr(canonical, name), (legacy_name, name)

for module_name in {RADAR_FACADE_MODULES!r}:
  suffix = "" if module_name == "__init__" else f".{{module_name}}"
  legacy = import_module(f"openpilot.tools.nrdr_radar_re{{suffix}}")
  canonical = import_module(f"openpilot.nrdr.tools.radar_re{{suffix}}")
  assert legacy.__all__ == canonical.__all__, module_name
  for name in canonical.__all__:
    assert getattr(legacy, name) is getattr(canonical, name), (module_name, name)
"""
    subprocess.run([sys.executable, "-c", script], cwd=self.repository_root, env=environment, check=True)

  def test_canonical_tools_do_not_depend_on_compatibility_paths(self):
    forbidden_modules = set(ROOT_TOOL_FACADES)
    forbidden_modules.update(path.removesuffix(".py") for path in ROOT_TOOL_FACADES)
    for directory in CANONICAL_TOOL_DIRS:
      for path in (self.repository_root / directory).rglob("*.py"):
        with self.subTest(path=path.relative_to(self.repository_root)):
          source = path.read_text()
          self.assertNotIn("openpilot.tools.nrdr_radar_re", source)
          tree = ast.parse(source, filename=str(path))
          imported: list[str] = []
          for node in ast.walk(tree):
            if isinstance(node, ast.Import):
              imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
              imported.append(node.module)
          self.assertFalse(any(name in forbidden_modules for name in imported), (path, imported))

  def test_tune_report_callers_invoke_the_canonical_module(self):
    expected = '["python3", "-m", "openpilot.nrdr.tools.lateral.tune_report", *paths]'
    callers = (
      "openpilot/nrdr/features/services/remote_actions.py",
      "openpilot/nrdr/ui/settings/lateral_tuning.py",
    )
    for relative_path in callers:
      with self.subTest(path=relative_path):
        source = (self.repository_root / relative_path).read_text()
        self.assertIn(expected, source)
        self.assertNotIn('"tune_report.py"', source)

  def test_canonical_and_compatibility_tool_files_ship_in_release(self):
    output = subprocess.check_output(
      [sys.executable, "tools/release/release_files.py"],
      cwd=self.repository_root,
    )
    released = {os.fsdecode(path) for path in output.split(b"\0") if path}
    expected = set(ROOT_TOOL_FACADES)
    expected.update(
      f"openpilot/tools/nrdr_radar_re/{module_name}.py"
      for module_name in RADAR_FACADE_MODULES
    )
    for directory in CANONICAL_TOOL_DIRS:
      expected.update(
        path.relative_to(self.repository_root).as_posix()
        for path in (self.repository_root / directory).rglob("*")
        if path.is_file() and path.suffix in (".ini", ".md", ".py")
      )
    self.assertEqual(expected - released, set())


if __name__ == "__main__":
  unittest.main()
