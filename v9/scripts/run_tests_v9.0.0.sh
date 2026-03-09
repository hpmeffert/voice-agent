#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/v9/test-logs"
LOG_FILE="$LOG_DIR/V9.0.0_testlog.txt"
mkdir -p "$LOG_DIR"

{
  echo "[V9.0.0] test start: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "[V9.0.0] root: $ROOT_DIR"

  cd "$ROOT_DIR"
  docker compose --project-directory "$ROOT_DIR" -f v9/docker/compose.dev.yml up -d --build

  for i in $(seq 1 120); do
    if curl -fsS --max-time 2 http://localhost:8085/api/health >/dev/null; then
      break
    fi
    sleep 1
  done

  echo "[V9.0.0] health"
  curl -fsS http://localhost:8085/api/health
  echo

  echo "[V9.0.0] models"
  curl -fsS http://localhost:8085/api/models >/dev/null
  echo "ok"

  echo "[V9.0.0] docs endpoint checks"
  for TYPE in user demo release; do
    for LANG in de en fr; do
      SIZE=$(curl -fsS "http://localhost:8085/api/docs?type=${TYPE}&lang=${LANG}" | wc -c | tr -d ' ')
      echo "type=${TYPE} lang=${LANG} size=${SIZE}"
      if [ "${SIZE}" -lt 200 ]; then
        echo "doc too small: type=${TYPE} lang=${LANG}" >&2
        exit 1
      fi
    done
  done

  echo "[V9.0.0] admin docs endpoint with token"
  ADMIN_STATUS=$(curl -s -o /tmp/v9_admin_doc.txt -w "%{http_code}" "http://localhost:8085/api/docs?type=admin&lang=de" -H "X-Admin-Token: ${ADMIN_UI_TOKEN:-demo-admin-123}")
  echo "admin_status=${ADMIN_STATUS}"
  if [ "$ADMIN_STATUS" != "200" ]; then
    echo "admin docs call failed with status ${ADMIN_STATUS}" >&2
    exit 1
  fi
  ADMIN_SIZE=$(wc -c </tmp/v9_admin_doc.txt | tr -d ' ')
  if [ "$ADMIN_SIZE" -lt 500 ]; then
    echo "admin docs too small: ${ADMIN_SIZE}" >&2
    exit 1
  fi

  echo "[V9.0.0] local doc checks"
  python3 v9/scripts/check_docs.py
  PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py
  PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/piper/app.py

  echo "[V9.0.0] agent language prefs + translation flow"
  curl -fsS -X POST http://localhost:8085/api/user/prefs \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"agenten-02","agent_lang":"en"}' >/tmp/v9_agent_prefs.json

  SID_JSON=$(curl -fsS -X POST http://localhost:8085/api/chat/text \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"kunde-de-9001","text":"Hallo, ich brauche Hilfe.","tts_lang":"de"}')
  SID=$(printf '%s' "$SID_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("session_id",""))')
  if [ -z "$SID" ]; then
    echo "no session id from chat/text" >&2
    exit 1
  fi

  AG_RESP=$(curl -fsS -X POST http://localhost:8085/api/agent/message \
    -H 'Content-Type: application/json' \
    -d "{\"session_id\":\"$SID\",\"agent_id\":\"agenten-02\",\"text\":\"Hello, I can help you now.\",\"speak\":true,\"tts_lang\":\"de\",\"agent_lang\":\"en\"}")
  echo "$AG_RESP" | python3 -c 'import sys,json;d=json.load(sys.stdin); assert d.get("agent_lang")=="en"; assert d.get("tts_lang")=="de"; assert d.get("answer_translated"); print("agent_flow_ok")'

  echo "[V9.0.0] test done: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} 2>&1 | tee "$LOG_FILE"
