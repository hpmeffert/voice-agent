#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="v9/artifacts/${RUN_ID}"
mkdir -p "$OUT_DIR"
LOG_FILE="$OUT_DIR/test-log-v9.1.15-ui-smoke.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"

API_BASE="${API_BASE:-http://localhost:8085/api}"
ADMIN_UI_URL="${ADMIN_UI_URL:-http://localhost:8085}"
ADMIN_USER_ID="${ADMIN_USER_ID:-admin-user-v9-1-15}"
CUSTOMER_USER_ID="${CUSTOMER_USER_ID:-customer-user-v9-1-15}"
ADMIN_TOKEN="${ADMIN_UI_TOKEN:-}"

pass=0
fail=0

log(){ printf "%s\n" "$*" | tee -a "$LOG_FILE"; }
ok(){ pass=$((pass+1)); log "[PASS] $*"; }
ko(){ fail=$((fail+1)); log "[FAIL] $*"; }

start_stack(){
  local compose_cmd=(docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml)
  if DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 "${compose_cmd[@]}" up -d --build >> "$LOG_FILE" 2>&1; then
    log "[INFO] stack started with classic builder"
    return 0
  fi
  log "[WARN] build failed, trying existing images/containers without rebuild"
  "${compose_cmd[@]}" up -d >> "$LOG_FILE" 2>&1
}

curl_json(){
  local method="$1"; shift
  local url="$1"; shift
  if [[ -n "$ADMIN_TOKEN" ]]; then
    curl -sf -X "$method" -H "X-Admin-Token: $ADMIN_TOKEN" "$@" "$url"
  else
    curl -sf -X "$method" "$@" "$url"
  fi
}

json_get(){
  python3 - "$1" "$2" <<'PY'
import json,sys
path, expr = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding='utf-8'))
cur = data
for part in expr.split('.'):
    if not part:
        continue
    if isinstance(cur, list):
        cur = cur[int(part)]
    else:
        cur = cur.get(part)
print("" if cur is None else cur)
PY
}

: > "$LOG_FILE"
log "# v9.1.15 perf dashboard smoke"
log "date=$(date -Iseconds)"
log "api_base=$API_BASE"

log "[STEP] start stack"
start_stack

log "[STEP] wait health"
for _ in $(seq 1 120); do
  if curl -sf "$API_BASE/health" >/dev/null; then break; fi
  sleep 1
done
if curl -sf "$API_BASE/health" >/dev/null; then ok "health"; else ko "health"; fi

log "[STEP] config/version"
if curl -sf "$API_BASE/config?user_id=$ADMIN_USER_ID" > "$OUT_DIR/config.json"; then
  ver=$(json_get "$OUT_DIR/config.json" "ui.version")
  if [[ "$ver" == "v9.1.15" ]]; then ok "config ui.version=v9.1.15"; else ko "config ui.version expected v9.1.15 got $ver"; fi
else
  ko "config endpoint"
fi

log "[STEP] admin html structure"
if curl -sf "$ADMIN_UI_URL" > "$OUT_DIR/admin.html"; then
  if rg -q "Voice Agent Admin Client v9.1.15" "$OUT_DIR/admin.html"; then ok "admin header version visible"; else ko "admin header version missing"; fi
  if rg -q "adminPerfCards" "$OUT_DIR/admin.html"; then ok "perf cards block present"; else ko "perf cards block missing"; fi
  if rg -q "adminPerfSpikesTable" "$OUT_DIR/admin.html"; then ok "worst spikes table present"; else ko "worst spikes table missing"; fi
  if rg -q "adminPerfSearchQuery" "$OUT_DIR/admin.html"; then ok "perf search present"; else ko "perf search missing"; fi
  if rg -q "max-width: 1280px" "$OUT_DIR/admin.html"; then ok "admin width constrained"; else ko "admin width constraint missing"; fi
  if rg -q "white-space: pre-wrap;" "$OUT_DIR/admin.html" && rg -q "word-break: break-word;" "$OUT_DIR/admin.html"; then ok "wrapping css present"; else ko "wrapping css missing"; fi
else
  ko "admin html fetch"
fi

log "[STEP] enable perf logging"
SET_PAYLOAD='{"user_id":"'"$ADMIN_USER_ID"'","perf_logging_enabled":true,"perf_metrics_enabled":true,"perf_logging_sample_rate":1.0,"perf_logging_retention_days":30,"perf_export_max_days":7}'
if curl_json POST "$API_BASE/admin/settings" -H "Content-Type: application/json" -d "$SET_PAYLOAD" > "$OUT_DIR/admin-settings-set.json"; then
  ok "admin/settings enable perf"
else
  ko "admin/settings enable perf"
fi

log "[STEP] create sample interactions"
CHAT_PAYLOAD='{"text":"Wallbox perf dashboard smoke fe77abc","user_id":"'"$CUSTOMER_USER_ID"'","backend":"ollama"}'
if curl_json POST "$API_BASE/chat/text" -H "Content-Type: application/json" -d "$CHAT_PAYLOAD" > "$OUT_DIR/chat.json"; then
  ok "chat/text"
else
  ko "chat/text"
fi
SESSION_ID="$(json_get "$OUT_DIR/chat.json" "session_id" || true)"
if [[ -n "$SESSION_ID" ]]; then
  JOIN_PAYLOAD='{"session_id":"'"$SESSION_ID"'","agent_id":"agenten-02"}'
  curl_json POST "$API_BASE/agent/join" -H "Content-Type: application/json" -d "$JOIN_PAYLOAD" > "$OUT_DIR/agent-join.json" && ok "agent/join" || ko "agent/join"
  AGENT_PAYLOAD='{"session_id":"'"$SESSION_ID"'","agent_id":"agenten-02","text":"Please check breaker status for the wallbox.","agent_lang":"en","speak":false}'
  curl_json POST "$API_BASE/agent/message" -H "Content-Type: application/json" -d "$AGENT_PAYLOAD" > "$OUT_DIR/agent-message.json" && ok "agent/message" || ko "agent/message"
else
  ko "session_id missing from chat response"
fi
sleep 1

log "[STEP] perf summary + spikes"
if curl_json GET "$API_BASE/admin/perf/summary?user_id=$ADMIN_USER_ID&window=24h" > "$OUT_DIR/admin-perf-summary.json"; then
  ok "admin/perf/summary"
  count="$(json_get "$OUT_DIR/admin-perf-summary.json" "count" || echo 0)"
  spikes="$(python3 - <<'PY' "$OUT_DIR/admin-perf-summary.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print(len(j.get('worst_spikes') or []))
PY
)"
  if [[ "${count:-0}" -ge 1 ]]; then ok "perf summary count=$count"; else ko "perf summary empty"; fi
  if [[ "${spikes:-0}" -ge 1 ]]; then ok "worst spikes count=$spikes"; else ko "worst spikes empty"; fi
else
  ko "admin/perf/summary"
fi

log "[STEP] perf search"
SEARCH_PREFIX="${CUSTOMER_USER_ID:0:12}*"
if [[ -n "$SESSION_ID" ]]; then
  SEARCH_PREFIX="${SESSION_ID:0:8}*"
fi
if curl_json GET "$API_BASE/admin/perf/search?user_id=$ADMIN_USER_ID&q=$SEARCH_PREFIX&limit=20" > "$OUT_DIR/admin-perf-search.json"; then
  ok "admin/perf/search"
  matches="$(python3 - <<'PY' "$OUT_DIR/admin-perf-search.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print(len(j.get('items') or []))
PY
)"
  if [[ "${matches:-0}" -ge 1 ]]; then ok "perf search matches=$matches"; else ko "perf search no matches"; fi
else
  ko "admin/perf/search"
fi

log "[STEP] perf export zip"
FROM_ISO="$(python3 - <<'PY'
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc)-timedelta(hours=1)).isoformat().replace('+00:00','Z'))
PY
)"
TO_ISO="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
PY
)"
if curl_json GET "$API_BASE/admin/perf/export?user_id=$ADMIN_USER_ID&from=$FROM_ISO&to=$TO_ISO&format=jsonl" -o "$OUT_DIR/perf-export.zip"; then
  ok "admin/perf/export"
else
  ko "admin/perf/export"
fi

if python3 - <<'PY' "$OUT_DIR/perf-export.zip"
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], 'r') as zf:
    names = zf.namelist()
ok = ('README.md' in names) and ('stats_summary.json' in names) and any(n.startswith('perf_events_') for n in names)
raise SystemExit(0 if ok else 1)
PY
then
  ok "perf export contents"
else
  ko "perf export contents"
fi

log "[STEP] collect logs"
{
  date -Iseconds
  echo "branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "commit=$(git rev-parse --short HEAD)"
  env | rg "MONGO|PERF|VOICE|OLLAMA|OPENAI|UI_VERSION|RETENTION" || true
} > "$OUT_DIR/ENV_SNAPSHOT.txt"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color api > "$OUT_DIR/docker-logs-api.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-admin > "$OUT_DIR/docker-logs-web-admin.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-agent > "$OUT_DIR/docker-logs-web-agent.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-customer > "$OUT_DIR/docker-logs-web-customer.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color mongo > "$OUT_DIR/docker-logs-mongo.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color piper > "$OUT_DIR/docker-logs-piper.txt" 2>&1 || true

result="PASS"
if [[ "$fail" -gt 0 ]]; then result="FAIL"; fi

cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.15 Perf Dashboard Smoke Summary

- run_id: $RUN_ID
- date: $(date -Iseconds)
- result: **$result**
- passed: $pass
- failed: $fail

## Artifacts
- $LOG_FILE
- $OUT_DIR/config.json
- $OUT_DIR/admin.html
- $OUT_DIR/admin-perf-summary.json
- $OUT_DIR/admin-perf-search.json
- $OUT_DIR/perf-export.zip
- $OUT_DIR/ENV_SNAPSHOT.txt
EOF_SUM

log "[RESULT] $result"
log "Artifacts: $OUT_DIR"

if [[ "$result" != "PASS" ]]; then
  exit 1
fi

python3 - <<'PY'
from pathlib import Path
base = Path('v9/artifacts')
if not base.exists():
    raise SystemExit(0)
runs = sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
for old in runs[3:]:
    for item in sorted(old.rglob('*'), reverse=True):
        if item.is_file() or item.is_symlink():
            item.unlink(missing_ok=True)
        elif item.is_dir():
            item.rmdir()
    old.rmdir()
PY
