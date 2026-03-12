#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="v9/artifacts/${RUN_ID}"
mkdir -p "$OUT_DIR"

LOG_FILE="$OUT_DIR/test-log-v9.1.14-perf.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"
SETTINGS_FILE="$OUT_DIR/admin_settings.json"
HEALTH_FILE="$OUT_DIR/perf_health.json"
RECENT_FILE="$OUT_DIR/perf_recent.json"
EXPORT_ZIP="$OUT_DIR/export_test.zip"
EXPORT_LIST="$OUT_DIR/export_contents.txt"

API_BASE="${API_BASE:-http://localhost:8003}"
ADMIN_USER_ID="${ADMIN_USER_ID:-admin-user-v9-1-14}"
CUSTOMER_USER_ID="${CUSTOMER_USER_ID:-customer-user-v9-1-14}"
ADMIN_TOKEN="${ADMIN_UI_TOKEN:-}"

pass=0
fail=0
voice_result="SKIP (no deterministic audio sample in this script)"

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

python_json_get(){
  local file="$1"
  local expr="$2"
  python3 - "$file" "$expr" <<'PY'
import json,sys
path, expr = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding="utf-8"))
cur = data
for part in expr.split("."):
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
log "# v9.1.14 perf logging test"
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

log "[STEP] enable perf logging"
ENABLE_PAYLOAD=$(cat <<JSON
{"user_id":"$ADMIN_USER_ID","perf_logging_enabled":true,"perf_metrics_enabled":true,"perf_logging_sample_rate":1.0,"perf_logging_retention_days":30,"perf_export_max_days":7}
JSON
)
if curl_json POST "$API_BASE/admin/settings" -H "Content-Type: application/json" -d "$ENABLE_PAYLOAD" > "$SETTINGS_FILE"; then
  ok "admin/settings enable perf"
else
  ko "admin/settings enable perf"
fi

log "[STEP] synthetic interactions"
CHAT_PAYLOAD=$(cat <<JSON
{"text":"Wallbox perf test customer request","user_id":"$CUSTOMER_USER_ID","backend":"ollama"}
JSON
)
if curl_json POST "$API_BASE/chat/text" -H "Content-Type: application/json" -d "$CHAT_PAYLOAD" > "$OUT_DIR/chat_response.json"; then
  ok "chat/text customer->agent"
else
  ko "chat/text customer->agent"
fi

SESSION_ID="$(python_json_get "$OUT_DIR/chat_response.json" "session_id" || true)"
if [[ -n "${SESSION_ID}" ]]; then
  JOIN_PAYLOAD="{\"session_id\":\"$SESSION_ID\",\"agent_id\":\"agenten-02\"}"
  if curl_json POST "$API_BASE/agent/join" -H "Content-Type: application/json" -d "$JOIN_PAYLOAD" > "$OUT_DIR/agent_join.json"; then
    ok "agent/join"
  else
    ko "agent/join"
  fi
  AGENT_MSG_PAYLOAD=$(cat <<JSON
{"session_id":"$SESSION_ID","agent_id":"agenten-02","text":"Please check your breaker and cable.","agent_lang":"en","speak":false}
JSON
)
  if curl_json POST "$API_BASE/agent/message" -H "Content-Type: application/json" -d "$AGENT_MSG_PAYLOAD" > "$OUT_DIR/agent_message.json"; then
    ok "agent/message agent->customer"
  else
    ko "agent/message agent->customer"
  fi
else
  ko "session_id missing from chat response"
fi

log "[STEP] voice path"
log "[INFO] $voice_result"

sleep 1

log "[STEP] verify perf events + ttl health"
if curl_json GET "$API_BASE/admin/metrics/recent?user_id=$ADMIN_USER_ID&limit=50" > "$RECENT_FILE"; then
  event_count="$(python_json_get "$RECENT_FILE" "count" || echo 0)"
  if [[ "${event_count:-0}" -ge 1 ]]; then ok "perf events exist count=${event_count}"; else ko "no perf events"; fi
else
  ko "admin/metrics/recent"
fi

if curl_json GET "$API_BASE/admin/perf/health?user_id=$ADMIN_USER_ID" > "$HEALTH_FILE"; then
  ttl_ok="$(python_json_get "$HEALTH_FILE" "has_ttl_index" || echo false)"
  logdb="$(python_json_get "$HEALTH_FILE" "log_db" || echo -)"
  if [[ "$ttl_ok" == "True" || "$ttl_ok" == "true" ]]; then ok "ttl index exists"; else ko "ttl index missing"; fi
  if [[ "$logdb" == "voice_agent_logs" ]]; then ok "log db is voice_agent_logs"; else ko "unexpected log db: $logdb"; fi
else
  ko "admin/perf/health"
fi

log "[STEP] export zip for last 5 minutes"
FROM_ISO="$(python3 - <<'PY'
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc)-timedelta(minutes=5)).isoformat().replace('+00:00','Z'))
PY
)"
TO_ISO="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
PY
)"
if curl_json GET "$API_BASE/admin/perf/export?user_id=$ADMIN_USER_ID&from=$FROM_ISO&to=$TO_ISO&format=jsonl" -o "$EXPORT_ZIP"; then
  ok "admin/perf/export download"
else
  ko "admin/perf/export download"
fi

python3 - "$EXPORT_ZIP" "$EXPORT_LIST" <<'PY'
import sys, zipfile
zip_path, out_list = sys.argv[1], sys.argv[2]
names = []
with zipfile.ZipFile(zip_path, "r") as zf:
    names = sorted(zf.namelist())
with open(out_list, "w", encoding="utf-8") as f:
    for n in names:
        f.write(n + "\n")
need = {"README.md", "stats_summary.json"}
ok = all(any(name.endswith(x) for name in names) for x in need)
ok = ok and any(name.startswith("perf_events_") and name.endswith(".jsonl") for name in names)
print("OK" if ok else "FAIL")
PY
if [[ "$(tail -n 1 "$EXPORT_LIST" 2>/dev/null || true)" == "OK" ]]; then
  ok "export zip contents"
else
  # python result is printed to stdout, so evaluate again robustly
  if python3 - "$EXPORT_ZIP" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], "r") as zf:
    names = zf.namelist()
ok = ("README.md" in names) and ("stats_summary.json" in names) and any(n.startswith("perf_events_") and n.endswith(".jsonl") for n in names)
raise SystemExit(0 if ok else 1)
PY
  then
    ok "export zip contents"
  else
    ko "export zip contents"
  fi
fi

log "[STEP] disable perf logging"
DISABLE_PAYLOAD="{\"user_id\":\"$ADMIN_USER_ID\",\"perf_logging_enabled\":false,\"perf_metrics_enabled\":false}"
if curl_json POST "$API_BASE/admin/settings" -H "Content-Type: application/json" -d "$DISABLE_PAYLOAD" > "$OUT_DIR/admin_settings_disabled.json"; then
  ok "admin/settings disable perf"
else
  ko "admin/settings disable perf"
fi

log "[STEP] collect docker logs + env snapshot"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color api > "$OUT_DIR/docker-logs-api.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-admin > "$OUT_DIR/docker-logs-web-admin.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-agent > "$OUT_DIR/docker-logs-web-agent.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-customer > "$OUT_DIR/docker-logs-web-customer.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color piper > "$OUT_DIR/docker-logs-piper.txt" 2>&1 || true
{
  date -Iseconds
  echo "branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "commit=$(git rev-parse --short HEAD)"
  env | rg "MONGO|PERF|VOICE|OLLAMA|OPENAI|UI_VERSION|RETENTION" || true
} > "$OUT_DIR/ENV_SNAPSHOT.txt"

result="PASS"
if [[ "$fail" -gt 0 ]]; then result="FAIL"; fi

cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.14 Perf Logging Test Summary

- run_id: $RUN_ID
- date: $(date -Iseconds)
- result: **$result**
- passed: $pass
- failed: $fail
- voice_path: $voice_result

## Artifacts
- $LOG_FILE
- $SETTINGS_FILE
- $HEALTH_FILE
- $RECENT_FILE
- $EXPORT_ZIP
- $EXPORT_LIST

## Notes
- Artifacts are local-only and must not be committed.
EOF_SUM

log "[RESULT] $result"
log "Artifacts: $OUT_DIR"

if [[ "$result" != "PASS" ]]; then
  exit 1
fi

# Keep only latest 3 runs locally.
python3 - <<'PY'
from pathlib import Path
base = Path("v9/artifacts")
if not base.exists():
    raise SystemExit(0)
runs = sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
for old in runs[3:]:
    for item in sorted(old.rglob("*"), reverse=True):
        if item.is_file() or item.is_symlink():
            item.unlink(missing_ok=True)
        elif item.is_dir():
            item.rmdir()
    old.rmdir()
PY
