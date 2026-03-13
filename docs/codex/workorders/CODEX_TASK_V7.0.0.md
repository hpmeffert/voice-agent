# CODEX_TASK_7.0.0.md
**Version:** 7.0.0  
**Date:** 2026-03-07 (Europe/Berlin)  
**Branch name:** `feature/v7-0-0-v7-scaffold-isolated-tree-demo-admin`  
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
Create a new major release **V7** isolated under `v7/`, using Mongo persistence and unique ports to avoid compose/orphan conflicts. Demo user is admin by default for testing.

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
- `v7/` directory tree scaffolded:
  - `v7/docker/api/` (FastAPI)
  - `v7/docker/piper/` (Piper sidecar wrapper)
  - `v7/docker/web/` (nginx)
  - `v7/docker/compose.dev.yml`
  - `v7/web/index.html`
  - `v7/docs/TEAM_QUICKSTART_V7_MAC.md`
- V7 uses MongoDB for persistence (same schema concepts as V6) with **demo admin user default**.


---

## Implementation Tasks
1. **Scaffold V7 tree**
   - Create `v7/` with `docker/` + `web/` + `docs/` like V6, but isolated.
   - Copy V6 code as a starting point ONLY into `v7/...` and adjust ports.
2. **Compose (dev)**
   - Add services: `mongo`, `api`, `piper`, `web`.
   - Bind host ports per V7 defaults: 8081/8001/5003/27018.
   - Ensure volumes/mounts use paths under `v7/` and are correct.
3. **Demo admin user default**
   - In V7 API, if `user_id` absent, generate one and mark role = `admin` (for testing only).
   - Persist `users` collection.
4. **Docs**
   - `v7/docs/TEAM_QUICKSTART_V7_MAC.md` with clean run commands and troubleshooting.


---

## Test Plan
- `docker compose -f v7/docker/compose.dev.yml up -d --build`
- `curl -s http://localhost:8081/api/health`
- Open `http://localhost:8081` → record / stop / send → see response + audio.
- Confirm Mongo is reachable:
  - `docker compose -f v7/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`


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



