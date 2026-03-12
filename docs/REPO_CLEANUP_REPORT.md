# Repo Cleanup Report

## Scope
Safe cleanup only. No runtime behavior, ports, compose entrypoints, or API contracts were intentionally changed.

## Categories
### 1. Artifact hygiene
- Strengthened `.gitignore` with explicit sections for OS/IDE, Python, Node/Web, Docker temp, and Artifacts/Logs/Exports.
- Added `scripts/check_no_artifacts_tracked.sh` to fail fast if artifact-like files are ever tracked.

### 2. Removed obvious junk
- Removed tracked artifact log file:
  - `v9/test-logs/V9.0.0_testlog.txt`
- `.gitkeep` in `v9/test-logs/` remains so the folder structure still exists.

### 3. Moved uncertain legacy files to attic
Moved to `attic/2026-03-12-v9-legacy-docs/`:
- `v9/docs/DOCUMENTATION_RULES.md`
- `v9/docs/HELP_ADMIN.md`
- `v9/docs/HELP_USER.md`
- `v9/docs/RELEASE.md`
- `v9/docs/TEAM_QUICKSTART_V6_MAC.md`
- `v9/docs/demo_guide.md`
- `v9/docs/admin/HELP_ADMIN.md`

Reason:
- These files pointed to older version trees (`v6/`, `v8/`) or duplicated active DE/EN documentation paths.
- They were not part of the active v9 help/doc delivery path.

### 4. README update
- Root README now points directly to current version-tree entrypoints and smoke/doc checks.

## Why this is safe
- No active `v9/docker/compose.dev.yml` entrypoint was changed.
- No runtime HTML, Dockerfiles, or API code were changed.
- Cleanup focuses on ignores, stale docs, and tracked artifact hygiene only.

## Checks
- `scripts/check_no_artifacts_tracked.sh`
- `python3 -m py_compile v9/docker/api/app.py`
- `python3 v9/scripts/check_docs.py`
- `bash scripts/run_v9_1_10_smoke.sh`

## No artifacts committed
- Test artifacts remain local under ignored artifact folders.
