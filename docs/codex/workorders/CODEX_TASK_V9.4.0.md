# CODEX_TASK — Voice Agent V9.x

**Base branch:** `origin/release/v8.x` (or current stable V8 release branch in the repo)  
**Work branch naming:** `feature/v9.<minor>.<patch>-<short-name>`  
**Scope:** V9 Admin + Security + Docs + i18n foundation (DE/EN)  
**Target:** keep system runnable locally via Docker Compose at all times.

# V9.4.0 — CI Security Pipeline (SAST/Deps/Containers/Secrets) + Artifacts

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
Add CI security checks: dependency audit, container scan, secret scan; always upload test logs as artifacts.

## Deliverables
- GitHub Actions workflow for v9:
  - run tests + `run_tests_v9.4.0.sh`
  - pip-audit / safety
  - trivy scan
  - gitleaks secret scan
  - optional CodeQL
- CI artifacts: test logs and scan reports
- Docs (DE/EN) updated

## Work Plan (Tasks)
1) Create/extend `.github/workflows/v9-ci.yml`.
2) Add steps: build, run test script, pip-audit, trivy, gitleaks, upload artifacts.
3) Update docs explaining what these checks do.
4) Ensure licensing-safe tools.

## Definition of Done (DoD)
- CI runs on PR/push and blocks on failures.
- Test logs uploaded as artifacts.
- Secret scanning active.
- Docs updated.

## Test Plan (must produce `v9/test-logs/V9.4.0_testlog.txt`)
- CI pipeline is the test; locally ensure script writes log and scans can run.
