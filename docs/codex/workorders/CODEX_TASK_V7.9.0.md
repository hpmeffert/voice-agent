# CODEX_TASK_7.9.0.md
**Version:** 7.9.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-9-0-admin-settings-store-admin-ui-page`  
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
Introduce an `admin_settings` store and admin UI page to configure retention, thresholds, templates, and feature toggles (still demo-admin by default).

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
- **Admin settings store** (still demo-admin user):
  - Mongo `admin_settings` collection
  - Settings: retention, thresholds, template selection, feature toggles
- Admin Settings UI screen and API endpoints to read/update.


---

## Implementation Tasks
1. **DB + API**
   - `admin_settings` with schema + defaults.
   - Endpoints:
     - `GET /admin/settings`
     - `POST /admin/settings`
   - Apply settings at runtime (listen thresholds, retention, template).
2. **UI**
   - Admin Settings screen accessible from menu.
3. **Docs**
   - Update admin doc: “How to test environment” and settings.


---

## Test Plan
- Change settings via UI → refresh → still applied.
- Verify endpoints return JSON and enforce admin role.


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



