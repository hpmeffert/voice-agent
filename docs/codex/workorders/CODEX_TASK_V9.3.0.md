# CODEX_TASK — Voice Agent V9.x

**Base branch:** `origin/release/v8.x` (or current stable V8 release branch in the repo)  
**Work branch naming:** `feature/v9.<minor>.<patch>-<short-name>`  
**Scope:** V9 Admin + Security + Docs + i18n foundation (DE/EN)  
**Target:** keep system runnable locally via Docker Compose at all times.

# V9.3.0 — Security Baseline (Headers, CORS, Rate Limits, Admin Gating)

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
Implement baseline security: security headers, strict CORS, rate limiting, consistent admin gating, and docs explaining it.

## Deliverables
- Nginx security headers
- CORS restricted by config
- Rate limiting (nginx preferred)
- Admin token gating verified for all admin endpoints
- Security section in Admin Docs (DE/EN)
- `run_tests_v9.3.0.sh` + log

## Work Plan (Tasks)
1) Add/verify admin token header (`X-Admin-Token`) for admin endpoints.
2) Implement strict CORS (allowed origins from config; default localhost).
3) Add security headers to nginx.conf.
4) Add rate limiting.
5) Tests: headers present, CORS denies unknown origin, admin endpoints protected.
6) Update docs and demo guide; script + log.

## Definition of Done (DoD)
- Headers and CORS active.
- Rate limiting active.
- Admin endpoints protected.
- Tests/log produced.

## Test Plan (must produce `v9/test-logs/V9.3.0_testlog.txt`)
- Script curls headers, simulates bad Origin, triggers rate limit, checks 401/403 without token, writes log.
