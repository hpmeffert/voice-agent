# CODEX_TASK_V8.10.2 — Multi‑Language TTS Translation + FR/IT/ES Voices + Bilingual Docs (DE/EN)

**Base / Branching**
- Base: latest V8.x on `main` (or your current V8 development branch)
- Create branch: `feature/v8.10-translate-tts-fr-it-es`
- Scope: keep changes **inside `v8/`** (do not break V7/V6 trees)

---

## 0) Non‑Negotiables (read first)

### 0.1 Licensing & Commercialization Guardrails (MANDATORY)
We are building a commercial product. Therefore:
- **Prefer permissive OSS** (MIT/Apache-2.0/BSD/ISC).
- **Avoid GPL/AGPL in the core** repo/runtime path.
- **If copyleft is unavoidable** (e.g., Piper), it must be an **external sidecar** service/binary/container, isolated from the core.
- **Do not vendor** copyleft source/binaries into the core repo.
- **Mark license risks** explicitly in PR notes and docs.

### 0.2 Documentation is a Release Gate (MANDATORY)
Every release must update docs and tests that verify docs are not empty and match the implementation.

**Help Menu structure must remain fixed**:
1) **Admin Token speichern** (Admin Token)
2) **Help / User Guide** (user documentation; **NO release notes here**)
3) **Demo Guide** (story-based demo flows)
4) **Admin Docs** (install/start/tests/parameters/dirs/component checks)
5) **Release Notes** (history from V7.0.0 → current)

**Always visible**:
- Current **Version/Release** in **Header** and inside **Help**.

**Silence Threshold default**:
- `SILENCE_THRESHOLD_MS = 1300` (default) unless explicitly changed.

### 0.3 Bilingual Documentation (DE/EN) Behavior (NEW REQUIREMENT)
We must provide **DE + EN versions** for each of:
- User Guide
- Demo Guide (≥ 3 stories/scenarios)
- Admin Docs
- Release Notes (per release + history)

**Display rule**:
- If UI language = **DE** → show **German docs**
- If UI language = **EN** → show **English docs**
- For any other UI language (FR/IT/ES/…) → show **English docs** (fallback)

Docs must be **detailed**, beginner-friendly (“explain like 16-year-old”), include examples and parameter explanations.

---

## 1) Goal of V8.10.x
Add “**TTS Output Language**” feature:
- User speaks/inputs in one language (e.g., German).
- LLM answers in the normal way (source/original answer).
- If user selected a **TTS output language** different from the answer language, the system:
  1) **Translates** the original answer into the selected TTS language.
  2) **Speaks** the translated answer via Piper.
  3) Shows **both**: original answer + translated answer in UI.
  4) Stores both **in logs** (metrics + transcript + answer + translation).

Add FR/IT/ES voices (male for now) so these can be used for TTS output.

---

## 2) Feature Spec

### 2.1 New UI controls (Admin view in V8)
Add controls in the Admin UI:
- **Menu language** dropdown (already present in V7.3/8.3 features; reuse).
- **TTS output language** dropdown:
  - Values: `auto` (match answer language), `de`, `en`, `fr`, `it`, `es`, plus existing languages you support.
  - Default: `auto`.
- Show two answer panes:
  - **Answer (original)** (no escaped `\n` displayed; render properly)
  - **Answer (translated)** only when translation applied
- Under the answer panes, show metrics in a compact card/table (no raw JSON control characters).

### 2.2 API changes (v8/docker/api/app.py)
Enhance `/voice` response & persistence:
- Input fields to `/voice` (Form fields):
  - `user_id`
  - `session_id`
  - `backend`
  - `model`
  - `tts_lang` (new; string; default `auto`)
- Output JSON:
  - `answer` (original)
  - `answer_translated` (nullable)
  - `answer_tts_lang` (final language used for TTS)
  - `translation_ms` (time spent translating; 0 if not used)
  - `metrics`: include `translation_ms` and update `total_ms`
- Persistence:
  - Store translation alongside original in the existing log collection/table:
    - `answer_original`, `answer_translated`, `answer_tts_lang`
    - `translation_ms`

### 2.3 Translation strategy
Translate **only if**:
- `tts_lang != "auto"` AND `tts_lang` differs from detected/selected answer language.

Implementation options (choose safest + consistent with performance):
- Reuse the same LLM backend for translation (default):
  - If backend=ollama → translate with Ollama model (fast local)
  - If backend=openai → translate with OpenAI (if configured)
- Provide a clear, strict translation prompt:
  - “Translate the following answer into <LANG>. Keep meaning, keep formatting. Do not add new facts.”
- Avoid excessive context; translation should be deterministic:
  - temperature low (0.1–0.2)
  - short max tokens

### 2.4 Piper voice support FR/IT/ES
Add voices to Piper mapping:
- Add env vars in `v8/docker/compose.dev.yml`:
  - `PIPER_VOICE_FR`, `PIPER_VOICE_IT`, `PIPER_VOICE_ES`
- Default filenames (examples; adjust to actual Piper voice names you will download):
  - `fr_FR-<male>-medium.onnx`
  - `it_IT-<male>-medium.onnx`
  - `es_ES-<male>-medium.onnx`
- Update `v8/docker/piper/app.py` to pick correct voice by `lang`:
  - Map `fr`, `it`, `es` to their voice files
  - Keep `de`, `en`, `sv`, `no`, `fi` mapping intact
- Document the exact voice files required:
  - `.onnx` + `.onnx.json` for each voice
- Important: voices remain **outside repo** (host-mounted), per licensing guardrails.

---

## 3) Documentation updates (DE + EN)
Update these files under `v8/docs/` (or wherever V8 docs live):

### 3.1 User Guide (DE/EN)
Explain:
- Record/Stop/Send
- How session memory works (user_id/session_id)
- Model switch
- TTS output language:
  - What it does
  - Example: “User speaks DE → answer translated to EN and spoken”
- What gets stored
- Privacy notes (delete history)

### 3.2 Demo Guide (DE/EN) — minimum 3 stories
Each story must start with an engaging question:
- “Kennen Sie das auch … ? / Have you ever … ?”

Include at least:
1) **Customer + virtual agent**: contract/address change / Issue with wallbox
2) **Customer + healthcare**: appointment triage (non-medical disclaimer) "This is not an emergency line! In cas of emergency call 112!"
3) **Admin demo**: show metrics, switch models, switch languages, export transcript, delete session/user

### 3.3 Admin Docs (DE/EN)
Must include:
- Install/Start commands (docker compose)
- Health checks sequence
- Verify components:
  - Whisper working
  - Piper working (voice files exist)
  - DB up (mongo ping)
  - Ollama reachable (tags)
- Parameter list (all env vars + meaning)
- Where directories are, where logs are stored, retention settings
- Troubleshooting section (ports, orphans, slow startup)

### 3.4 Release Notes (DE/EN)
- Add V8.10.x entry to history
- Mention translation feature, FR/IT/ES voices, UI improvements, metrics addition
- Include any breaking changes

### 3.5 Help Menu wiring (UI)
Ensure Help menu shows:
- Admin Token speichern
- User Guide
- Demo Guide
- Admin Docs
- Release Notes
With language switching behavior described in 0.3.

---

## 4) Tests / Checks (must be included)
Add lightweight checks (script or minimal automated test) that verify:
- Docs are not empty (DE + EN files exist and have content > N chars)
- New functionality is added and described
- `/api/models` reachable
- `/api/health` ok
- `/api/voice` returns `answer_translated` when `tts_lang` forces translation (can be mocked with text-only path if needed)
- Retention indexes unchanged and logs now include translation fields

---

## 5) Deliverables
1) Code changes in `v8/` only:
   - API: translation + response fields + logging
   - Piper: FR/IT/ES voice selection
   - UI: language dropdown + TTS language dropdown + improved answer rendering + metrics display
2) Docs DE/EN:
   - User Guide
   - Demo Guide (≥ 3)
   - Admin Docs (incl. test routines)
   - Release Notes (history)
3) Update `v8/docs/TEAM_QUICKSTART...` with:
   - Voice file list including FR/IT/ES
   - How to enable translation / tts_lang
4) PR description must include:
   - Licensing check statement
   - How to run locally
   - What was added

---

## 6) Runbook (for reviewer)
```bash
# from repo root
git checkout feature/v8.10-translate-tts-fr-it-es

docker compose -f v8/docker/compose.dev.yml up -d --build

curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

Manual demo:
- Set UI language to DE, verify German docs.
- Set UI language to EN, verify English docs.
- Set UI language to FR, verify English docs fallback.
- Set TTS output language to EN while speaking German:
  - UI shows original answer (DE) + translated answer (EN)
  - Piper speaks EN voice
  - Metrics include translation_ms
