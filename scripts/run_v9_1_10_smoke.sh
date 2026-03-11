#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="v9/artifacts/${RUN_ID}"
mkdir -p "$OUT_DIR"
LOG_FILE="$OUT_DIR/test-log-v9.1.11-smoke.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"

API_BASE="${API_BASE:-http://localhost:8085/api}"
ADMIN_UI_URL="${ADMIN_UI_URL:-http://localhost:8085}"
AGENT_UI_URL="${AGENT_UI_URL:-http://localhost:8087}"
ADMIN_USER_ID="${ADMIN_USER_ID:-admin-user-v9-1-10}"
CUSTOMER_USER_ID="${CUSTOMER_USER_ID:-customer-user-v9-1-10}"
ADMIN_TOKEN="${ADMIN_UI_TOKEN:-}"

pass=0
fail=0

log(){ printf "%s\n" "$*" | tee -a "$LOG_FILE"; }
ok(){ pass=$((pass+1)); log "[PASS] $*"; }
ko(){ fail=$((fail+1)); log "[FAIL] $*"; }

curl_json(){
  local method="$1"; shift
  local url="$1"; shift
  if [[ -n "$ADMIN_TOKEN" ]]; then
    curl -sf -X "$method" -H "X-Admin-Token: $ADMIN_TOKEN" "$@" "$url"
  else
    curl -sf -X "$method" "$@" "$url"
  fi
}

: > "$LOG_FILE"
log "# v9.1.11 smoke"
log "date=$(date -Iseconds)"
log "api_base=$API_BASE"

log "[STEP] start stack"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml up -d --build >> "$LOG_FILE" 2>&1

log "[STEP] wait health"
for _ in $(seq 1 120); do
  if curl -sf "$API_BASE/health" >/dev/null; then break; fi
  sleep 1
done
if curl -sf "$API_BASE/health" >/dev/null; then ok "health"; else ko "health"; fi

log "[STEP] config/version"
if curl -sf "$API_BASE/config" > "$OUT_DIR/config.json"; then
  ver=$(python3 - <<'PY' "$OUT_DIR/config.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print((j.get('ui') or {}).get('version',''))
PY
)
  if [[ "$ver" == "v9.1.11" ]]; then ok "config ui.version=v9.1.11"; else ko "config ui.version expected v9.1.11 got $ver"; fi
else
  ko "config endpoint"
fi

log "[STEP] role separation in static UIs"
if curl -sf "$AGENT_UI_URL" > "$OUT_DIR/agent.html"; then
  if rg -q "Agent Settings ⚙︎|Agent Settings" "$OUT_DIR/agent.html"; then ok "agent has Agent Settings button"; else ko "agent missing Agent Settings button"; fi
  if rg -q "Admin token \\(optional\\)" "$OUT_DIR/agent.html"; then ko "agent still exposes admin token control"; else ok "agent does not expose admin token control"; fi
else
  ko "agent html fetch"
fi
if curl -sf "$ADMIN_UI_URL" > "$OUT_DIR/admin.html"; then
  if rg -q "adminHeaderSearchQuery" "$OUT_DIR/admin.html"; then ok "admin has unified header search"; else ko "admin missing header search"; fi
  if rg -q "adminHdrTotal" "$OUT_DIR/admin.html"; then ok "admin has perf header badges"; else ko "admin missing perf header badges"; fi
else
  ko "admin html fetch"
fi

log "[STEP] admin settings + search endpoints"
SET_PAYLOAD='{"user_id":"'"$ADMIN_USER_ID"'","perf_metrics_enabled":true,"search_max_results":42,"allow_text_regex_fallback":true,"default_backend":"ollama","default_model":"qwen2.5:3b"}'
if curl_json POST "$API_BASE/admin/settings" -H "Content-Type: application/json" -d "$SET_PAYLOAD" > "$OUT_DIR/admin-settings-set.json"; then
  ok "admin/settings POST"
else
  ko "admin/settings POST"
fi
if curl_json GET "$API_BASE/admin/settings?user_id=$ADMIN_USER_ID" > "$OUT_DIR/admin-settings-get.json"; then
  ok "admin/settings GET"
else
  ko "admin/settings GET"
fi

CHAT_PAYLOAD='{"text":"Wallbox smoke v9.1.11 fe774f alpha","user_id":"'"$CUSTOMER_USER_ID"'","session_id":"","backend":"ollama"}'
if curl_json POST "$API_BASE/chat/text" -H "Content-Type: application/json" -d "$CHAT_PAYLOAD" > "$OUT_DIR/chat.json"; then
  ok "chat/text"
else
  ko "chat/text"
fi
if curl_json GET "$API_BASE/admin/search?user_id=$ADMIN_USER_ID&q=fe774f*&mode=auto&since_days=7&limit=20" > "$OUT_DIR/admin-search.json"; then
  matches=$(python3 - <<'PY' "$OUT_DIR/admin-search.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print(len(j.get('matches') or []))
PY
)
  if [[ "$matches" -ge 1 ]]; then ok "admin/search matches=$matches"; else ko "admin/search no matches"; fi
else
  ko "admin/search request"
fi
if curl -sf "$API_BASE/agent/search?user_id=agenten-02&q=Wallbox&mode=text&since_days=7&limit=20" > "$OUT_DIR/agent-search.json"; then
  matches=$(python3 - <<'PY' "$OUT_DIR/agent-search.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print(len(j.get('matches') or []))
PY
)
  if [[ "$matches" -ge 1 ]]; then ok "agent/search matches=$matches"; else ko "agent/search no matches"; fi
else
  ko "agent/search request"
fi

log "[STEP] metrics summary endpoint"
if curl_json GET "$API_BASE/admin/metrics/summary?user_id=$ADMIN_USER_ID&window=10m" > "$OUT_DIR/admin-metrics-summary.json"; then
  ok "admin/metrics/summary"
else
  ko "admin/metrics/summary"
fi

log "[STEP] environment snapshot + docker logs"
{
  date -Iseconds
  echo "branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "commit=$(git rev-parse --short HEAD)"
  env | rg "VOICE|LANG|TTS|OLLAMA|OPENAI|MONGO|VALKEY|REDIS|RETENTION|UI_VERSION" || true
} > "$OUT_DIR/ENV_SNAPSHOT.txt"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color api > "$OUT_DIR/docker-logs-api.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-agent > "$OUT_DIR/docker-logs-web-agent.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-customer > "$OUT_DIR/docker-logs-web-customer.txt" 2>&1 || true

result="PASS"
if [[ "$fail" -gt 0 ]]; then result="FAIL"; fi

cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.11 Smoke Summary

- run_id: $RUN_ID
- date: $(date -Iseconds)
- result: **$result**
- passed: $pass
- failed: $fail

## Commands
- docker compose --project-directory "\$PWD" -f v9/docker/compose.dev.yml up -d --build
- curl -s $API_BASE/health
- bash scripts/run_v9_1_10_smoke.sh

## Artifacts
- $LOG_FILE
- $OUT_DIR/config.json
- $OUT_DIR/admin.html
- $OUT_DIR/agent.html
- $OUT_DIR/admin-search.json
- $OUT_DIR/agent-search.json
- $OUT_DIR/admin-metrics-summary.json
- $OUT_DIR/ENV_SNAPSHOT.txt
EOF_SUM

log "[RESULT] $result"
log "Artifacts: $OUT_DIR"

if [[ "$result" != "PASS" ]]; then
  exit 1
fi
