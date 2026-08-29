import ast
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_LAUNCHER = REPO_ROOT / "release" / "build_prebuilt.sh"
BUILD_SCRIPT = REPO_ROOT / "openpilot" / "nrdr" / "tools" / "release" / "build_prebuilt.sh"
CLEAN_OVERLAY = BUILD_SCRIPT.parent / "clean_overlay"
CLEAN_OVERLAY_TARGETS = {
  "events.py": Path("openpilot/nrdr/hooks/events.py"),
  "events_sp.py": Path("openpilot/nrdr/hooks/events_sp.py"),
  "driver_monitoring.py": Path("openpilot/nrdr/hooks/driver_monitoring.py"),
  "mads.py": Path("openpilot/nrdr/features/driver_policy/mads.py"),
  "backend_env.sh": Path("openpilot/nrdr/config/backend_env.sh"),
}


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


def bash_environment_path() -> str:
  assert BASH is not None
  result = subprocess.run([BASH, "-c", 'printf "%s" "$PATH"'], check=True, capture_output=True, text=True)
  return result.stdout


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


def shell_quote(value: str) -> str:
  return "'" + value.replace("'", "'\"'\"'") + "'"


def write_probe_executable(path: Path, log_path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  contents = "\n".join((
    "#!/usr/bin/env bash",
    f"printf '%s\\t%s\\n' \"$*\" \"${{VIRTUAL_ENV:-}}\" >> {shell_quote(bash_path(log_path))}",
    "exit 0",
    "",
  ))
  path.write_text(contents, encoding="utf-8")
  make_executable(path)


def write_fake_readelf(path: Path, log_path: Path, locationd_runpath: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  contents = "\n".join((
    "#!/usr/bin/env bash",
    f"printf '%s\\n' \"$*\" >> {shell_quote(bash_path(log_path))}",
    'artifact="${@: -1}"',
    'if [[ "$1" == "-h" || "$1" == "--file-header" ]]; then',
    "  printf '%s\\n' 'ELF Header:' '  Class:                             ELF64'",
    'elif [[ "$artifact" == */locationd ]]; then',
    "  printf '%s\\n' 'Dynamic section at offset 0x0 contains 2 entries:'",
    "  printf '%s\\n' ' 0x0000000000000001 (NEEDED)             Shared library: [liblive.so]'",
    f"  printf '%s\\n' {shell_quote(f' 0x000000000000001d (RUNPATH)            Library runpath: [{locationd_runpath}]')}",
    "else",
    "  printf '%s\\n' 'Dynamic section at offset 0x0 contains 1 entry:'",
    "  printf '%s\\n' ' 0x000000000000000e (SONAME)             Library soname: [liblive.so]'",
    "fi",
    "exit 0",
    "",
  ))
  path.write_text(contents, encoding="utf-8")
  make_executable(path)


def make_runtime_linkage_fixture(build: Path) -> tuple[Path, Path]:
  locationd = build / "openpilot" / "sunnypilot" / "selfdrive" / "locationd" / "locationd"
  liblive = locationd.parent / "models" / "generated" / "liblive.so"
  for artifact in (locationd, liblive):
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"\x7fELF fake test artifact\n")
    make_executable(artifact)
  return locationd, liblive


def make_startup_probes(tmp_path: Path) -> tuple[Path, Path, Path]:
  home = tmp_path / "fake-home"
  home.mkdir()
  profile_log = tmp_path / "profile-sourced.log"
  profile_command = f"printf '%s\\n' sourced >> {shell_quote(bash_path(profile_log))}\n"
  for name in (".profile", ".bash_profile", ".bashrc"):
    (home / name).write_text(profile_command, encoding="utf-8")

  shims = tmp_path / "agnos-shims"
  uv_log = tmp_path / "uv-invoked.log"
  write_probe_executable(shims / "uv", uv_log)
  return home, shims, profile_log


def write_manifest(source: Path, entries: list[str]) -> None:
  manifest = source / "tools" / "release" / "release_files.py"
  manifest.parent.mkdir(parents=True, exist_ok=True)
  contents = "\n".join((
    "#!/usr/bin/env python3",
    "import os",
    "import sys",
    f"entries = {entries!r}",
    "for entry in entries:",
    "  sys.stdout.buffer.write(os.fsencode(entry) + b'\\0')",
    "",
  ))
  manifest.write_text(contents, encoding="utf-8")
  make_executable(manifest)


def make_source(tmp_path: Path, entries: list[str], existing_entries: list[str]) -> Path:
  source = tmp_path / "openpilot"
  release_dir = source / "release"
  release_dir.mkdir(parents=True)
  shutil.copy2(BUILD_LAUNCHER, release_dir / BUILD_LAUNCHER.name)
  make_executable(release_dir / BUILD_LAUNCHER.name)

  canonical_release = source / "openpilot" / "nrdr" / "tools" / "release"
  canonical_release.mkdir(parents=True)
  shutil.copy2(BUILD_SCRIPT, canonical_release / BUILD_SCRIPT.name)
  make_executable(canonical_release / BUILD_SCRIPT.name)

  backend_env = source / "openpilot" / "nrdr" / "config" / "backend_env.sh"
  backend_env.parent.mkdir(parents=True)
  shutil.copy2(REPO_ROOT / "openpilot" / "nrdr" / "config" / "backend_env.sh", backend_env)
  required_entries = [
    "tools/release/release_files.py",
    "openpilot/sunnypilot/common/version.h",
    "release/build_prebuilt.sh",
    "openpilot/nrdr/tools/release/build_prebuilt.sh",
    "openpilot/nrdr/config/backend_env.sh",
  ]
  write_manifest(source, [*required_entries, *entries])

  version = source / "openpilot" / "sunnypilot" / "common" / "version.h"
  version.parent.mkdir(parents=True)
  version.write_text('#define COMMA_VERSION "0.0.1-test"\n', encoding="utf-8")
  for directory in (source / "openpilot" / "third_party", source / "openpilot" / "selfdrive" / "modeld" / "models"):
    directory.mkdir(parents=True)
    (directory / ".fixture").write_text("fixture\n", encoding="utf-8")

  clean_overlay = canonical_release / "clean_overlay"
  clean_overlay.mkdir()
  for name in ("events.py", "events_sp.py", "driver_monitoring.py", "mads.py"):
    (clean_overlay / name).write_text("# clean overlay fixture\n", encoding="utf-8")
  shutil.copy2(CLEAN_OVERLAY / "backend_env.sh", clean_overlay / "backend_env.sh")

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


def source_backend_environment(launch_env: Path) -> subprocess.CompletedProcess[str]:
  assert BASH is not None
  return subprocess.run(
    [
      BASH,
      "-c",
      'unset API_HOST ATHENA_HOST; source "$1"; printf "%s\\n%s\\n" "${API_HOST-}" "${ATHENA_HOST-}"',
      "bash",
      bash_path(launch_env),
    ],
    capture_output=True,
    text=True,
    timeout=10,
  )


def result_details(result: subprocess.CompletedProcess[str]) -> str:
  return f"exit={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def assert_repo_unchanged(source: Path, original_head: str) -> None:
  assert source.is_dir()
  assert git("rev-parse", "HEAD", cwd=source).stdout.strip() == original_head
  assert git("branch", "--show-current", cwd=source).stdout.strip() == "main"
  assert git("remote", "get-url", "origin", cwd=source).stdout.strip() == "https://example.invalid/original.git"
  assert git("status", "--porcelain", cwd=source).stdout == ""


def test_release_shell_entry_points_and_backend_fragments_parse() -> None:
  scripts = (
    BUILD_LAUNCHER,
    BUILD_SCRIPT,
    REPO_ROOT / "launch_env.sh",
    REPO_ROOT / "openpilot" / "nrdr" / "config" / "backend_env.sh",
    CLEAN_OVERLAY / "backend_env.sh",
  )
  assert BASH is not None
  result = subprocess.run(
    [BASH, "-n", *(bash_path(script) for script in scripts)],
    capture_output=True,
    text=True,
    timeout=10,
  )
  assert result.returncode == 0, result_details(result)


def test_launch_env_selects_nrdr_backend_through_owned_fragment() -> None:
  result = source_backend_environment(REPO_ROOT / "launch_env.sh")

  assert result.returncode == 0, result_details(result)
  assert result.stdout.splitlines() == ["https://api.konik.ai", "wss://athena.konik.ai"]


def test_root_launcher_and_canonical_builder_have_preflight_parity(tmp_path: Path) -> None:
  source = make_source(tmp_path, [], [])
  original_head = init_repo(source)
  build = tmp_path / "prebuilt-build"
  canonical = source / "openpilot" / "nrdr" / "tools" / "release" / "build_prebuilt.sh"
  launcher = source / "release" / "build_prebuilt.sh"

  direct_result = run_builder(canonical, source=source, build=build, PREBUILT_PREFLIGHT_ONLY="1")
  launcher_result = run_builder(launcher, source=source, build=build, PREBUILT_PREFLIGHT_ONLY="1")

  assert direct_result.returncode == 0, result_details(direct_result)
  assert launcher_result.returncode == 0, result_details(launcher_result)
  assert launcher_result.stdout == direct_result.stdout
  assert launcher_result.stderr == direct_result.stderr
  assert not build.exists()
  assert_repo_unchanged(source, original_head)


@pytest.mark.parametrize("entry_point", [BUILD_LAUNCHER, BUILD_SCRIPT], ids=["launcher", "canonical"])
def test_entry_points_resolve_repository_without_source_override(tmp_path: Path, entry_point: Path) -> None:
  assert BASH is not None
  build = tmp_path / "prebuilt-build"
  environment = os.environ.copy()
  environment.pop("SOURCE_DIR", None)
  environment.update({
    "BUILD_DIR": bash_path(build),
    "SCONS_BIN": bash_path(Path(BASH)),
    "PREBUILT_PREFLIGHT_ONLY": "1",
    "PUSH": "0",
    "REBOOT_WHEN_DONE": "0",
  })

  result = subprocess.run(
    [BASH, bash_path(entry_point)],
    cwd=REPO_ROOT,
    env=environment,
    capture_output=True,
    text=True,
    timeout=30,
  )

  assert result.returncode == 0, result_details(result)
  assert "PREBUILT_PREFLIGHT_ONLY=1: no files changed" in result.stdout
  assert not build.exists()


def test_runtime_linkage_check_rejects_locationd_runpath_into_temporary_build_tree(tmp_path: Path) -> None:
  source = make_source(tmp_path, [], [])
  original_head = init_repo(source)
  build = tmp_path / "prebuilt-build"
  locationd, liblive = make_runtime_linkage_fixture(build)
  artifact_bytes = {artifact: artifact.read_bytes() for artifact in (locationd, liblive)}
  readelf = tmp_path / "tools" / "readelf"
  readelf_log = tmp_path / "readelf.log"
  absolute_runpath = f"{bash_path(build)}/openpilot/sunnypilot/selfdrive/locationd/models/generated"
  write_fake_readelf(readelf, readelf_log, f"$ORIGIN/models/generated:{absolute_runpath}")

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_RUNTIME_CHECK_ONLY="1",
    READELF_BIN=bash_path(readelf),
  )

  assert result.returncode != 0, result_details(result)
  assert "temporary build directory" in f"{result.stdout}\n{result.stderr}"
  assert all(artifact.read_bytes() == contents for artifact, contents in artifact_bytes.items())
  assert_repo_unchanged(source, original_head)


def test_runtime_linkage_check_accepts_relocatable_locationd_runpath(tmp_path: Path) -> None:
  source = make_source(tmp_path, [], [])
  original_head = init_repo(source)
  build = tmp_path / "prebuilt-build"
  locationd, liblive = make_runtime_linkage_fixture(build)
  artifact_bytes = {artifact: artifact.read_bytes() for artifact in (locationd, liblive)}
  readelf = tmp_path / "tools" / "readelf"
  readelf_log = tmp_path / "readelf.log"
  write_fake_readelf(readelf, readelf_log, "$ORIGIN/models/generated")

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_RUNTIME_CHECK_ONLY="1",
    READELF_BIN=bash_path(readelf),
  )

  assert result.returncode == 0, result_details(result)
  readelf_invocations = readelf_log.read_text(encoding="utf-8").splitlines()
  assert any(str(PurePosixPath(*locationd.relative_to(build).parts)) in line for line in readelf_invocations)
  assert any(str(PurePosixPath(*liblive.relative_to(build).parts)) in line for line in readelf_invocations)
  assert all(artifact.read_bytes() == contents for artifact, contents in artifact_bytes.items())
  assert_repo_unchanged(source, original_head)


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


def test_agnos_preflight_uses_explicit_venv_without_profiles_or_uv(tmp_path: Path) -> None:
  entries = ["root.txt"]
  source = make_source(tmp_path, entries, entries)
  build = tmp_path / "prebuilt-build"
  original_head = init_repo(source)
  marker = tmp_path / "AGNOS"
  marker.touch()
  venv = tmp_path / "agnos-venv"
  scons_log = tmp_path / "agnos-scons.log"
  python_log = tmp_path / "agnos-python.log"
  write_probe_executable(venv / "bin" / "scons", scons_log)
  write_probe_executable(venv / "bin" / "python3", python_log)
  home, shims, profile_log = make_startup_probes(tmp_path)
  uv_log = tmp_path / "uv-invoked.log"

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
    SCONS_BIN="",
    AGNOS_MARKER=bash_path(marker),
    AGNOS_VENV=bash_path(venv),
    AGNOS_SHIMS=bash_path(shims),
    HOME=bash_path(home),
    PATH=bash_environment_path(),
  )

  assert result.returncode == 0, result_details(result)
  assert scons_log.read_text(encoding="utf-8").splitlines() == [f"--version\t{bash_path(venv)}"]
  assert python_log.read_text(encoding="utf-8").splitlines() == [f"-c import SCons\t{bash_path(venv)}"]
  assert not profile_log.exists()
  assert not uv_log.exists()
  build_script = BUILD_SCRIPT.read_text(encoding="utf-8")
  assert ". /etc/profile" not in build_script
  assert "source /etc/profile" not in build_script
  assert not build.exists()
  assert_repo_unchanged(source, original_head)


def test_agnos_preflight_honors_explicit_scons_override(tmp_path: Path) -> None:
  entries = ["root.txt"]
  source = make_source(tmp_path, entries, entries)
  build = tmp_path / "prebuilt-build"
  original_head = init_repo(source)
  marker = tmp_path / "AGNOS"
  marker.touch()
  venv = tmp_path / "agnos-venv"
  default_scons_log = tmp_path / "default-scons.log"
  python_log = tmp_path / "agnos-python.log"
  write_probe_executable(venv / "bin" / "scons", default_scons_log)
  write_probe_executable(venv / "bin" / "python3", python_log)
  override_scons = tmp_path / "explicit-tools" / "scons"
  override_scons_log = tmp_path / "override-scons.log"
  write_probe_executable(override_scons, override_scons_log)
  home, shims, profile_log = make_startup_probes(tmp_path)

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
    SCONS_BIN=bash_path(override_scons),
    AGNOS_MARKER=bash_path(marker),
    AGNOS_VENV=bash_path(venv),
    AGNOS_SHIMS=bash_path(shims),
    HOME=bash_path(home),
    PATH=bash_environment_path(),
  )

  assert result.returncode == 0, result_details(result)
  assert override_scons_log.read_text(encoding="utf-8").splitlines() == [f"--version\t{bash_path(venv)}"]
  assert not default_scons_log.exists()
  assert python_log.is_file()
  assert not profile_log.exists()
  assert not (tmp_path / "uv-invoked.log").exists()
  assert not build.exists()
  assert_repo_unchanged(source, original_head)


def test_non_agnos_preflight_resolves_scons_from_path_without_startup_side_effects(tmp_path: Path) -> None:
  entries = ["root.txt"]
  source = make_source(tmp_path, entries, entries)
  build = tmp_path / "prebuilt-build"
  original_head = init_repo(source)
  tools_dir = tmp_path / "path-tools"
  scons_log = tmp_path / "path-scons.log"
  write_probe_executable(tools_dir / "scons", scons_log)
  home, shims, profile_log = make_startup_probes(tmp_path)
  baseline_path = bash_environment_path()

  result = run_builder(
    source / "release" / BUILD_SCRIPT.name,
    source=source,
    build=build,
    PREBUILT_PREFLIGHT_ONLY="1",
    SCONS_BIN="",
    AGNOS_MARKER=bash_path(tmp_path / "not-agnos"),
    AGNOS_VENV=bash_path(tmp_path / "unused-venv"),
    AGNOS_SHIMS=bash_path(shims),
    HOME=bash_path(home),
    PATH=f"{bash_path(tools_dir)}:{bash_path(shims)}:{baseline_path}",
    VIRTUAL_ENV="",
  )

  assert result.returncode == 0, result_details(result)
  assert scons_log.read_text(encoding="utf-8").splitlines() == ["--version\t"]
  assert not profile_log.exists()
  assert not (tmp_path / "uv-invoked.log").exists()
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
    Path("launch_env.sh"),
    Path("openpilot/common/api/comma_connect.py"),
    Path("openpilot/system/athena/athenad.py"),
    Path("openpilot/nrdr/ui/home/layout.py"),
    Path("openpilot/nrdr/ui/home/mici.py"),
    Path("openpilot/nrdr/ui/settings/party_tricks.py"),
  )
  for relative in overlay_targets:
    copy_file_from_source(relative, build)

  for relative in CLEAN_OVERLAY_TARGETS.values():
    copy_file_from_source(relative, build)

  generic_files = (
    Path("launch_env.sh"),
    Path("openpilot/common/api/comma_connect.py"),
    Path("openpilot/system/athena/athenad.py"),
  )
  generic_bytes = {relative: (build / relative).read_bytes() for relative in generic_files}

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

  for name, relative in CLEAN_OVERLAY_TARGETS.items():
    assert (build / relative).read_bytes() == (CLEAN_OVERLAY / name).read_bytes()
  assert not list((build / "openpilot" / "nrdr").rglob("__pycache__"))

  for relative, contents in generic_bytes.items():
    assert (build / relative).read_bytes() == contents
  assert "openpilot/nrdr/config/backend_env.sh" in (build / "launch_env.sh").read_text(encoding="utf-8")
  assert "konik.ai" not in (build / "openpilot/nrdr/config/backend_env.sh").read_text(encoding="utf-8")
  assert "https://api.commadotai.com" in (build / "openpilot/common/api/comma_connect.py").read_text(encoding="utf-8")
  assert "wss://athena.comma.ai" in (build / "openpilot/system/athena/athenad.py").read_text(encoding="utf-8")
  clean_environment = source_backend_environment(build / "launch_env.sh")
  assert clean_environment.returncode == 0, result_details(clean_environment)
  assert clean_environment.stdout.splitlines() == ["", ""]

  home = (build / "openpilot/nrdr/ui/home/layout.py").read_text(encoding="utf-8")
  assert "Your drives will upload to connect.comma.ai." in home
  assert "Your drives will upload to stable.konik.ai." not in home

  mici_home = (build / "openpilot/nrdr/ui/home/mici.py").read_text(encoding="utf-8")
  assert 'home._version_label.set_text("connect.comma.ai")' in mici_home
  assert 'home._version_label.set_text("stable.konik.ai")' not in mici_home

  party_tricks = (build / "openpilot/nrdr/ui/settings/party_tricks.py").read_text(encoding="utf-8")
  assert "      self._reregister_item," not in party_tricks
