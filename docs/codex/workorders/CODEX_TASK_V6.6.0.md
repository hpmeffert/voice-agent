# CODEX_TASK_V6.6.0.md

**Project:** Voice Agent  
**Version:** V6.6.0  
**Date:** 2026-03-07  
**Base:** `origin/release/v5.4-azure-stable` as golden baseline for V6 line, with all V6 work isolated under `v6/`.

> This task file is designed for Codex execution. It must be implemented as a PR-ready branch with commits, tests, and updated docs.

## Title
Transcript export UX: per-user toggle + persisted preference + visible export status

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
- Let a user toggle CRM/export transcript generation on/off in the UI (persisted per user).
- Store the preference in MongoDB (`users` collection) and reflect it in exports.

## Configuration / ENV
- ``CRM_EXPORT_DEFAULT_ENABLED` (default: true)`

## API Surface
- `POST `/user/prefs` (JSON: {user_id, crm_export_enabled}) -> {ok}`
- `GET `/user/prefs?user_id=...` -> {crm_export_enabled, ...}`

## Required Changes
- Add UI toggle switch `CRM Export` (on/off) with tooltip.
- API: store user preference `crm_export_enabled` in `users` doc.
- When `crm_export_enabled=false`, API must not generate/export transcript artifacts (but still store messages).
- Expose status in response JSON: `crm_export_enabled` and `export_generated` (bool).

## Files / Paths (expected)
- `v6/docker/api/app.py`
- `v6/web/index.html`
- `v6/docker/api/requirements.txt (if needed)`

## Documentation Updates
- Update `v6/docs/TEAM_QUICKSTART_V6_MAC.md` with CRM Export toggle behavior.

## Acceptance Criteria
- Toggling CRM Export persists across refreshes (same user_id) and is enforced server-side.
- When disabled, no export file is produced and response indicates `export_generated=false`.

## Tests / Verification (must provide commands + expected output)
- Toggle off → send voice → verify response shows export disabled and no file endpoint returned.
- Toggle on → send voice → verify export is generated (existing V6 behavior).
- Restart containers → preference remains (Mongo).

## Deliverables
- A PR-ready branch with clean commits.
- Updated docs.
- No changes to V5 runtime outside `v6/`.
