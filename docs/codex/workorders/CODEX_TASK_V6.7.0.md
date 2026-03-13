# CODEX_TASK_V6.7.0.md

**Project:** Voice Agent  
**Version:** V6.7.0  
**Date:** 2026-03-07  
**Base:** `origin/release/v5.4-azure-stable` as golden baseline for V6 line, with all V6 work isolated under `v6/`.

> This task file is designed for Codex execution. It must be implemented as a PR-ready branch with commits, tests, and updated docs.

## Title
Performance instrumentation: latency breakdown + simple metrics endpoint

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
- Measure time spent in STT, LLM, and TTS for each request.
- Expose a lightweight metrics endpoint for demo/troubleshooting.

## API Surface
- `GET `/metrics/recent?user_id=...&limit=20``

## Required Changes
- API: capture durations `stt_ms`, `llm_ms`, `tts_ms`, `total_ms` and include them in `/voice` JSON responses.
- Persist timing metadata to `messages` (or a dedicated `metrics` field).
- Add endpoint `GET /metrics/recent?user_id=&limit=` returning last N requests with timings.
- Add UI: show latency breakdown under result panel.

## Files / Paths (expected)
- `v6/docker/api/app.py`
- `v6/web/index.html`

## Documentation Updates
- Extend `v6/docs/ui/DEMO_GUIDE.md` with a short performance section and tuning tips.

## Acceptance Criteria
- `/voice` response includes timing fields (non-negative ints).
- `/metrics/recent` works and is scoped to `user_id` (no cross-user leakage).
- UI renders timings cleanly.

## Tests / Verification (must provide commands + expected output)
- Send 3 voice requests; verify timings appear and are persisted (Mongo).
- Call `/metrics/recent` and verify it returns newest entries.

## Notes
Include tuning guidance (smaller model, lower num_predict, smaller Whisper model). Do not change defaults silently.

## Deliverables
- A PR-ready branch with clean commits.
- Updated docs.
- No changes to V5 runtime outside `v6/`.
