# CODEX WORKORDER — <Version / Topic>

## Goal
Describe the exact change to implement. Keep the goal concrete and testable.

## Scope
- Repo: `voice-agent`
- Branch base: `develop/v9.1` unless a stable hotfix is explicitly requested
- Affected paths:
  - `<path>`
  - `<path>`

## Non-Goals
- No runtime port changes unless explicitly requested.
- No compose rewiring unless explicitly requested.
- No artifacts committed.

## Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS licenses (MIT/Apache/BSD).
- Avoid GPL/AGPL in the core runtime.
- If a copyleft component is required, isolate it as an external sidecar and document the risk.
- Document every new dependency: name, version, license, reason.

## Documentation Rules (MANDATORY)
- Help menu structure must stay exactly:
  1. `Save Admin Token`
  2. `Help` = User Documentation only
  3. `Demo Guide`
  4. `Admin Docs`
  5. `Release Notes`
- Docs must be understandable for a 16-year-old.
- Docs must never be empty.
- UI language switch:
  - DE UI -> DE docs
  - EN UI -> EN docs
  - other UI languages -> EN docs
- Version must be visible in page header and help menu.
- Silence threshold default must remain `1300 ms`.

## Stable / Dev Policy
- Stable branch: `release/v9.1`
- Development branch: `develop/v9.1`
- Demo user remains Admin until user management arrives in `v14.x`.
- New version work starts from `develop/v9.1`.

## Artifact Policy (MANDATORY)
- Test outputs go only under `v9/artifacts/runs/<run-id>/`.
- Never commit artifacts, logs, zip exports, or ws traces.
- `bash scripts/check_no_artifacts_tracked.sh` must pass before commit.
- Every run must produce a `SUMMARY.md` artifact.

## Implementation Checklist
1. Update code.
2. Update DE/EN docs.
3. Run automated regression.
4. Perform manual proof if required.
5. Prepare concise PR summary.

## Required Automated Tests
- `bash scripts/check_no_artifacts_tracked.sh`
- `python3 v9/scripts/check_docs.py`
- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
- `bash scripts/run_full_regression.sh`

## Manual Proof
Describe the 2-minute browser check for Admin/Agent/Customer.

## Deliverables
- Code changes
- Updated docs
- Artifact folder path
- PR-ready commit list
