# CODEX_TASK_7.4.0.md
**Version:** 7.4.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-4-0-crm-transcript-export-with-configurable-mit-templates`  
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
Provide CRM-ready transcript exports (MD/JSON) using **repo-owned, text-only, MIT** templates that can later be admin-editable.

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
- **Conversation transcript export** (structured) improved for CRM:
  - Markdown and JSON exports supported.
  - Includes: date/time, caller/user_id, session_id, language, turns.
- Configurable export templates are **text-only** and **MIT-licensed** (repo-owned).


---

## Implementation Tasks
1. **Export endpoints**
   - `GET /session/{session_id}/export?user_id=...&format=md|json`
   - Ensure ownership check: session belongs to user.
2. **Template system (text-only)**
   - Store templates under `v7/templates/exports/` (MIT, no external assets).
   - Use placeholders like:
     - `{{session_id}}`, `{{user_id}}`, `{{started_at}}`, `{{messages_md}}`
3. **Docs**
   - How to download export and where to customize templates.


---

## Test Plan
- Record a multi-turn conversation → export MD downloads and renders clean.
- Export JSON validates and contains turns in order.


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



