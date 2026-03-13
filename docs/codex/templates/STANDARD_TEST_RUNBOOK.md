# Voice Agent — Standard Test Runbook

## Purpose
Run a repeatable verification for each version/patch:
- Dual-lane correctness for Chat and Voice
- Customer and Agent history consistency after reload
- Search behavior in Admin and Agent
- Help/docs integrity
- Artifact hygiene

## Guardrails
- Prefer permissive OSS licenses (MIT/Apache/BSD).
- Avoid GPL/AGPL in the core; isolate copyleft as sidecar.
- Do not commit artifacts.
- Silence threshold default must remain `1300 ms`.
- Demo user remains Admin until user management is introduced in `v14.x`.
- Branching policy:
  - stable: `release/v9.1`
  - development: `develop/v9.1`

## Help / Docs Rules
Help menu structure must remain:
1. `Save Admin Token`
2. `Help`
3. `Demo Guide`
4. `Admin Docs`
5. `Release Notes`

## Standard Command Order
1. `git status --porcelain`
2. `bash scripts/check_no_artifacts_tracked.sh`
3. `python3 v9/scripts/check_docs.py`
4. `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
5. `docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml up -d --build`
6. `bash scripts/run_full_regression.sh`

## Required Artifact Output
Every run writes to:
- `v9/artifacts/runs/<run-id>/`

Required files:
- `SUMMARY.md`
- `ENV_SNAPSHOT.txt`
- command logs
- optional WS traces / docker logs if a suite needs them

## Summary Format
- Run-ID
- Timestamp
- Branch
- Commit
- Version
- PASS/FAIL for: artifact guard, docs, syntax, search, WS regression, UI smoke, manual proof
- Notes + follow-up actions
- Policy confirmations
