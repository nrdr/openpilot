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
  git push -f origin "$RELEASE_BRANCH:$RELEASE_BRANCH"

  git remote set-url origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  git remote set-url --push origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
  unset AUTH_REMOTE
  unset GITHUB_TOKEN
  set -x
else
  echo "[-] PUSH=0: skipping git push. Prebuilt tree is local at $BUILD_DIR"
fi

echo "[-] done T=$SECONDS"
