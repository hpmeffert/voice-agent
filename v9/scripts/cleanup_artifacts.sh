#!/usr/bin/env bash
set -euo pipefail

KEEP="${1:-10}"
ROOT="v9/artifacts"

if ! [[ "$KEEP" =~ ^[0-9]+$ ]] || [[ "$KEEP" -lt 1 ]]; then
  echo "Usage: $0 <keep_count>=1..N" >&2
  exit 2
fi

mkdir -p "$ROOT"

# Keep newest N timestamped run folders.
COUNT=$(find "$ROOT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
if (( COUNT <= KEEP )); then
  echo "[cleanup] nothing to delete (have $COUNT, keep $KEEP)"
  exit 0
fi

DELETE_COUNT=$((COUNT - KEEP))
find "$ROOT" -mindepth 1 -maxdepth 1 -type d | sort | head -n "$DELETE_COUNT" | while IFS= read -r target; do
  rm -rf "$target"
  echo "[cleanup] deleted $target"
done

echo "[cleanup] kept latest $KEEP runs in $ROOT"
