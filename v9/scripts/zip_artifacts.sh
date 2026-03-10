#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

RUN_DIR="${1:-}"
if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: v9/scripts/zip_artifacts.sh <v9/artifacts/<run_dir>>"
  exit 1
fi

if [[ ! -d "$RUN_DIR" ]]; then
  echo "Run directory not found: $RUN_DIR"
  exit 1
fi

OUT_ZIP="${RUN_DIR%/}.zip"
rm -f "$OUT_ZIP"
(
  cd "$(dirname "$RUN_DIR")"
  zip -r "$(basename "$OUT_ZIP")" "$(basename "$RUN_DIR")" >/dev/null
)

echo "Created: $OUT_ZIP"
