# CODEX_TASK_V8.0.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
V8 scaffold + Valkey sidecar + transport layer skeleton

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
- Create isolated `v8/` tree (compose, api, web assets, docs).
- Add **Valkey** (Redis-compatible) as sidecar and define a minimal transport abstraction for pub/sub.
- Keep existing v7 UI as **Admin View** in v8 (same functionality), with version visible.

## Deliverables
- `v8/docker/compose.dev.yml` with services: api, web-admin, piper(sidecar), mongo, valkey.
- `v8/docker/api/app.py` with Valkey connection + basic pub/sub helper module.
- `v8/docs/TEAM_QUICKSTART_V8_MAC.md` updated; Help menu contract enforced.

## Implementation Steps
1. Copy v7 working baseline into `v8/` (do not symlink).
2. Add `valkey` service to compose; wire env vars `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`.
3. Implement a small Python module/class: `EventBus` with publish/subscribe (JSON messages).
4. Expose `GET /health` and `GET /models` unchanged; include version string constant `APP_VERSION`.
5. Update Admin UI header/footer + help menu to show version/release.

## Tests / Verification
- `docker compose -f v8/docker/compose.dev.yml up -d --build` works on Mac.
- Health checks for api/web/piper/mongo/valkey.
- Docs test: Help menu sections not empty; version visible.
- Smoke test: publish to Valkey channel and observe subscriber receives message (unit test).

## Notes
Use official Valkey image. Keep Piper as sidecar (license).
