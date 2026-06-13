#!/usr/bin/env bash
set -euo pipefail
set -x

BUILD_DIR=/data/openpilot
SRC_DIR=/data/openpilot-src
GITHUB_USER="${GITHUB_USER:=nrdr}"
GITHUB_REPO="${GITHUB_REPO:=openpilot}"

# Daily defaults
# Branch date follows your local (Eastern) calendar day, not the device's UTC clock,
# so an evening build doesn't roll over to tomorrow's date.
: "${RELEASE_BRANCH:=nrdr-staging-$(TZ='America/New_York' date +%m.%d.%Y)}"
: "${PUSH:=1}"
: "${CLEANUP:=0}"
: "${RESTORE_SOURCE_NAME:=0}"
: "${DELETE_BUILD_DIR_WHEN_DONE:=1}"
# Unattended auth: drop your PAT here during your daily SSH bootstrap (chmod 600).
# Env GITHUB_TOKEN still wins; this file is just so the build never stops to prompt.
: "${GITHUB_TOKEN_FILE:=/data/gh_token}"
# Strip the baked-in driving model from the release (smaller, relies on model download).
# Set STRIP_ONNX=0 to keep a model floor so a fresh device is driveable without a download.
: "${STRIP_ONNX:=1}"
# Reboot after a successful run. The build moves/deletes/restores /data/openpilot
# underneath the running openpilot processes, leaving a corrupted "ghost build" in
# memory until the device restarts. Set REBOOT_WHEN_DONE=0 to skip.
: "${REBOOT_WHEN_DONE:=1}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
SOURCE_DIR="$(cd "$DIR/.." && pwd)"

restore_source_name() {
  status=$?

  set +e
  cd /data || true

  if [ -d "$BUILD_DIR/.git" ]; then
    git -C "$BUILD_DIR" remote set-url origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git" 2>/dev/null || true
    git -C "$BUILD_DIR" remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git" 2>/dev/null || true
  fi

  if [ "${RESTORE_SOURCE_NAME:-0}" = "1" ] && [ "${DELETE_BUILD_DIR_WHEN_DONE:-1}" = "1" ] && [ -d "$BUILD_DIR" ] && [ "$BUILD_DIR" != "$SRC_DIR" ]; then
    echo "[-] Removing runtime build tree $BUILD_DIR"
    rm -rf "$BUILD_DIR" || true
  fi

  if [ "${RESTORE_SOURCE_NAME:-0}" = "1" ] && [ -d "$SRC_DIR" ] && [ ! -e "$BUILD_DIR" ]; then
    echo "[-] Restoring source repo $SRC_DIR -> $BUILD_DIR"
    mv "$SRC_DIR" "$BUILD_DIR" || true
  fi

  # Reboot only after a fully successful device run, and only after the restore
  # above is done - the running processes are still on the deleted build tree
  # (the "ghost build") until the device comes back up on the restored repo.
  if [ "$status" = "0" ] && [ "${REBOOT_WHEN_DONE:-1}" = "1" ] && [ "${RESTORE_SOURCE_NAME:-0}" = "1" ]; then
    echo "[-] Rebooting to leave the ghost build behind (REBOOT_WHEN_DONE=0 to skip)"
    sync
    sudo reboot
  fi

  exit "$status"
}

trap restore_source_name EXIT INT TERM

# If source repo is currently /data/openpilot, move it to /data/openpilot-src,
# then restart this script from the new location.
if [ "$SOURCE_DIR" = "$BUILD_DIR" ]; then
  if [ -e "$SRC_DIR" ]; then
    echo "ERROR: $SRC_DIR already exists; refusing to overwrite it"
    exit 1
  fi

  # Arm the restore BEFORE the move, so a failure between here and the re-exec
  # can't leave you with the source stranded at $SRC_DIR.
  export RESTORE_SOURCE_NAME=1

  echo "[-] Moving source repo $BUILD_DIR -> $SRC_DIR"
  cd /data
  mv "$BUILD_DIR" "$SRC_DIR"

  exec bash "$SRC_DIR/release/build_prebuilt.sh" "$@"
fi

SOURCE_DIR="$SRC_DIR"
DIR="$SOURCE_DIR/release"

cd "$DIR"

echo "[-] Release branch: $RELEASE_BRANCH"
echo "[-] Source dir: $SOURCE_DIR"
echo "[-] Build dir: $BUILD_DIR"

echo "[-] Setting up runtime tree T=$SECONDS"
if [ "$CLEANUP" = "1" ]; then
  rm -rf "$BUILD_DIR"
else
  echo "[-] CLEANUP=0: leaving existing $BUILD_DIR in place if present"
fi

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

git init
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
git remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
git checkout --orphan "$RELEASE_BRANCH"

echo "[-] Copying release files T=$SECONDS"
cd "$SOURCE_DIR"
cp -pR --parents $(./release/release_files.py) "$BUILD_DIR/"

cd "$BUILD_DIR"

rm -f panda/board/obj/panda.bin.signed || true
rm -f panda/board/obj/panda_h7.bin.signed || true

VERSION="$(cat sunnypilot/common/version.h | awk -F[\"-] '{print $2}')"
echo "[-] committing version $VERSION T=$SECONDS"

git add -f .
git commit -a -m "openpilot v$VERSION prebuilt"

echo "[-] Building T=$SECONDS"
export PYTHONPATH="$BUILD_DIR"
scons -j"$(nproc)" --minimal
scons -j"$(nproc)" panda/

echo "[-] Ensuring no submodules in release"
if test "$(git submodule status --recursive | wc -l)" -gt "0"; then
  git submodule status --recursive
  exit 1
fi

echo "[-] Cleanup build junk"
find . -name '*.a' -delete
find . -name '*.o' -delete
find . -name '*.os' -delete
find . -name '*.pyc' -delete
find . -name 'moc_*' -delete
find . -name '__pycache__' -delete
rm -rf .sconsign.dblite Jenkinsfile release/ || true

if [ "$STRIP_ONNX" = "1" ]; then
  echo "[-] Stripping baked-in driving model (STRIP_ONNX=1)"
  rm -f selfdrive/modeld/models/driving_vision.onnx || true
  rm -f selfdrive/modeld/models/driving_policy.onnx || true
  rm -f sunnypilot/modeld*/models/supercombo.onnx || true
else
  echo "[-] STRIP_ONNX=0: keeping baked-in model so a fresh device is driveable without a download"
fi

git checkout -- third_party/ || true

touch prebuilt

git add -f .
git commit --amend -m "openpilot v$VERSION prebuilt"

echo "[-] Optional onroad test skipped"
# RELEASE=1 pytest -n0 -s selfdrive/test/test_onroad.py

# Changes that must never appear in nrdr-clean. Static reverse-patches are shipped
# in release/clean_excludes/ (generated from commits 181c61ee + a1c50bb6) because a
# fresh device install is shallow/prebuilt and does NOT have those commits in its
# local history (that is why 'git show <sha>' failed here on 06.11). The patches are
# reverse-applied to the prebuilt tree BEFORE the clean branch's single commit is
# created, so the published history never contains the excluded changes.
CLEAN_BRANCH="${CLEAN_BRANCH:=nrdr-clean}"
NIGHTLY_BRANCH="${NIGHTLY_BRANCH:=nrdr-nightly}"
CLEAN_EXCLUDES_DIR="$SOURCE_DIR/release/clean_excludes"

build_clean_tree() {
  # Reverse-apply the excluded patches onto the current prebuilt working tree.
  # Returns nonzero (without dying, caller checks) if any patch doesn't apply.
  local p found=0
  for p in "$CLEAN_EXCLUDES_DIR"/*.patch; do
    if [ ! -f "$p" ]; then
      echo "[!] WARNING: no patches found in $CLEAN_EXCLUDES_DIR"
      return 1
    fi
    found=1
    if ! git apply -R --whitespace=nowarn "$p"; then
      echo "[!] WARNING: could not reverse-apply $(basename "$p") onto the prebuilt tree"
      return 1
    fi
  done
  [ "$found" = "1" ] || return 1

  # nrdr-clean must not ship the konik API/Athena host exports.
  sed -i '/^export API_HOST=.*konik\.ai/d; /^export ATHENA_HOST=.*konik\.ai/d' launch_openpilot.sh launch_env.sh

  # nrdr-clean must register/upload to comma, not konik: revert the Python host defaults.
  sed -i "s|os.getenv('API_HOST', 'https://api.konik.ai')|os.getenv('API_HOST', 'https://api.commadotai.com')|" common/api/comma_connect.py
  sed -i "s|os.getenv('ATHENA_HOST', 'wss://athena.konik.ai')|os.getenv('ATHENA_HOST', 'wss://athena.comma.ai')|" system/athena/athenad.py

  # nrdr-clean uploads to comma, so the home screen must say so.
  sed -i 's|Your drives will upload to stable\.konik\.ai\.|Your drives will upload to connect.comma.ai.|' selfdrive/ui/layouts/home.py
  return 0
}

if [ "$PUSH" = "1" ]; then
  echo "[-] PUSH T=$SECONDS"

  set +x
  # Token precedence: env GITHUB_TOKEN -> $GITHUB_TOKEN_FILE -> interactive prompt.
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

  # 1) Dated staging branch (kept), 2) nightly (overwritten every run).
  git push -f origin "$RELEASE_BRANCH:$RELEASE_BRANCH"
  git push -f origin "$RELEASE_BRANCH:$NIGHTLY_BRANCH"

  # 3) nrdr-clean (overwritten every run): a fresh single commit whose tree never
  # contained the excluded changes. Failure here must not fail the whole build,
  # staging and nightly are already published.
  echo "[-] Building $CLEAN_BRANCH tree T=$SECONDS"
  if build_clean_tree; then
    git branch -D "$CLEAN_BRANCH" 2>/dev/null || true  # stale local branch from a CLEANUP=0 rerun
    git checkout --orphan "$CLEAN_BRANCH"
    git add -f .
    git commit -m "openpilot v$VERSION prebuilt"
    git push -f origin "$CLEAN_BRANCH:$CLEAN_BRANCH"
  else
    echo "[!] WARNING: skipping $CLEAN_BRANCH this run (see above); staging/nightly were pushed"
  fi

  set +x
  git remote set-url origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  git remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  unset AUTH_REMOTE
  unset GITHUB_TOKEN
  set -x
else
  echo "[-] PUSH=0: skipping git push. Prebuilt tree is local at $BUILD_DIR"
fi

echo "[-] done T=$SECONDS"
