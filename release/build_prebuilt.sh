#!/usr/bin/env bash
set -euo pipefail
set -x

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
SOURCE_DIR="$(cd "$DIR/.." && pwd)"     # /data/openpilot-src (repo root)
BUILD_DIR=/data/openpilot               # runtime tree

: "${RELEASE_BRANCH:?RELEASE_BRANCH is not set}"
: "${PUSH:=0}"       # set to 0 to disable git push
: "${CLEANUP:=0}"    # set to 0 to keep BUILD_DIR and avoid deleting it

cd "$DIR"

# optional: set git identity if you want
# source "$DIR/identity.sh"

echo "[-] Setting up runtime tree T=$SECONDS"
if [ "$CLEANUP" = "1" ]; then
  rm -rf "$BUILD_DIR"
else
  echo "[-] CLEANUP=0: leaving existing $BUILD_DIR in place"
fi

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
git init
git remote add origin https://github.com/nrdr/openpilot.git
git checkout --orphan "$RELEASE_BRANCH"

echo "[-] Copying release files T=$SECONDS"
cd "$SOURCE_DIR"
cp -pR --parents $(./release/release_files.py) "$BUILD_DIR/"

cd "$BUILD_DIR"

# remove any leftover signed fw artifacts
rm -f panda/board/obj/panda.bin.signed || true
rm -f panda/board/obj/panda_h7.bin.signed || true

VERSION="$(cat sunnypilot/common/version.h | awk -F[\"-] '{print $2}')"
echo "[-] committing version $VERSION T=$SECONDS"
git add -f .
git commit -a -m "openpilot v$VERSION prebuilt"

echo "[-] Building T=$SECONDS"
export PYTHONPATH="$BUILD_DIR"
scons -j"$(nproc)" --minimal

# Build panda (no Comma release certs on community devices)
scons -j"$(nproc)" panda/

echo "[-] Ensuring no submodules in release"
if test "$(git submodule--helper list | wc -l)" -gt "0"; then
  git submodule--helper list
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

# remove big models not needed in prebuilt tree (keep consistent with your fork’s expectations)
rm -f selfdrive/modeld/models/driving_vision.onnx || true
rm -f selfdrive/modeld/models/driving_policy.onnx || true
rm -f sunnypilot/modeld*/models/supercombo.onnx || true

# restore third_party if your release_files pulled extra host junk
git checkout -- third_party/ || true

touch prebuilt

git add -f .
git commit --amend -m "openpilot v$VERSION prebuilt"

echo "[-] (Optional) onroad test"
#RELEASE=1 pytest -n0 -s selfdrive/test/test_onroad.py

if [ "$PUSH" = "1" ]; then
  echo "[-] PUSH T=$SECONDS"

  # Force HTTPS remote every run because device resets may recreate origin with SSH push URL.
  git remote set-url origin "https://github.com/nrdr/openpilot.git"
  git remote set-url --push origin "https://github.com/nrdr/openpilot.git"

  git remote -v
  git push -f origin "$RELEASE_BRANCH:$RELEASE_BRANCH"
else
  echo "[-] PUSH=0: skipping git push. Prebuilt tree is local at $BUILD_DIR"
fi

echo "[-] done T=$SECONDS"