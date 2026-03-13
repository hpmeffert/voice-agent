# CODEX_TASK — Voice Agent V9.x

**Base branch:** `origin/release/v8.x` (or current stable V8 release branch in the repo)  
**Work branch naming:** `feature/v9.<minor>.<patch>-<short-name>`  
**Scope:** V9 Admin + Security + Docs + i18n foundation (DE/EN)  
**Target:** keep system runnable locally via Docker Compose at all times.

# V9.5.0 — Admin Diagnostics + Self-Test Runner + Admin Docs: Full Test Routines

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
Add diagnostics + self-test endpoints and UI. Admin docs must include step-by-step test routines for all components.

## Deliverables
- Admin endpoints: `GET /api/admin/diagnostics`, `POST /api/admin/selftest` (admin gated)
- Diagnostics checks: Mongo/TTL indexes, Piper voices + CLI, Whisper, Ollama, OpenAI (optional)
- Admin UI page showing green/yellow/red matrix
- Admin Docs (DE/EN) with full testing routines and troubleshooting
- `run_tests_v9.5.0.sh` + log

## Work Plan (Tasks)
1) Implement diagnostics module (timings, ok/err).
2) Implement selftest (real calls):
   - small TTS
   - small STT using tiny fixture audio (created by us)
   - small LLM prompt to ollama
3) Add Admin UI to display results.
4) Update Admin Docs with directories, start/stop, tests in order, expected output, fixes.
5) Tests: endpoints gated, keys present.
6) Script + log.

## Definition of Done (DoD)
- Diagnostics returns complete component matrix.
- Selftest performs real checks (or returns partial with clear errors).
- Admin docs contains test routines and troubleshooting.
- Tests and log produced.

## Test Plan (must produce `v9/test-logs/V9.5.0_testlog.txt`)
- Script calls diagnostics/selftest with token and verifies keys exist; writes log.
