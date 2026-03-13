# CODEX_TASK_V8.3.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Transport upgrade: WebSocket gateway + reconnect + backpressure basics

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
- Move from polling to **WebSocket** for real-time conversation.
- Implement reconnect, heartbeat, and minimal backpressure handling.

## Deliverables
- API: `/ws/session/{session_id}` websocket endpoint.
- Client libraries in customer/agent/admin UIs for ws connect + reconnect.
- Docs: troubleshooting realtime.

## Implementation Steps
1. Implement WS endpoint that validates `user_id` or agent token (MVP: demo admin).
2. On connect: stream last N messages from Mongo, then subscribe to Valkey channel and forward.
3. On disconnect: unsubscribe; include ping/pong heartbeat.
4. Client: auto-reconnect with exponential backoff.

## Tests / Verification
- Manual test: refresh browser; chat continues without losing session.
- Load test light: send 20 quick messages; no crash.

## Notes
Later we can extract WS gateway into Rust for latency; keep Python for now.
