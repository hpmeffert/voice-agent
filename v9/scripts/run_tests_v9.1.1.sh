#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="output"
LOG_FILE="$LOG_DIR/test-log-v9.1.1.txt"
mkdir -p "$LOG_DIR"
exec > >(tee "$LOG_FILE") 2>&1

echo "# V9.1.1 Test Log"
echo "date_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "version_target: v9.1.1"
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
MODELS_JSON=$(curl -sS --max-time 10 "http://localhost:8085/api/models")
echo "$MODELS_JSON" | head -c 500; echo
CONFIG_JSON=$(curl -sS --max-time 10 "http://localhost:8085/api/config?user_id=test-user-v911")
echo "$CONFIG_JSON"

echo
echo "## Existing V9 docs check"
python3 v9/scripts/check_docs.py

echo
echo "## Dual-lane regression (reuse v9.1.0 contract check)"
python3 - <<'PY'
import ast
from pathlib import Path

src = Path('v9/docker/api/app.py').read_text(encoding='utf-8')
mod = ast.parse(src)
needed = {'_normalize_lang','sanitize_tts_text','build_dual_lane_event'}
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
exec('from __future__ import annotations\nimport re\n\n' + '\n\n'.join(chunks), ns)
build = ns['build_dual_lane_event']

cases = [
    ('customer','Meine **Wallbox** geht immer aus.','de','en','de'),
    ('agent','Let us check the *power* supply now.','en','en','de'),
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
    )
    assert 'agent' in ev and 'customer' in ev and 'tts' in ev
    if role == 'customer':
        assert ev['agent']['lang'] == agent_lang
        assert ev['tts']['agent_lang'] == agent_lang
        assert ev['tts']['agent_text'] == '[en] Meine Wallbox geht immer aus.' if agent_lang == 'en' else ev['tts']['agent_text']
    else:
        assert ev['customer']['lang'] == customer_lang
        assert ev['tts']['customer_lang'] == customer_lang
    print(f'dual_lane_case_{i}: PASS role={role}')
print('dual_lane_regression: PASS')
PY

echo
echo "## Sanitizer tests"
python3 v9/scripts/test_tts_sanitize.py

echo
echo "## Result"
echo "status: PASS"
echo "log_file: $LOG_FILE"
