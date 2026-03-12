#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

RUN_TS="$(date +%Y%m%d-%H%M%S)"
RUN_ID="v9.1.16-search-${RUN_TS}"
OUT_DIR="v9/artifacts/runs/${RUN_ID}"
mkdir -p "$OUT_DIR"

LOG_FILE="$OUT_DIR/test-log-v9.1.16-search.txt"
SUMMARY_FILE="$OUT_DIR/SUMMARY.md"
HTTP_LOG="$OUT_DIR/http_requests.log"
SEED_FILE="$OUT_DIR/seed.json"
RESULTS_FILE="$OUT_DIR/results.json"
ENV_FILE="$OUT_DIR/ENV_SNAPSHOT.txt"

ADMIN_API="${ADMIN_API:-http://localhost:8085/api}"
AGENT_API="${AGENT_API:-http://localhost:8087/api}"
CUSTOMER_API="${CUSTOMER_API:-http://localhost:8086/api}"
ADMIN_USER_ID="${ADMIN_USER_ID:-admin-search-v9-1-16}"
AGENT_USER_ID="${AGENT_USER_ID:-agenten-02}"
RUN_TOKEN="${RUN_TOKEN:-$(date +%s)}"
CUSTOMER_USER_ID="${CUSTOMER_USER_ID:-fe77-user-${RUN_TOKEN}}"
SESSION_ID="${SESSION_ID:-fe77-session-${RUN_TOKEN}}"
SEARCH_PREFIX="${SEARCH_PREFIX:-fe77*}"

pass=0
fail=0
warn=0

log(){ printf '%s\n' "$*" | tee -a "$LOG_FILE"; }
ok(){ pass=$((pass+1)); log "[PASS] $*"; }
ko(){ fail=$((fail+1)); log "[FAIL] $*"; }
wa(){ warn=$((warn+1)); log "[WARN] $*"; }

request(){
  local name="$1"; shift
  local method="$1"; shift
  local url="$1"; shift
  printf '[%s] %s %s\n' "$(date -Iseconds)" "$method" "$url" >> "$HTTP_LOG"
  if [[ "$method" == "GET" ]]; then
    curl -sS --max-time 120 "$url" "$@"
  else
    curl -sS --max-time 180 -X "$method" "$url" "$@"
  fi
}

: > "$LOG_FILE"
: > "$HTTP_LOG"

log "# V9.1.16 search tests"
log "date=$(date -Iseconds)"
log "admin_api=$ADMIN_API"
log "agent_api=$AGENT_API"
log "customer_api=$CUSTOMER_API"
log "customer_user_id=$CUSTOMER_USER_ID"
log "session_id=$SESSION_ID"

wait_for_health() {
  local url="$1"
  local label="$2"
  for _ in $(seq 1 90); do
    if request health GET "$url" >/dev/null 2>>"$LOG_FILE"; then
      ok "health $label"
      return 0
    fi
    sleep 1
  done
  ko "health $label"
  return 1
}

wait_for_health "$ADMIN_API/health" "$ADMIN_API/health"
wait_for_health "$AGENT_API/health" "$AGENT_API/health"
wait_for_health "$CUSTOMER_API/health" "$CUSTOMER_API/health"

if [[ "$fail" -gt 0 ]]; then
  log "[RESULT] FAIL (health precondition)"
  exit 1
fi

cat > "$ENV_FILE" <<ENV
run_id=$RUN_ID
date=$(date -Iseconds)
branch=$(git rev-parse --abbrev-ref HEAD)
commit=$(git rev-parse --short HEAD)
admin_api=$ADMIN_API
agent_api=$AGENT_API
customer_api=$CUSTOMER_API
customer_user_id=$CUSTOMER_USER_ID
session_id=$SESSION_ID
ENV

cat > "$SEED_FILE" <<SEED
{
  "customer_user_id": "$CUSTOMER_USER_ID",
  "session_id": "$SESSION_ID",
  "messages": [
    "Meine Wallbox geht immer aus. Ich brauche Hilfe mit dem Abschlag im Vertrag.",
    "Bitte pruefen Sie den Abschlag und den Vertrag fuer die Wallbox.",
    "Der Vertrag ist gefunden, und die Wallbox-Diagnose ist jetzt sichtbar."
  ]
}
SEED

CHAT1='{"text":"Meine Wallbox geht immer aus. Ich brauche Hilfe mit dem Abschlag im Vertrag.","user_id":"'"$CUSTOMER_USER_ID"'","session_id":"'"$SESSION_ID"'","backend":"ollama","lang":"de","tts_lang":"de"}'
CHAT2='{"text":"Bitte pruefen Sie den Abschlag und den Vertrag fuer die Wallbox.","user_id":"'"$CUSTOMER_USER_ID"'","session_id":"'"$SESSION_ID"'","backend":"ollama","lang":"de","tts_lang":"de"}'
AGENT_MSG='{"session_id":"'"$SESSION_ID"'","agent_id":"'"$AGENT_USER_ID"'","text":"The contract is visible and the wallbox diagnostics are available now.","speak":false,"tts_lang":"de","agent_lang":"en"}'

if request chat1 POST "$CUSTOMER_API/chat/text" -H 'Content-Type: application/json' -d "$CHAT1" > "$OUT_DIR/chat1.json"; then ok "seed chat #1"; else ko "seed chat #1"; fi
if request chat2 POST "$CUSTOMER_API/chat/text" -H 'Content-Type: application/json' -d "$CHAT2" > "$OUT_DIR/chat2.json"; then ok "seed chat #2"; else ko "seed chat #2"; fi
if request agentmsg POST "$AGENT_API/agent/message" -H 'Content-Type: application/json' -d "$AGENT_MSG" > "$OUT_DIR/agent-message.json"; then ok "seed agent message"; else ko "seed agent message"; fi

if request search_session GET "$ADMIN_API/admin/search?user_id=${ADMIN_USER_ID}&q=${SESSION_ID}&mode=session_id&since_days=7&limit=20&include_snippets=true" > "$OUT_DIR/admin-search-session.json"; then ok "admin search session_id"; else ko "admin search session_id"; fi
if request search_user GET "$ADMIN_API/admin/search?user_id=${ADMIN_USER_ID}&q=${CUSTOMER_USER_ID}&mode=user_id&since_days=7&limit=20&include_snippets=true" > "$OUT_DIR/admin-search-user.json"; then ok "admin search user_id"; else ko "admin search user_id"; fi
if request search_prefix GET "$ADMIN_API/admin/search?user_id=${ADMIN_USER_ID}&q=${SEARCH_PREFIX}&mode=auto&since_days=7&limit=20&include_snippets=true" > "$OUT_DIR/admin-search-prefix.json"; then ok "admin search prefix"; else ko "admin search prefix"; fi
if request search_wallbox GET "$ADMIN_API/admin/search?user_id=${ADMIN_USER_ID}&q=*wallbox*&mode=text&since_days=7&limit=20&include_snippets=true" > "$OUT_DIR/admin-search-wallbox.json"; then ok "admin search wallbox"; else ko "admin search wallbox"; fi
if request search_vertrag GET "$ADMIN_API/admin/search?user_id=${ADMIN_USER_ID}&q=*vertrag*&mode=text&since_days=7&limit=20&include_snippets=true" > "$OUT_DIR/admin-search-vertrag.json"; then ok "admin search vertrag"; else ko "admin search vertrag"; fi
if request agent_search GET "$AGENT_API/agent/search?user_id=${AGENT_USER_ID}&q=*wallbox*&mode=text&since_days=7&limit=20&include_snippets=true" > "$OUT_DIR/agent-search-wallbox.json"; then ok "agent search wallbox"; else ko "agent search wallbox"; fi
if request session_dump GET "$AGENT_API/session/${SESSION_ID}?user_id=${CUSTOMER_USER_ID}&limit=50&agent_lang=en" > "$OUT_DIR/session.json"; then ok "session history"; else ko "session history"; fi

python3 - <<'PY' "$OUT_DIR" "$SESSION_ID" "$CUSTOMER_USER_ID" "$SUMMARY_FILE" "$LOG_FILE" || exit 1
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
session_id = sys.argv[2]
user_id = sys.argv[3]
summary_path = Path(sys.argv[4])
log_path = Path(sys.argv[5])

checks = []
warns = []

def load(name):
    return json.loads((out / name).read_text(encoding='utf-8'))

def record(name, ok, detail):
    checks.append((name, ok, detail))

session_search = load('admin-search-session.json')
user_search = load('admin-search-user.json')
prefix_search = load('admin-search-prefix.json')
wallbox_search = load('admin-search-wallbox.json')
vertrag_search = load('admin-search-vertrag.json')
agent_search = load('agent-search-wallbox.json')
session_dump = load('session.json')

for name, payload in [
    ('exact session_id', session_search),
    ('exact user_id', user_search),
    ('prefix fe77*', prefix_search),
    ('text *wallbox*', wallbox_search),
    ('text *vertrag*', vertrag_search),
    ('agent text *wallbox*', agent_search),
]:
    matches = payload.get('matches') or []
    ok = any(str(m.get('session_id') or '') == session_id for m in matches)
    detail = f"matches={len(matches)}"
    if name == 'text *wallbox*' and ok:
        snippets = []
        for m in matches:
            if str(m.get('session_id') or '') == session_id:
                snippets = m.get('snippets') or []
                break
        if not any('wallbox' in str(s).lower() for s in snippets):
            ok = False
            detail = f"snippet missing wallbox; snippets={snippets}"
    record(name, ok, detail)

messages = session_dump.get('messages') or []
customer_msgs = [m for m in messages if str(m.get('role') or '').lower() == 'customer']
if not customer_msgs:
    record('session history dual-lane', False, 'no customer messages found')
else:
    lane_ok = any(
        'wallbox' in str(m.get('text_original') or '').lower()
        and str(m.get('lang_for_agent') or '').lower() == 'en'
        and str(m.get('text_for_agent') or '').strip()
        and str(m.get('text_for_agent') or '') != str(m.get('text_original') or '')
        for m in customer_msgs
    )
    record('session history dual-lane', lane_ok, f'customer_messages={len(customer_msgs)}')

for payload_name, payload in [('admin-search-wallbox.json', wallbox_search), ('agent-search-wallbox.json', agent_search)]:
    took_ms = int((payload.get('meta') or {}).get('took_ms') or 0)
    if took_ms > 2000:
        warns.append(f'{payload_name} took {took_ms}ms (>2000ms)')

result = 'PASS' if all(ok for _, ok, _ in checks) else 'FAIL'
with log_path.open('a', encoding='utf-8') as fh:
    for name, ok, detail in checks:
        fh.write(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}\n")
    for item in warns:
        fh.write(f"[WARN] {item}\n")

summary_lines = [
    '# V9.1.16 Search Summary',
    '',
    f'- result: **{result}**',
    f'- session_id: `{session_id}`',
    f'- user_id: `{user_id}`',
    '',
    '## Assertions',
]
for name, ok, detail in checks:
    summary_lines.append(f'- {name}: {"PASS" if ok else "FAIL"} ({detail})')
if warns:
    summary_lines.append('')
    summary_lines.append('## Warnings')
    for item in warns:
        summary_lines.append(f'- {item}')
summary_lines.extend([
    '',
    '## Artifacts',
    f'- `{out / "test-log-v9.1.16-search.txt"}`',
    f'- `{out / "http_requests.log"}`',
    f'- `{out / "seed.json"}`',
    f'- `{out / "results.json"}`',
])
summary_path.write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')
(out / 'results.json').write_text(json.dumps({
    'checks': [{'name': name, 'ok': ok, 'detail': detail} for name, ok, detail in checks],
    'warnings': warns,
    'session_id': session_id,
    'user_id': user_id,
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
if result != 'PASS':
    raise SystemExit(1)
PY

bash scripts/capture_logs.sh "$OUT_DIR" >/dev/null 2>&1 || true

log "[RESULT] PASS"
log "Artifacts: $OUT_DIR"

python3 - <<'PY'
from pathlib import Path
base = Path('v9/artifacts/runs')
if not base.exists():
    raise SystemExit(0)
runs = sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
for old in runs[8:]:
    for item in sorted(old.rglob('*'), reverse=True):
        if item.is_file() or item.is_symlink():
            item.unlink(missing_ok=True)
        elif item.is_dir():
            item.rmdir()
    old.rmdir()
PY
