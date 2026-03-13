# CODEX_TASK_V6.10.0.md

**Project:** Voice Agent  
**Version:** V6.10.0  
**Date:** 2026-03-07  
**Base:** `origin/release/v5.4-azure-stable` as golden baseline for V6 line, with all V6 work isolated under `v6/`.

> This task file is designed for Codex execution. It must be implemented as a PR-ready branch with commits, tests, and updated docs.

## Title
Help menu + Demo Guide + Admin Docs (Option A token gate via /whoami)

## Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer permissive licenses (MIT/Apache-2.0/BSD). Avoid GPL/AGPL in core/runtime dependencies.
- If a useful component is GPL/AGPL (e.g., Piper), keep it as an **external sidecar** process/container with a clean HTTP boundary.
- Do **not** vendor/copy GPL/AGPL code into this repo. Do not link against copyleft libs in the core.
- For any new dependency: record its license (with source link) and **flag risks**. If unclear, choose an alternative.
- Any templates/docs/assets we author for this feature must be **repo-owned** and MIT-licensed.


## Context
We have Voice Agent V6 isolated under `v6/` with:
- `v6/docker/compose.dev.yml` (mongo + api + piper + web)
- `v6/docker/api/app.py` (FastAPI: STT → LLM → TTS + Mongo persistence + TTL + delete endpoints)
- `v6/web/index.html` (UI with persistent `user_id`, session memory, model switch)
- `v6/docs/*` (quickstarts + docs)

We are iterating V6.x on macOS first. Azure adaptation comes later (V9+).


## Goals
- Add top-right Help menu that opens user documentation inside the app.
- Add Demo Guide and keep it updated as features land.
- Add Admin Docs visible only to admins (Option A: token checked via API).

## Configuration / ENV
- ``ADMIN_UI_TOKEN` (default empty/disabled)`

## API Surface
- `GET `/whoami?user_id=...` (reads `X-Admin-Token`)`

## Required Changes
- Web: implement Help menu (top-right) with items: `Help`, `Demo Guide`, `Admin Docs` (admin only).
- Web: render markdown docs stored in repo (no external assets).
- Nginx: serve `v6/docs/**` so UI can fetch markdown locally.
- API: add `GET /whoami?user_id=...` returning `{user_id, is_admin}` where `is_admin=true` iff request header `X-Admin-Token` matches `ADMIN_UI_TOKEN` env.
- Web: store optional admin token in localStorage and send it in `X-Admin-Token` header; hide Admin Docs if not admin.

## Files / Paths (expected)
- `v6/web/index.html`
- `v6/docker/web/nginx.conf`
- `v6/docs/ui/HELP_USER.md`
- `v6/docs/ui/DEMO_GUIDE.md`
- `v6/docs/admin/HELP_ADMIN.md`
- `v6/docker/api/app.py`

## Documentation Updates
- Create/extend HELP_USER + HELP_ADMIN; include an explicit security caveat about demo-grade token gating.

## Acceptance Criteria
- Help menu opens and renders markdown docs correctly.
- Admin Docs hidden unless correct token is present; server still enforces gate.
- Docs are plain markdown in repo and MIT-owned.

## Tests / Verification (must provide commands + expected output)
- No token: Admin Docs hidden; Help/Demo Guide visible.
- With token: Admin Docs visible and loads.
- Restart: admin token persists only client-side; gate still enforced by API.

## Notes
This is a demo-grade gate. Real auth/roles (OTP via RCS/SMS) is planned for V9+.

## Deliverables
- A PR-ready branch with clean commits.
- Updated docs.
- No changes to V5 runtime outside `v6/`.
