# CODEX_TASK_7.1.0.md
**Version:** 7.1.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-1-0-hands-free-listen-mode-auto-stop-on-silence-auto-resume`  
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
Add **Listen Mode** to create a more natural voice conversation: auto-stop on silence, send automatically, and return to listening after TTS playback.

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
- UI “**Listen Mode**” toggle (off by default).
- Automatic voice turn-taking:
  - Record starts automatically when Listen Mode is ON.
  - Recording auto-stops after **silence threshold** (configurable).
  - After TTS playback ends, it returns to **listening** automatically.
- Config options stored in Mongo (per-user settings) with safe defaults.


---

## Implementation Tasks
1. **UI: Listen Mode**
   - Add toggle + status indicator: `Listening / Recording / Sending / Speaking`.
   - Implement WebAudio-based voice activity detection (simple energy threshold) OR MediaRecorder + silence timer:
     - While recording, monitor input level; if below threshold for `SILENCE_MS` (e.g., 900–1400ms), auto-stop.
   - When `audioReply` ends (`ended` event), auto-start recording again **if Listen Mode is ON**.
2. **API: no change in contract**
   - Continue to accept existing `/voice` endpoint.
3. **Persist user settings**
   - Create/extend `users` doc: `{ user_id, role, settings: { listen_mode_default, silence_ms, threshold } }`.
   - Add endpoints:
     - `GET /user/{user_id}` (returns settings)
     - `POST /user/settings` (update settings)
4. **Docs update**
   - Explain how to use Listen Mode and how to disable it.


---

## Test Plan
- Enable Listen Mode → speak → stop talking → recording auto-stops and sends.
- After reply plays, it automatically starts recording again.
- Turn Listen Mode OFF → no auto start/stop; manual buttons still work.
- Verify settings persisted by refreshing page (same user_id) and reloading settings via API.


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



