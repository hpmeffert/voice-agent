#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="${RUN_ID:-v9.1.15-p3-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="v9/artifacts/runs/${RUN_ID}"
mkdir -p "$OUT_DIR"
LOG_FILE="$OUT_DIR/test-log-v9.1.15-p3.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"

ADMIN_UI_URL="${ADMIN_UI_URL:-http://localhost:8085}"
CUSTOMER_UI_URL="${CUSTOMER_UI_URL:-http://localhost:8086}"
AGENT_UI_URL="${AGENT_UI_URL:-http://localhost:8087}"
API_BASE="${API_BASE:-http://localhost:8085/api}"
ADMIN_TOKEN="${ADMIN_UI_TOKEN:-}"
PROBE_DURATION_SEC="${PROBE_DURATION_SEC:-12}"

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
log "# v9.1.15 patch3 smoke"
log "date=$(date -Iseconds)"
log "run_id=$RUN_ID"
log "api_base=$API_BASE"

log "[STEP] start stack"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml up -d --build >> "$LOG_FILE" 2>&1

log "[STEP] wait for health"
for _ in $(seq 1 120); do
  if curl -sf "$API_BASE/health" >/dev/null; then break; fi
  sleep 1
done
if curl -sf "$API_BASE/health" > "$OUT_DIR/health.json"; then
  ok "api health"
else
  ko "api health"
fi

log "[STEP] config/version"
if curl -sf "$API_BASE/config" > "$OUT_DIR/config.json"; then
  ver=$(python3 - <<'PY' "$OUT_DIR/config.json"
import json,sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data=json.load(fh)
print(((data.get("ui") or {}).get("version") or "").strip())
PY
)
  if [[ "$ver" == "v9.1.15" ]]; then ok "config ui.version=v9.1.15"; else ko "config ui.version expected v9.1.15 got $ver"; fi
else
  ko "config endpoint"
fi

log "[STEP] fetch HTML"
curl -sf "$ADMIN_UI_URL" > "$OUT_DIR/admin.html" || ko "admin html fetch"
curl -sf "$AGENT_UI_URL" > "$OUT_DIR/agent.html" || ko "agent html fetch"
curl -sf "$CUSTOMER_UI_URL" > "$OUT_DIR/customer.html" || ko "customer html fetch"

if [[ -f "$OUT_DIR/admin.html" ]]; then
  rg -q 'id="adminWsState"' "$OUT_DIR/admin.html" && ok "admin has WS state pill" || ko "admin missing WS state pill"
  rg -q 'id="adminWsRtt"' "$OUT_DIR/admin.html" && ok "admin has WS RTT pill" || ko "admin missing WS RTT pill"
fi
if [[ -f "$OUT_DIR/agent.html" ]]; then
  rg -q 'id="wsRtt"' "$OUT_DIR/agent.html" && ok "agent has WS RTT pill" || ko "agent missing WS RTT pill"
fi
if [[ -f "$OUT_DIR/customer.html" ]]; then
  rg -q 'id="headerWsState"' "$OUT_DIR/customer.html" && ok "customer has WS state line" || ko "customer missing WS state line"
  rg -q 'id="headerWsRtt"' "$OUT_DIR/customer.html" && ok "customer has WS RTT line" || ko "customer missing WS RTT line"
fi

log "[STEP] docs endpoints not empty"
for doc in "user&lang=de" "user&lang=en" "demo&lang=de" "admin&lang=de" "release&lang=de"; do
  if curl -sf "$API_BASE/docs?type=${doc}" > "$OUT_DIR/doc-$(echo "$doc" | tr '&=' '__').txt"; then
    if [[ $(wc -c < "$OUT_DIR/doc-$(echo "$doc" | tr '&=' '__').txt") -gt 200 ]]; then
      ok "docs $doc"
    else
      ko "docs $doc too small"
    fi
  else
    ko "docs $doc fetch"
  fi
done

log "[STEP] websocket RTT probe"
if python3 - <<'PY' "$OUT_DIR" "$ADMIN_UI_URL" "$AGENT_UI_URL" "$CUSTOMER_UI_URL" "$PROBE_DURATION_SEC"
import json
import os
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.getcwd())
from scripts.ws_probe import SimpleWSClient

out_dir, admin_url, agent_url, customer_url, probe_duration_sec = sys.argv[1:6]
probe_duration_sec = float(probe_duration_sec)

def to_ws(base, path):
    parsed = urlparse(base)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return f"{scheme}://{parsed.netloc}{path}"

targets = {
    "admin": to_ws(admin_url, "/api/ws/ping"),
    "agent": to_ws(agent_url, "/api/ws/session/smoke-agent-rtt?client=agent&user_id=agenten-02&agent_lang=en"),
    "customer": to_ws(customer_url, "/api/ws/session/smoke-agent-rtt?client=customer&user_id=customer-rtt-01&customer_lang=de"),
}

results = {}
for name, url in targets.items():
    client = SimpleWSClient(url, timeout_sec=2.5)
    samples = []
    try:
      client.connect()
      deadline = time.time() + probe_duration_sec
      while time.time() < deadline and len(samples) < 2:
          sent = int(time.time() * 1000)
          client._send_frame(0x1, json.dumps({"type":"ping","t":sent}).encode("utf-8"))
          inner_deadline = time.time() + 2.5
          while time.time() < inner_deadline:
              msg = client.recv_text()
              if not msg:
                  continue
              payload = json.loads(msg)
              if payload.get("type") == "pong" and int(payload.get("t", -1)) == sent:
                  samples.append(int(time.time() * 1000) - sent)
                  break
          time.sleep(0.5)
      results[name] = {
          "ok": len(samples) >= 1,
          "samples_ms": samples,
          "avg_ms": round(sum(samples) / len(samples), 1) if samples else None,
          "url": url,
      }
    except Exception as exc:
      results[name] = {"ok": False, "error": str(exc), "url": url}
    finally:
      try:
          client.close()
      except Exception:
          pass

with open(os.path.join(out_dir, "ws-rtt-probe.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=2)

if not all(item.get("ok") for item in results.values()):
    raise SystemExit(1)
PY
then
  ok "ws RTT ping/pong works for admin/agent/customer"
else
  ko "ws RTT ping/pong probe"
fi

log "[STEP] dual-lane chat quick proof"
USER_ID="smoke-user-$(date +%s)"
SESSION_ID="smoke-session-$(date +%s)"
AGENT_WS_URL="$(python3 - <<'PY' "$AGENT_UI_URL" "$SESSION_ID" "$USER_ID"
import sys
from urllib.parse import urlparse
base, sid, uid = sys.argv[1:4]
parsed = urlparse(base)
scheme = "wss" if parsed.scheme == "https" else "ws"
print(f"{scheme}://{parsed.netloc}/api/ws/session/{sid}?client=agent&user_id=agenten-02&agent_lang=en")
PY
)"
CUSTOMER_WS_URL="$(python3 - <<'PY' "$CUSTOMER_UI_URL" "$SESSION_ID" "$USER_ID"
import sys
from urllib.parse import urlparse
base, sid, uid = sys.argv[1:4]
parsed = urlparse(base)
scheme = "wss" if parsed.scheme == "https" else "ws"
print(f"{scheme}://{parsed.netloc}/api/ws/session/{sid}?client=customer&user_id={uid}&customer_lang=de")
PY
)"
python3 scripts/ws_probe.py \
  --agent-url "$AGENT_WS_URL" \
  --customer-url "$CUSTOMER_WS_URL" \
  --agent-out "$OUT_DIR/ws_agent_events.jsonl" \
  --customer-out "$OUT_DIR/ws_customer_events.jsonl" \
  --duration-sec 10 \
  > "$OUT_DIR/ws_probe_status.json" 2>&1 &
PROBE_PID=$!
sleep 1
if curl_json POST "$API_BASE/chat/text" -H "Content-Type: application/json" -d "{\"text\":\"Meine Wallbox blinkt rot. Was kann ich tun?\",\"user_id\":\"$USER_ID\",\"session_id\":\"$SESSION_ID\",\"backend\":\"ollama\"}" > "$OUT_DIR/chat-proof.json"; then
  ok "chat/text dual-lane proof request"
else
  ko "chat/text dual-lane proof request"
fi
wait "$PROBE_PID" || true
if curl_json GET "$API_BASE/session/$SESSION_ID?user_id=$USER_ID&agent_lang=en&limit=20" > "$OUT_DIR/session-duallane.json"; then
  ok "session history fetched for dual-lane proof"
else
  ko "session history fetch for dual-lane proof"
fi
if python3 - <<'PY' "$OUT_DIR/session-duallane.json"
import json,sys
path=sys.argv[1]
ok=False
j=json.load(open(path, encoding="utf-8"))
for msg in (j.get("messages") or []):
    if (msg.get("role") or msg.get("from_role")) != "customer":
        continue
    if msg.get("lang_for_agent") == "en" and msg.get("text_original") and msg.get("text_for_agent") and msg.get("text_original") != msg.get("text_for_agent"):
        ok=True
        break
raise SystemExit(0 if ok else 1)
PY
then
  ok "agent dual-lane chat proof stored in session"
else
  ko "agent dual-lane chat proof missing"
fi

log "[STEP] environment snapshot + docker logs"
{
  date -Iseconds
  echo "branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "commit=$(git rev-parse --short HEAD)"
  env | rg "VOICE|LANG|TTS|OLLAMA|OPENAI|MONGO|VALKEY|REDIS|RETENTION|UI_VERSION" || true
} > "$OUT_DIR/ENV_SNAPSHOT.txt"
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color api > "$OUT_DIR/docker-logs-api.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web > "$OUT_DIR/docker-logs-web-admin.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-agent > "$OUT_DIR/docker-logs-web-agent.txt" 2>&1 || true
docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml logs --no-color web-customer > "$OUT_DIR/docker-logs-web-customer.txt" 2>&1 || true

result="PASS"
if [[ "$fail" -gt 0 ]]; then result="FAIL"; fi

cat > "$SUMMARY_FILE" <<EOF_SUM
# V9.1.15 Patch 3 Smoke Summary

- run_id: $RUN_ID
- date: $(date -Iseconds)
- result: **$result**
- passed: $pass
- failed: $fail

## Commands
- docker compose --project-directory "\$PWD" -f v9/docker/compose.dev.yml up -d --build
- curl -s $API_BASE/health
- bash scripts/run_v9_1_10_smoke.sh

## Checks
- API health
- version v9.1.15 in config
- WS RTT elements in admin/agent/customer headers
- WS ping/pong on admin + agent + customer sockets
- docs endpoints non-empty
- customer chat dual-lane payload reaches agent

## Artifacts
- $LOG_FILE
- $OUT_DIR/health.json
- $OUT_DIR/config.json
- $OUT_DIR/admin.html
- $OUT_DIR/agent.html
- $OUT_DIR/customer.html
- $OUT_DIR/ws-rtt-probe.json
- $OUT_DIR/ws_agent_events.jsonl
- $OUT_DIR/ws_customer_events.jsonl
- $OUT_DIR/session-duallane.json
- $OUT_DIR/ENV_SNAPSHOT.txt
EOF_SUM

log "[RESULT] $result"
log "Artifacts: $OUT_DIR"

if [[ "$result" != "PASS" ]]; then
  exit 1
fi
