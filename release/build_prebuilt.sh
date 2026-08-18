#!/usr/bin/env bash
set -euo pipefail
set -x

GITHUB_USER="${GITHUB_USER:-nrdr}"
GITHUB_REPO="${GITHUB_REPO:-openpilot}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"
# Never build over the running checkout. Keeping the generated tree beside it avoids
# breaking hardwared/manager while the release is being assembled.
BUILD_DIR="${BUILD_DIR:-/data/openpilot-prebuilt-build}"

# Daily defaults. The branch date follows Eastern time, even when the C4 clock is UTC.
: "${RELEASE_BRANCH:=nrdr-staging-$(TZ='America/New_York' date +%m.%d.%Y)}"
: "${CLEAN_BRANCH:=nrdr-clean}"
: "${NIGHTLY_BRANCH:=nrdr-nightly}"
: "${PUSH:=1}"
: "${CLEANUP:=1}"
: "${DELETE_BUILD_DIR_WHEN_DONE:=1}"
: "${GITHUB_TOKEN_FILE:=/data/gh_token}"
: "${STRIP_ONNX:=1}"
: "${REBOOT_WHEN_DONE:=0}"
: "${PREBUILT_PREFLIGHT_ONLY:=0}"
: "${CLEAN_OVERLAY_ONLY:=0}"
: "${PREBUILT_RUNTIME_CHECK_ONLY:=0}"
: "${SCONS_BIN:=}"
: "${READELF_BIN:=}"
: "${SCONS_JOBS:=4}"
: "${AGNOS_MARKER:=/AGNOS}"
: "${AGNOS_VENV:=/usr/local/venv}"
: "${AGNOS_SHIMS:=/usr/comma/shims}"

RELEASE_FILES_SCRIPT="$SOURCE_DIR/tools/release/release_files.py"
CLEAN_OVERLAY_DIR="$SOURCE_DIR/release/clean_overlay"
BUILD_READY=0
BUILD_DIR_OWNED=0
declare -a RELEASE_FILES=()

die() {
  echo "[!] ERROR: $*" >&2
  return 1
}

resolve_path() {
  realpath -m -- "$1"
}

configure_build_environment() {
  local detected_scons python_bin

  # Manager inherits these immutable AGNOS tool paths from /etc/profile, while
  # a standalone SSH command does not. Export only the required environment;
  # do not source a user/system profile or create a project virtualenv.
  if [ -f "$AGNOS_MARKER" ]; then
    [ -d "$AGNOS_VENV/bin" ] || die "missing AGNOS build environment: $AGNOS_VENV/bin"
    export VIRTUAL_ENV="$AGNOS_VENV"
    export PATH="$AGNOS_SHIMS:$AGNOS_VENV/bin:$PATH"
    [ -n "$SCONS_BIN" ] || SCONS_BIN="$AGNOS_VENV/bin/scons"
  fi

  if [ -n "$SCONS_BIN" ]; then
    detected_scons="$(command -v "$SCONS_BIN" 2>/dev/null || true)"
  else
    detected_scons="$(command -v scons 2>/dev/null || true)"
  fi
  [ -n "$detected_scons" ] || \
    die "SCons is unavailable; install the project build environment or set SCONS_BIN"
  [ -x "$detected_scons" ] || die "SCons is not executable: $detected_scons"
  SCONS_BIN="$detected_scons"
  "$SCONS_BIN" --version >/dev/null 2>&1 || die "SCons failed its version check: $SCONS_BIN"

  if [ -f "$AGNOS_MARKER" ]; then
    python_bin="$(command -v python3 2>/dev/null || true)"
    [ -n "$python_bin" ] || die "python3 is unavailable in the AGNOS build environment"
    "$python_bin" -c 'import SCons' >/dev/null 2>&1 || \
      die "AGNOS python3 cannot import SCons: $python_bin"
  fi
  echo "[-] Build tool: $SCONS_BIN"
}

run_scons() {
  if "$SCONS_BIN" -j"$SCONS_JOBS" "$@"; then
    return 0
  fi
  [ "$SCONS_JOBS" != "1" ] || return 1
  echo "[!] Parallel build failed; retrying serially"
  "$SCONS_BIN" -j1 "$@"
}

validate_runtime_linkage() {
  local locationd="$BUILD_DIR/openpilot/sunnypilot/selfdrive/locationd/locationd"
  local liblive="$BUILD_DIR/openpilot/sunnypilot/selfdrive/locationd/models/generated/liblive.so"
  local readelf_bin artifact dynamic_section relative

  [ -f "$locationd" ] || die "missing Sunny locationd: $locationd"
  [ -f "$liblive" ] || die "missing Sunny locationd runtime library: $liblive"

  if [ -n "$READELF_BIN" ]; then
    readelf_bin="$(command -v "$READELF_BIN" 2>/dev/null || true)"
  else
    readelf_bin="$(command -v readelf 2>/dev/null || true)"
  fi
  [ -n "$readelf_bin" ] || die "readelf is required to validate release runtime linkage"
  [ -x "$readelf_bin" ] || die "readelf is not executable: $readelf_bin"

  dynamic_section="$("$readelf_bin" -d "$locationd" 2>/dev/null)" || \
    die "could not inspect Sunny locationd dynamic linkage"
  grep -Fq 'liblive.so' <<< "$dynamic_section" || \
    die "Sunny locationd does not declare its liblive.so dependency"
  grep -Fq '$ORIGIN/models/generated' <<< "$dynamic_section" || \
    die "Sunny locationd does not use a relocatable \$ORIGIN runtime path"
  if grep -Fq "$BUILD_DIR" <<< "$dynamic_section"; then
    die "Sunny locationd runtime path embeds the temporary build directory"
    return 1
  fi

  while IFS= read -r -d '' artifact; do
    dynamic_section="$("$readelf_bin" -d "$artifact" 2>/dev/null || true)"
    if grep -Fq "$BUILD_DIR" <<< "$dynamic_section"; then
      relative="${artifact#"$BUILD_DIR"/}"
      die "runtime ELF embeds the temporary build directory: $relative"
      return 1
    fi
  done < <(find "$BUILD_DIR" -path "$BUILD_DIR/.git" -prune -o \
    -type f \( -perm /111 -o -name '*.so' -o -name '*.so.*' \) -print0)

  echo "[-] Runtime linkage is relocatable"
}

validate_layout() {
  local source_resolved build_resolved
  source_resolved="$(resolve_path "$SOURCE_DIR")"
  build_resolved="$(resolve_path "$BUILD_DIR")"

  [ -d "$source_resolved" ] || die "source directory does not exist: $source_resolved"
  [ "$build_resolved" != "/" ] || die "refusing to use / as BUILD_DIR"
  [ "$build_resolved" != "/data" ] || die "refusing to use /data as BUILD_DIR"
  [ "$build_resolved" != "$source_resolved" ] || die "BUILD_DIR must not be the source/runtime checkout"
  case "$build_resolved/" in
    "$source_resolved/"*) die "BUILD_DIR must not be inside SOURCE_DIR" ;;
  esac
  case "$source_resolved/" in
    "$build_resolved/"*) die "SOURCE_DIR must not be inside BUILD_DIR" ;;
  esac

  SOURCE_DIR="$source_resolved"
  BUILD_DIR="$build_resolved"
  RELEASE_FILES_SCRIPT="$SOURCE_DIR/tools/release/release_files.py"
  CLEAN_OVERLAY_DIR="$SOURCE_DIR/release/clean_overlay"
}

validate_source_tree() {
  local item manifest_output validation_error="" has_version=0 has_helper=0
  validate_layout

  [ -f "$RELEASE_FILES_SCRIPT" ] || die "missing canonical release manifest: $RELEASE_FILES_SCRIPT"
  [ -f "$SOURCE_DIR/openpilot/sunnypilot/common/version.h" ] || die "missing nested version file"
  [ -d "$SOURCE_DIR/openpilot/third_party" ] || die "missing nested third_party tree"
  [ -d "$SOURCE_DIR/openpilot/selfdrive/modeld/models" ] || die "missing nested model tree"

  for item in events.py events_sp.py driver_monitoring.py mads.py; do
    [ -f "$CLEAN_OVERLAY_DIR/$item" ] || die "missing clean overlay file: $CLEAN_OVERLAY_DIR/$item"
  done

  set +x
  manifest_output="$(cd "$SOURCE_DIR" && python3 "$RELEASE_FILES_SCRIPT" | sed -e 's/\r$//' -e 's#\\#/#g')"
  mapfile -t RELEASE_FILES <<< "$manifest_output"
  for item in "${RELEASE_FILES[@]}"; do
    if [ -z "$item" ]; then
      validation_error="release manifest contains an empty path"
      break
    fi
    case "$item" in
      /*|../*|*/../*|*/..) validation_error="unsafe release manifest path: $item"; break ;;
    esac
    if [ ! -e "$SOURCE_DIR/$item" ] && [ ! -L "$SOURCE_DIR/$item" ]; then
      validation_error="release manifest path is missing: $item"
      break
    fi
    [ "$item" = "openpilot/sunnypilot/common/version.h" ] && has_version=1
    [ "$item" = "tools/release/release_files.py" ] && has_helper=1
  done
  set -x

  [ "${#RELEASE_FILES[@]}" -gt 0 ] || die "release manifest returned no files"
  [ -z "$validation_error" ] || die "$validation_error"
  [ "$has_version" = "1" ] || die "release manifest omits the version file"
  [ "$has_helper" = "1" ] || die "release manifest omits its canonical helper"

  git check-ref-format --branch "$RELEASE_BRANCH" >/dev/null
  git check-ref-format --branch "$NIGHTLY_BRANCH" >/dev/null
  git check-ref-format --branch "$CLEAN_BRANCH" >/dev/null
  [ "$RELEASE_BRANCH" != "$NIGHTLY_BRANCH" ] || die "release and nightly branch names must differ"
  [ "$RELEASE_BRANCH" != "$CLEAN_BRANCH" ] || die "release and clean branch names must differ"
  [ "$NIGHTLY_BRANCH" != "$CLEAN_BRANCH" ] || die "nightly and clean branch names must differ"
  echo "[-] Preflight passed: ${#RELEASE_FILES[@]} release files"
}

validate_source_git_state() {
  local source_status submodule_status
  git -C "$SOURCE_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "source is not a Git worktree"
  source_status="$(git -C "$SOURCE_DIR" status --porcelain --untracked-files=all)" || die "could not inspect source worktree"
  [ -z "$source_status" ] || \
    die "source worktree is not clean; commit or remove local changes before publishing"
  submodule_status="$(git -C "$SOURCE_DIR" submodule status --recursive)" || die "could not inspect source submodules"
  if printf '%s\n' "$submodule_status" | grep -Eq '^[-+U]'; then
    die "source submodules do not match the recorded commits"
  fi
}

replace_once() {
  local file="$1" old="$2" new="$3"
  grep -Fq -- "$old" "$file" || die "clean overlay expected text not found in $file: $old"
  python3 - "$file" "$old" "$new" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
old, new = sys.argv[2], sys.argv[3]
text = path.read_text()
if text.count(old) != 1:
  raise SystemExit(f"expected exactly one occurrence in {path}, found {text.count(old)}")
path.write_text(text.replace(old, new))
PY
}

apply_clean_overlay() {
  local target="$BUILD_DIR/openpilot/sunnypilot/nrdr" item
  [ -d "$BUILD_DIR/.git" ] || die "clean overlay target is not a Git tree: $BUILD_DIR"
  [ -d "$target" ] || die "clean overlay target is missing: $target"

  for item in events.py events_sp.py driver_monitoring.py mads.py; do
    cp -p -- "$CLEAN_OVERLAY_DIR/$item" "$target/$item"
  done

  # Route registration and uploads to comma on the clean branch.
  sed -i '/^export API_HOST=https:\/\/api\.konik\.ai$/d; /^export ATHENA_HOST=wss:\/\/athena\.konik\.ai$/d' \
    "$BUILD_DIR/launch_env.sh" "$BUILD_DIR/launch_openpilot.sh"
  replace_once "$BUILD_DIR/openpilot/common/api/comma_connect.py" \
    "os.getenv('API_HOST', 'https://api.konik.ai')" \
    "os.getenv('API_HOST', 'https://api.commadotai.com')"
  replace_once "$BUILD_DIR/openpilot/system/athena/athenad.py" \
    "os.getenv('ATHENA_HOST', 'wss://athena.konik.ai')" \
    "os.getenv('ATHENA_HOST', 'wss://athena.comma.ai')"
  replace_once "$BUILD_DIR/openpilot/sunnypilot/nrdr/home.py" \
    "Your drives will upload to stable.konik.ai." \
    "Your drives will upload to connect.comma.ai."
  replace_once "$BUILD_DIR/openpilot/sunnypilot/nrdr/mici_home.py" \
    'home._version_label.set_text("stable.konik.ai")' \
    'home._version_label.set_text("connect.comma.ai")'
  replace_once "$BUILD_DIR/openpilot/selfdrive/ui/sunnypilot/layouts/settings/nrdr_sub_layouts/party_tricks.py" \
    '      self._reregister_item,' \
    ''

  ! grep -Eq '^export (API_HOST|ATHENA_HOST)=.*konik\.ai' "$BUILD_DIR/launch_env.sh" "$BUILD_DIR/launch_openpilot.sh" || \
    die "clean launch files still select the konik backend"
  grep -Fq "https://api.commadotai.com" "$BUILD_DIR/openpilot/common/api/comma_connect.py"
  grep -Fq "wss://athena.comma.ai" "$BUILD_DIR/openpilot/system/athena/athenad.py"
  grep -Fq "connect.comma.ai" "$BUILD_DIR/openpilot/sunnypilot/nrdr/home.py"
  grep -Fq "connect.comma.ai" "$BUILD_DIR/openpilot/sunnypilot/nrdr/mici_home.py"
  python3 -m py_compile \
    "$target/events.py" \
    "$target/events_sp.py" \
    "$target/driver_monitoring.py" \
    "$target/mads.py"
  find "$target" -name '__pycache__' -type d -prune -exec rm -rf -- '{}' +
}

safe_remove_build_dir() {
  local resolved
  resolved="$(resolve_path "$BUILD_DIR")"
  if [ "$resolved" != "$BUILD_DIR" ]; then
    die "BUILD_DIR resolution changed unexpectedly"
    return 1
  fi
  if [ "$resolved" = "/" ] || [ "$resolved" = "/data" ] || [ "$resolved" = "$SOURCE_DIR" ]; then
    die "refusing to remove unsafe BUILD_DIR: $resolved"
    return 1
  fi
  rm -rf -- "$resolved"
}

finish() {
  local status=$?
  set +e

  if [ -d "$BUILD_DIR/.git" ]; then
    git -C "$BUILD_DIR" remote set-url origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git" 2>/dev/null || true
    git -C "$BUILD_DIR" remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git" 2>/dev/null || true
  fi

  if [ "$status" = "0" ]; then
    if [ "$PUSH" = "1" ] && [ "$DELETE_BUILD_DIR_WHEN_DONE" = "1" ] && [ "$BUILD_DIR_OWNED" = "1" ]; then
      echo "[-] Removing completed temporary build tree $BUILD_DIR"
      safe_remove_build_dir || true
    fi
  elif [ "$BUILD_READY" = "1" ] && [ -d "$BUILD_DIR/.git" ]; then
    echo "[!] Run failed after a complete prebuilt was committed; preserving $BUILD_DIR for a push retry."
    echo "[!] Retry all three refs atomically from that tree after fixing connectivity/auth:"
    echo "[!]   git remote set-url origin git@github.com:${GITHUB_USER}/${GITHUB_REPO}.git"
    echo "[!]   git push --atomic -f origin ${RELEASE_BRANCH}:${RELEASE_BRANCH} ${RELEASE_BRANCH}:${NIGHTLY_BRANCH} ${CLEAN_BRANCH}:${CLEAN_BRANCH}"
  elif [ "$BUILD_DIR_OWNED" = "1" ] && [ -e "$BUILD_DIR" ]; then
    echo "[!] Run failed before a publishable prebuilt existed; removing the incomplete temporary tree."
    safe_remove_build_dir || true
  fi

  if [ "$status" = "0" ] && [ "$REBOOT_WHEN_DONE" = "1" ]; then
    echo "[-] Reboot requested explicitly (REBOOT_WHEN_DONE=1)"
    sync
    sudo reboot
  fi
  exit "$status"
}

validate_source_tree

if [ "$CLEAN_OVERLAY_ONLY" != "1" ] && [ "$PREBUILT_RUNTIME_CHECK_ONLY" != "1" ]; then
  configure_build_environment
fi

if [ "$PREBUILT_PREFLIGHT_ONLY" = "1" ]; then
  echo "[-] PREBUILT_PREFLIGHT_ONLY=1: no files changed"
  exit 0
fi

if [ "$PREBUILT_RUNTIME_CHECK_ONLY" = "1" ]; then
  validate_runtime_linkage
  echo "[-] PREBUILT_RUNTIME_CHECK_ONLY=1: no files changed"
  exit 0
fi

if [ "$CLEAN_OVERLAY_ONLY" = "1" ]; then
  apply_clean_overlay
  echo "[-] CLEAN_OVERLAY_ONLY=1: overlay applied to $BUILD_DIR"
  exit 0
fi

validate_source_git_state
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "[-] Release branch: $RELEASE_BRANCH"
echo "[-] Source dir: $SOURCE_DIR"
echo "[-] Temporary build dir: $BUILD_DIR"

if [ -e "$BUILD_DIR" ]; then
  if [ "$CLEANUP" != "1" ]; then
    die "$BUILD_DIR already exists; set CLEANUP=1 to replace this dedicated temporary build tree"
  fi
  echo "[-] Removing previous temporary build tree $BUILD_DIR"
  safe_remove_build_dir
fi

mkdir -p "$BUILD_DIR"
BUILD_DIR_OWNED=1
cd "$BUILD_DIR"

git init
git remote add origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
git remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
git checkout --orphan "$RELEASE_BRANCH"

echo "[-] Copying release files T=$SECONDS"
cd "$SOURCE_DIR"
cp -pR --parents -- "${RELEASE_FILES[@]}" "$BUILD_DIR/"

cd "$BUILD_DIR"
# The source checkout normally gets these links from setup. Recreate them in the
# standalone tree so the build never depends on host-checkout symlink behavior.
ln -sfn msgq_repo/msgq msgq
ln -sfn opendbc_repo/opendbc opendbc
ln -sfn rednose_repo/rednose rednose
ln -sfn teleoprtc_repo/teleoprtc teleoprtc
ln -sfn tinygrad_repo/tinygrad tinygrad
rm -f panda/board/obj/panda.bin.signed panda/board/obj/panda_h7.bin.signed || true

VERSION="$(awk -F'["-]' 'NR == 1 {print $2}' openpilot/sunnypilot/common/version.h)"
[ -n "$VERSION" ] || die "could not read release version"
echo "[-] Committing version $VERSION T=$SECONDS"

git add -f .
git commit -m "openpilot v$VERSION prebuilt"

echo "[-] Building T=$SECONDS"
export PYTHONPATH="$BUILD_DIR"
run_scons --minimal
run_scons panda/

echo "[-] Ensuring no submodules in release"
if test "$(git submodule status --recursive | wc -l)" -gt 0; then
  git submodule status --recursive
  exit 1
fi

echo "[-] Cleaning build junk"
find . -name '*.a' -delete
find . -name '*.o' -delete
find . -name '*.os' -delete
find . -name '*.pyc' -delete
find . -name 'moc_*' -delete
find . -name '__pycache__' -type d -prune -exec rm -rf -- '{}' +
rm -rf -- .sconsign.dblite Jenkinsfile release/ tools/release/ || true

echo "[-] Stripping oversized driving model (>100 MB GitHub limit)"
rm -f openpilot/selfdrive/modeld/models/big_driving_supercombo.onnx || true

if [ "$STRIP_ONNX" = "1" ]; then
  echo "[-] Stripping baked-in driving models (STRIP_ONNX=1)"
  rm -f openpilot/selfdrive/modeld/models/driving_supercombo.onnx || true
  rm -f openpilot/sunnypilot/modeld*/models/supercombo.onnx || true
else
  echo "[-] STRIP_ONNX=0: retaining the standard model floor"
fi

git checkout -- openpilot/third_party/ || true
touch prebuilt

validate_runtime_linkage

git add -A -f .
git commit --amend -m "openpilot v$VERSION prebuilt"

oversized="$(find . -type f -size +100M -not -path './.git/*' 2>/dev/null)"
if [ -n "$oversized" ]; then
  echo "[!] ERROR: files over GitHub's 100 MB limit remain:"
  echo "$oversized" | sed 's#^#[!]   #'
  exit 1
fi

RELEASE_COMMIT="$(git rev-parse HEAD)"

echo "[-] Building mandatory $CLEAN_BRANCH tree T=$SECONDS"
apply_clean_overlay
git branch -D "$CLEAN_BRANCH" 2>/dev/null || true
git checkout --orphan "$CLEAN_BRANCH"
git add -A -f .
git commit -m "openpilot v$VERSION prebuilt"
CLEAN_COMMIT="$(git rev-parse HEAD)"
[ "$(git rev-parse "$CLEAN_COMMIT^{tree}")" != "$(git rev-parse "$RELEASE_COMMIT^{tree}")" ] || \
  die "clean branch tree is unexpectedly identical to the full release"
BUILD_READY=1

if [ "$PUSH" = "1" ]; then
  echo "[-] PUSH T=$SECONDS"
  set +x
  if [ -z "${GITHUB_TOKEN:-}" ] && [ -f "$GITHUB_TOKEN_FILE" ]; then
    echo "[-] Using GitHub token from $GITHUB_TOKEN_FILE"
    GITHUB_TOKEN="$(tr -d '[:space:]' < "$GITHUB_TOKEN_FILE")"
  fi
  if [ -z "${GITHUB_TOKEN:-}" ]; then
    printf "GitHub PAT for %s: " "$GITHUB_USER"
    read -r -s GITHUB_TOKEN
    printf "\n"
  fi

  AUTH_REMOTE="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  git remote set-url origin "$AUTH_REMOTE"
  git remote set-url --push origin "$AUTH_REMOTE"
  set -x

  git config http.version HTTP/1.1
  git config http.postBuffer 524288000
  git config http.lowSpeedLimit 1000
  git config http.lowSpeedTime 600

  push_all_with_retry() {
    local tries=0
    while :; do
      if git push --atomic -f origin \
        "$RELEASE_BRANCH:$RELEASE_BRANCH" \
        "$RELEASE_BRANCH:$NIGHTLY_BRANCH" \
        "$CLEAN_BRANCH:$CLEAN_BRANCH"; then
        return 0
      fi
      tries=$((tries + 1))
      [ "$tries" -ge 3 ] && return 1
      echo "[!] Atomic release push failed (try $tries/3); retrying in 15s..."
      sleep 15
    done
  }

  # All three refs move together, or none do. This prevents a stale clean branch.
  push_all_with_retry || exit 1

  set +x
  git remote set-url origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  git remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  unset AUTH_REMOTE GITHUB_TOKEN
  set -x
else
  echo "[-] PUSH=0: release and clean trees are committed locally at $BUILD_DIR"
fi

echo "[-] Done T=$SECONDS"
