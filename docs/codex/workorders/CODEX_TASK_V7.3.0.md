# CODEX_TASK_7.3.0.md
**Version:** 7.3.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-3-0-readable-output-ui-metrics-panel-debug-json`  
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
Improve demo readability: show transcript and answer cleanly (no raw escapes), show metrics below, and keep raw JSON in a collapsible debug section.

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
- **Readable transcript panel**: show transcript + answer nicely (no raw JSON escapes like `\n`).
- **Metrics panel** under the transcript: `audio_read_ms`, `stt_ms`, `llm_ms`, `tts_ms`, `total_ms`.
- Raw JSON still available via a collapsible “Debug JSON” section.


---

## Implementation Tasks
1. **UI: restructure result**
   - Replace single `<pre>` dump with:
     - Transcript block
     - Answer block (render `\n` as newlines)
     - Metrics row/table below
     - Collapsible debug JSON for developers
2. **API: ensure metrics are in a single `metrics` object**
   - Keep compatibility but prefer:
     - `metrics: { audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms }`
3. **Docs**
   - Update demo guide: show how to explain latency using metrics.


---

## Test Plan
- Send a request → transcript and answer render with correct wrapping/newlines.
- Metrics visible under output; debug JSON collapsible.


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



