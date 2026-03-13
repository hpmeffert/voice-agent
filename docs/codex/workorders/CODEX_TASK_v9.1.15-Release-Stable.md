# CODEX WORKORDER — Release/Dev Branching Setup (V9.1.15 stable, V9.1.16–V9.1.19 dev)

## Goal
We have a working release: **v9.1.15**.  
We want to label it as the “stable/release line” and treat **v9.1.16–v9.1.19** as “development”.

Deliverables:
1) A stable branch anchored to tag `v9.1.15` (no runtime changes).
2) A development branch for upcoming work (v9.1.16+).
3) Clear repo documentation + lightweight policy (how to work from here).
4) No artifact files tracked. No orphan/ports/compose regressions. No license traps.

## Hard Guardrails (MUST)
- Prefer permissive OSS (MIT/Apache/BSD). Avoid GPL/AGPL in core. If copyleft needed, isolate as external sidecar and document licensing risk.
- Do NOT commit artifacts (logs, zips, exports, runtime dumps). Follow Artifact Policy.
- Do NOT change runtime ports or compose entrypoints as part of this work order.
- Do NOT modify v9.1.15 tag content. It is frozen.

## Preconditions
- Tag `v9.1.15` exists and is pushed.
- Working tree is clean.

Run:
- `git status --porcelain` must be empty.
- If not clean: STOP and report.

---

## Step 1 — Verify current state
Commands:
- `git fetch --all --tags`
- `git tag --list | grep v9.1.15`
- `git show v9.1.15 --oneline --no-patch`

Expected:
- Tag exists and resolves to the release commit.

---

## Step 2 — Create stable branch from the tag
We create a stable branch that always points to the released state.  
Name: `release/v9.1.15-stable`

Commands:
- `git checkout -b release/v9.1.15-stable v9.1.15`
- `git push -u origin release/v9.1.15-stable`

Rules:
- This branch is “maintenance only” (hotfixes) later.
- Do NOT merge dev features here unless explicitly requested.

---

## Step 3 — Create development branch for 9.1.16+
We create a dev line starting from the released tag.

Name: `develop/v9.1.x` (or `develop/v9.1.16-19` if you prefer; default: `develop/v9.1.x`)

Commands:
- `git checkout -b develop/v9.1.x v9.1.15`
- `git push -u origin develop/v9.1.x`

---

## Step 4 — Optional: Branch naming conventions for upcoming releases
We will use:
- Feature branches: `codex/feature/v9.1.16-<short-topic>`
- Fix branches: `codex/bugfix/v9.1.16-<short-topic>`
- Chore branches: `codex/chore/<short-topic>`

All future work for v9.1.16–v9.1.19 starts from `develop/v9.1.x`.

---

## Step 5 — Update documentation to reflect stable/dev policy
Update (small, safe) docs:
- Root `README.md` (or `docs/` if that’s your convention)
Add a section:
- “Release Strategy”
  - v9.1.15 is stable (tag + stable branch)
  - v9.1.16–v9.1.19 are development on develop branch
  - how to create next tags/releases

Also add:
- `docs/BRANCHING_POLICY.md` (short)
- include:
  - which branch to base work on
  - how to cut releases (tag + gh release)
  - artifact policy reminder
  - license guardrails reminder

IMPORTANT:
- Do not change runtime behavior, compose, ports.
- Docs-only change allowed.

Commit:
- `git checkout develop/v9.1.x`
- edit docs
- `git add README.md docs/BRANCHING_POLICY.md`
- `git commit -m "Docs: branching policy (stable v9.1.15 + develop v9.1.x)"`
- `git push`

---

## Step 6 — Checks (MUST PASS)
Run these checks from repo root:
- `bash scripts/check_no_artifacts_tracked.sh`
- `python3 v9/scripts/check_docs.py`
- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`

Also ensure:
- no new untracked artifacts under v9/artifacts are committed

If any fail:
- fix and re-run, then report.

---

## Step 7 — Create PR (optional but recommended)
If docs were updated on `develop/v9.1.x`, open PR into `develop/v9.1.x` (if you prefer PR workflow even on develop).
PR title:
- `Docs: stable/dev branching policy (v9.1.15 stable)`

PR body:
- explain new stable branch + dev branch
- confirm no runtime changes
- confirm checks pass

---

## Final Output required from Codex
Provide:
1) `git branch -vv` output (showing new branches tracking origin)
2) URLs or names of pushed branches
3) Commit hash of docs commit (if created)
4) Output of required checks (PASS)
5) Confirm: "No artifacts tracked", "No runtime changes", "License guardrails respected"

---

## Definition of Done (DoD)
- `release/v9.1.15-stable` exists on origin and points to tag v9.1.15 commit.
- `develop/v9.1.x` exists on origin and starts from v9.1.15.
- Docs updated with branching policy (optional but recommended), committed to develop.
- All checks pass.
- Repo remains clean; no artifacts committed.
- No port/compose/orphan changes introduced.