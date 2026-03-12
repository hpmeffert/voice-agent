# Branching Policy

## Stable and development lines
- `v9.1.15` is the frozen release tag.
- `release/v9.1` is the maintenance branch for hotfix-only work based on that stable line.
- `develop/v9.1` is the development line for `v9.1.16` to `v9.1.19`.

## Where to branch from
- New feature work starts from `develop/v9.1`.
- Branch naming:
  - Feature: `codex/feature/v9.1.16-<short-topic>`
  - Fix: `codex/bugfix/v9.1.16-<short-topic>`
  - Chore: `codex/chore/<short-topic>`
- Hotfixes for released `v9.1.15` start from `release/v9.1`.

## Release flow
1. Finish work on a feature/fix branch from `develop/v9.1`.
2. Run checks:
   - `bash scripts/check_no_artifacts_tracked.sh`
   - `python3 v9/scripts/check_docs.py`
   - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
3. Merge into the intended release line.
4. Create an annotated tag from `release/v9.1`.
5. Create or update the GitHub Release.

## Artifact policy reminder
- Do not commit logs, zip exports, or test artifacts.
- Local evidence belongs under `v9/artifacts/<timestamp>/`.
- The repo must stay clean after test runs.

## License guardrails reminder
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in the core runtime.
- If a copyleft component is required, isolate it as an external sidecar and document the risk.
