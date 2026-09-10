import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_DEVICE = REPOSITORY_ROOT / "openpilot" / "nrdr" / "tools" / "device"
COMPATIBILITY_SCRIPTS = REPOSITORY_ROOT / "scripts"
HELPERS = ("opsync.sh", "setup_dev_helpers.sh")


def find_bash() -> str | None:
  if os.name == "nt":
    for candidate in (Path(r"C:\Program Files\Git\bin\bash.exe"), Path(r"C:\Program Files\Git\usr\bin\bash.exe")):
      if candidate.is_file():
        return str(candidate)
  return shutil.which("bash")


def bash_path(path: Path) -> str:
  if os.name != "nt":
    return str(path)

  assert BASH is not None
  result = subprocess.run(
    [BASH, "-c", 'cygpath -u "$1"', "bash", str(path)],
    check=True,
    capture_output=True,
    text=True,
  )
  return result.stdout.strip()


def make_executable(path: Path) -> None:
  path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


BASH = find_bash()


def test_compatibility_paths_are_thin_argument_preserving_launchers() -> None:
  for helper in HELPERS:
    source = (COMPATIBILITY_SCRIPTS / helper).read_text(encoding="utf-8")
    policy_lines = [line for line in source.splitlines() if line and not line.startswith("#")]
    assert policy_lines == [
      "set -euo pipefail",
      'REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null && pwd)"',
      f'exec "$REPO_ROOT/openpilot/nrdr/tools/device/{helper}" "$@"',
    ]


def test_canonical_helpers_keep_their_distinct_update_policies() -> None:
  force_sync = (CANONICAL_DEVICE / "opsync.sh").read_text(encoding="utf-8")
  installed_helper = (CANONICAL_DEVICE / "setup_dev_helpers.sh").read_text(encoding="utf-8")

  for required in ("git reset --hard FETCH_HEAD", "git submodule update --init --recursive --force", "systemctl --no-block restart comma"):
    assert required in force_sync
    assert required not in installed_helper

  for required in ('git pull origin "${branch}" --no-tags', "/data/openpilot/tools/op.sh start"):
    assert required in installed_helper
    assert required not in force_sync


def test_boot_calls_the_canonical_setup_owner() -> None:
  launcher = (REPOSITORY_ROOT / "launch_chffrplus.sh").read_text(encoding="utf-8")
  canonical_path = "openpilot/nrdr/tools/device/setup_dev_helpers.sh"

  assert launcher.count(canonical_path) == 2
  assert "scripts/setup_dev_helpers.sh" not in launcher


@pytest.mark.skipif(BASH is None, reason="device helper syntax checks require bash")
def test_all_device_helper_shell_scripts_parse() -> None:
  scripts = [*(CANONICAL_DEVICE / helper for helper in HELPERS), *(COMPATIBILITY_SCRIPTS / helper for helper in HELPERS)]
  subprocess.run([BASH, "-n", *(bash_path(script) for script in scripts)], check=True)


@pytest.mark.skipif(BASH is None, reason="launcher behavior checks require bash")
@pytest.mark.parametrize("helper", HELPERS)
def test_compatibility_launchers_preserve_arguments_and_exit_status(tmp_path: Path, helper: str) -> None:
  launcher = tmp_path / "scripts" / helper
  launcher.parent.mkdir(parents=True)
  shutil.copy2(COMPATIBILITY_SCRIPTS / helper, launcher)

  implementation = tmp_path / "openpilot" / "nrdr" / "tools" / "device" / helper
  implementation.parent.mkdir(parents=True)
  implementation.write_text(
    "#!/usr/bin/env bash\nprintf '<%s>\\n' \"$@\"\nexit 37\n",
    encoding="utf-8",
  )
  make_executable(implementation)

  result = subprocess.run(
    [BASH, bash_path(launcher), "alpha beta", "--flag=value"],
    check=False,
    capture_output=True,
    text=True,
  )

  assert result.returncode == 37
  assert result.stdout.splitlines() == ["<alpha beta>", "<--flag=value>"]


def test_device_helpers_ship_in_release() -> None:
  output = subprocess.check_output(
    [sys.executable, "tools/release/release_files.py"],
    cwd=REPOSITORY_ROOT,
  )
  released = {os.fsdecode(path) for path in output.split(b"\0") if path}
  expected = {
    *(f"scripts/{helper}" for helper in HELPERS),
    *(f"openpilot/nrdr/tools/device/{helper}" for helper in HELPERS),
    "openpilot/nrdr/tools/device/README.md",
  }

  assert expected - released == set()
