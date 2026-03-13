# CODEX_TASK_7.5.0.md
**Version:** 7.5.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-5-0-demo-mode-admin-toggles-demo-user-is-admin`  
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
Add a one-click **Demo Mode** for hands-free conversation loops and admin-only toggles for export/debug (demo user is admin for now).

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
- “Hands-free demo mode”:
  - One-click start and the UI cycles: listen → send → speak → listen.
- Admin-only quick toggles (for now demo user is admin):
  - Toggle CRM export on/off
  - Toggle debug panel on/off


---

## Implementation Tasks
1. **UI: demo mode**
   - Add `Demo Mode` toggle (admin-visible).
   - If ON, Listen Mode is forced ON and UI shows guidance prompts.
2. **Admin-only toggles**
   - With demo admin default, expose toggles.
   - Keep role check in code so later real auth can slot in.
3. **Docs**
   - Add a short “Demo Script” section (what to click, what to say).


---

## Test Plan
- Enable Demo Mode → verify flow loops automatically after speaking.
- Disable Demo Mode → behavior returns to user-selected settings.


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



