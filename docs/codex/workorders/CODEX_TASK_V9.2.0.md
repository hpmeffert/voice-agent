# CODEX WORKORDER — V9.2.0 (Consolidate v9.1.18/19 into v9.2 + Admin-only Model Policy + Default 3B)

Date: 2026-03-12
Owner: Cody (strategy) / Codex (implementation)
Branch base: develop/v9.1 (DO NOT touch release/v9.1.17)
Target branch: codex/feature/v9.2.0-consolidation
Release tag later: v9.2.0 (no stable tagging until Cody says so)

## 0) Non-Negotiables / Guardrails
### Licensing & Commercialization Guardrails
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL components in the core.
- If copyleft is unavoidable: isolate as external sidecar; clearly mark license risks.
- Do not introduce new license risk silently.

### Artifact Policy (mandatory)
- NEVER commit artifacts (logs, zips, exports, captures).
- All test outputs go to: `v9/artifacts/runs/<run-id>/...`
- Repo must remain clean: `bash scripts/check_no_artifacts_tracked.sh` must PASS.

### Documentation Rules (mandatory every release)
Help menu structure must ALWAYS be:
1) Admin Token speichern
2) Help (User Documentation) — NOT release notes
3) Demo Guide (story-driven, ≥3 scenarios)
4) Admin Docs (install/start/tests/params/components checks)
5) Release Notes (history from v7.0.0 to current)

Also:
- Version + Release must be visible in Header AND in Help.
- Default Silence Threshold = 1300 ms.
- Docs must be beginner-friendly (like explaining to a 16-year-old).
- Docs must be updated with every feature change (DE/EN where applicable).

## 1) Goal
Close v9.1.x at v9.1.17 (already frozen) and move all planned v9.1.18/v9.1.19 work into v9.2.
Implement the Admin-only Model Policy:
- Default model is qwen2.5:3b
- Admin sets model; customer+agent follow; customer cannot see model; agent can view only.

## 2) Scope (V9.2.0)
### 2.1 Admin-only model configuration (source of truth)
- Add/confirm Admin Settings key: `llm_model` (string)
- Default: `qwen2.5:3b`
- Store in Admin settings DB table/collection (already used for settings).
- Provide API endpoints (if not already existing):
  - GET `/admin/settings` returns llm_model
  - POST `/admin/settings` updates llm_model (admin-only)
- Runtime:
  - All LLM calls use admin-configured model.
  - No per-agent or per-customer override.

### 2.2 UI enforcement
- Customer UI:
  - Must NOT show model anywhere.
  - Must not allow changing model.
- Agent UI:
  - May show model read-only (label only).
  - Must not allow changing model.
- Admin UI:
  - Model dropdown (not free text) to avoid typos.
  - Populate dropdown from `/api/models` or known list.
  - Save persists to DB.

### 2.3 Consolidation + cleanup
- Identify any pending features that were planned for v9.1.18/19 and move them here as v9.2.0 scope items (without touching v9.1.17 stable).
- Ensure all three clients show the SAME version in:
  - Header
  - Help menu line "Version …"

### 2.4 Tests must be upgraded (no flakiness allowed)
- Add/Update automated suite scripts:
  - Search tests
  - Dual-lane WS regression tests
  - UI smoke tests
  - Docs checks
  - No-artifact guard
- Ensure the suite produces ONE consolidated `SUMMARY.md` per run.

## 3) Implementation Steps
1) Create branch from `develop/v9.1`.
2) Implement admin-only model policy in backend.
3) Update Admin UI: model selection dropdown + save.
4) Update Agent UI: model read-only display.
5) Update Customer UI: remove model visibility.
6) Update docs (DE/EN as per current project rule; if bilingual system not yet active, keep EN default and DE optional; do not regress docs rendering).
7) Implement tests + consolidated summary artifact.

## 4) Test Plan (Automated)
Create a new script:
- `scripts/run_v9_2_0_full_regression.sh`

It must run in this order and write outputs to `v9/artifacts/runs/v9.2.0-<ts>/`:
1) `bash scripts/check_no_artifacts_tracked.sh`
2) `python3 v9/scripts/check_docs.py`
3) `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
4) Search tests (admin+agent)
5) WS dual-lane regression (3 scenarios)
6) UI smoke (admin+agent+customer)
7) Generate consolidated `SUMMARY.md` with:
   - PASS/FAIL per step
   - key timings (WS RTT if available)
   - model policy checks (see below)

### Required assertions (Model policy)
Automated checks must verify:
- Customer UI does not show model string anywhere (basic DOM grep or HTTP snapshot)
- Agent UI shows model read-only (string present but no input/select)
- Admin UI has dropdown and persists model
- Backend uses configured model:
  - set model to qwen2.5:3b, run one request, record model used in response/debug
  - set model to qwen2.5:7b, run one request, record model used
  - switch back to qwen2.5:3b as default

## 5) Manual Proof (2 minutes)
Document in `v9/docs/admin_docs.*`:
- Open Admin UI -> set model to qwen2.5:3b -> Save
- Open Agent UI -> confirm model is visible but not changeable
- Open Customer UI -> confirm model not visible
- Send 1 chat -> confirm works

## 6) Deliverables
- Code changes for admin-only model policy
- Updated docs
- Full regression script producing `SUMMARY.md`
- NO artifacts committed

## 7) DoD
- Full regression PASS (or only WARN for latency thresholds if already allowed by policy)
- Model policy enforced across all clients
- Help menu structure correct and docs not empty
- Default Silence Threshold 1300ms unchanged
- No artifacts tracked
- No licensing regressions