#!/usr/bin/env bash
set -euo pipefail

if git ls-files | rg -n '(^|/)(artifacts|output|tmp|test_artifacts)(/|$)|\.log$|\.zip$|ENV_SNAPSHOT.*\.txt$|session_dump.*\.json$|ws_.*events.*\.jsonl$|testlog\.txt$|_testlog\.md$' >/tmp/no_artifacts_tracked.out; then
  echo "[FAIL] tracked artifact-like files found:"
  cat /tmp/no_artifacts_tracked.out
  exit 1
fi

echo "[OK] no tracked artifact-like files found"
