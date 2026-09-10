import ast
import os
from pathlib import Path
import subprocess
import sys
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_RELEASE = REPOSITORY_ROOT / "openpilot" / "nrdr" / "tools" / "release"


def getenv_default(path: Path, name: str) -> str:
  tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
  for node in tree.body:
    if not isinstance(node, ast.Assign) or not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
      continue
    call = node.value
    if (
      isinstance(call, ast.Call)
      and isinstance(call.func, ast.Attribute)
      and isinstance(call.func.value, ast.Name)
      and call.func.value.id == "os"
      and call.func.attr == "getenv"
      and len(call.args) == 2
      and isinstance(call.args[1], ast.Constant)
      and isinstance(call.args[1].value, str)
    ):
      return call.args[1].value
  raise AssertionError(f"could not find {name} os.getenv default in {path}")


class TestReleaseOwnership(unittest.TestCase):
  def test_generic_backend_modules_keep_comma_defaults(self):
    comma_connect = REPOSITORY_ROOT / "openpilot" / "common" / "api" / "comma_connect.py"
    athenad = REPOSITORY_ROOT / "openpilot" / "system" / "athena" / "athenad.py"

    self.assertEqual(getenv_default(comma_connect, "API_HOST"), "https://api.commadotai.com")
    self.assertEqual(getenv_default(athenad, "ATHENA_HOST"), "wss://athena.comma.ai")
    self.assertNotIn("konik.ai", comma_connect.read_text(encoding="utf-8"))
    self.assertNotIn("konik.ai", athenad.read_text(encoding="utf-8"))

  def test_launch_env_has_one_nrdr_backend_policy_seam(self):
    launch_env = (REPOSITORY_ROOT / "launch_env.sh").read_text(encoding="utf-8")
    nrdr_lines = [line for line in launch_env.splitlines() if "openpilot/nrdr" in line]

    self.assertEqual(nrdr_lines, ['source "$(dirname "${BASH_SOURCE[0]}")/openpilot/nrdr/config/backend_env.sh"'])
    self.assertNotIn("api.konik.ai", launch_env)
    self.assertNotIn("athena.konik.ai", launch_env)

  def test_backend_policy_and_clean_replacement_have_single_owners(self):
    active = REPOSITORY_ROOT / "openpilot" / "nrdr" / "config" / "backend_env.sh"
    clean = CANONICAL_RELEASE / "clean_overlay" / "backend_env.sh"
    active_source = active.read_text(encoding="utf-8")
    clean_source = clean.read_text(encoding="utf-8")

    self.assertIn("export API_HOST=https://api.konik.ai", active_source)
    self.assertIn("export ATHENA_HOST=wss://athena.konik.ai", active_source)
    self.assertNotIn("export API_HOST", clean_source)
    self.assertNotIn("export ATHENA_HOST", clean_source)
    self.assertFalse((REPOSITORY_ROOT / "release" / "clean_overlay").exists())

  def test_root_builder_is_an_explicit_thin_launcher(self):
    launcher = (REPOSITORY_ROOT / "release" / "build_prebuilt.sh").read_text(encoding="utf-8")
    policy_lines = [line for line in launcher.splitlines() if line and not line.startswith("#")]
    modes = subprocess.check_output(
      [
        "git", "ls-files", "--stage", "--",
        "release/build_prebuilt.sh",
        "openpilot/nrdr/tools/release/build_prebuilt.sh",
      ],
      cwd=REPOSITORY_ROOT,
      text=True,
    ).splitlines()

    self.assertEqual(len(policy_lines), 3)
    self.assertIn("set -euo pipefail", policy_lines)
    self.assertIn('exec "$REPO_ROOT/openpilot/nrdr/tools/release/build_prebuilt.sh" "$@"', policy_lines)
    self.assertNotIn("CLEAN_BRANCH", launcher)
    self.assertNotIn("konik.ai", launcher)
    self.assertEqual(len(modes), 2)
    self.assertTrue(all(line.startswith("100755 ") for line in modes), modes)

  def test_release_manifest_contains_launcher_implementation_policy_and_overlays(self):
    output = subprocess.check_output(
      [sys.executable, "tools/release/release_files.py"],
      cwd=REPOSITORY_ROOT,
    )
    released = {os.fsdecode(path) for path in output.split(b"\0") if path}
    expected = {
      "release/build_prebuilt.sh",
      "openpilot/nrdr/config/backend_env.sh",
      "openpilot/nrdr/tools/release/build_prebuilt.sh",
      *(
        path.relative_to(REPOSITORY_ROOT).as_posix()
        for path in (CANONICAL_RELEASE / "clean_overlay").iterdir()
        if path.is_file()
      ),
    }

    self.assertEqual(expected - released, set())


if __name__ == "__main__":
  unittest.main()
