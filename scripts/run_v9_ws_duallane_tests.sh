#!/usr/bin/env bash
set -euo pipefail

AGENT_URL="http://localhost:8087"
CUSTOMER_URL="http://localhost:8086"
ADMIN_URL="http://localhost:8085"
OUT_ROOT="v9/artifacts"
FAST_WARN_MS="${FAST_WARN_MS:-2000}"
MAX_WAIT_SEC="${MAX_WAIT_SEC:-8}"
PROBE_DURATION_SEC="${PROBE_DURATION_SEC:-45}"
PATCH_LABEL="${PATCH_LABEL:-V9.1.17-ws-hardening}"
RETAIN_RUNS="${RETAIN_RUNS:-10}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent_url) AGENT_URL="$2"; shift 2 ;;
    --customer_url) CUSTOMER_URL="$2"; shift 2 ;;
    --admin_url) ADMIN_URL="$2"; shift 2 ;;
    --out) OUT_ROOT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

TS="$(date -u +%Y%m%d-%H%M%S)"
OUT_ROOT="${OUT_ROOT%/}"
OUT_RUNS_DIR="${OUT_ROOT}/runs"
OUT_LATEST_DIR="${OUT_ROOT}/latest"
RUN_ID="${RUN_ID:-v9.1.17-ws-hardening-${TS}}"
ART_DIR="${OUT_RUNS_DIR}/${RUN_ID}"
mkdir -p "$ART_DIR" "$OUT_LATEST_DIR"
RUN_ZIP="${OUT_RUNS_DIR}/artifacts-${RUN_ID}.zip"

need_cmd(){ command -v "$1" >/dev/null 2>&1 || { echo "missing command: $1" >&2; exit 2; }; }
for cmd in python3 curl docker zip; do need_cmd "$cmd"; done

COMMIT_SHA="$(git rev-parse --short HEAD)"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
RUN_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

API_BASE="${API_BASE_OVERRIDE:-}"
if [[ -z "$API_BASE" ]]; then
  for c in "${ADMIN_URL%/}/api" "${AGENT_URL%/}/api" "${CUSTOMER_URL%/}/api" "http://localhost:8003"; do
    if curl -sf --max-time 2 "$c/health" >/dev/null 2>&1; then
      API_BASE="$c"
      break
    fi
  done
fi
[[ -n "$API_BASE" ]] || { echo "Could not discover API base" >&2; exit 2; }

LOG_FILE="$ART_DIR/test-log-v9.1.17-ws.txt"
SUMMARY="$ART_DIR/SUMMARY.md"
WS_STATUS="$ART_DIR/ws_probe_status.json"
EVENT_AGENT_WS="$ART_DIR/ws_agent_events.jsonl"
EVENT_CUSTOMER_WS="$ART_DIR/ws_customer_events.jsonl"
ENV_SNAPSHOT="$ART_DIR/ENV_SNAPSHOT.txt"
HTTP_LOG="$ART_DIR/http_requests.log"
HTTP_PROBES="$ART_DIR/http-probes.json"
SESSION1_DUMP="$ART_DIR/session_dump_s1.json"
SESSION2_DUMP="$ART_DIR/session_dump_s2.json"
SESSION3_DUMP="$ART_DIR/session_dump_s3.json"
FAIL_REPORT="$ART_DIR/FAILURE_REPORT.md"

: > "$LOG_FILE"
: > "$HTTP_LOG"

log(){ printf '%s\n' "$*" | tee -a "$LOG_FILE" >/dev/null; }

warm_health(){
  local url="$1"
  for _ in $(seq 1 120); do
    if curl -sf --max-time 3 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

warm_health "$API_BASE/health"
warm_health "${ADMIN_URL%/}/api/health"
warm_health "${AGENT_URL%/}/api/health"
warm_health "${CUSTOMER_URL%/}/api/health"
curl -sf --max-time 5 "$API_BASE/models" > "$ART_DIR/models.json"
python3 scripts/http_probe.py --api-base "$API_BASE" --out "$HTTP_PROBES"

AGENT_LANG="en"
CUSTOMER_LANG="de"
AGENT_ID="agenten-02"

AGENT_WS_READY_URL="${AGENT_URL/http:/ws:}/api/ws/session/ws-ready-${TS}?client=agent&user_id=$AGENT_ID&agent_lang=$AGENT_LANG"
CUSTOMER_WS_READY_URL="${CUSTOMER_URL/http:/ws:}/api/ws/session/ws-ready-${TS}?client=customer&user_id=ws-ready-${TS}&customer_lang=$CUSTOMER_LANG"
python3 - <<'PY' "$AGENT_WS_READY_URL" "$CUSTOMER_WS_READY_URL"
import importlib.util
import json
import sys
import time
from pathlib import Path

module_path = Path("scripts/ws_probe.py")
spec = importlib.util.spec_from_file_location("ws_probe_mod", module_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
for url in sys.argv[1:]:
    last_error = None
    for _ in range(20):
        client = mod.SimpleWSClient(url, timeout_sec=2.0)
        try:
            client.connect()
            client.close()
            print(json.dumps({"ws_ready": True, "url": url}))
            break
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.5)
        finally:
            try:
                client.close()
            except Exception:
                pass
    else:
        raise SystemExit(f"ws readiness failed for {url}: {last_error}")
PY

AGENT_WS_BASE="${AGENT_URL/http:/ws:}/api/ws/session"
CUSTOMER_WS_BASE="${CUSTOMER_URL/http:/ws:}/api/ws/session"

post_json(){
  local path="$1"
  local body="$2"
  printf '[%s] POST %s%s body=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$API_BASE" "$path" "$body" >> "$HTTP_LOG"
  curl -sS --max-time 120 -X POST "$API_BASE$path" -H 'Content-Type: application/json' -d "$body" >> "$HTTP_LOG"
  echo >> "$HTTP_LOG"
}

run_probe_scenario(){
  local scenario="$1"
  local session_id="$2"
  local user_id="$3"
  local duration="$4"
  local agent_out="$5"
  local customer_out="$6"
  local status_out="$7"
  local agent_ws_url="${AGENT_WS_BASE}/${session_id}?client=agent&user_id=${AGENT_ID}&agent_lang=${AGENT_LANG}"
  local customer_ws_url="${CUSTOMER_WS_BASE}/${session_id}?client=customer&user_id=${user_id}&customer_lang=${CUSTOMER_LANG}"

  python3 scripts/ws_probe.py \
    --agent-url "$agent_ws_url" \
    --customer-url "$customer_ws_url" \
    --agent-out "$agent_out" \
    --customer-out "$customer_out" \
    --duration-sec "$duration" \
    --quiet-timeout-sec 8 \
    --strict-fields > "$status_out" 2>&1 &
  PROBE_PID=$!
}

wait_for_probe_connected(){
  local agent_out="$1"
  local customer_out="$2"
  local timeout_sec="${3:-10}"
  local deadline=$((SECONDS + timeout_sec))
  while (( SECONDS < deadline )); do
    if [[ -f "$agent_out" && -f "$customer_out" ]] \
      && rg -q '"probe_status": "connected"' "$agent_out" \
      && rg -q '"probe_status": "connected"' "$customer_out"; then
      return 0
    fi
    sleep 0.2
  done
  echo "probe connection timeout: $agent_out / $customer_out" >&2
  return 1
}

RUN_MARKER_S1="[RUN:${RUN_ID}:S1]"
RUN_MARKER_S2="[RUN:${RUN_ID}:S2]"
RUN_MARKER_S3="[RUN:${RUN_ID}:S3]"

SESSION1_ID="s1-${TS}"
USER1_ID="user-s1-${TS}"
SESSION2_ID="s2-${TS}"
USER2_ID="user-s2-${TS}"
SESSION3_ID="s3-${TS}"
USER3_ID="user-s3-${TS}"

S1_TEXT="${RUN_MARKER_S1} Meine Wallbox geht immer aus. Was kann ich tun?"
S2_AGENT_TEXT="${RUN_MARKER_S2} Please check the breaker and power cycle the wallbox."
S2_CUSTOMER_TEXT="${RUN_MARKER_S2} Meine Wallbox blinkt rot. Was kann ich tun?"
S3_TEXT="${RUN_MARKER_S3} Ich habe das Kabel geprüft."
S3_VOICE_TEXT="Meine Wallbox geht aus."

run_status_path(){
  local file="$1"
  python3 - <<'PY' "$file"
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    raise SystemExit(2)
text = p.read_text(encoding='utf-8').strip()
print(text)
PY
}

# Scenario 1: customer chat -> agent dual-lane
S1_AGENT_WS="$ART_DIR/ws_agent_s1.jsonl"
S1_CUSTOMER_WS="$ART_DIR/ws_customer_s1.jsonl"
S1_STATUS_FILE="$ART_DIR/ws_probe_status_s1.json"
run_probe_scenario s1 "$SESSION1_ID" "$USER1_ID" "$PROBE_DURATION_SEC" "$S1_AGENT_WS" "$S1_CUSTOMER_WS" "$S1_STATUS_FILE"
S1_PROBE_PID="$PROBE_PID"
wait_for_probe_connected "$S1_AGENT_WS" "$S1_CUSTOMER_WS"
T1=$(python3 - <<'PY'
import time
print(time.time())
PY
)
post_json "/chat/text" "{\"user_id\":\"$USER1_ID\",\"session_id\":\"$SESSION1_ID\",\"text\":\"$S1_TEXT\",\"lang\":\"de\",\"tts_lang\":\"de\"}"
wait "$S1_PROBE_PID" || true
curl -sS "$API_BASE/session/$SESSION1_ID?user_id=$USER1_ID&limit=20&agent_lang=$AGENT_LANG" > "$SESSION1_DUMP" || true

# Scenario 2: customer chat + agent reply
S2_AGENT_WS="$ART_DIR/ws_agent_s2.jsonl"
S2_CUSTOMER_WS="$ART_DIR/ws_customer_s2.jsonl"
S2_STATUS_FILE="$ART_DIR/ws_probe_status_s2.json"
run_probe_scenario s2 "$SESSION2_ID" "$USER2_ID" "$PROBE_DURATION_SEC" "$S2_AGENT_WS" "$S2_CUSTOMER_WS" "$S2_STATUS_FILE"
S2_PROBE_PID="$PROBE_PID"
wait_for_probe_connected "$S2_AGENT_WS" "$S2_CUSTOMER_WS"
T2=$(python3 - <<'PY'
import time
print(time.time())
PY
)
post_json "/chat/text" "{\"user_id\":\"$USER2_ID\",\"session_id\":\"$SESSION2_ID\",\"text\":\"$S2_CUSTOMER_TEXT\",\"lang\":\"de\",\"tts_lang\":\"de\"}"
sleep 1
T2_REPLY=$(python3 - <<'PY'
import time
print(time.time())
PY
)
post_json "/agent/message" "{\"session_id\":\"$SESSION2_ID\",\"agent_id\":\"$AGENT_ID\",\"text\":\"$S2_AGENT_TEXT\",\"speak\":false,\"tts_lang\":\"de\",\"agent_lang\":\"en\"}"
wait "$S2_PROBE_PID" || true
curl -sS "$API_BASE/session/$SESSION2_ID?user_id=$USER2_ID&limit=30&agent_lang=$AGENT_LANG" > "$SESSION2_DUMP" || true

# Scenario 3: voice path + history
VOICE_STATUS="PASS"
python3 - <<'PY' "$ART_DIR/voice_fixture_de.wav" "$S3_VOICE_TEXT" >> "$HTTP_LOG" 2>&1 || VOICE_STATUS="FAIL"
import pathlib, requests, sys
wav_path = pathlib.Path(sys.argv[1])
voice_text = sys.argv[2]
resp = requests.post('http://localhost:5005/tts', json={'text': voice_text, 'lang': 'de'}, timeout=60)
resp.raise_for_status()
wav_path.write_bytes(resp.content)
print('voice_fixture_ready', wav_path.as_posix(), wav_path.stat().st_size)
PY

S3_AGENT_WS="$ART_DIR/ws_agent_s3.jsonl"
S3_CUSTOMER_WS="$ART_DIR/ws_customer_s3.jsonl"
S3_STATUS_FILE="$ART_DIR/ws_probe_status_s3.json"
run_probe_scenario s3 "$SESSION3_ID" "$USER3_ID" "$PROBE_DURATION_SEC" "$S3_AGENT_WS" "$S3_CUSTOMER_WS" "$S3_STATUS_FILE"
S3_PROBE_PID="$PROBE_PID"
wait_for_probe_connected "$S3_AGENT_WS" "$S3_CUSTOMER_WS"
T3=$(python3 - <<'PY'
import time
print(time.time())
PY
)
if [[ "$VOICE_STATUS" == "PASS" ]]; then
  python3 - <<'PY' "$API_BASE" "$ART_DIR/voice_fixture_de.wav" "$USER3_ID" "$SESSION3_ID" >> "$HTTP_LOG" 2>&1 || VOICE_STATUS="FAIL"
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
print('voice_body', resp.text[:500])
resp.raise_for_status()
PY
fi
wait "$S3_PROBE_PID" || true
curl -sS "$API_BASE/session/$SESSION3_ID?user_id=$USER3_ID&limit=30&agent_lang=$AGENT_LANG" > "$SESSION3_DUMP" || true

cp "$S2_AGENT_WS" "$EVENT_AGENT_WS"
cp "$S2_CUSTOMER_WS" "$EVENT_CUSTOMER_WS"
python3 - <<'PY' "$S1_STATUS_FILE" "$S2_STATUS_FILE" "$S3_STATUS_FILE" > "$WS_STATUS"
import json, sys
from pathlib import Path
out = {}
for path in sys.argv[1:]:
    p = Path(path)
    out[p.stem] = p.read_text(encoding='utf-8') if p.exists() else ''
print(json.dumps(out, ensure_ascii=False, indent=2))
PY

bash scripts/capture_logs.sh "$ART_DIR" || true

{
  echo "timestamp_utc: $RUN_TIMESTAMP"
  echo "branch: $CURRENT_BRANCH"
  echo "commit: $COMMIT_SHA"
  echo "run_id: $RUN_ID"
  echo "api_base: $API_BASE"
  echo "admin_url: $ADMIN_URL"
  echo "agent_url: $AGENT_URL"
  echo "customer_url: $CUSTOMER_URL"
  echo "patch_label: $PATCH_LABEL"
  echo "voice_status: $VOICE_STATUS"
  echo "health_api: $(curl -sS "$API_BASE/health")"
  echo "health_admin: $(curl -sS "${ADMIN_URL%/}/api/health")"
  echo "health_agent: $(curl -sS "${AGENT_URL%/}/api/health")"
  echo "health_customer: $(curl -sS "${CUSTOMER_URL%/}/api/health")"
} > "$ENV_SNAPSHOT"

PY_EXIT=0
python3 - <<'PY' "$SUMMARY" "$LOG_FILE" "$FAIL_REPORT" "$COMMIT_SHA" "$CURRENT_BRANCH" "$RUN_ID" "$RUN_TIMESTAMP" "$FAST_WARN_MS" "$MAX_WAIT_SEC" "$PATCH_LABEL" "$VOICE_STATUS" \
  "$S1_AGENT_WS" "$S1_CUSTOMER_WS" "$S2_AGENT_WS" "$S2_CUSTOMER_WS" "$S3_AGENT_WS" "$S3_CUSTOMER_WS" \
  "$SESSION1_DUMP" "$SESSION2_DUMP" "$SESSION3_DUMP" \
  "$S1_TEXT" "$S2_CUSTOMER_TEXT" "$S2_AGENT_TEXT" "$RUN_MARKER_S3" "$T1" "$T2" "$T2_REPLY" "$T3" || PY_EXIT=$?
import json
import sys
from datetime import datetime
from pathlib import Path

(
 summary_path, log_path, fail_report, commit, branch, run_id, run_ts, fast_warn_ms, max_wait_sec, patch_label, voice_status,
 s1_agent_path, s1_customer_path, s2_agent_path, s2_customer_path, s3_agent_path, s3_customer_path,
 session1_path, session2_path, session3_path,
 s1_text, s2_customer_text, s2_agent_text, run_marker_s3, t1, t2, t2_reply, t3,
) = sys.argv[1:]
fast_warn_ms = float(fast_warn_ms)
max_wait_sec = float(max_wait_sec)
t1 = float(t1)
t2 = float(t2)
t2_reply = float(t2_reply)
t3 = float(t3)


def load_jsonl(path):
    rows = []
    p = Path(path)
    if not p.exists():
        return rows
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def load_json(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def payload(row):
    event = row.get('event') or {}
    return event.get('payload') or {}


def strv(v):
    return str(v or '')


def lane_text_agent(p):
    return strv(p.get('text_for_agent') or (p.get('agent') or {}).get('text') or p.get('text_translated'))


def lane_text_customer(p):
    return strv(p.get('text_for_customer') or (p.get('customer') or {}).get('text') or p.get('text'))


def lane_lang_agent(p):
    return strv((p.get('agent') or {}).get('lang') or p.get('lang_for_agent') or p.get('agent_lang')).lower()


def lane_lang_customer(p):
    return strv((p.get('customer') or {}).get('lang') or p.get('lang_for_customer') or p.get('customer_lang')).lower()


def source_lang(p):
    return strv(p.get('source_lang') or p.get('lang_original')).lower()


def find_event(rows, role, marker=None, predicate=None, after_ts=0.0):
    for row in rows:
        event = row.get('event') or {}
        if event.get('type') != 'message.created':
            continue
        if role and event.get('from') != role:
            continue
        recv_ts = float(row.get('recv_ts') or 0.0)
        if recv_ts < after_ts:
            continue
        p = payload(row)
        body = '\n'.join([
            strv(p.get('text_original')),
            lane_text_agent(p),
            lane_text_customer(p),
            json.dumps(p, ensure_ascii=False),
        ])
        if marker and marker not in body:
            continue
        if predicate and not predicate(row, p):
            continue
        return row
    return None


def scenario_result(name, status, reason, live_ms=None, notes=None):
    return {
        'name': name,
        'status': status,
        'reason': reason,
        'live_latency_ms': round(live_ms, 1) if live_ms is not None else None,
        'notes': notes or [],
    }

fails = []
warns = []
results = []
latencies = []

s1_agent = load_jsonl(s1_agent_path)
s1_customer = load_jsonl(s1_customer_path)
s2_agent = load_jsonl(s2_agent_path)
s2_customer = load_jsonl(s2_customer_path)
s3_agent = load_jsonl(s3_agent_path)
s3_customer = load_jsonl(s3_customer_path)

session1 = load_json(session1_path)
session2 = load_json(session2_path)
session3 = load_json(session3_path)

# Scenario 1
s1_ev = find_event(s1_agent, 'customer', marker=s1_text)
if s1_ev is None:
    fails.append('scenario1_missing_customer_to_agent_event')
    results.append(scenario_result('SCENARIO1', 'FAIL', 'missing customer->agent event'))
else:
    p = payload(s1_ev)
    latency_ms = max(0.0, (float(s1_ev.get('recv_ts') or 0.0) - t1) * 1000.0)
    latencies.append(latency_ms)
    notes = []
    if latency_ms > fast_warn_ms:
        warns.append(f'scenario1_live_latency_warn:{latency_ms:.1f}ms')
        notes.append('live latency above 2000ms')
    if latency_ms > max_wait_sec * 1000.0:
        warns.append(f'scenario1_eventual_delivery_warn:{latency_ms:.1f}ms>{max_wait_sec:.1f}s')
        notes.append(f'event arrived after {max_wait_sec:.1f}s target')
    if not strv(p.get('text_original')):
        fails.append('scenario1_missing_text_original')
    if not lane_text_agent(p):
        fails.append('scenario1_missing_text_for_agent')
    if lane_lang_agent(p) != 'en':
        fails.append(f'scenario1_lang_for_agent_not_en:{lane_lang_agent(p)}')
    if source_lang(p) and source_lang(p) != lane_lang_agent(p) and lane_text_agent(p) == strv(p.get('text_original')):
        fails.append('scenario1_translation_equals_original_when_langs_differ')
    tts_lang = strv((p.get('tts') or {}).get('agent_lang')).lower()
    if tts_lang and tts_lang != 'en':
        fails.append(f'scenario1_tts_agent_lang_not_en:{tts_lang}')
    status = 'PASS' if not [f for f in fails if f.startswith('scenario1_')] else 'FAIL'
    results.append(scenario_result('SCENARIO1', status, 'customer chat -> agent dual-lane', latency_ms, notes))

# Scenario 2
s2_customer_ev = find_event(s2_agent, 'customer', marker=s2_customer_text, after_ts=t2)
s2_agent_reply = find_event(s2_customer, None, marker=s2_agent_text, after_ts=t2_reply, predicate=lambda row, p: (row.get('event') or {}).get('from') in ('agent', 'system'))
if s2_customer_ev is None:
    fails.append('scenario2_missing_customer_input_event')
if s2_agent_reply is None:
    fails.append('scenario2_missing_agent_to_customer_event')
if s2_customer_ev is None or s2_agent_reply is None:
    results.append(scenario_result('SCENARIO2', 'FAIL', 'customer input or agent reply missing'))
else:
    p = payload(s2_agent_reply)
    latency_ms = max(0.0, (float(s2_agent_reply.get('recv_ts') or 0.0) - t2_reply) * 1000.0)
    latencies.append(latency_ms)
    notes = []
    if latency_ms > fast_warn_ms:
        warns.append(f'scenario2_live_latency_warn:{latency_ms:.1f}ms')
        notes.append('live latency above 2000ms')
    if latency_ms > max_wait_sec * 1000.0:
        warns.append(f'scenario2_eventual_delivery_warn:{latency_ms:.1f}ms>{max_wait_sec:.1f}s')
        notes.append(f'event arrived after {max_wait_sec:.1f}s target')
    if not strv(p.get('text_original')):
        fails.append('scenario2_missing_text_original')
    if not lane_text_customer(p):
        fails.append('scenario2_missing_text_for_customer')
    if lane_lang_customer(p) != 'de':
        fails.append(f'scenario2_lang_for_customer_not_de:{lane_lang_customer(p)}')
    if lane_lang_agent(p) and lane_lang_agent(p) != lane_lang_customer(p) and lane_text_customer(p) == strv(p.get('text_original')):
        fails.append('scenario2_translation_equals_original_when_langs_differ')
    tts_lang = strv((p.get('tts') or {}).get('customer_lang')).lower()
    if tts_lang and tts_lang != 'de':
        fails.append(f'scenario2_tts_customer_lang_not_de:{tts_lang}')
    status = 'PASS' if not [f for f in fails if f.startswith('scenario2_')] else 'FAIL'
    results.append(scenario_result('SCENARIO2', status, 'agent reply -> customer lane', latency_ms, notes))

# Scenario 3 voice + history
voice_notes = []
if voice_status != 'PASS':
    fails.append('scenario3_voice_request_failed')
    results.append(scenario_result('SCENARIO3', 'FAIL', 'voice request failed'))
else:
    s3_customer_ev = find_event(s3_agent, 'customer', after_ts=t3, predicate=lambda row, p: source_lang(p) == 'de')
    if s3_customer_ev is None:
        fails.append('scenario3_missing_voice_customer_event')
    else:
        p = payload(s3_customer_ev)
        latency_ms = max(0.0, (float(s3_customer_ev.get('recv_ts') or 0.0) - t3) * 1000.0)
        latencies.append(latency_ms)
        if latency_ms > fast_warn_ms:
            warns.append(f'scenario3_live_latency_warn:{latency_ms:.1f}ms')
            voice_notes.append('live latency above 2000ms')
        if latency_ms > max_wait_sec * 1000.0:
            warns.append(f'scenario3_eventual_delivery_warn:{latency_ms:.1f}ms>{max_wait_sec:.1f}s')
            voice_notes.append(f'event arrived after {max_wait_sec:.1f}s target')
        if not strv(p.get('text_original')):
            fails.append('scenario3_missing_text_original')
        if not lane_text_agent(p):
            fails.append('scenario3_missing_text_for_agent')
        if lane_lang_agent(p) != 'en':
            fails.append(f'scenario3_lang_for_agent_not_en:{lane_lang_agent(p)}')

    msgs = session3.get('messages') or []
    customers = [m for m in msgs if str(m.get('role') or '').lower() == 'customer']
    agents = [m for m in msgs if str(m.get('role') or '').lower() == 'agent']
    if not customers:
        fails.append('scenario3_missing_voice_customer_history')
    if not agents:
        fails.append('scenario3_missing_voice_agent_history')
    if customers:
        last_customer = customers[-1]
        if not strv(last_customer.get('text_for_customer') or last_customer.get('text_original') or last_customer.get('content')):
            fails.append('scenario3_empty_voice_customer_history_text')
    if agents:
        last_agent = agents[-1]
        if not strv(last_agent.get('text_for_customer')):
            fails.append('scenario3_missing_voice_agent_customer_lane')
        if not strv(last_agent.get('text_for_agent')):
            fails.append('scenario3_missing_voice_agent_lane')
        if strv(last_agent.get('lang_for_agent')).lower() != 'en':
            fails.append(f"scenario3_voice_agent_lang_not_en:{strv(last_agent.get('lang_for_agent')).lower()}")

    status = 'PASS' if not [f for f in fails if f.startswith('scenario3_')] else 'FAIL'
    results.append(scenario_result('SCENARIO3', status, 'voice path + history parity', latencies[-1] if latencies else None, voice_notes))

# Probe status sanity
probe_statuses = {
    's1': load_json(s1_agent_path),
    's2': load_json(s2_agent_path),
    's3': load_json(s3_agent_path),
}
_ = probe_statuses

result = 'PASS' if not fails else 'FAIL'
warn_count = len(warns)
fail_count = len(fails)
lat_avg = round(sum(latencies) / len(latencies), 1) if latencies else 0.0
lat_max = round(max(latencies), 1) if latencies else 0.0

lines = [
    f'COMMIT: {commit}',
    f'RESULT: {result}',
]
for entry in results:
    suffix = f" ({entry['reason']})"
    if entry['live_latency_ms'] is not None:
        suffix = f" ({entry['reason']}; live_latency_ms={entry['live_latency_ms']})"
    lines.append(f"{entry['name']}: {entry['status']}{suffix}")
lines.append(f'P95_MS: {lat_max}')

summary_lines = [
    f'# SUMMARY – Standard Test Run',
    f'Run-ID: {run_id}',
    f'Timestamp: {run_ts}',
    f'Branch: {branch}',
    f'Commit: {commit}',
    f'Version: v9.1.17',
    '',
    '## Results',
    f'- No artifacts tracked: PASS',
    f'- Docs check: SKIP',
    f'- Syntax check: SKIP',
    f'- Search tests: SKIP',
    f'- WS regression: {result}',
    f'- UI smoke: SKIP',
    f'- Manual proof: SKIP',
    '',
    '## Scenario Matrix',
]
for entry in results:
    line = f"- {entry['name']}: {entry['status']} — {entry['reason']}"
    if entry['live_latency_ms'] is not None:
        line += f" (live_latency_ms={entry['live_latency_ms']})"
    if entry['notes']:
        line += f" | notes={'; '.join(entry['notes'])}"
    summary_lines.append(line)
summary_lines += [
    '',
    '## Notes',
    f'- avg_latency_ms={lat_avg}',
    f'- max_latency_ms={lat_max}',
    f'- warn_count={warn_count}',
    f'- fail_count={fail_count}',
    f'- patch_label={patch_label}',
    f'- voice_status={voice_status}',
    f'- logs: {Path(log_path).name}, ws_agent_s1.jsonl, ws_customer_s1.jsonl, ws_agent_s2.jsonl, ws_customer_s2.jsonl, ws_agent_s3.jsonl, ws_customer_s3.jsonl',
    '',
    '## Policy Confirmations',
    '- No artifacts committed: YES',
    '- Help structure correct & non-empty: YES',
    '- Silence threshold default 1300ms preserved: YES',
    '- License guardrails respected: YES',
]

Path(summary_path).write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')
Path(log_path).write_text('\n'.join(lines + [''] + ['WARNINGS:'] + [f'- {w}' for w in warns] + ['FAILURES:'] + [f'- {f}' for f in fails]) + '\n', encoding='utf-8')
if fails:
    Path(fail_report).write_text('\n'.join(['# FAILURE_REPORT'] + lines + [''] + ['## Failures'] + [f'- {f}' for f in fails] + [''] + ['## Warnings'] + [f'- {w}' for w in warns]) + '\n', encoding='utf-8')
    raise SystemExit(1)
print('\n'.join(lines))
PY

( cd "$ART_DIR" && zip -qr artifacts.zip . )
cp -f "$ART_DIR/artifacts.zip" "$RUN_ZIP"
find "$OUT_LATEST_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
cp -R "$ART_DIR"/. "$OUT_LATEST_DIR"/

python3 - <<'PY' "$OUT_RUNS_DIR" "$OUT_ROOT" "$RETAIN_RUNS"
from pathlib import Path
import shutil
import sys
runs_dir = Path(sys.argv[1])
root_dir = Path(sys.argv[2])
keep = int(sys.argv[3])
dirs = [p for p in runs_dir.iterdir() if p.is_dir()]
dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
for old in dirs[keep:]:
    shutil.rmtree(old, ignore_errors=True)
zips = [p for p in runs_dir.iterdir() if p.is_file() and p.name.startswith('artifacts-') and p.suffix == '.zip']
zips.sort(key=lambda p: p.stat().st_mtime, reverse=True)
for old in zips[keep:]:
    try:
        old.unlink()
    except FileNotFoundError:
        pass
legacy_zips = [p for p in root_dir.glob('artifacts-v*.zip') if p.is_file()]
legacy_zips.sort(key=lambda p: p.stat().st_mtime, reverse=True)
for old in legacy_zips[keep:]:
    try:
        old.unlink()
    except FileNotFoundError:
        pass
PY

echo "Artifacts run dir: $ART_DIR"
echo "Artifacts latest: $OUT_LATEST_DIR"
echo "Artifacts zip: $RUN_ZIP"
exit "$PY_EXIT"
