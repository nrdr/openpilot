#!/usr/bin/env bash

set -e

BRANCH=$(git branch --show-current)

echo "Pulling branch: $BRANCH"
git pull origin "$BRANCH"

echo "Starting openpilot..."
op start