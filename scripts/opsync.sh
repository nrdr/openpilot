#!/usr/bin/env bash
set -e

cd /data/openpilot

BRANCH=$(git branch --show-current)

if [ -z "$BRANCH" ]; then
  echo "Not on a branch. Refusing to pull."
  exit 1
fi

echo "Pulling only current branch: $BRANCH"
git pull origin "$BRANCH" --no-tags

echo "Starting openpilot..."
/data/openpilot/tools/op.sh start