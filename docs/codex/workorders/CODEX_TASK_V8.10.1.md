# CODEX_TASK_V8.10.1 — Multilingual TTS (FR/IT/ES) + Translation Display/Logging (Update)

**Base:** `origin/release/v8.10.0` (or current V8.10 branch/tag)  
**Target:** `v8/` tree (major V8 isolated), preserve V7/V6 trees unchanged.  
**Version:** **V8.10.1** (patch update to V8.10.0)  
**Goal:** Add **Piper voices** for **French (FR), Italian (IT), Spanish (ES)** and wire them into the existing V8.10 “TTS language => translate answer” feature (UI + DB/log).  
**Scope:** **Mac-first** (dev), Azure later.

---

## 0) Licensing & Commercialization Guardrails (MUST FOLLOW)

1. Prefer **permissive licenses** (MIT/Apache-2.0/BSD/ISC) for anything in the **core repo/runtime**.
2. **Avoid GPL/AGPL** dependencies in the core runtime.
3. If a needed component is copyleft (example: **Piper**), keep it as a **sidecar/external service**, not linked into core, and keep all copyleft code isolated.
4. **Never** add 3rd‑party assets (voice models, binaries) into the repo unless their license is explicitly compatible and reviewed.  
   - Piper voice models should remain **outside repo** (host-mounted).
5. If you detect license risk, **stop** and **flag it** in the PR description + docs.

---

## 1) Add FR/IT/ES Piper voice downloads (host-mounted, NOT in repo)

### 1.1 Target directory (Mac)
Use the existing convention (or add if missing):

- `~/models/piper-voices/`

Each voice requires **two files**:
- `*.onnx`
- `*.onnx.json`

### 1.2 Recommended voices (male only for now)
Use these canonical Piper voice identifiers:

- **French:** `fr_FR-siwis-medium`
- **Italian:** `it_IT-paola-medium` *(female name but keep—voice quality good; if we must be strict “male only”, use `it_IT-riccardo-x_low` instead)*
- **Spanish:** `es_ES-sharvard-medium`

**Alternatives (if a URL 404s):**
- Italian alt: `it_IT-riccardo-x_low`
- Spanish alt: `es_ES-davefx-medium`
- French alt: `fr_FR-gilles-low` (if available)

### 1.3 Download commands (Mac — copy/paste)
Create `v8/scripts/download_piper_voices_fr_it_es.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

DEST="${HOME}/models/piper-voices"
mkdir -p "${DEST}"

BASE="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

voices=(
  "fr/fr_FR/siwis/medium/fr_FR-siwis-medium"
  "it/it_IT/paola/medium/it_IT-paola-medium"
  "es/es_ES/sharvard/medium/es_ES-sharvard-medium"
)

for v in "${voices[@]}"; do
  echo "Downloading ${v} ..."
  curl -L --fail -o "${DEST}/$(basename "${v}").onnx" "${BASE}/${v}.onnx"
  curl -L --fail -o "${DEST}/$(basename "${v}").onnx.json" "${BASE}/${v}.onnx.json"
done

echo ""
echo "Done. Files in: ${DEST}"
ls -la "${DEST}" | tail -n +1
```

Make it executable:
```bash
chmod +x v8/scripts/download_piper_voices_fr_it_es.sh
```

Run it:
```bash
v8/scripts/download_piper_voices_fr_it_es.sh
```

---

## 2) Piper sidecar mapping update (FR/IT/ES)

### 2.1 Update voice map
Update the existing `LANG -> voice` mapping (wherever it currently lives, likely `v8/docker/piper/app.py` or similar).

Add:
- `fr` -> `fr_FR-siwis-medium`
- `it` -> `it_IT-paola-medium` (or `it_IT-riccardo-x_low` if you decide “male only strictly”)
- `es` -> `es_ES-sharvard-medium`

### 2.2 Ensure the container sees the voices dir
In `v8/docker/compose.dev.yml` (or equivalent), ensure:

- `piper` has a volume mount:
  - `${HOME}/models/piper-voices:/voices:ro`
- Piper reads voices from `/voices`.

---

## 3) Translation display + persistence (already in V8.10) — extend for FR/IT/ES

**Requirement (from V8.10):**  
If **TTS output language** is set to a language, **translate** the original answer into that language.  
- Show translation in an additional UI panel.  
- Store translation alongside original in logs.

### 3.1 Expand allowed languages list
Add FR/IT/ES to:
- UI language selectors (if present)
- API validation (if present)
- Any DB schema constraints

### 3.2 DB/log fields
Ensure log entry includes:
- `tts_lang` (e.g., `fr`, `it`, `es`)
- `answer_original`
- `answer_translated`
- timings: `audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms`
- identifiers: `user_id, session_id`

---

## 4) Help/Docs updates (mandatory)

Update `v8/docs/...` with:
- How to download FR/IT/ES voices (script usage)
- Where voices live (host path)
- How to validate Piper health + a test TTS request
- Mention that voices are **not** committed to git

Also ensure the **Help menu structure** remains correct:
1) Admin token speichern  
2) Help (User docs only)  
3) Demo Guide  
4) Admin Docs (install/start/tests/parameters/components checks)  
5) Release Notes (history from V7 onward)

---

## 5) Tests & validation

### 5.1 Smoke test commands
```bash
docker compose -f v8/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

### 5.2 Piper FR/IT/ES test (inside piper container)
```bash
docker compose -f v8/docker/compose.dev.yml exec -T piper python -c "import json,urllib.request; req=urllib.request.Request('http://localhost:5002/tts', data=json.dumps({'text':'Bonjour','lang':'fr'}).encode(), headers={'Content-Type':'application/json'}, method='POST'); print('ok', len(urllib.request.urlopen(req).read()))"
docker compose -f v8/docker/compose.dev.yml exec -T piper python -c "import json,urllib.request; req=urllib.request.Request('http://localhost:5002/tts', data=json.dumps({'text':'Ciao','lang':'it'}).encode(), headers={'Content-Type':'application/json'}, method='POST'); print('ok', len(urllib.request.urlopen(req).read()))"
docker compose -f v8/docker/compose.dev.yml exec -T piper python -c "import json,urllib.request; req=urllib.request.Request('http://localhost:5002/tts', data=json.dumps({'text':'Hola','lang':'es'}).encode(), headers={'Content-Type':'application/json'}, method='POST'); print('ok', len(urllib.request.urlopen(req).read()))"
```

---

## 6) Deliverables

1. Script: `v8/scripts/download_piper_voices_fr_it_es.sh`
2. Updated Piper mapping for `fr/it/es`
3. UI + API allow FR/IT/ES for translation+TTS
4. Docs updated (Admin docs + demo guide if needed)
5. PR description includes:
   - What changed
   - How to download voices
   - Licensing note: voices stay outside repo; Piper remains sidecar

---

## 7) Acceptance criteria

- UI can select `fr/it/es` as TTS output language.
- After speaking, system:
  - generates answer (original language),
  - translates to `tts_lang`,
  - shows both in UI (separate fields),
  - speaks translated audio with Piper,
  - logs translation + timings in log store.
- No Piper voices or other 3rd-party assets committed to repo.
- All services start cleanly with documented commands.
