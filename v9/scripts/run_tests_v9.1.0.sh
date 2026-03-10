#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="output"
LOG_FILE="$LOG_DIR/test-log-v9.1.0.txt"
mkdir -p "$LOG_DIR"

exec > >(tee "$LOG_FILE") 2>&1

echo "# V9.1.0 Test Log"
echo "date_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "version_target: v9.1.0"
echo "git_commit: $(git rev-parse --short HEAD)"
echo

echo "## Smoke: API"
for i in $(seq 1 60); do
  if curl -sS --max-time 5 "http://localhost:8085/api/health" | grep -q '"status":"ok"'; then
    break
  fi
  sleep 1
done
HEALTH_JSON=$(curl -sS --max-time 10 "http://localhost:8085/api/health")
echo "$HEALTH_JSON"
echo "$HEALTH_JSON" | grep -q '"status":"ok"'
echo
MODELS_JSON=$(curl -sS --max-time 10 "http://localhost:8085/api/models")
echo "$MODELS_JSON" | head -c 600
echo "$MODELS_JSON" | grep -q '"app_version"'
echo
CONFIG_JSON=$(curl -sS --max-time 10 "http://localhost:8085/api/config?user_id=test-user-v910")
echo "$CONFIG_JSON"
echo "$CONFIG_JSON" | grep -q '"listen_silence_ms_default":1300'
echo

echo "## Smoke: voice endpoint (expected graceful error on empty audio)"
VOICE_STATUS=$(curl -sS --max-time 20 -o /tmp/v910_voice_resp.json -w "%{http_code}" -F "file=@/dev/null;filename=empty.wav" -F "user_id=test-user-v910" -F "session_id=" -F "return_audio=0" "http://localhost:8085/api/voice" || true)
echo "voice_http_status: ${VOICE_STATUS}"
cat /tmp/v910_voice_resp.json || true
grep -q '"error"' /tmp/v910_voice_resp.json
echo

echo "## Doc checks"
python3 v9/scripts/check_docs.py

echo "## Dual-lane contract checks (4 required cases)"
python3 - <<'PY'
import ast
from pathlib import Path

src = Path('v9/docker/api/app.py').read_text(encoding='utf-8')
mod = ast.parse(src)
needed = {'_normalize_lang','build_dual_lane_event'}
chunks = []
for n in mod.body:
    if isinstance(n, ast.FunctionDef) and n.name in needed:
        chunks.append(ast.get_source_segment(src, n))

ns = {
    'SUPPORTED_TTS_LANGS': ['de','en','fr','it','es','sv','no','fi'],
    'AGENT_LANG_CHOICES': ['de','en','no','sv','fi'],
    'DEFAULT_UI_LANG': 'de',
}
def detect_lang_from_text(text):
    t = (text or '').lower()
    if 'hej' in t:
        return 'sv'
    if 'hallo' in t or 'wallbox' in t:
        return 'de'
    return 'en'

def translate_answer_text(**kwargs):
    return f"[{kwargs.get('target_lang')}] {kwargs.get('text','')}"

ns['detect_lang_from_text'] = detect_lang_from_text
ns['translate_answer_text'] = translate_answer_text

exec('from __future__ import annotations\n\n' + '\n\n'.join(chunks), ns)
build = ns['build_dual_lane_event']

cases = [
    ('customer','was kann ich tun? Meine wallbox geht immer aus.','de','en','de'),
    ('agent','I can help you with troubleshooting right now.','en','en','de'),
    ('customer','Can you hear me now?','en','sv','en'),
    ('agent','Hej! Jag hjälper dig gärna.','sv','sv','en'),
]

for i,(role,text,orig,agent_lang,customer_lang) in enumerate(cases,1):
    ev = build(
        from_role=role,
        text_original=text,
        lang_original_hint=orig,
        customer_lang_ui=customer_lang,
        agent_lang_ui=agent_lang,
        backend='ollama',
        model_override='qwen2.5:7b',
        canonical_enabled=True,
        pivot_lang='de',
    )
    assert 'agent' in ev and 'customer' in ev and 'tts' in ev
    if role == 'customer':
        assert ev['agent']['lang'] == agent_lang
        assert ev['tts']['agent_lang'] == agent_lang
        assert ev['tts']['agent_text'] == ev['agent']['text']
        if orig != agent_lang:
            assert ev['agent']['text'].startswith(f'[{agent_lang}] ')
        assert ev['tts']['customer_text'] is None
    else:
        assert ev['customer']['lang'] == customer_lang
        assert ev['tts']['customer_lang'] == customer_lang
        assert ev['tts']['customer_text'] == ev['customer']['text']
        if orig != customer_lang:
            assert ev['customer']['text'].startswith(f'[{customer_lang}] ')
        assert ev['tts']['agent_text'] is None
    assert ev.get('canonical',{}).get('lang') == 'de'
    print(f'case_{i}: PASS role={role} original={orig} agent={agent_lang} customer={customer_lang}')

print('dual_lane_contract: PASS')
PY

echo
echo "## Result"
echo "status: PASS"
echo "log_file: $LOG_FILE"
