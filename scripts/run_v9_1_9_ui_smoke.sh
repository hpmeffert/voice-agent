#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="artifacts/v9.1.9/${RUN_ID}"
mkdir -p "$OUT_DIR"
LOG_FILE="$OUT_DIR/test-log-v9.1.9-ui-smoke.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"
LATEST_SUMMARY="artifacts/v9.1.9/SUMMARY.md"

API_BASE="${API_BASE:-http://localhost:8085/api}"
ADMIN_USER_ID="${ADMIN_USER_ID:-admin-user-v9-1-9}"
CUSTOMER_USER_ID="${CUSTOMER_USER_ID:-customer-user-v9-1-9}"
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
log "# v9.1.9 ui smoke"
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
  if [[ -n "$ver" ]]; then ok "config ui.version=$ver"; else ko "config missing ui.version"; fi
else
  ko "config endpoint"
fi

log "[STEP] admin settings roundtrip"
SET_PAYLOAD='{"user_id":"'"$ADMIN_USER_ID"'","perf_metrics_enabled":true,"search_max_results":42,"allow_text_regex_fallback":true,"default_backend":"ollama","default_model":"qwen2.5:3b"}'
if curl_json POST "$API_BASE/admin/settings" -H "Content-Type: application/json" -d "$SET_PAYLOAD" > "$OUT_DIR/admin-settings-set.json"; then
  ok "admin/settings POST"
else
  ko "admin/settings POST"
fi
if curl_json GET "$API_BASE/admin/settings?user_id=$ADMIN_USER_ID" > "$OUT_DIR/admin-settings-get.json"; then
  limit=$(python3 - <<'PY' "$OUT_DIR/admin-settings-get.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print(((j.get('settings') or {}).get('search_max_results',0)))
PY
)
  if [[ "$limit" == "42" ]]; then ok "admin/settings GET roundtrip"; else ko "admin/settings GET expected 42 got $limit"; fi
else
  ko "admin/settings GET"
fi

log "[STEP] seed conversation + admin search"
CHAT_PAYLOAD='{"text":"fe774f alpha test for unified search","user_id":"'"$CUSTOMER_USER_ID"'","session_id":"","backend":"ollama"}'
if curl_json POST "$API_BASE/chat/text" -H "Content-Type: application/json" -d "$CHAT_PAYLOAD" > "$OUT_DIR/chat.json"; then
  ok "chat/text"
else
  ko "chat/text"
fi
session_id=$(python3 - <<'PY' "$OUT_DIR/chat.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print(j.get('session_id',''))
PY
)
if [[ -n "$session_id" ]]; then
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
else
  ko "missing session id"
fi

log "[STEP] metrics summary numeric"
if curl_json GET "$API_BASE/admin/metrics/summary?user_id=$ADMIN_USER_ID&window=10m" > "$OUT_DIR/admin-metrics-summary.json"; then
  numeric=$(python3 - <<'PY' "$OUT_DIR/admin-metrics-summary.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
avg=j.get('avg_ms') or {}
p95=j.get('p95_ms') or {}
keys=['stt_ms','llm_ms','total_ms']
ok=all(isinstance(avg.get(k,0),(int,float)) and isinstance(p95.get(k,0),(int,float)) for k in keys)
print('1' if ok else '0')
PY
)
  if [[ "$numeric" == "1" ]]; then ok "metrics summary numeric avg+p95"; else ko "metrics summary invalid"; fi
else
  ko "metrics summary endpoint"
fi

result="PASS"
if [[ "$fail" -gt 0 ]]; then result="FAIL"; fi

cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.9 UI Smoke Summary

- run_id: $RUN_ID
- date: $(date -Iseconds)
- result: **$result**
- passed: $pass
- failed: $fail

## Files
- log: $LOG_FILE
- config: $OUT_DIR/config.json
- admin settings set/get: $OUT_DIR/admin-settings-set.json, $OUT_DIR/admin-settings-get.json
- admin search: $OUT_DIR/admin-search.json
- metrics summary: $OUT_DIR/admin-metrics-summary.json
EOF_SUM
cp -f "$SUMMARY_FILE" "$LATEST_SUMMARY"

log "[RESULT] $result"
log "Artifacts: $OUT_DIR"

if [[ "$result" != "PASS" ]]; then
  exit 1
fi
