# CODEX_TASK_V7.10.0 — Add FR/IT/ES Languages (Piper male), UI i18n expansion, and defaults

**Branch:** `feature/v7.10.0-lang-fr-it-es`  
**Base:** `origin/release/v7.9.0` (or latest `origin/release/v7.x` if you’ve standardized that)  
**Target Tag (later):** `v7.10.0`

> Goal: Extend the Voice Agent (V7 tree) to support **French, Italian, Spanish** end-to-end:
> - UI language selector + translations (DB-backed)
> - STT language detection/selection compatibility
> - TTS voice mapping in Piper (male voices for now)
> - Documentation + demo guide updates
> - Keep licensing/commercialization safe (avoid GPL/AGPL in core; keep Piper as sidecar).

---

## 0) Guardrails (Non‑negotiable)

### 0.1 Licensing & Commercialization Guardrails (must follow)
- Prefer **permissive OSS**: MIT / Apache-2.0 / BSD.
- **Avoid GPL/AGPL** in the *core* application (API/UI).  
- If a needed component is copyleft (e.g., **Piper**), isolate it as an **external sidecar** (separate Docker service), do not vendor its source into core, do not link/compile it into core binaries.
- Explicitly **flag** any dependency that is not permissive.
- Do **not** commit voice model files (`*.onnx`, `*.onnx.json`) to repo.

### 0.2 Stability Guardrails (no “ports/orphans/compose” regressions)
- V7 must stay **isolated under `v7/`** (like V6 under `v6/`).
- Compose files must have:
  - explicit `container_name` only when needed; otherwise avoid collisions.
  - deterministic project naming guidance (`--project-directory` or `COMPOSE_PROJECT_NAME` in docs).
  - no hard-coded ports that collide with V6/V5; document overrides.
- Provide a **single** canonical command sequence for bring-up/down that avoids orphan containers.

---

## 1) Scope

### 1.1 Languages
Add language support for:
- **French** (`fr`)
- **Italian** (`it`)
- **Spanish** (`es`)

Notes:
- UI labels must be translatable, with **German + English** already existing from V7.3.0 requirement; now add `fr`, `it`, `es` scaffolding.
- Piper: **male voices only** for now; later expansions can add female/variants.

### 1.2 What “support” means (end-to-end)
- UI can be switched to `fr/it/es`, stored per user, applied on load.
- API returns `lang` in responses and uses it for TTS selection.
- Piper sidecar can synthesize in `fr/it/es` using configured voices.
- Demo guide includes steps that demonstrate each language.

---

## 2) Repo Structure

V7 is a **major release** with its own tree (example):
```
v7/
  docker/
    api/
      app.py
      requirements.txt
      Dockerfile
    piper/
      app.py
      requirements.txt
      Dockerfile
    web/
      Dockerfile
      nginx.conf
      start.sh
    compose.dev.yml
  web/
    index.html
    assets/        # keep empty or permissive-only assets
  docs/
    TEAM_QUICKSTART_V7_MAC.md
    HELP_USER.md
    HELP_ADMIN.md
    DEMO_GUIDE.md
```

If your V7 already exists, **extend within that**. Do not change V6 tree.

---

## 3) Configuration (defaults + overrides)

### 3.1 API env vars (add/confirm)
- `DEFAULT_UI_LANG` (default: `de`)
- `SUPPORTED_UI_LANGS` (default: `de,en,fr,it,es`)
- `SUPPORTED_TTS_LANGS` (default: `de,en,fr,it,es,sv,no,fi` as currently supported)
- `CRM_EXPORT_ENABLED_DEFAULT` (unchanged; ensure compatibility)
- Existing retention vars remain.

### 3.2 Piper env vars (voice mapping)
Add env vars with sensible defaults (filenames only, voices live in mounted folder):
- `PIPER_VOICE_FR` (e.g. `fr_FR-<male>-medium.onnx`)
- `PIPER_VOICE_IT` (e.g. `it_IT-<male>-medium.onnx`)
- `PIPER_VOICE_ES` (e.g. `es_ES-<male>-medium.onnx`)

Keep existing:
- `PIPER_VOICE_DE`, `PIPER_VOICE_EN`, `PIPER_VOICE_SV`, `PIPER_VOICE_NO`, `PIPER_VOICE_FI`

> IMPORTANT: choose **real Piper voice names** that exist in the rhasspy/piper-voices catalog. Do not invent filenames.  
> If multiple male voices exist, pick one stable “medium” voice per language and document alternatives.

### 3.3 Compose (V7 compose)
- Ensure `piper` service mounts voices directory from host:
  - macOS example: `${HOME}/models/piper-voices:/voices:ro`
- Ensure API points at `PIPER_BASE_URL=http://piper:5002`
- Ensure Web proxies `/tts/` to Piper.
- Ensure no collisions with V6 ports. Recommend V7 ports:
  - Web: `8090`
  - API: `8010`
  - Piper: `5012`
  - Mongo: `27027`
(If you already use other ports in V7, keep them but document clearly.)

---

## 4) Database / i18n design (DB-backed translations)

### 4.1 Collections (add if missing)
- `ui_translations`
  - document schema:
    ```json
    {
      "_id": "btn.record",
      "de": "Aufnehmen",
      "en": "Record",
      "fr": "Enregistrer",
      "it": "Registra",
      "es": "Grabar",
      "updated_at": "ISODate"
    }
    ```
  - `_id` is a stable translation key.
  - Values are strings; missing language falls back to `en`, then key.

- `user_prefs` (or extend `users`)
  - store `ui_lang` per user:
    ```json
    {
      "user_id": "...",
      "ui_lang": "de",
      "updated_at": "ISODate"
    }
    ```

### 4.2 API endpoints (add/extend)
- `GET /ui/i18n`  
  Returns:
  - supported languages list
  - current user language (from query `user_id`)
  - translation dictionary for requested `lang`
  - fallback language
  Query params:
  - `lang` optional (defaults to user pref or DEFAULT_UI_LANG)
  - `user_id` optional
- `POST /ui/lang`  
  Body:
  ```json
  {"user_id":"...","ui_lang":"fr"}
  ```
  Stores preference (validate against supported list).

### 4.3 Bootstrap translations
- Provide a seed script or code path that ensures core keys exist.
- Keep it minimal but complete for current UI.

---

## 5) UI changes (V7 web/index.html)

### 5.1 Language selector
- Add a dropdown for UI language with `de/en/fr/it/es`.
- On change:
  - call `POST /api/ui/lang`
  - refresh labels immediately without full reload (re-render strings).
- On load:
  - call `GET /api/ui/i18n?user_id=...`
  - set default language and render.

### 5.2 Translation mechanism
- Replace hard-coded UI labels with `t("key")`.
- `t(key)` reads from loaded dictionary.
- Fallback order: current lang -> `en` -> key.

### 5.3 Keep demo-user admin visible (testing mode)
- Ensure demo user is treated as admin in the UI until real RBAC exists (as you requested).
- Add a small badge “Admin (demo)” visible.

### 5.4 Update Help menu + demo guide hooks
- Help menu should include a “Languages” section, updated for FR/IT/ES.

---

## 6) Piper sidecar changes (v7/docker/piper/app.py)

### 6.1 Voice selection
- Extend `pick_voice(lang)` to map:
  - `fr` / `fr-FR` / `fr_FR` → `PIPER_VOICE_FR`
  - `it` / `it-IT` / `it_IT` → `PIPER_VOICE_IT`
  - `es` / `es-ES` / `es_ES` → `PIPER_VOICE_ES`
- Maintain existing mapping for de/en/sv/no/fi.
- If lang unknown: default to `PIPER_VOICE_EN` (or DE if your product prefers German—document choice).

### 6.2 Error handling improvements
- If the ONNX file is missing in `/voices`, return 400 with actionable message:
  - which voice file was expected
  - where `/voices` is mounted
- Add `GET /voices` endpoint (safe) that lists available `.onnx` filenames (no paths).

---

## 7) API changes (v7/docker/api/app.py)

### 7.1 Language propagation
- Ensure `lang` used for TTS is derived as:
  1) Whisper detected language (if available)
  2) else user UI lang (as rough fallback)
  3) else DEFAULT_UI_LANG
- Keep `lang` in response.

### 7.2 Models endpoint
- Ensure `/models` includes supported UI languages and supported TTS languages:
  ```json
  {
    "ollama": {...},
    "openai": {...},
    "ui": {"langs":["de","en","fr","it","es"], "default":"de"},
    "tts": {"langs":["de","en","fr","it","es","sv","no","fi"]}
  }
  ```

---

## 8) Docs updates

Update/ensure:
- `v7/docs/TEAM_QUICKSTART_V7_MAC.md`
  - add FR/IT/ES voice files list and where to place them
  - add UI language selector usage
- `v7/docs/HELP_USER.md`
  - include “Language” section + screenshots optional (no non-permissive assets)
- `v7/docs/HELP_ADMIN.md`
  - include how to seed translations and manage them
- `v7/docs/DEMO_GUIDE.md`
  - add a 3-step demo for each language:
    - speak in French → output + speak-back French
    - same for Italian, Spanish

---

## 9) Tests / Validation checklist

### 9.1 Local bring-up (Mac)
- `docker compose -f v7/docker/compose.dev.yml up -d --build`
- check:
  - `/api/health`
  - `/api/models`
  - `/api/ui/i18n`
  - `/tts/health`
  - `/tts/voices`

### 9.2 Functional checks
- Switch UI language to `fr`; labels change immediately.
- Record French input; confirm:
  - transcript language shows `fr`
  - Piper returns audio (no 500)
- Repeat for `it`, `es`.

### 9.3 Guardrails checks
- No new GPL/AGPL dependencies in API/UI.
- Piper remains sidecar.
- No voice models committed.

---

## 10) Deliverables

1) Code changes under `v7/` only.  
2) Updated compose + docs.  
3) Seed translation mechanism + endpoints.  
4) Verified working FR/IT/ES TTS with real Piper voices.

---

## 11) Release Notes (draft)

Create `v7/docs/RELEASE_NOTES_v7.10.0.md`:
- Highlights: UI i18n + FR/IT/ES + Piper voice mapping
- Config changes (env vars)
- Demo guide updates
- Known limitations (male voices only; billing needed for OpenAI; etc.)

---

## 12) Suggested Git commands (for Codex runner)

```bash
git checkout -b feature/v7.10.0-lang-fr-it-es origin/release/v7.9.0
# implement
git add v7/
git commit -m "V7.10: add FR/IT/ES languages (UI i18n + Piper male voices)"
git push -u origin feature/v7.10.0-lang-fr-it-es
```

---

### Notes / Assumptions
- This task assumes V7 already exists as a tree like V6. If not, first create `v7/` scaffold from the V6 pattern.
- Choose real Piper voice filenames; document the required `.onnx` and `.onnx.json` pairs.
