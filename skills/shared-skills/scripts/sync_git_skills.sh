#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <target-skill-dir>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SOURCE_DIR="$REPO_ROOT/skills"
TARGET_DIR="$1"

mkdir -p "$TARGET_DIR"

# Keep the target aligned with the canonical repo without touching git metadata.
rsync -a --delete \
  --exclude '.DS_Store' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "$SOURCE_DIR/" "$TARGET_DIR/"

echo "synced skills from $SOURCE_DIR to $TARGET_DIR"
