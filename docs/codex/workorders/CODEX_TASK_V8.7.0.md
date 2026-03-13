# CODEX_TASK_V8.7.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Valkey channels design + conversation handoff workflow (A-first)

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
- Define channel naming scheme and message types for: customer, agent, system.
- Add a simple workflow: LLM triage → optional human handoff.

## Deliverables
- Spec doc `v8/docs/transport_channels.md`.
- API flag `handoff_requested` and event types `handoff.request`, `handoff.accept`.
- Agent UI shows 'handoff requested' badge.

## Implementation Steps
1. Implement message types and publish events for handoff.
2. Customer UI can request human; agent can accept; both UIs update status.
3. Persist handoff state in session doc.

## Tests / Verification
- Demo: customer requests human; agent accepts; conversation continues.
- State persists across refresh.

## Notes
Keep licensing clean; Valkey is permissive.
