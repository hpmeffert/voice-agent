# CODEX_TASK_V8.5.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Admin view: realtime metrics panel + clean transcript display

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
- Fix transcript display readability: no `\n`/raw JSON clutter.
- Show metrics in a separate panel below, and log metrics to separate collection.

## Deliverables
- UI: transcript+answer rendered nicely; metrics panel below with latency breakdown.
- Mongo: new collection `perf_logs` with TTL index (configurable retention).
- API includes `metrics` but UI renders cleanly.

## Implementation Steps
1. UI: render transcript and answer as paragraphs/bullets; escape control characters.
2. API: keep response JSON for dev, but UI should parse and display fields.
3. Mongo: store `perf_logs`: `{ts, user_id, session_id, audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms, model, backend}` with TTL `PERF_LOG_RETENTION_DAYS`.
4. Add endpoint `/admin/perf/query` (admin-only MVP: demo user).

## Tests / Verification
- Metrics visible and readable; no raw JSON in main transcript view.
- Perf logs can be queried; TTL index exists.

## Notes
Ensure perf_logs is separate from conversation data (compliance).
