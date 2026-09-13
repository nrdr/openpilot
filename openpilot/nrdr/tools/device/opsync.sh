#!/usr/bin/env bash
# opsync.sh - "Force Update": hard-sync /data/openpilot (parent repo AND all
# submodules) to exactly match the current branch on GitHub, then restart.
#
# Unlike `git pull` (a merge that ignores submodules), this force-overwrites
# local state, so it cannot get stuck on conflicts and it correctly follows a
# force-pushed / rewritten branch. The submodule steps are what the old
# `git pull` never did, and why the parent and opendbc kept drifting apart.
set -e

cd /data/openpilot

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ -z "$BRANCH" ] || [ "$BRANCH" = "HEAD" ]; then
  echo "Detached HEAD / not on a branch. Refusing to sync."
  exit 1
fi

echo "Force-syncing '$BRANCH' to origin (local changes will be discarded)..."
git fetch origin "$BRANCH" --no-tags --force --prune

# Parent repo -> exactly the fetched remote tip. No merge, no conflicts.
git checkout --force --no-recurse-submodules -B "$BRANCH" FETCH_HEAD
git reset --hard FETCH_HEAD

# Submodules -> exactly the commits the parent now points at, recursively.
# submodule sync picks up any .gitmodules URL change (e.g. opendbc repoint);
# --force overwrites a dirty/diverged submodule working tree.
git submodule sync --recursive
git submodule update --init --recursive --force
git submodule foreach --recursive git reset --hard

# OPTIONAL pristine clean: removes untracked files so the tree matches GitHub
# byte-for-byte. Left OFF by default -- with -x it also deletes compiled build
# artifacts and would force a full rebuild before openpilot can start, which is
# rough when you hop between compiled and non-compiled branches. Uncomment only
# if you deliberately want a from-scratch tree.
# git clean -ffd
# git submodule foreach --recursive git clean -ffd

echo "Restarting openpilot into the synced code..."
sudo systemctl --no-block restart comma
