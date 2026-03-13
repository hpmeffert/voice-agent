# CODEX_TASK_V8.6.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Docs hardening: menu split, admin docs test suite

## Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer permissive OSS licenses: **MIT / Apache-2.0 / BSD**.
- **Avoid GPL/AGPL in core** (API, web UI, shared libs). If a needed component is GPL/AGPL/copy-left, isolate it as an **external sidecar/service** (separate process/container) with clear boundaries.
- Explicitly mark any license risk in PR description and docs.
- Do **not** commit secrets/keys. `.env` stays ignored.

## Help / Documentation Contract (MUST FOLLOW EACH RELEASE)
The UI **must** keep this Help menu structure (and content must NOT be empty):
1) **Admin Token speichern**
2) **Help** (User documentation — *no release notes here*)
3) **Demo Guide** (story-driven demo flows)
4) **Admin Docs** (install/start/tests/params/dirs/component checks; admin-only)
5) **Release Notes** (history from **V7.0.0** to current)

Additional rules:
- **Version/Release** must be visible in **header** and **Help**.
- Default **Silence Threshold = 1300 ms**.
- Every release must add/adjust docs + include an automated test that docs are not empty.

## Goals
- Help menu shows separate pages (user/help/demo/admin/release).
- Admin docs contain: start/stop, directories, component checks (whisper/piper/mongo/valkey/ollama).
- Add automated tests to ensure docs are non-empty + correct menu structure.

## Deliverables
- UI help menu with sub-items; version line included.
- Admin Docs includes test routines and paths.
- CI or local test script `v8/scripts/check_docs.py`.

## Implementation Steps
1. Implement help router with separate markdown files in repo (MIT licensed).
2. Add smoke test script to assert files exist and contain minimum headings.
3. Update Demo Guide with 2 story flows (self-service + call center handoff).

## Tests / Verification
- Run `python v8/scripts/check_docs.py` passes.
- Manual: Help menu displays all 5 required items; none are empty.

## Notes
Make sure Release Notes aggregates from V7 onward.
