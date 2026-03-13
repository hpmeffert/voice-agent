# CODEX_TASK — Voice Agent V9.x

**Base branch:** `origin/release/v8.x` (or current stable V8 release branch in the repo)  
**Work branch naming:** `feature/v9.<minor>.<patch>-<short-name>`  
**Scope:** V9 Admin + Security + Docs + i18n foundation (DE/EN)  
**Target:** keep system runnable locally via Docker Compose at all times.

# V9.0.0 — Help System v2 + Bilingual Docs (DE/EN) + Version Visible

## Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer permissive OSS licenses (MIT/Apache-2.0/BSD) for all new dependencies and code.
- Avoid GPL/AGPL in the core product. If a capability is only available under copyleft (e.g., Piper GPL), isolate it as an external sidecar/service with a clean boundary (HTTP).
- Never copy GPL/AGPL code into core repositories. Do not link/compile copyleft code into core artifacts.
- If any dependency has unclear licensing, stop and flag it in the PR description and in `docs/ADMIN_DOCS.md` under “License Risks”.
- Any new template/content added to repo must be authored by us and MIT-licensed (no third‑party assets unless explicitly vetted).


## Help / Documentation Rules (Non‑negotiable)
Help menu structure must always be:
1) Admin Token speichern
2) Help (User Guide) — user documentation only (NO release notes)
3) Demo Guide — story-driven demos (>= 3 scenarios) + an Admin demo
4) Admin Docs — install/start/tests/parameters/dirs/component checks
5) Release Notes — full history from v7.0.0 to current
Additional requirements:
- Version + Release must be visible in page header AND in Help menu.
- Default Silence Threshold = 1300 ms (configurable, but default must be 1300).
- Docs must be written so a 16‑year‑old can follow (simple language, step-by-step, examples).
- Docs must never be empty. Add automated tests that fail if any required doc section is empty.
- For V9: documentation must be bilingual (DE/EN) and switch dynamically with UI language:
  - UI language DE → show DE docs
  - UI language EN → show EN docs
  - any other language → show EN docs (fallback)


## Test Logging Requirement
- Create `v9/test-logs/` (git tracked, but keep files small; commit sample logs only).
- For each release, add a script `v9/scripts/run_tests_<version>.sh` that:
  - runs the automated test suite
  - runs smoke curls (health/models/docs endpoints)
  - saves combined output to `v9/test-logs/<version>_testlog.txt`
- The script must exit non-zero on failures.
- In CI (GitHub Actions), run the test script and upload the test log as an artifact.


## Goal
Create a robust Help system with strict menu structure, bilingual documentation (DE/EN) switching with UI language, and make version/release visible in the header and Help menu. Fix the recurring “empty admin docs / wrong content under Help” issue permanently using automated tests.

## Deliverables
- `v9/` isolated tree (like V6/V8): `v9/docker`, `v9/web`, `v9/docs`, `v9/scripts`, `v9/test-logs`
- Web UI updates:
  - Help menu with 5 items in the exact order
  - Header shows current version/release string
  - Language dropdown (DE/EN + fallback behavior)
- Documentation files (all MIT-authored):
  - `v9/docs/user_guide.en.md`, `v9/docs/user_guide.de.md`
  - `v9/docs/demo_guide.en.md`, `v9/docs/demo_guide.de.md` (>= 3 story scenarios + 1 admin demo)
  - `v9/docs/admin_docs.en.md`, `v9/docs/admin_docs.de.md`
  - `v9/docs/release_notes.en.md`, `v9/docs/release_notes.de.md` (history from v7.0.0 to v9.0.0)
- API endpoint: `GET /api/docs?type=user|demo|admin|release&lang=...` (fallback rules)
- Automated tests: fail if any required doc is empty/missing required headings
- Test runner: `v9/scripts/run_tests_v9.0.0.sh` + sample `v9/test-logs/V9.0.0_testlog.txt`

## Work Plan (Tasks)
1) Create V9 isolated folder structure under `v9/` (no impact on V8 runtime).
2) Implement Help menu UI with exact structure:
   - Admin Token speichern (token UI)
   - Help → User Guide
   - Demo Guide → Demo Guide
   - Admin Docs → Admin documentation
   - Release Notes → Release Notes history
3) Add language switch:
   - UI language DE/EN selectable
   - DE → load DE docs, EN → load EN docs, others → load EN docs
4) Add “Version/Release” line in header AND Help menu (single constant source).
5) Implement `/api/docs` endpoint returning markdown text (validate type/lang; apply fallback).
6) Write full docs content (DE/EN) with examples:
   - User Guide, Demo Guide (>=3 stories + admin demo), Admin Docs, Release Notes.
   - Demo Guide create a story for the Translation between client i.e writes in german and agent writes or speakes in different language i.e english  and this gets translated for the client.
7) Add tests:
   - doc files exist & non-empty
   - required headings exist
   - help menu mapping correct
8) Add test script writing `v9/test-logs/V9.0.0_testlog.txt`.

## Definition of Done (DoD)
- Help menu has exactly 5 items in correct order and renders correct document.
- Header and help show version/release.
- Docs switch DE/EN dynamically; other languages use EN fallback.
- Admin Docs never empty; tests catch regressions.
- Test script passes and produces the test log.
- No new copyleft in core; GPL only as sidecar where unavoidable.

## Test Plan (must produce `v9/test-logs/V9.0.0_testlog.txt`)
- Run `v9/scripts/run_tests_v9.0.0.sh`:
  - start stack
  - curl health/models
  - curl docs (admin/de/en) and assert size > 500 chars
  - run unit tests
  - save output to log
