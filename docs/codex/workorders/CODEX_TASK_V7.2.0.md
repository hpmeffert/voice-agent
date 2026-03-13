# CODEX_TASK_7.2.0.md
**Version:** 7.2.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-2-0-audio-pipeline-hardening-ffmpeg-convert-json-errors`  
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
Make STT reliable by converting uploaded audio to stable WAV via ffmpeg before Whisper; normalize all errors to JSON so the UI never shows nginx HTML.

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
- Improved audio reliability:
  - Ensure recorded blob is valid (fix “EOFError End of file” issues).
  - Convert browser audio to a stable format server-side (ffmpeg) before Whisper.
- API returns structured error JSON always (no nginx HTML leak in UI).


---

## Implementation Tasks
1. **UI: audio capture hardening**
   - Force a preferred mime type if available: `audio/webm;codecs=opus`.
   - Ensure MediaRecorder `onstop` completes before enabling Send.
2. **API: robust audio decoding**
   - Save uploaded file as `.webm` (or original extension) not always `.wav`.
   - Use `ffmpeg` to convert input to 16kHz mono WAV **before** Whisper:
     - `ffmpeg -y -i input -ac 1 -ar 16000 output.wav`
   - If conversion fails, return `400` with clear message.
3. **Error normalization**
   - Ensure all API errors are JSON: `{ error, detail?, session_id?, user_id? }`.
4. **Docs**
   - Add “If you see EOFError” troubleshooting + why conversion fixes it.


---

## Test Plan
- Record short clips and long clips; confirm Whisper doesn’t crash with EOFError.
- `curl -F file=@...` works with `.webm` input.
- Force an error (send empty file) → UI shows JSON error message, not HTML.


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



