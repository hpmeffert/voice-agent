# CODEX_TASK_V8.8.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Security baseline for V8: harden headers, rate limits, input limits

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
- Add basic protections: size limits, rate limiting, secure headers.
- Document admin security checklist.

## Deliverables
- Nginx headers (CSP baseline), API rate limit middleware, max upload size.
- Docs/AZURE_SECURITY style doc but for Mac/dev.

## Implementation Steps
1. Add request size checks (audio bytes), text length, and simple per-IP rate limit in API.
2. Set Nginx headers: X-Content-Type-Options, Referrer-Policy, basic CSP (no inline if possible).
3. Document security items in Admin Docs.

## Tests / Verification
- Try uploading >MAX_AUDIO_BYTES returns 413/400.
- Spam 30 requests quickly triggers 429.

## Notes
Keep CSP practical for demo.
