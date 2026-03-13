# CODEX_TASK_V6.8.0.md

**Project:** Voice Agent  
**Version:** V6.8.0  
**Date:** 2026-03-07  
**Base:** `origin/release/v5.4-azure-stable` as golden baseline for V6 line, with all V6 work isolated under `v6/`.

> This task file is designed for Codex execution. It must be implemented as a PR-ready branch with commits, tests, and updated docs.

## Title
Hands-free recording: auto-stop on silence + optional auto-send (client-side)

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
- Make recording feel conversational by auto-stopping when user is silent for N ms.
- Keep implementation client-side (no streaming yet).

## Required Changes
- UI: implement simple silence detection with Web Audio API RMS threshold (AnalyserNode).
- If RMS below threshold for `SILENCE_MS` (e.g., 1200ms), auto-stop recording.
- Add UI toggles: `Auto-stop on silence` and `Auto-send after stop`.
- Manual Stop still works; do not break existing flow.

## Files / Paths (expected)
- `v6/web/index.html`

## Documentation Updates
- Add notes to `v6/docs/ui/HELP_USER.md` or extend `v6/docs/ui/DEMO_GUIDE.md` about silence threshold + mic permission quirks.

## Acceptance Criteria
- Auto-stop triggers reliably after silence window.
- Auto-send (if enabled) sends immediately after auto-stop.
- No JS console errors; can still Record/Stop/Send manually.

## Tests / Verification (must provide commands + expected output)
- Enable auto-stop; speak then pause; confirm it stops automatically.
- Enable auto-send; confirm it sends after auto-stop.

## Deliverables
- A PR-ready branch with clean commits.
- Updated docs.
- No changes to V5 runtime outside `v6/`.
