#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$PWD}"
AGENT_URL="${AGENT_URL:-http://localhost:8087}"
CUSTOMER_URL="${CUSTOMER_URL:-http://localhost:8086}"
API_BASE_OVERRIDE="${API_BASE_OVERRIDE:-http://localhost:8003}"
FAST_SEC="${FAST_SEC:-4}"
EVENTUAL_SEC="${EVENTUAL_SEC:-30}"
PROBE_DURATION_SEC="${PROBE_DURATION_SEC:-120}"
RETAIN_RUNS="${RETAIN_RUNS:-10}"

TS="$(date -u +%Y%m%d-%H%M%S)"
RUN_DIR="v9/artifacts/${TS}"
WORK_ROOT="v9/.artifacts_work"
RUN_LOG="$RUN_DIR/test-log-v9.1.6.txt"
mkdir -p "$RUN_DIR"

# Ensure stack is up before tests.
bash v9/scripts/tests/run_v9_smoke.sh

set +e
FAST_SEC="$FAST_SEC" \
EVENTUAL_SEC="$EVENTUAL_SEC" \
PROBE_DURATION_SEC="$PROBE_DURATION_SEC" \
RETAIN_RUNS="$RETAIN_RUNS" \
API_BASE_OVERRIDE="$API_BASE_OVERRIDE" \
bash scripts/run_v9_ws_duallane_tests.sh --agent_url "$AGENT_URL" --customer_url "$CUSTOMER_URL" --out "$WORK_ROOT" \
  | tee "$RUN_LOG"
TEST_EXIT=${PIPESTATUS[0]}
set -e

SRC_RUN_DIR="$(awk -F': ' '/Artifacts run dir:/ {print $2}' "$RUN_LOG" | tail -n1)"
if [[ -z "$SRC_RUN_DIR" ]]; then
  SRC_RUN_DIR="$(awk -F': ' '/Artifacts:/ {print $2}' "$RUN_LOG" | tail -n1)"
fi

if [[ -z "$SRC_RUN_DIR" || ! -d "$SRC_RUN_DIR" ]]; then
  echo "[V9.1.6][FAIL] Could not resolve source artifact directory." >> "$RUN_LOG"
  exit 2
fi

# Copy required outputs into the official V9 artifact folder.
cp -f "$SRC_RUN_DIR/events-agent.jsonl" "$RUN_DIR/events-agent.jsonl" 2>/dev/null || true
cp -f "$SRC_RUN_DIR/events-customer.jsonl" "$RUN_DIR/events-customer.jsonl" 2>/dev/null || true
cp -f "$SRC_RUN_DIR/ws_agent_events.jsonl" "$RUN_DIR/events-agent.jsonl" 2>/dev/null || true
cp -f "$SRC_RUN_DIR/ws_customer_events.jsonl" "$RUN_DIR/events-customer.jsonl" 2>/dev/null || true
cp -f "$SRC_RUN_DIR/ws_probe_status.json" "$RUN_DIR/ws_probe_status.json" 2>/dev/null || true
cp -f "$SRC_RUN_DIR/session_dump.json" "$RUN_DIR/session_dump.json" 2>/dev/null || true
cp -f "$SRC_RUN_DIR/http-probes.json" "$RUN_DIR/http-probes.json" 2>/dev/null || true

# Collect fresh logs/env snapshot with dedicated script.
bash v9/scripts/tests/collect_artifacts.sh "$RUN_DIR"

RUN_DIR_ENV="$RUN_DIR" python3 - <<'PY'
import json, re, subprocess
import os
from pathlib import Path
run_dir = Path(os.environ["RUN_DIR_ENV"])
log = run_dir.joinpath("test-log-v9.1.6.txt").read_text(encoding="utf-8", errors="ignore")
commit = subprocess.check_output(["git","rev-parse","--short","HEAD"], text=True).strip()
res = re.search(r"^RESULT:\s*(PASS|FAIL)", log, re.M)
s1 = re.search(r"^SCENARIO1:\s*(.*)$", log, re.M)
s2 = re.search(r"^SCENARIO2:\s*(.*)$", log, re.M)
s3 = re.search(r"^SCENARIO3:\s*(.*)$", log, re.M)
p95 = re.search(r"^P95_MS:\s*([0-9.]+)", log, re.M)
voice = re.search(r"^VOICE_SCENARIO:\s*(.*)$", log, re.M)

def find_event(path, from_role):
    p = run_dir / path
    if not p.exists():
      return {}
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
      try:
        row = json.loads(line)
      except Exception:
        continue
      ev = row.get("event", {})
      pl = ev.get("payload", {})
      if ev.get("type") == "message.created" and ev.get("from") == from_role:
        if from_role == "customer" and pl.get("text_original") == "Meine Wallbox geht aus.":
          return pl
        if from_role == "agent" and pl.get("text_original") == "Please check the breaker and power cycle the wallbox.":
          return pl
    return {}

voice_ev = find_event("events-agent.jsonl", "customer")
reply_ev = find_event("events-customer.jsonl", "agent")

summary = [
  f"COMMIT: {commit}",
  f"RESULT: {(res.group(1) if res else 'FAIL')}",
  f"SCENARIO1: {(s1.group(1) if s1 else 'n/a')}",
  f"SCENARIO2: {(s2.group(1) if s2 else 'n/a')}",
  f"SCENARIO3: {(s3.group(1) if s3 else 'n/a')}",
  f"P95_MS: {(p95.group(1) if p95 else 'n/a')}",
  "",
  f"VOICE_SCENARIO: {(voice.group(1) if voice else 'n/a')}",
  "",
  "## Voice Proof",
  f"- text_original: {voice_ev.get('text_original','n/a')}",
  f"- text_for_agent: {voice_ev.get('text_for_agent','n/a')}",
  f"- lang_for_agent: {voice_ev.get('lang_for_agent','n/a')}",
  f"- tts_lang_agent: {voice_ev.get('tts_lang_agent','n/a')}",
  "",
  "## Reply Proof",
  f"- text_original: {reply_ev.get('text_original','n/a')}",
  f"- text_for_customer: {reply_ev.get('text_for_customer','n/a')}",
  f"- lang_for_customer: {reply_ev.get('lang_for_customer','n/a')}",
  f"- tts_lang_customer: {reply_ev.get('tts_lang_customer','n/a')}",
  "",
  "## Human 2-minute proof checklist",
  "- Agent URL: http://localhost:8087",
  "- Customer URL: http://localhost:8086",
  "- Agent setup: language=en, incoming speak=ON, customer output on agent=OFF, auto-refresh=ON",
  "- Customer setup: language=de, customer speak=ON",
  "- Voice check: customer DE -> agent sees Original+EN lane and hears EN lane only",
  "- Reply check: agent EN -> customer sees/hears DE lane",
]
(run_dir / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
PY

(
  cd "$RUN_DIR"
  zip -qr artifacts.zip .
)

# Retention for official v9 artifact folders.
bash v9/scripts/cleanup_artifacts.sh "$RETAIN_RUNS" >/dev/null || true

echo "Artifacts: $RUN_DIR"
exit "$TEST_EXIT"
