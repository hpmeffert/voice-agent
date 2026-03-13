# CODEX_TASK_7.7.0.md
**Version:** 7.7.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-7-0-tts-language-override-demo-trick-placeholders-for-new-languages`  
**Base branch:** `origin/release/v6.10.0` (golden)  
**Scope:** V7 is a **major** release isolated under `v7/`.

## Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer **permissive OSS** (MIT / Apache-2.0 / BSD) for all core components.
- **Avoid GPL/AGPL** dependencies in the **core** runtime. If an essential component is GPL/AGPL (e.g., Piper),
  it MUST be isolated as an **external sidecar service** (separate container/process) with a clean API boundary.
- Do **not** copy GPL/AGPL code into this repo’s core services.
- If any dependency has unclear/changed licensing, **flag it explicitly** in the PR and propose an alternative.
- All newly created templates/docs/code in this task should be **MIT-licensed** (project default).


---

## Goal
Allow overriding TTS language voice (Auto/DE/EN/SV/NO/FI). Prepare extension points for later FR/IT/ES without adding voices yet.

---

## V7 Isolation Rules
- All new code lives under **`v7/`** (no edits to `v6/` files unless explicitly requested by this task).
- Compose uses **unique ports** (see below) to avoid “port already allocated” and orphan issues.
- Use `docker compose --project-directory <repo-root> -f v7/docker/compose.dev.yml ...` in docs to avoid path confusion.

## Standard Ports for V7 Dev (avoid conflicts with V6/V5)
Use these defaults in `v7/docker/compose.dev.yml` to prevent port clashes:

- Web (nginx): **8081** → container 8080
- API (FastAPI): **8001** → container 8000
- Piper sidecar: **5003** → container 5002
- MongoDB: **27018** → container 27017


---

## Deliverables
- **Language selection UX** for TTS voice choice (still auto-detect STT language):
  - Allow overriding TTS voice language (useful for demos).
- Adds placeholders for V7.10 FR/IT/ES but does not implement voices yet.


---

## Implementation Tasks
1. **UI: TTS language override**
   - Dropdown: `Auto (use detected)`, `de`, `en`, `sv`, `no`, `fi`.
2. **API**
   - Accept `tts_lang` form field in `/voice` and pass to Piper if provided.
3. **Docs**
   - Demo guide: show “speak German but TTS English” trick.


---

## Test Plan
- Speak German → set `tts_lang=en` → reply spoken in English voice.
- Auto mode uses detected language as before.


---

## Definition of Done
- `docker compose -f v7/docker/compose.dev.yml up -d --build` succeeds on macOS.
- Web UI loads at `http://localhost:8081` and can record/stop/send.
- Session + user persistence works (MongoDB), demo user is admin by default.
- No changes to V6 runtime paths; V7 is isolated under `v7/`.
- Release notes drafted under `v7/docs/RELEASE_NOTES_v7.x.y.md` using the shared template.


---

## Release Notes Template
## Release Notes (copy into GitHub Release)
### Highlights
- …
### Breaking changes
- … (if any)
### Added
- …
### Changed
- …
### Fixed
- …
### Ops / Deployment notes
- …



