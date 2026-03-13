# CODEX_TASK — Voice Agent V9.x

**Base branch:** `origin/release/v8.x` (or current stable V8 release branch in the repo)  
**Work branch naming:** `feature/v9.<minor>.<patch>-<short-name>`  
**Scope:** V9 Admin + Security + Docs + i18n foundation (DE/EN)  
**Target:** keep system runnable locally via Docker Compose at all times.

# V9.1.0 — Config Store in MongoDB + Defaults + Silence Threshold 1300ms

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
Introduce a centralized configuration store in MongoDB with safe defaults. Load config at startup, cache it, expose it to admin. Silence threshold default 1300ms.

## Deliverables
- MongoDB `config` collection schema + indexes
- Config loader precedence: defaults → env (optional) → DB overrides
- Admin endpoint: `GET /api/config` returns effective config + source per key
- Minimum config keys: `silence_threshold_ms` (default 1300), retention, feature toggles, max sizes
- Admin Docs (DE/EN) updated with parameter list + examples
- `v9/scripts/run_tests_v9.1.0.sh` + `v9/test-logs/V9.1.0_testlog.txt`

## Work Plan (Tasks)
1) Add `config` collection with one active doc `name="default"`.
2) Implement `load_config()` with caching and precedence.
3) Add admin-gated `GET /api/config`.
4) Wire `silence_threshold_ms` into voice pipeline; default 1300.
5) Update docs (DE/EN) with full parameter list.
6) Tests: defaults work, DB overrides work, endpoint gated.
7) Add test script + log.

## Definition of Done (DoD)
- Default silence threshold is 1300ms.
- Config endpoint shows effective config and sources.
- Docs updated and not empty; tests enforce.
- Test log generated and CI uploads artifact.

## Test Plan (must produce `v9/test-logs/V9.1.0_testlog.txt`)
- Script starts stack, calls `/api/config` with token, asserts 1300 default, inserts override, restarts, asserts override, writes log.
