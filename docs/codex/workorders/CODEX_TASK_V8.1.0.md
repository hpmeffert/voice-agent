# CODEX_TASK_V8.1.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Customer/Speaker minimal client (separate web) + API auth via anonymous user_id

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
- Add a **Customer/Speaker** client UI as separate web app (minimal: speak or type).
- Customer client must not show admin metrics/params.
- Reuse existing `user_id` + `session_id` concept.

## Deliverables
- `v8/web-customer/` static site with minimal UI (voice + chat input).
- Nginx service `web-customer` mapped to its own port (or path `/customer/`).
- Docs: add Customer UI usage to Help + Demo Guide.

## Implementation Steps
1. Add a second Nginx container or route to serve customer UI.
2. Implement customer UI: record/stop/send + text input; show only conversation.
3. Persist `user_id` in localStorage; `session_id` per conversation; minimal status (listening/thinking/speaking).
4. API: ensure endpoints accept `user_id` and validate session ownership as in v6/v7.
5. Hide admin-only endpoints/routes from customer UI.

## Tests / Verification
- Customer UI loads and can complete a full round-trip voice conversation.
- Customer UI does not display metrics/debug panels.
- Regression: Admin UI still works.

## Notes
Prefer path-based routing `/admin/` and `/customer/` if you want single port; otherwise document ports.
