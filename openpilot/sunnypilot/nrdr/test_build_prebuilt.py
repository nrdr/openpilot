import ast
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = REPO_ROOT / "release" / "build_prebuilt.sh"
CLEAN_OVERLAY = REPO_ROOT / "release" / "clean_overlay"


def find_bash() -> str | None:
  if os.name == "nt":
    for candidate in (Path(r"C:\Program Files\Git\bin\bash.exe"), Path(r"C:\Program Files\Git\usr\bin\bash.exe")):
      if candidate.is_file():
        return str(candidate)
  return shutil.which("bash")


BASH = find_bash()
pytestmark = pytest.mark.skipif(BASH is None, reason="build_prebuilt.sh tests require bash")


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


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
  return subprocess.run(["git", *args], cwd=cwd, check=check, capture_output=True, text=True)


def init_repo(path: Path) -> str:
  git("init", "-q", "-b", "main", cwd=path)
  git("config", "user.name", "prebuilt-test", cwd=path)
  git("config", "user.email", "prebuilt-test@example.invalid", cwd=path)
  git("remote", "add", "origin", "https://example.invalid/original.git", cwd=path)
  git("add", "-A", cwd=path)
  git("commit", "-q", "-m", "fixture", cwd=path)
  return git("rev-parse", "HEAD", cwd=path).stdout.strip()


def make_executable(path: Path) -> None:
  path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_manifest(source: Path, entries: list[str]) -> None:
  manifest = source / "tools" / "release" / "release_files.py"
  manifest.parent.mkdir(parents=True, exist_ok=True)
  contents = "\n".join((
    "#!/usr/bin/env python3",
    f"entries = {entries!r}",
    "for entry in entries:",
    "  print(entry)",
    "",
  ))
  manifest.write_text(contents, encoding="utf-8")
  make_executable(manifest)


def make_source(tmp_path: Path, entries: list[str], existing_entries: list[str]) -> Path:
  source = tmp_path / "openpilot"
  release_dir = source / "release"
  release_dir.mkdir(parents=True)
  shutil.copy2(BUILD_SCRIPT, release_dir / BUILD_SCRIPT.name)
  make_executable(release_dir / BUILD_SCRIPT.name)
  required_entries = [
    "tools/release/release_files.py",
    "openpilot/sunnypilot/common/version.h",
  ]
  write_manifest(source, [*required_entries, *entries])

  version = source / "openpilot" / "sunnypilot" / "common" / "version.h"
  version.parent.mkdir(parents=True)
  version.write_text('#define COMMA_VERSION "0.0.1-test"\n', encoding="utf-8")
  for directory in (source / "openpilot" / "third_party", source / "openpilot" / "selfdrive" / "modeld" / "models"):
    directory.mkdir(parents=True)
    (directory / ".fixture").write_text("fixture\n", encoding="utf-8")

  clean_overlay = release_dir / "clean_overlay"
  clean_overlay.mkdir()
  for name in ("events.py", "events_sp.py", "driver_monitoring.py", "mads.py"):
    (clean_overlay / name).write_text("# clean overlay fixture\n", encoding="utf-8")

  # A deliberately broken copy at the pre-migration location proves preflight
  # uses tools/release/release_files.py, not release/release_files.py.
  legacy_manifest = release_dir / "release_files.py"
  legacy_manifest.write_text("#!/usr/bin/env python3\nraise SystemExit(86)\n", encoding="utf-8")
  make_executable(legacy_manifest)

  for entry in existing_entries:
    relative = PurePosixPath(entry)
    assert not relative.is_absolute() and ".." not in relative.parts
    target = source.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"fixture for {entry}\n", encoding="utf-8")

  return source


def run_builder(script: Path, *, source: Path, build: Path, **extra_env: str) -> subprocess.CompletedProcess[str]:
  assert BASH is not None
  env = os.environ.copy()
  env.update({
    "BUILD_DIR": bash_path(build),
    "SOURCE_DIR": bash_path(source),
    # Behavioral tests never compile, but preflight intentionally verifies the
    # configured build tool before it permits any filesystem mutation.
    "SCONS_BIN": bash_path(Path(BASH)),
    "PUSH": "0",
    "CLEANUP": "0",
    "RESTORE_SOURCE_NAME": "0",
    "DELETE_BUILD_DIR_WHEN_DONE": "0",
    "REBOOT_WHEN_DONE": "0",
    **extra_env,
  })
  return subprocess.run(
    [BASH, bash_path(script)],
    cwd=script.parent.parent,
    env=env,
    capture_output=True,
    text=True,
    timeout=30,
  )


def result_details(result: subprocess.CompletedProcess[str]) -> str:
  return f"exit={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def assert_repo_unchanged(source: Path, original_head: str) -> None:
  assert source.is_dir()
  assert git("rev-parse", "HEAD", cwd=source).stdout.strip() == original_head
  assert git("branch", "--show-current", cwd=source).stdout.strip() == "main"
  assert git("remote", "get-url", "origin", cwd=source).stdout.strip() == "https://example.invalid/original.git"
  assert git("status", "--porcelain", cwd=source).stdout == ""


@pytest.mark.parametrize("build_relation", ["same", "inside-source", "contains-source"])
def test_preflight_rejects_overlapping_source_and_build_without_mutation(tmp_path: Path, build_relation: str) -> None:
  entries = ["root.txt", "nested/kept.txt"]
  source = make_source(tmp_path, entries, entries)
  original_head = init_repo(source)
  build = {
    "same": source,
    "inside-source": source / "prebuilt-build",
    "contains-source": tmp_path,
  }[build_relation]

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
  )

  assert result.returncode != 0, result_details(result)
  assert_repo_unchanged(source, original_head)
  assert not (source / "prebuilt-build").exists()
  assert not (tmp_path / "openpilot-src").exists()


def test_preflight_only_is_non_mutating_and_uses_canonical_nested_manifest(tmp_path: Path) -> None:
  entries = ["root.txt", "nested/one two/kept file.txt"]
  source = make_source(tmp_path, entries, entries)
  build = tmp_path / "prebuilt-build"
  original_head = init_repo(source)

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
  )

  assert result.returncode == 0, result_details(result)
  assert not build.exists()
  assert (source / "nested" / "one two" / "kept file.txt").is_file()
  assert_repo_unchanged(source, original_head)


def test_preflight_rejects_missing_scons_before_build_mutation(tmp_path: Path) -> None:
  entries = ["root.txt"]
  source = make_source(tmp_path, entries, entries)
  build = tmp_path / "prebuilt-build"
  original_head = init_repo(source)

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
    SCONS_BIN="definitely-missing-scons-for-prebuilt-test",
  )

  assert result.returncode != 0, result_details(result)
  assert "SCons is unavailable" in result.stderr
  assert not build.exists()
  assert_repo_unchanged(source, original_head)


@pytest.mark.parametrize(
  "bad_entry",
  ["../escape.txt", "/etc/passwd", "nested/missing.txt"],
  ids=["traversal", "absolute", "missing"],
)
def test_preflight_rejects_unsafe_or_missing_manifest_entries_before_build_mutation(tmp_path: Path, bad_entry: str) -> None:
  source = make_source(tmp_path, [bad_entry], [])
  build = tmp_path / "prebuilt-build"
  (tmp_path / "escape.txt").write_text("must not be accepted through ..\n", encoding="utf-8")
  original_head = init_repo(source)

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
  )

  assert result.returncode != 0, result_details(result)
  assert not build.exists()
  assert_repo_unchanged(source, original_head)


@pytest.mark.parametrize("dirty_kind", ["tracked", "untracked"])
def test_normal_build_rejects_dirty_source_before_creating_build_tree(tmp_path: Path, dirty_kind: str) -> None:
  entries = ["root.txt", "nested/kept.txt"]
  source = make_source(tmp_path, entries, entries)
  build = tmp_path / "prebuilt-build"
  original_head = init_repo(source)

  if dirty_kind == "tracked":
    (source / "root.txt").write_text("dirty tracked file\n", encoding="utf-8")
  else:
    (source / "untracked.txt").write_text("dirty untracked file\n", encoding="utf-8")
  status_before = git("status", "--porcelain", cwd=source).stdout

  result = run_builder(source / "release" / BUILD_SCRIPT.name, source=source, build=build)

  assert result.returncode != 0, result_details(result)
  assert "source worktree is not clean" in f"{result.stdout}\n{result.stderr}"
  assert "Building T=" not in f"{result.stdout}\n{result.stderr}"
  assert not build.exists()
  assert git("rev-parse", "HEAD", cwd=source).stdout.strip() == original_head
  assert git("branch", "--show-current", cwd=source).stdout.strip() == "main"
  assert git("remote", "get-url", "origin", cwd=source).stdout.strip() == "https://example.invalid/original.git"
  assert git("status", "--porcelain", cwd=source).stdout == status_before


def copy_file_from_source(relative: Path, destination_root: Path) -> None:
  source = REPO_ROOT / relative
  assert source.is_file(), f"clean exclusion targets missing current source file: {relative.as_posix()}"
  destination = destination_root / relative
  destination.parent.mkdir(parents=True, exist_ok=True)
  shutil.copy2(source, destination)


def test_clean_events_sp_keeps_only_speed_limit_pre_active_override() -> None:
  source = (CLEAN_OVERLAY / "events_sp.py").read_text(encoding="utf-8")
  tree = ast.parse(source)
  referenced = {
    node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else node.name
    for node in ast.walk(tree)
    if isinstance(node, (ast.Name, ast.Attribute, ast.FunctionDef))
  }
  overridden_events = {
    node.slice.attr
    for node in ast.walk(tree)
    if isinstance(node, ast.Subscript)
    and isinstance(node.value, ast.Name)
    and node.value.id == "events"
    and isinstance(node.slice, ast.Attribute)
  }

  assert overridden_events == {"speedLimitPreActive"}
  assert "speed_limit_pre_active_alert" in referenced
  assert not {
    "controlsMismatchLateral",
    "laneTurnLeft",
    "laneTurnRight",
    "speedLimitActive",
    "speedLimitPending",
  } & referenced


def test_clean_overlay_only_applies_current_exclusions_without_branch_or_build_side_effects(tmp_path: Path) -> None:
  build = tmp_path / "prebuilt-tree"
  build.mkdir()

  overlay_targets = (
    Path("launch_openpilot.sh"),
    Path("launch_env.sh"),
    Path("openpilot/common/api/comma_connect.py"),
    Path("openpilot/system/athena/athenad.py"),
    Path("openpilot/sunnypilot/nrdr/home.py"),
    Path("openpilot/sunnypilot/nrdr/mici_home.py"),
    Path("openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/party_tricks.py"),
  )
  for relative in overlay_targets:
    copy_file_from_source(relative, build)

  for name in ("events.py", "events_sp.py", "driver_monitoring.py", "mads.py"):
    copy_file_from_source(Path("openpilot/sunnypilot/nrdr") / name, build)

  original_head = init_repo(build)
  result = run_builder(
    BUILD_SCRIPT,
    source=REPO_ROOT,
    build=build,
    CLEAN_OVERLAY_ONLY="1",
  )

  assert result.returncode == 0, result_details(result)
  assert git("rev-parse", "HEAD", cwd=build).stdout.strip() == original_head
  assert git("branch", "--show-current", cwd=build).stdout.strip() == "main"
  assert git("remote", "get-url", "origin", cwd=build).stdout.strip() == "https://example.invalid/original.git"
  assert git("branch", "--list", "nrdr-clean", cwd=build).stdout.strip() == ""
  assert not (build / "prebuilt").exists()

  for name in ("events.py", "events_sp.py", "driver_monitoring.py", "mads.py"):
    assert (build / "openpilot" / "sunnypilot" / "nrdr" / name).read_bytes() == (CLEAN_OVERLAY / name).read_bytes()
  assert not list((build / "openpilot" / "sunnypilot" / "nrdr").rglob("__pycache__"))

  assert "konik.ai" not in (build / "launch_openpilot.sh").read_text(encoding="utf-8")
  assert "konik.ai" not in (build / "launch_env.sh").read_text(encoding="utf-8")
  assert "https://api.commadotai.com" in (build / "openpilot/common/api/comma_connect.py").read_text(encoding="utf-8")
  assert "wss://athena.comma.ai" in (build / "openpilot/system/athena/athenad.py").read_text(encoding="utf-8")

  home = (build / "openpilot/sunnypilot/nrdr/home.py").read_text(encoding="utf-8")
  assert "Your drives will upload to connect.comma.ai." in home
  assert "Your drives will upload to stable.konik.ai." not in home

  mici_home = (build / "openpilot/sunnypilot/nrdr/mici_home.py").read_text(encoding="utf-8")
  assert 'home._version_label.set_text("connect.comma.ai")' in mici_home
  assert 'home._version_label.set_text("stable.konik.ai")' not in mici_home

  party_tricks = (build / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/party_tricks.py").read_text(encoding="utf-8")
  assert "      self._reregister_item," not in party_tricks
