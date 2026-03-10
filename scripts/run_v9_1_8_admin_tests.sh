#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="$(date +%Y-%m-%d_v9.1.8_%H%M%S)"
OUT_DIR="v9/artifacts/${RUN_ID}"
mkdir -p "$OUT_DIR"
LOG_FILE="$OUT_DIR/test-log-v9.1.8.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"

API_BASE="${API_BASE:-http://localhost:8085/api}"
ADMIN_USER_ID="${ADMIN_USER_ID:-admin-user-v9-1-8}"
CUSTOMER_USER_ID="${CUSTOMER_USER_ID:-customer-user-v9-1-8}"
AGENT_ID="${AGENT_ID:-agenten-02}"
ADMIN_TOKEN="${ADMIN_UI_TOKEN:-}"

declare -a AUTH_HEADER
if [[ -n "$ADMIN_TOKEN" ]]; then
  AUTH_HEADER=(-H "X-Admin-Token: $ADMIN_TOKEN")
else
  AUTH_HEADER=()
fi

PASS_COUNT=0
FAIL_COUNT=0

log(){
  printf "%s\n" "$*" | tee -a "$LOG_FILE"
}

mark_pass(){
  PASS_COUNT=$((PASS_COUNT+1))
  log "[PASS] $1"
}

mark_fail(){
  FAIL_COUNT=$((FAIL_COUNT+1))
  log "[FAIL] $1"
}

json_get(){
  local url="$1"
  if [[ ${#AUTH_HEADER[@]} -gt 0 ]]; then
    curl -sf "${AUTH_HEADER[@]}" "$url"
  else
    curl -sf "$url"
  fi
}

json_post(){
  local url="$1"
  local body="$2"
  if [[ ${#AUTH_HEADER[@]} -gt 0 ]]; then
    curl -sf "${AUTH_HEADER[@]}" -H "Content-Type: application/json" -d "$body" "$url"
  else
    curl -sf -H "Content-Type: application/json" -d "$body" "$url"
  fi
}

: > "$LOG_FILE"
log "# V9.1.8 Admin test run"
log "date=$(date -Iseconds)"
log "run_id=$RUN_ID"
log "api_base=$API_BASE"

log "[STEP] Start stack"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml up -d --build >> "$LOG_FILE" 2>&1

log "[STEP] Wait for /health"
for _ in $(seq 1 120); do
  if curl -sf "$API_BASE/health" >/dev/null; then
    break
  fi
  sleep 1
done
if ! curl -sf "$API_BASE/health" >/dev/null; then
  mark_fail "health endpoint unavailable"
else
  mark_pass "health endpoint reachable"
fi

log "[STEP] Probe /models"
if json_get "$API_BASE/models" > "$OUT_DIR/models.json"; then
  mark_pass "models endpoint reachable"
else
  mark_fail "models endpoint unreachable"
fi

log "[STEP] Enable perf logging"
SETTINGS_ENABLE='{"user_id":"'"$ADMIN_USER_ID"'","perf_logging_enabled":true,"perf_logging_sample_rate":1.0,"perf_logging_retention_days":30,"search_max_results":50,"allow_text_regex_fallback":true}'
if json_post "$API_BASE/admin/settings" "$SETTINGS_ENABLE" > "$OUT_DIR/admin-settings-enable.json"; then
  mark_pass "admin settings updated (perf on)"
else
  mark_fail "admin settings update (perf on) failed"
fi

log "[STEP] Send customer chat message"
CHAT_REQ='{"text":"Meine Wallbox geht immer aus. Bitte pruefen Sie die Stromversorgung.","user_id":"'"$CUSTOMER_USER_ID"'","session_id":"","backend":"ollama"}'
if json_post "$API_BASE/chat/text" "$CHAT_REQ" > "$OUT_DIR/chat-response.json"; then
  mark_pass "chat/text succeeded"
else
  mark_fail "chat/text failed"
fi

SESSION_ID="$(python3 - <<'PY' "$OUT_DIR/chat-response.json"
import json,sys
p=sys.argv[1]
try:
    d=json.load(open(p,'r',encoding='utf-8'))
    print(d.get('session_id',''))
except Exception:
    print('')
PY
)"

if [[ -z "$SESSION_ID" ]]; then
  mark_fail "session_id missing from chat response"
else
  mark_pass "session_id resolved: $SESSION_ID"
fi

log "[STEP] Send agent reply"
if [[ -n "$SESSION_ID" ]]; then
  AGENT_REQ='{"session_id":"'"$SESSION_ID"'","agent_id":"'"$AGENT_ID"'","text":"Please check the breaker and power supply.","speak":false,"agent_lang":"en"}'
  if json_post "$API_BASE/agent/message" "$AGENT_REQ" > "$OUT_DIR/agent-response.json"; then
    mark_pass "agent/message succeeded"
  else
    mark_fail "agent/message failed"
  fi
fi

sleep 1

log "[STEP] Assert perf logs exist"
if json_get "$API_BASE/admin/metrics/recent?user_id=$ADMIN_USER_ID&limit=20" > "$OUT_DIR/admin-metrics-recent.json"; then
  METRIC_COUNT="$(python3 - <<'PY' "$OUT_DIR/admin-metrics-recent.json"
import json,sys
d=json.load(open(sys.argv[1],'r',encoding='utf-8'))
print(int(d.get('count',0)))
PY
)"
  if [[ "$METRIC_COUNT" -ge 1 ]]; then
    mark_pass "perf log entries present ($METRIC_COUNT)"
  else
    mark_fail "no perf log entries found"
  fi
else
  mark_fail "admin/metrics/recent failed"
fi

log "[STEP] Search by partial session_id"
if [[ -n "$SESSION_ID" ]]; then
  PARTIAL="${SESSION_ID:0:8}*"
  if json_get "$API_BASE/admin/search?user_id=$ADMIN_USER_ID&q=$PARTIAL&mode=session_id&limit=20" > "$OUT_DIR/admin-search-session.json"; then
    FOUND="$(python3 - <<'PY' "$OUT_DIR/admin-search-session.json"
import json,sys
d=json.load(open(sys.argv[1],'r',encoding='utf-8'))
print(len(d.get('matches',[])))
PY
)"
    if [[ "$FOUND" -ge 1 ]]; then
      mark_pass "admin/search session_id matched ($FOUND)"
    else
      mark_fail "admin/search session_id returned no matches"
    fi
  else
    mark_fail "admin/search session_id request failed"
  fi
fi

log "[STEP] Search by text"
if json_get "$API_BASE/admin/search?user_id=$ADMIN_USER_ID&q=breaker&mode=text&since_days=7&limit=20" > "$OUT_DIR/admin-search-text.json"; then
  FOUND_TEXT="$(python3 - <<'PY' "$OUT_DIR/admin-search-text.json"
import json,sys
d=json.load(open(sys.argv[1],'r',encoding='utf-8'))
print(len(d.get('matches',[])))
PY
)"
  if [[ "$FOUND_TEXT" -ge 1 ]]; then
    mark_pass "admin/search text matched ($FOUND_TEXT)"
  else
    mark_fail "admin/search text returned no matches"
  fi
else
  mark_fail "admin/search text request failed"
fi

log "[STEP] Disable perf logging"
SETTINGS_DISABLE='{"user_id":"'"$ADMIN_USER_ID"'","perf_logging_enabled":false}'
if json_post "$API_BASE/admin/settings" "$SETTINGS_DISABLE" > "$OUT_DIR/admin-settings-disable.json"; then
  mark_pass "admin settings updated (perf off)"
else
  mark_fail "admin settings update (perf off) failed"
fi

log "[STEP] Collect logs and env snapshot"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color api > "$OUT_DIR/docker-logs-api.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-admin > "$OUT_DIR/docker-logs-web-admin.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-agent > "$OUT_DIR/docker-logs-web-agent.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-customer > "$OUT_DIR/docker-logs-web-customer.txt" 2>&1 || true
env | grep -E "VOICE|LANG|TTS|OLLAMA|OPENAI|MONGO|VALKEY|REDIS|RETENTION|ADMIN" > "$OUT_DIR/ENV_SNAPSHOT.txt" || true

RESULT="PASS"
if [[ "$FAIL_COUNT" -gt 0 ]]; then
  RESULT="FAIL"
fi

cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.8 Admin Test Summary

- Run ID: $RUN_ID
- Date: $(date -Iseconds)
- Result: **$RESULT**
- Passed checks: $PASS_COUNT
- Failed checks: $FAIL_COUNT

## Evidence files
- test log: \`$LOG_FILE\`
- env snapshot: \`$OUT_DIR/ENV_SNAPSHOT.txt\`
- api logs: \`$OUT_DIR/docker-logs-api.txt\`
- web-admin logs: \`$OUT_DIR/docker-logs-web-admin.txt\`
- web-agent logs: \`$OUT_DIR/docker-logs-web-agent.txt\`
- web-customer logs: \`$OUT_DIR/docker-logs-web-customer.txt\`
- metrics recent: \`$OUT_DIR/admin-metrics-recent.json\`
- search by session: \`$OUT_DIR/admin-search-session.json\`
- search by text: \`$OUT_DIR/admin-search-text.json\`
EOF_SUM

if [[ "$RESULT" == "PASS" ]]; then
  log "[RESULT] PASS"
  exit 0
fi
log "[RESULT] FAIL"
exit 1
