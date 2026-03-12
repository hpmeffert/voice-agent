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
   - UI smoke and WS regression for the target version
   - manual 2-minute browser proof before any release tag
3. Update release documentation before every tag:
   - `v9/docs/release_notes.de.md`
   - `v9/docs/release_notes.en.md`
   - `v9/docs/user_guide.de.md` / `v9/docs/user_guide.en.md`
   - `v9/docs/demo_guide.de.md` / `v9/docs/demo_guide.en.md`
   - `v9/docs/admin_docs.de.md` / `v9/docs/admin_docs.en.md`
4. Create an annotated tag from `release/v9.1` only.
5. Create or update the GitHub Release and attach the DE/EN release note files.

## Documentation guardrails
- Help menu structure must remain fixed:
  1. `Admin token speichern`
  2. `Help` = User Docs only
  3. `Demo Guide`
  4. `Admin Docs`
  5. `Release Notes`
- Version must be visible in header and Help for Admin, Agent, and Customer.
- Silence threshold default stays `1300 ms`.
- UI language `de` shows German docs, `en` shows English docs, all others fall back to English.

## Artifact policy reminder
- Do not commit logs, zip exports, or test artifacts.
- Local evidence belongs under `v9/artifacts/<timestamp>/`.
- The repo must stay clean after test runs.

## License guardrails reminder
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in the core runtime.
- If a copyleft component is required, isolate it as an external sidecar and document the risk.
