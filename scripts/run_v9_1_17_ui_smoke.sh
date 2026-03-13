#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

TS="$(date -u +%Y%m%d-%H%M%S)"
RUN_ID="v9.1.17-ui-smoke-${TS}"
OUT_DIR="v9/artifacts/runs/${RUN_ID}"
mkdir -p "$OUT_DIR"
LOG_FILE="$OUT_DIR/test-log-v9.1.17-ui-smoke.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"
HTTP_LOG="$OUT_DIR/http_requests.log"
ENV_FILE="$OUT_DIR/ENV_SNAPSHOT.txt"

API_BASE="${API_BASE:-http://localhost:8085/api}"
ADMIN_UI_URL="${ADMIN_UI_URL:-http://localhost:8085}"
AGENT_UI_URL="${AGENT_UI_URL:-http://localhost:8087}"
CUSTOMER_UI_URL="${CUSTOMER_UI_URL:-http://localhost:8086}"
EXPECTED_VERSION="v9.1.17"
AGENT_LANG="en"
CUSTOMER_LANG="de"
AGENT_ID="agenten-02"
USER_ID="customer-ui-smoke-${TS}"
SESSION_ID="ui-smoke-session-${TS}"

pass=0
fail=0
log(){ printf "%s\n" "$*" | tee -a "$LOG_FILE"; }
ok(){ pass=$((pass+1)); log "[PASS] $*"; }
ko(){ fail=$((fail+1)); log "[FAIL] $*"; }
fetch_with_retry(){
  local url="$1"
  local out="$2"
  local attempts="${3:-5}"
  local max_time="${4:-15}"
  local i
  for i in $(seq 1 "$attempts"); do
    if curl -sf --max-time "$max_time" "$url" > "$out"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

: > "$LOG_FILE"
: > "$HTTP_LOG"

log "# v9.1.17 ui smoke"
log "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "api_base=$API_BASE"

for _ in $(seq 1 120); do
  if curl -sf --max-time 3 "$API_BASE/health" >/dev/null 2>&1 \
    && curl -sf --max-time 3 "${AGENT_UI_URL%/}/api/health" >/dev/null 2>&1 \
    && curl -sf --max-time 3 "${CUSTOMER_UI_URL%/}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if curl -sf --max-time 3 "$API_BASE/health" >/dev/null; then ok "admin api health"; else ko "admin api health"; fi
if curl -sf --max-time 3 "${AGENT_UI_URL%/}/api/health" >/dev/null; then ok "agent api health"; else ko "agent api health"; fi
if curl -sf --max-time 3 "${CUSTOMER_UI_URL%/}/api/health" >/dev/null; then ok "customer api health"; else ko "customer api health"; fi

if curl -sf --max-time 5 "$API_BASE/config" > "$OUT_DIR/config.json"; then
  ver=$(python3 - <<'PY' "$OUT_DIR/config.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
print((j.get('ui') or {}).get('version',''))
PY
)
  [[ "$ver" == "$EXPECTED_VERSION" ]] && ok "config ui.version=$EXPECTED_VERSION" || ko "config ui.version expected $EXPECTED_VERSION got $ver"
else
  ko "config endpoint"
fi

for page in admin agent customer; do
  case "$page" in
    admin) url="$ADMIN_UI_URL" ;;
    agent) url="$AGENT_UI_URL" ;;
    customer) url="$CUSTOMER_UI_URL" ;;
  esac
  if curl -sf --max-time 5 "$url" > "$OUT_DIR/${page}.html"; then
    if rg -q "$EXPECTED_VERSION" "$OUT_DIR/${page}.html"; then ok "$page header version visible"; else ko "$page header version missing"; fi
  else
    ko "$page html fetch"
  fi
done

chat_payload=$(printf '{"text":"Meine Wallbox blinkt rot. Was kann ich tun?","user_id":"%s","session_id":"%s","lang":"de","tts_lang":"de"}' "$USER_ID" "$SESSION_ID")
printf '[%s] POST %s/chat/text body=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$API_BASE" "$chat_payload" >> "$HTTP_LOG"
if curl -sf --max-time 30 -X POST "$API_BASE/chat/text" -H 'Content-Type: application/json' -d "$chat_payload" > "$OUT_DIR/chat.json"; then
  ok "chat/text"
else
  ko "chat/text"
fi

agent_payload=$(printf '{"session_id":"%s","agent_id":"%s","text":"Please check the breaker and restart the wallbox.","speak":false,"tts_lang":"de","agent_lang":"en"}' "$SESSION_ID" "$AGENT_ID")
printf '[%s] POST %s/agent/message body=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$API_BASE" "$agent_payload" >> "$HTTP_LOG"
if curl -sf --max-time 30 -X POST "$API_BASE/agent/message" -H 'Content-Type: application/json' -d "$agent_payload" > "$OUT_DIR/agent-message.json"; then
  ok "agent/message"
else
  ko "agent/message"
fi

if fetch_with_retry "$API_BASE/session/$SESSION_ID?user_id=$USER_ID&limit=20&agent_lang=$AGENT_LANG" "$OUT_DIR/session-chat.json" 6 15; then
  python3 - <<'PY' "$OUT_DIR/session-chat.json" > "$OUT_DIR/chat-check.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
msgs=j.get('messages') or []
customer=next((m for m in msgs if str(m.get('role','')).lower()=='customer'), {})
agent=next((m for m in reversed(msgs) if str(m.get('role','')).lower()=='agent'), {})
out={
  'customer_original': customer.get('text_original',''),
  'customer_agent_lane': customer.get('text_for_agent',''),
  'customer_agent_lang': customer.get('lang_for_agent',''),
  'agent_original': agent.get('text_original',''),
  'agent_agent_lane': agent.get('text_for_agent',''),
  'agent_agent_lang': agent.get('lang_for_agent',''),
  'agent_customer_lane': agent.get('text_for_customer',''),
}
print(json.dumps(out))
PY
  if python3 - <<'PY' "$OUT_DIR/chat-check.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
assert j['customer_original']
assert j['customer_agent_lane']
assert j['customer_agent_lang'] == 'en'
assert j['customer_original'] != j['customer_agent_lane']
assert j['agent_original']
assert j['agent_agent_lane']
assert j['agent_agent_lang'] == 'en'
assert j['agent_customer_lane']
PY
  then
    ok "chat history dual-lane customer+agent"
  else
    ko "chat history dual-lane customer+agent"
  fi
else
  ko "session history after chat"
fi

VOICE_STATUS="PASS"
python3 - <<'PY' "$OUT_DIR/voice_fixture_de.wav" >> "$HTTP_LOG" 2>&1 || VOICE_STATUS="FAIL"
import pathlib, requests, sys
wav_path = pathlib.Path(sys.argv[1])
resp = requests.post('http://localhost:5005/tts', json={'text':'Meine Wallbox laedt nicht mehr.', 'lang':'de'}, timeout=60)
resp.raise_for_status()
wav_path.write_bytes(resp.content)
print('voice_fixture_ready', wav_path.as_posix(), wav_path.stat().st_size)
PY

if [[ "$VOICE_STATUS" == "PASS" ]]; then
  python3 - <<'PY' "$API_BASE" "$OUT_DIR/voice_fixture_de.wav" "$USER_ID" "$SESSION_ID" >> "$HTTP_LOG" 2>&1 || VOICE_STATUS="FAIL"
import pathlib, requests, sys
api_base, wav_path, user_id, session_id = sys.argv[1:5]
with pathlib.Path(wav_path).open('rb') as fh:
    resp = requests.post(
        f"{api_base}/voice",
        data={
            'user_id': user_id,
            'session_id': session_id,
            'return_audio': '0',
            'customer_lang': 'de',
        },
        files={'file': ('voice_de.wav', fh, 'audio/wav')},
        timeout=180,
    )
print('voice_status_code', resp.status_code)
print('voice_body', resp.text[:400])
resp.raise_for_status()
PY
fi

if [[ "$VOICE_STATUS" != "PASS" ]]; then
  ko "voice request"
else
  ok "voice request"
  if fetch_with_retry "$API_BASE/session/$SESSION_ID?user_id=$USER_ID&limit=40&agent_lang=$AGENT_LANG" "$OUT_DIR/session-voice.json" 6 15; then
    if python3 - <<'PY' "$OUT_DIR/session-voice.json"
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
msgs=j.get('messages') or []
customers=[m for m in msgs if str(m.get('role','')).lower()=='customer']
agents=[m for m in msgs if str(m.get('role','')).lower()=='agent']
assert customers
assert agents
last_customer=customers[-1]
last_agent=agents[-1]
assert (last_customer.get('text_for_customer') or last_customer.get('text_original') or '').strip()
assert (last_agent.get('text_for_customer') or '').strip()
assert (last_agent.get('text_for_agent') or '').strip()
assert str(last_agent.get('lang_for_agent') or '').lower() == 'en'
PY
    then
      ok "voice history customer transcript + answer + agent lane"
    else
      ko "voice history customer transcript + answer + agent lane"
    fi
  else
    ko "session history after voice"
  fi
fi

{
  date -u +%Y-%m-%dT%H:%M:%SZ
  echo "branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "commit=$(git rev-parse --short HEAD)"
  env | rg "VOICE|LANG|TTS|OLLAMA|OPENAI|MONGO|VALKEY|REDIS|RETENTION|UI_VERSION|TEST_MODE" || true
} > "$ENV_FILE"

bash scripts/capture_logs.sh "$OUT_DIR" >> "$LOG_FILE" 2>&1 || true

RESULT="PASS"
[[ "$fail" -gt 0 ]] && RESULT="FAIL"
cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.17 UI Smoke Summary

- run_id: $RUN_ID
- date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- branch: $(git rev-parse --abbrev-ref HEAD)
- commit: $(git rev-parse --short HEAD)
- result: **$RESULT**
- passed: $pass
- failed: $fail
- licensing: no new runtime dependencies added; permissive OSS guardrails unchanged

## Commands
- bash scripts/check_no_artifacts_tracked.sh
- python3 v9/scripts/check_docs.py
- PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py
- bash scripts/run_v9_1_17_ui_smoke.sh

## Artifacts
- $LOG_FILE
- $HTTP_LOG
- $ENV_FILE
- $OUT_DIR/session-chat.json
- $OUT_DIR/session-voice.json
EOF_SUM

log "[RESULT] $RESULT"
log "Artifacts: $OUT_DIR"
[[ "$RESULT" == "PASS" ]]
