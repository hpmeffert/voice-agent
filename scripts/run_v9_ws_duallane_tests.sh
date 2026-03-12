#!/usr/bin/env bash
set -euo pipefail

AGENT_URL="http://localhost:8087"
CUSTOMER_URL="http://localhost:8086"
OUT_ROOT="v9/artifacts"
FAST_SEC="${FAST_SEC:-2}"
EVENTUAL_SEC="${EVENTUAL_SEC:-20}"
ANSWER_EVENTUAL_SEC="${ANSWER_EVENTUAL_SEC:-45}"
PROBE_DURATION_SEC="${PROBE_DURATION_SEC:-120}"
PATCH_LABEL="${PATCH_LABEL:-V9.1.5-fix-voice-duallane}"
RETAIN_RUNS="${RETAIN_RUNS:-10}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent_url) AGENT_URL="$2"; shift 2 ;;
    --customer_url) CUSTOMER_URL="$2"; shift 2 ;;
    --out) OUT_ROOT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

TS="$(date -u +%Y%m%d-%H%M%S)"
OUT_ROOT="${OUT_ROOT%/}"
OUT_RUNS_DIR="${OUT_ROOT}/runs"
OUT_LATEST_DIR="${OUT_ROOT}/latest"
RUN_ID="${RUN_ID:-v9.1.5-${TS}}"
ART_DIR="${OUT_RUNS_DIR}/${RUN_ID}"
RUN_ZIP="${OUT_RUNS_DIR}/artifacts-${RUN_ID}.zip"
mkdir -p "$ART_DIR" "$OUT_LATEST_DIR"

AGENT_WS_BASE="${AGENT_URL/http:/ws:}/api/ws/session"
CUSTOMER_WS_BASE="${CUSTOMER_URL/http:/ws:}/api/ws/session"

API_BASE=""
if [[ -n "${API_BASE_OVERRIDE:-}" ]]; then
  API_BASE="$API_BASE_OVERRIDE"
else
  for c in "${AGENT_URL%/}/api" "${CUSTOMER_URL%/}/api" "http://localhost:8003" "http://localhost:8085/api" "http://localhost:8080/api"; do
    [[ -z "$c" ]] && continue
    if curl -sf --max-time 2 "$c/health" >/dev/null 2>&1; then
      API_BASE="$c"
      break
    fi
  done
fi
if [[ -z "$API_BASE" ]]; then
  echo "Could not discover API base" >&2
  exit 2
fi

COMMIT_SHA="$(git rev-parse --short HEAD)"

LOG_FILE="$ART_DIR/test-log-v9.1.15-p1-ws.txt"
EVENT_AGENT_WS="$ART_DIR/ws_agent_events.jsonl"
EVENT_CUSTOMER_WS="$ART_DIR/ws_customer_events.jsonl"
EVENT_AGENT="$ART_DIR/events-agent.jsonl"
EVENT_CUSTOMER="$ART_DIR/events-customer.jsonl"
HTTP_PROBES="$ART_DIR/http-probes.json"
SESSION_DUMP="$ART_DIR/session_dump.json"
ENV_SNAPSHOT="$ART_DIR/ENV_SNAPSHOT.txt"
WS_STATUS="$ART_DIR/ws_probe_status.json"
SUMMARY="$ART_DIR/SUMMARY.md"
HTTP_LOG="$ART_DIR/http_requests.log"
FAIL_REPORT="$ART_DIR/FAILURE_REPORT.md"

: > "$LOG_FILE"
: > "$HTTP_LOG"

need_cmd(){ command -v "$1" >/dev/null 2>&1 || { echo "missing command: $1"; exit 2; }; }
need_cmd python3
need_cmd curl
need_cmd docker
need_cmd zip

for _ in $(seq 1 120); do
  if \
    curl -sf "$API_BASE/health" >/dev/null 2>&1 && \
    curl -sf "${AGENT_URL%/}/api/health" >/dev/null 2>&1 && \
    curl -sf "${CUSTOMER_URL%/}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -sf "$API_BASE/health" >/dev/null

USER_ID="test-user-${TS}"
SESSION_ID="test-session-${TS}"
AGENT_ID="agenten-02"
AGENT_LANG="en"
CUSTOMER_LANG="de"

{
  echo "timestamp_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "commit: $COMMIT_SHA"
  echo "agent_url: $AGENT_URL"
  echo "customer_url: $CUSTOMER_URL"
  echo "api_base: $API_BASE"
  echo "user_id: $USER_ID"
  echo "session_id: $SESSION_ID"
  echo "agent_id: $AGENT_ID"
  echo "agent_lang: $AGENT_LANG"
  echo "customer_lang: $CUSTOMER_LANG"
  echo "patch_label: $PATCH_LABEL"
  echo "health: $(curl -sS "$API_BASE/health")"
  echo "models: $(curl -sS "$API_BASE/models" | head -c 800)"
  echo "config: $(curl -sS "$API_BASE/config?user_id=$USER_ID")"
} > "$ENV_SNAPSHOT"

python3 scripts/http_probe.py --api-base "$API_BASE" --out "$HTTP_PROBES"

post_json(){
  local path="$1"; shift
  local body="$1"; shift
  printf "[%s] POST %s%s body=%s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$API_BASE" "$path" "$body" >> "$HTTP_LOG"
  curl -sS --max-time 90 -X POST "$API_BASE$path" -H 'Content-Type: application/json' -d "$body" >> "$HTTP_LOG"
  echo >> "$HTTP_LOG"
}

AGENT_WS_URL="$AGENT_WS_BASE/$SESSION_ID?client=agent&user_id=$AGENT_ID&agent_lang=$AGENT_LANG"
CUSTOMER_WS_URL="$CUSTOMER_WS_BASE/$SESSION_ID?client=customer&user_id=$USER_ID&customer_lang=$CUSTOMER_LANG"

python3 scripts/ws_probe.py \
  --agent-url "$AGENT_WS_URL" \
  --customer-url "$CUSTOMER_WS_URL" \
  --agent-out "$EVENT_AGENT_WS" \
  --customer-out "$EVENT_CUSTOMER_WS" \
  --duration-sec "$PROBE_DURATION_SEC" \
  --quiet-timeout-sec 8 \
  --strict-fields > "$WS_STATUS" 2>&1 &
PROBE_PID=$!

sleep 1
T1=$(python3 - <<'PY'
import time
print(time.time())
PY)
SCENARIO1_TEXT="Meine Wallbox geht immer aus. Was kann ich tun?"
post_json "/chat/text" "{\"user_id\":\"$USER_ID\",\"session_id\":\"$SESSION_ID\",\"text\":\"$SCENARIO1_TEXT\",\"lang\":\"de\",\"tts_lang\":\"de\"}"

T2=$(python3 - <<'PY'
import time
print(time.time())
PY)
SCENARIO2_TEXT="Please check the breaker and power cycle the wallbox."
post_json "/agent/message" "{\"session_id\":\"$SESSION_ID\",\"agent_id\":\"$AGENT_ID\",\"text\":\"$SCENARIO2_TEXT\",\"speak\":false,\"tts_lang\":\"de\",\"agent_lang\":\"en\"}"

T3=$(python3 - <<'PY'
import time
print(time.time())
PY)
SCENARIO3_TEXT="Ich habe das Kabel geprüft."
post_json "/chat/text" "{\"user_id\":\"$USER_ID\",\"session_id\":\"$SESSION_ID\",\"text\":\"$SCENARIO3_TEXT\",\"lang\":\"de\",\"tts_lang\":\"de\"}"

SCENARIO4_TEXT="Meine Wallbox geht aus."
VOICE_STATUS="PASS"
python3 - <<PY >> "$HTTP_LOG" 2>&1 || VOICE_STATUS="FAIL"
import requests, pathlib
voice_text = "$SCENARIO4_TEXT"
art_dir = pathlib.Path("$ART_DIR")
wav_path = art_dir / "voice_fixture_de.wav"
tts = requests.post("http://localhost:5005/tts", json={"text": voice_text, "lang": "de"}, timeout=60)
tts.raise_for_status()
wav_path.write_bytes(tts.content)
print("voice_fixture_ready", wav_path.as_posix(), wav_path.stat().st_size)
PY

T4=$(python3 - <<'PY'
import time
print(time.time())
PY)

python3 - <<PY >> "$HTTP_LOG" 2>&1 || VOICE_STATUS="FAIL"
import requests, pathlib
api_base = "$API_BASE"
wav_path = pathlib.Path("$ART_DIR/voice_fixture_de.wav")
with wav_path.open("rb") as fh:
    resp = requests.post(
        f"{api_base}/voice",
        data={
            "user_id": "$USER_ID",
            "session_id": "$SESSION_ID",
            "return_audio": "0",
            "customer_lang": "de",
        },
        files={"file": ("voice_de.wav", fh, "audio/wav")},
        timeout=180,
    )
print("voice_status_code", resp.status_code)
print("voice_headers_x_detected_lang", resp.headers.get("X-Detected-Lang", ""))
print("voice_body_sample", resp.text[:500])
resp.raise_for_status()
PY

wait "$PROBE_PID" || true

cp "$EVENT_AGENT_WS" "$EVENT_AGENT" 2>/dev/null || :
cp "$EVENT_CUSTOMER_WS" "$EVENT_CUSTOMER" 2>/dev/null || :

curl -sS "$API_BASE/session/$SESSION_ID?user_id=$USER_ID&limit=30&agent_lang=$AGENT_LANG" > "$SESSION_DUMP" || true
bash scripts/capture_logs.sh "$ART_DIR" || true
cp "$ART_DIR/docker-logs-api.txt" "$ART_DIR/docker-api.log" 2>/dev/null || true
cp "$ART_DIR/docker-logs-web-agent.txt" "$ART_DIR/docker-web-agent.log" 2>/dev/null || true
cp "$ART_DIR/docker-logs-web-customer.txt" "$ART_DIR/docker-web-customer.log" 2>/dev/null || true

PY_EXIT=0
python3 - <<PY || PY_EXIT=$?
import json
from pathlib import Path
from datetime import datetime, timezone

commit = "$COMMIT_SHA"
summary_path = Path("$SUMMARY")
log_path = Path("$LOG_FILE")

agent_file = Path("$EVENT_AGENT")
customer_file = Path("$EVENT_CUSTOMER")

T1 = float("$T1")
T2 = float("$T2")
T3 = float("$T3")
T4 = float("$T4")
S1 = "$SCENARIO1_TEXT"
S2 = "$SCENARIO2_TEXT"
S3 = "$SCENARIO3_TEXT"
S4 = "$SCENARIO4_TEXT"
VOICE_STATUS = "$VOICE_STATUS"
FAST_SEC = float("$FAST_SEC")
EVENTUAL_SEC = float("$EVENTUAL_SEC")
ANSWER_EVENTUAL_SEC = float("$ANSWER_EVENTUAL_SEC")
PATCH_LABEL = "$PATCH_LABEL"


def load(p):
    arr=[]
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            line=line.strip()
            if not line:
                continue
            try:
                arr.append(json.loads(line))
            except Exception:
                pass
    return arr

agent=load(agent_file)
customer=load(customer_file)
try:
    session_dump = json.loads(Path("$SESSION_DUMP").read_text(encoding="utf-8")) if Path("$SESSION_DUMP").exists() else {}
except Exception:
    session_dump = {}

fails=[]
warns=[]

# transport p95 = recv_ts - server event ts for message.created
lat=[]
for src in (agent, customer):
    for row in src:
        e=row.get("event")
        if not isinstance(e, dict) or e.get("type") != "message.created":
            continue
        ts=e.get("ts")
        recv=row.get("recv_ts")
        if not ts or recv is None:
            continue
        try:
            from datetime import datetime
            s=datetime.fromisoformat(str(ts).replace("Z","+00:00")).timestamp()
            d=float(recv)-s
            if d >= 0:
                lat.append(d)
        except Exception:
            pass
p95_ms=0
if lat:
    lat=sorted(lat)
    idx=int(0.95*(len(lat)-1))
    p95_ms=round(lat[idx]*1000,1)
    if p95_ms>500:
        warns.append(f"transport_p95_above_target:{p95_ms}ms")

# helpers

def payload(ev):
    return ((ev.get("event") or {}).get("payload") or {}) if isinstance(ev, dict) else {}

def strv(v):
    return str(v or "")

# Scenario1: customer chat -> agent
s1_ev=None
for ev in agent:
    e=ev.get("event") or {}
    p=payload(ev)
    if e.get("type")=="message.created" and e.get("from")=="customer":
        if S1 in strv(p.get("text_original")):
            s1_ev=ev
            break

if s1_ev is None:
    s1_status=("FAIL","missing customer->agent event")
else:
    p=payload(s1_ev)
    lane=(p.get("lane") or {}).get("agent") if isinstance(p.get("lane"), dict) else {}
    src_lang=strv(p.get("source_lang") or p.get("lang_original")).lower()
    tgt_lang=strv((p.get("agent") or {}).get("lang") or p.get("lang_for_agent") or p.get("agent_lang")).lower()
    original=strv(p.get("text_original"))
    translated=strv(p.get("text_for_agent") or (p.get("agent") or {}).get("text") or p.get("text_translated"))
    has_translation = bool(lane.get("has_translation")) if isinstance(lane, dict) else False
    recv=float(s1_ev.get("recv_ts") or 0)
    delta=recv-T1
    fast_ok=delta<=FAST_SEC
    eventual_ok=delta<=EVENTUAL_SEC
    if not eventual_ok:
        fails.append(f"scenario1_eventual_delivery_failed:{delta:.3f}s")
    if not fast_ok:
        warns.append(f"scenario1_fast_delivery_slow:{delta:.3f}s")
    if not original:
        fails.append("scenario1_missing_text_original")
    if not translated:
        fails.append("scenario1_missing_text_for_agent")
    if translated and original and src_lang and tgt_lang and src_lang != tgt_lang and translated == original:
        fails.append("scenario1_text_for_agent_equals_original_when_langs_differ")
    if tgt_lang!="en":
        fails.append(f"scenario1_lang_for_agent_not_en:{tgt_lang}")
    if src_lang and src_lang!=tgt_lang and (translated==original and not has_translation):
        fails.append("scenario1_translation_not_applied_when_langs_differ")
    if src_lang and src_lang==tgt_lang and has_translation:
        warns.append("scenario1_has_translation_true_with_equal_langs")
    tts=(p.get("tts") or {})
    tts_lang=strv(tts.get("agent_lang")).lower()
    if tts_lang and tts_lang!="en":
        fails.append(f"scenario1_tts_agent_lang_not_en:{tts_lang}")
    s1_reason=f"chat_injection fast_delivery_ok={fast_ok}, eventual_delivery_ok={eventual_ok}"
    s1_status=("PASS" if not [f for f in fails if f.startswith("scenario1_")] else "FAIL", s1_reason)

# Scenario2: agent->customer
s2_ev=None
for ev in customer:
    e=ev.get("event") or {}
    p=payload(ev)
    if e.get("type")=="message.created" and e.get("from") in ("agent","system"):
        if S2 in strv(p.get("text_original")):
            s2_ev=ev
            break

if s2_ev is None:
    s2_status=("FAIL","missing agent->customer message.created on customer ws")
    fails.append("scenario2_missing_agent_to_customer_event")
else:
    p=payload(s2_ev)
    lane=(p.get("lane") or {}).get("customer") if isinstance(p.get("lane"), dict) else {}
    recv=float(s2_ev.get("recv_ts") or 0)
    delta=recv-T2
    fast_ok=delta<=FAST_SEC
    eventual_ok=delta<=EVENTUAL_SEC
    if not eventual_ok:
        fails.append(f"scenario2_eventual_delivery_failed:{delta:.3f}s")
    if not fast_ok:
        warns.append(f"scenario2_fast_delivery_slow:{delta:.3f}s")
    ctext=strv(p.get("text_for_customer") or (p.get("customer") or {}).get("text") or p.get("text"))
    clang=strv((p.get("customer") or {}).get("lang") or p.get("lang_for_customer") or p.get("customer_lang")).lower()
    a_lang=strv((p.get("agent") or {}).get("lang") or p.get("lang_for_agent") or p.get("agent_lang")).lower()
    original=strv(p.get("text_original"))
    translated=ctext
    has_translation = bool(lane.get("has_translation")) if isinstance(lane, dict) else False
    if not ctext:
        fails.append("scenario2_missing_text_for_customer")
    if clang!="de":
        fails.append(f"scenario2_lang_for_customer_not_de:{clang}")
    if a_lang and clang and a_lang!=clang and (translated==original and not has_translation):
        fails.append("scenario2_translation_not_applied_when_langs_differ")
    if a_lang and clang and a_lang==clang and has_translation:
        warns.append("scenario2_has_translation_true_with_equal_langs")
    tts=(p.get("tts") or {})
    tts_lang=strv(tts.get("customer_lang")).lower()
    if tts_lang and tts_lang!="de":
        fails.append(f"scenario2_tts_customer_lang_not_de:{tts_lang}")
    s2_reason=f"fast_delivery_ok={fast_ok}, eventual_delivery_ok={eventual_ok}"
    s2_status=("PASS" if not [f for f in fails if f.startswith("scenario2_")] else "FAIL", s2_reason)

# Scenario3: customer input produces answer
s3_in=None
for ev in agent:
    e=ev.get("event") or {}
    p=payload(ev)
    if e.get("type")=="message.created" and e.get("from")=="customer" and S3 in strv(p.get("text_original")):
        s3_in=ev
        break

s3_out=None
for ev in customer:
    e=ev.get("event") or {}
    if e.get("type")=="message.created" and e.get("from") in ("agent","system") and float(ev.get("recv_ts") or 0) >= T3:
        s3_out=ev
        break

if s3_in is None:
    fails.append("scenario3_missing_customer_input_event")
if s3_out is None:
    fails.append("scenario3_missing_answer_event")
if s3_in is None or s3_out is None:
    s3_status=("FAIL","customer input or routed answer missing")
else:
    d_in=float(s3_in.get("recv_ts") or 0)-T3
    d_out=float(s3_out.get("recv_ts") or 0)-T3
    fast_ok=(d_in<=FAST_SEC and d_out<=FAST_SEC)
    eventual_ok=(d_in<=EVENTUAL_SEC and d_out<=ANSWER_EVENTUAL_SEC)
    if not eventual_ok:
        fails.append(f"scenario3_eventual_delivery_failed:in={d_in:.3f}s,out={d_out:.3f}s")
    if not fast_ok:
        warns.append(f"scenario3_fast_delivery_slow:in={d_in:.3f}s,out={d_out:.3f}s")
    # Translation enforcement for the second customer message path.
    p_in = payload(s3_in)
    s3_src_lang = strv(p_in.get("source_lang") or p_in.get("lang_original")).lower()
    s3_agent_lang = strv((p_in.get("agent") or {}).get("lang") or p_in.get("lang_for_agent") or p_in.get("agent_lang")).lower()
    s3_original = strv(p_in.get("text_original"))
    s3_agent_text = strv(p_in.get("text_for_agent") or (p_in.get("agent") or {}).get("text") or p_in.get("text_translated"))
    s3_lane_agent = (p_in.get("lane") or {}).get("agent") if isinstance(p_in.get("lane"), dict) else {}
    s3_has_translation = bool(s3_lane_agent.get("has_translation")) if isinstance(s3_lane_agent, dict) else False
    if s3_src_lang and s3_agent_lang and s3_src_lang != s3_agent_lang and (s3_agent_text == s3_original and not s3_has_translation):
        fails.append("scenario3_translation_not_applied_when_langs_differ")
    s3_status=("PASS" if not [f for f in fails if f.startswith("scenario3_")] else "FAIL", f"fast_delivery_ok={fast_ok}, eventual_delivery_ok={eventual_ok}")

# Scenario4: voice path customer DE -> agent EN translation enforcement
s4_ev = None
for ev in agent:
    e = ev.get("event") or {}
    p = payload(ev)
    if e.get("type") != "message.created" or e.get("from") != "customer":
        continue
    if float(ev.get("recv_ts") or 0) < T4:
        continue
    dbg = p.get("debug") if isinstance(p.get("debug"), dict) else {}
    if dbg.get("customer_lang_requested") == "de":
        s4_ev = ev
        break
    # fallback: accept first customer message after voice injection timestamp
    if s4_ev is None:
        s4_ev = ev

if VOICE_STATUS != "PASS":
    fails.append("scenario4_voice_request_failed")
    s4_status = ("FAIL", "voice request returned non-2xx")
elif s4_ev is None:
    fails.append("scenario4_missing_voice_customer_event")
    s4_status = ("FAIL", "missing voice customer->agent event")
else:
    p = payload(s4_ev)
    recv = float(s4_ev.get("recv_ts") or 0)
    delta = recv - T4
    fast_ok = delta <= FAST_SEC
    eventual_ok = delta <= EVENTUAL_SEC
    if not eventual_ok:
        fails.append(f"scenario4_eventual_delivery_failed:{delta:.3f}s")
    if not fast_ok:
        warns.append(f"scenario4_fast_delivery_slow:{delta:.3f}s")
    src_lang = strv(p.get("source_lang") or p.get("lang_original")).lower()
    translated = strv(p.get("text_for_agent") or (p.get("agent") or {}).get("text") or p.get("text_translated"))
    original = strv(p.get("text_original"))
    tgt_lang = strv((p.get("agent") or {}).get("lang") or p.get("lang_for_agent") or p.get("agent_lang")).lower()
    lane_agent = (p.get("lane") or {}).get("agent") if isinstance(p.get("lane"), dict) else {}
    has_translation = bool(lane_agent.get("has_translation")) if isinstance(lane_agent, dict) else False
    tts_lang = strv(((p.get("tts") or {}).get("agent_lang"))).lower()
    if tgt_lang != "en":
        fails.append(f"scenario4_lang_for_agent_not_en:{tgt_lang}")
    if src_lang and src_lang != tgt_lang and (translated == original and not has_translation):
        fails.append("scenario4_translation_not_applied_when_langs_differ")
    if tts_lang and tts_lang != "en":
        fails.append(f"scenario4_tts_agent_lang_not_en:{tts_lang}")
    s4_status = ("PASS" if not [f for f in fails if f.startswith("scenario4_")] else "FAIL", f"fast_delivery_ok={fast_ok}, eventual_delivery_ok={eventual_ok}")

# Scenario5: session/history customer chat -> agent dual-lane
s5_status = ("PASS", "history_dual_lane_persisted")
s5_match = None
for msg in (session_dump.get("messages") or []):
    if str(msg.get("role") or "") != "customer":
        continue
    if S1 in strv(msg.get("text_original")):
        s5_match = msg
        break

if s5_match is None:
    fails.append("scenario5_missing_session_history_customer_message")
    s5_status = ("FAIL", "missing customer message in session history")
else:
    original = strv(s5_match.get("text_original"))
    translated = strv(s5_match.get("text_for_agent"))
    tgt_lang = strv(s5_match.get("lang_for_agent")).lower()
    if not original:
        fails.append("scenario5_missing_text_original")
    if not translated:
        fails.append("scenario5_missing_text_for_agent")
    if tgt_lang != "en":
        fails.append(f"scenario5_lang_for_agent_not_en:{tgt_lang}")
    if original and translated and original == translated:
        fails.append("scenario5_text_for_agent_equals_original_when_langs_differ")
    s5_status = ("PASS" if not [f for f in fails if f.startswith("scenario5_")] else "FAIL", "history_dual_lane_persisted")

result="PASS" if not fails else "FAIL"

six_lines=[
    f"COMMIT: {commit}",
    f"RESULT: {result}",
    f"SCENARIO1: {s1_status[0]} ({s1_status[1]})",
    f"SCENARIO2: {s2_status[0]} ({s2_status[1]})",
    f"SCENARIO3: {s3_status[0]} ({s3_status[1]})",
    f"P95_MS: {p95_ms}",
]

summary_path.write_text("\n".join(six_lines)+"\n", encoding="utf-8")

with log_path.open("a", encoding="utf-8") as fh:
    fh.write(f"PATCH: {PATCH_LABEL}\n")
    fh.write("\n".join(six_lines)+"\n")
    fh.write(f"VOICE_SCENARIO: {s4_status[0]} ({s4_status[1]})\n")
    fh.write(f"HISTORY_SCENARIO: {s5_status[0]} ({s5_status[1]})\n")
    if warns:
        fh.write("WARNINGS:\n")
        for w in warns: fh.write(f"- {w}\n")
    if fails:
        fh.write("FAILURES:\n")
        for f in fails: fh.write(f"- {f}\n")

# Keep legacy alias for older tooling.
Path("$ART_DIR/test-log-v9.1x.txt").write_text(log_path.read_text(encoding="utf-8") if log_path.exists() else "", encoding="utf-8")
Path("$ART_DIR/test-log-v9.1x-voicefix.txt").write_text(log_path.read_text(encoding="utf-8") if log_path.exists() else "", encoding="utf-8")

print("\n".join(six_lines))
if fails:
    Path("$FAIL_REPORT").write_text("\n".join(["# FAILURE_REPORT",*six_lines,"","## Failures",*[f"- {f}" for f in fails],"","## Warnings",*[f"- {w}" for w in warns]]), encoding="utf-8")
    raise SystemExit(1)
PY

( cd "$ART_DIR" && zip -qr artifacts.zip . )
cp -f "$ART_DIR/artifacts.zip" "$RUN_ZIP"

# Refresh latest/ snapshot to simplify manual testing workflow.
find "$OUT_LATEST_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
cp -R "$ART_DIR"/. "$OUT_LATEST_DIR"/

# Retention: keep only the newest N runs and run-zips.
python3 - <<PY
from pathlib import Path
import shutil

runs_dir = Path("$OUT_RUNS_DIR")
root_dir = Path("$OUT_ROOT")
keep = int("$RETAIN_RUNS")

dirs = [p for p in runs_dir.iterdir() if p.is_dir()]
dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
for old in dirs[keep:]:
    shutil.rmtree(old, ignore_errors=True)

zips = [p for p in runs_dir.iterdir() if p.is_file() and p.name.startswith("artifacts-") and p.suffix == ".zip"]
zips.sort(key=lambda p: p.stat().st_mtime, reverse=True)
for old in zips[keep:]:
    try:
        old.unlink()
    except FileNotFoundError:
        pass

# Legacy cleanup from older layouts in artifacts/ root.
legacy_dirs = []
for pat in ("v9_ws_*", "v9_duallane_run_*", "voice_debug_*", "release_gate_v*"):
    legacy_dirs.extend([p for p in root_dir.glob(pat) if p.is_dir()])
legacy_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
for old in legacy_dirs[keep:]:
    shutil.rmtree(old, ignore_errors=True)

legacy_zips = [p for p in root_dir.glob("artifacts-v*.zip") if p.is_file()]
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
