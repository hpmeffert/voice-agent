# CODEX_TASK_V8.4.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Voice turn-taking (hands-free) MVP for Customer UI

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
- Customer UI can stay in **listen mode**: auto-start recording again after TTS finishes.
- Silence threshold default 1300ms; configurable per user later.

## Deliverables
- Customer UI: Listen Mode toggle; continuous loop record→send→play→record.
- API: return `tts_audio_duration_ms` or client infers end via `ended` event.
- Docs + Demo Guide updated.

## Implementation Steps
1. Implement client state machine: `idle/listening/uploading/thinking/speaking`.
2. Auto-start recording on audio `ended` if listen mode enabled.
3. Stop condition: user presses Stop/End Conversation.
4. Silence detect: use MediaRecorder + WebAudio VAD or use server-side VAD (keep simple).

## Tests / Verification
- Hands-free conversation works for 3 turns without manual clicks.
- Silence threshold default 1300ms respected.
- No runaway loops if TTS fails.

## Notes
Client-side VAD is preferred for responsiveness; keep fallback to manual.
