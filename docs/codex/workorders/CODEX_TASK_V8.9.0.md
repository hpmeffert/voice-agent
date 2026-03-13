# CODEX_TASK_V8.9.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Packaging: stable V8 release + migration notes

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
- Cut a stable V8 release with upgrade notes from V7.
- Ensure all three UIs exist and core flows demo-ready.

## Deliverables
- Release notes, tag, and consolidated quickstart.
- Migration notes: env vars, ports, services.

## Implementation Steps
1. Write release notes template for V8 line.
2. Ensure compose uses non-conflicting ports and includes `--remove-orphans` guidance.
3. Finalize docs and demo guide.

## Tests / Verification
- Clean `docker compose up` from repo root (V8 only).
- No empty doc pages; version visible in header+help.

## Notes
After this, we can start V9 admin auth + OTP modules.
