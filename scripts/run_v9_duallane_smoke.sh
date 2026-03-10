#!/usr/bin/env bash
set -euo pipefail

TS="$(date -u +%Y%m%dT%H%M%SZ)"
ART_DIR="artifacts/v9_duallane_run_${TS}"
mkdir -p "$ART_DIR"

AGENT_BASE="http://localhost:8087"
CUSTOMER_BASE="http://localhost:8086"
API_BASE=""
for c in "http://localhost:8085/api" "http://localhost:8080/api"; do
  if curl -sf --max-time 2 "$c/health" >/dev/null 2>&1; then
    API_BASE="$c"
    break
  fi
done
if [[ -z "$API_BASE" ]]; then
  echo "No reachable API base (tried :8085/api and :8080/api)" >&2
  exit 2
fi

USER_ID="test-user-1"
SESSION_ID="test-session-1"
AGENT_ID="agenten-02"
AGENT_LANG="en"
CUSTOMER_LANG="de"

WS_AGENT_FILE="$ART_DIR/ws_agent_events.jsonl"
WS_CUSTOMER_FILE="$ART_DIR/ws_customer_events.jsonl"
HTTP_LOG="$ART_DIR/http_requests.log"
SUMMARY="$ART_DIR/SUMMARY.md"
SESSION_DUMP="$ART_DIR/session_dump.json"
ENV_SNAPSHOT="$ART_DIR/ENV_SNAPSHOT.txt"

: > "$HTTP_LOG"

log_http() {
  printf "\n[%s] %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$HTTP_LOG"
}

api_post_json() {
  local path="$1"; shift
  local body="$1"; shift
  log_http "POST $API_BASE$path body=$body"
  curl -sS --max-time 90 -X POST "$API_BASE$path" -H 'Content-Type: application/json' -d "$body" | tee -a "$HTTP_LOG"
}

api_get() {
  local path="$1"; shift
  log_http "GET $API_BASE$path"
  curl -sS --max-time 30 "$API_BASE$path" | tee -a "$HTTP_LOG"
}

for _ in $(seq 1 120); do
  if curl -sf --max-time 2 "$API_BASE/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -sf --max-time 2 "$API_BASE/health" >/dev/null

{
  echo "timestamp_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "agent_base: $AGENT_BASE"
  echo "customer_base: $CUSTOMER_BASE"
  echo "api_base: $API_BASE"
  echo "user_id: $USER_ID"
  echo "session_id: $SESSION_ID"
  echo "agent_id: $AGENT_ID"
  echo "agent_lang: $AGENT_LANG"
  echo "customer_lang: $CUSTOMER_LANG"
  echo "version_health: $(curl -sS --max-time 5 "$API_BASE/health")"
  echo "config: $(curl -sS --max-time 10 "$API_BASE/config?user_id=$USER_ID")"
  echo "models: $(curl -sS --max-time 10 "$API_BASE/models" | head -c 600)"
} > "$ENV_SNAPSHOT"

AGENT_WS_URL="ws://localhost:8087/api/ws/session/${SESSION_ID}?client=agent&user_id=${AGENT_ID}&agent_lang=${AGENT_LANG}"
CUSTOMER_WS_URL="ws://localhost:8086/api/ws/session/${SESSION_ID}?client=customer&user_id=${USER_ID}&customer_lang=${CUSTOMER_LANG}"

python3 scripts/ws_probe.py \
  --agent-url "$AGENT_WS_URL" \
  --customer-url "$CUSTOMER_WS_URL" \
  --agent-out "$WS_AGENT_FILE" \
  --customer-out "$WS_CUSTOMER_FILE" \
  --duration-sec 16 \
  --quiet-timeout-sec 4 \
  --strict-fields > "$ART_DIR/ws_probe_status.json" 2>&1 &
PROBE_PID=$!

sleep 1

# Case 1: Customer DE -> Agent EN
T1=$(python3 - <<'PY'
import time
print(time.time())
PY)
api_post_json "/chat/text" "{\"user_id\":\"${USER_ID}\",\"session_id\":\"${SESSION_ID}\",\"text\":\"Meine Wallbox geht immer aus. Was kann ich tun?\",\"lang\":\"de\",\"tts_lang\":\"de\"}" >/dev/null

# Case 2: Agent EN -> Customer DE
api_post_json "/agent/message" "{\"session_id\":\"${SESSION_ID}\",\"agent_id\":\"${AGENT_ID}\",\"text\":\"Please check the breaker and power cycle the wallbox.\",\"speak\":false,\"tts_lang\":\"de\",\"agent_lang\":\"en\"}" >/dev/null

# Case 3: Customer text input produces answer
api_post_json "/chat/text" "{\"user_id\":\"${USER_ID}\",\"session_id\":\"${SESSION_ID}\",\"text\":\"Ich habe das Kabel geprüft.\",\"lang\":\"de\",\"tts_lang\":\"de\"}" >/dev/null

wait "$PROBE_PID" || true

api_get "/session/${SESSION_ID}?user_id=${USER_ID}&limit=20" > "$SESSION_DUMP"

docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml logs --tail=300 api > "$ART_DIR/docker-api.log" || true
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml logs --tail=200 web-agent > "$ART_DIR/docker-web-agent.log" || true
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml logs --tail=200 web-customer > "$ART_DIR/docker-web-customer.log" || true

python3 - <<PY
import json
from pathlib import Path
from datetime import datetime, timezone

agent_path = Path("$WS_AGENT_FILE")
customer_path = Path("$WS_CUSTOMER_FILE")
summary_path = Path("$SUMMARY")
inject_t1 = float("$T1")


def load(p):
    out=[]
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            line=line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

agent = load(agent_path)
customer = load(customer_path)

fails=[]
passes=[]

case1 = [e for e in agent if isinstance(e.get('event'), dict) and e['event'].get('type')=='message.created' and e['event'].get('from')=='customer']
if not case1:
    fails.append('Case1: missing customer->agent WS message.created')
else:
    ev = case1[0]
    recv_ts = float(ev.get('recv_ts', 0))
    payload = (ev.get('event') or {}).get('payload') or {}
    agent_lane = payload.get('agent') or {}
    if recv_ts - inject_t1 > 2.5:
        fails.append(f'Case1: delivery too slow ({recv_ts-inject_t1:.3f}s > 2.5s)')
    if not payload.get('text_original'):
        fails.append('Case1: missing text_original')
    if (agent_lane.get('lang') or payload.get('agent_lang')) != 'en':
        fails.append('Case1: lang_for_agent is not en')
    if not (agent_lane.get('text') or payload.get('text_translated') or ''):
        fails.append('Case1: missing text_for_agent/text_translated')
    tts = payload.get('tts') or {}
    if tts.get('agent_lang') and tts.get('agent_lang') != 'en':
        fails.append('Case1: tts_lang_for_agent mismatch (expected en)')
    if not any('Case1' in x for x in fails):
        passes.append('Case1 PASS')

case2 = [e for e in customer if isinstance(e.get('event'), dict) and e['event'].get('type')=='message.created' and e['event'].get('from')=='agent']
if not case2:
    fails.append('Case2: missing agent->customer WS message.created')
else:
    ev = case2[0]
    payload = (ev.get('event') or {}).get('payload') or {}
    lane = payload.get('customer') or {}
    if (lane.get('lang') or payload.get('customer_lang')) != 'de':
        fails.append('Case2: lang_for_customer is not de')
    if not (lane.get('text') or payload.get('text') or ''):
        fails.append('Case2: missing text_for_customer')
    tts = payload.get('tts') or {}
    if tts.get('customer_lang') and tts.get('customer_lang') != 'de':
        fails.append('Case2: tts_lang_for_customer mismatch (expected de)')
    if not any('Case2' in x for x in fails):
        passes.append('Case2 PASS')

case3_customer = [e for e in agent if isinstance(e.get('event'), dict) and e['event'].get('type')=='message.created' and e['event'].get('from')=='customer' and 'Ich habe das Kabel geprüft' in json.dumps((e.get('event') or {}).get('payload') or {}, ensure_ascii=False)]
case3_agent = [e for e in customer if isinstance(e.get('event'), dict) and e['event'].get('type')=='message.created' and e['event'].get('from')=='agent']
if not case3_customer:
    fails.append('Case3: no new customer text event visible on agent WS')
if not case3_agent:
    fails.append('Case3: no agent answer routed to customer WS')
if case3_customer and case3_agent:
    passes.append('Case3 PASS')

status = 'PASS' if not fails else 'FAIL'
lines = []
lines.append(f'# V9 Dual-Lane Smoke Summary ({status})')
lines.append('')
lines.append(f'- generated_at_utc: {datetime.now(timezone.utc).isoformat()}')
lines.append(f'- session_id: {"$SESSION_ID"}')
lines.append(f'- user_id: {"$USER_ID"}')
lines.append(f'- agent_id: {"$AGENT_ID"}')
lines.append('')
if passes:
    lines.append('## Passed')
    for p in passes:
        lines.append(f'- {p}')
    lines.append('')
if fails:
    lines.append('## Failed')
    for f in fails:
        lines.append(f'- {f}')
    lines.append('')

summary_path.write_text('\n'.join(lines), encoding='utf-8')
print(status)
if fails:
    raise SystemExit(1)
PY

cat > "$ART_DIR/BROWSER_CHECKLIST.md" <<'MD'
# 2-Minute Browser Checklist

1. Agent UI: `http://localhost:8087` (`agent_lang=en`).
2. Customer UI: `http://localhost:8086` (`customer_lang=de`).
3. Customer sends German text.
   - Agent sees live event without reload.
   - Agent lane text is English.
4. Agent sends English text.
   - Customer lane text is German.
5. Customer sends second text.
   - Agent receives live event + customer receives routed answer.
MD

echo "Artifacts: $ART_DIR"
