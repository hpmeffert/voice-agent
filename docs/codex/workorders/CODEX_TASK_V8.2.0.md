# CODEX_TASK_V8.2.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Call-Center Agent client (Inbox + Chat) — separate UI

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
- Add **Agent UI** with an inbox of active sessions and ability to join a session.
- Agent can chat (text) and optionally speak; customer sees agent responses in real-time via bus.

## Deliverables
- `v8/web-agent/` UI (Inbox + Chat).
- API endpoints: list sessions, join session, post agent message.
- Valkey channels for session events (customer<->agent).

## Implementation Steps
1. Define event message format v1: `{type, session_id, from, payload, ts}`.
2. API: `GET /agent/sessions?status=active`, `POST /agent/join`, `POST /agent/message`.
3. On message post: persist to Mongo + publish to Valkey session channel.
4. Customer UI subscribes via SSE or WebSocket (decide one; WS preferred).
5. Agent UI receives live updates similarly.

## Tests / Verification
- Agent UI shows sessions and can send messages that appear on customer side.
- Mongo stores messages with roles (customer/agent/system).
- Docs updated (Demo Guide: 'Call center handoff').

## Notes
Keep this as MVP; real authentication/roles comes later.
