# CODEX_TASK_V6.9.0.md

**Project:** Voice Agent  
**Version:** V6.9.0  
**Date:** 2026-03-07  
**Base:** `origin/release/v5.4-azure-stable` as golden baseline for V6 line, with all V6 work isolated under `v6/`.

> This task file is designed for Codex execution. It must be implemented as a PR-ready branch with commits, tests, and updated docs.

## Title
Configurable protocol template v1: repo-owned MIT template + runtime override

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
- Provide standardized protocol export with header fields (date, weekday, time, caller/user id, session id).
- Use repo-owned MIT template (text/markdown/json only).
- Allow template override via mounted file path (admin-editable later).

## Configuration / ENV
- ``PROTOCOL_TEMPLATE_PATH` (default: built-in template path inside container)`

## API Surface
- `GET `/export/protocol?user_id=...&session_id=...``

## Required Changes
- Add `v6/templates/protocol_template.md` (MIT-owned, no external assets).
- API: render export using template placeholders: `{{date}}`, `{{time}}`, `{{weekday}}`, `{{user_id}}`, `{{session_id}}`, `{{messages}}`.
- Support env `PROTOCOL_TEMPLATE_PATH` to load alternate template file at runtime (mounted).
- Add endpoint `GET /export/protocol?user_id=&session_id=` returning rendered markdown/text for download.

## Files / Paths (expected)
- `v6/templates/protocol_template.md`
- `v6/docker/api/app.py`
- `v6/docker/compose.dev.yml (optional mount)`

## Documentation Updates
- Update `v6/docs/TEAM_QUICKSTART_V6_MAC.md` explaining template override + export endpoint.

## Acceptance Criteria
- Export includes correct header + chronological messages with timestamps.
- Swapping template via mounted path changes output without code changes.
- Template remains MIT-owned and contains only text/markdown/json.

## Tests / Verification (must provide commands + expected output)
- Create a session with 2+ turns; call `/export/protocol` and validate placeholders are filled.
- Mount a custom template and verify output changes.

## Deliverables
- A PR-ready branch with clean commits.
- Updated docs.
- No changes to V5 runtime outside `v6/`.
