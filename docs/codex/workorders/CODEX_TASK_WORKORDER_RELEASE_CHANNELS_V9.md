# CODEX WORKORDER — Release Channel Setup (V9.1.15 stable, V9.1.16–V9.1.19 dev)

## Goal
We have a **stable release** at **v9.1.15**. Everything after that should be treated as **development**.
Implement a clean Git/GitHub workflow:
- v9.1.15 stays the **stable release** (tag + GitHub Release already exists)
- v9.1.16–v9.1.19 are **development iterations**
- integrate the **safe repo cleanup** branch via PR (no runtime breakage)
- ensure branch naming and release discipline are consistent going forward

## Non-Negotiables / Guardrails
1) **Do not break** the stable runtime (v9.1.15).
2) **No artifacts** (logs, zips, exports, recordings) committed to Git.
3) **Licensing guardrails**: prefer permissive OSS (MIT/Apache/BSD). Avoid GPL/AGPL in core. If unavoidable, isolate copyleft as a sidecar and mark risks.
4) Keep the Help Menu structure and doc rules stable:
   - (1) Admin token speichern
   - (2) Help = User Docs (NOT release notes)
   - (3) Demo Guide (3+ scenarios/story style)
   - (4) Admin Docs (install/start/tests/params/dirs/component checks)
   - (5) Release Notes history from V7.0.0 → current
   - Version visible in header & Help
   - Silence threshold default = 1300 ms
5) Add/keep repo checks that fail CI if docs empty or artifacts tracked.

## Inputs / Current State (assumptions)
- Stable tag exists: `v9.1.15`
- Current cleanup branch exists and is clean: `codex/chore/repo-cleanup-safe-v9`
- Stable work happens on `main` or a release branch (determine actual default branch)
- We want v9.1.16–v9.1.19 as "development channel"

If anything differs, adapt commands accordingly but preserve intent.

---

# Phase 1 — Verify repo state (no surprises)
Run:
- `git status`
- `git branch --show-current`
- `git remote -v`
- `git tag --list | grep v9.1.15`
- `gh repo view --json defaultBranchRef,nameWithOwner`

Deliver:
- short summary of current branch, default branch, and whether tag `v9.1.15` exists locally & remote.

---

# Phase 2 — Establish “Stable vs Dev” Branching Model
## Target Model
- Stable line: `release/v9.1` (tracks released fixes only)
- Dev line: `develop/v9.1` (for v9.1.16–v9.1.19)
- Feature branches: `codex/feature/v9.1.16-...`, `codex/bugfix/...`

## Steps
1) Create stable branch from the v9.1.15 tag:
   - `git checkout -b release/v9.1 v9.1.15`
   - `git push -u origin release/v9.1`

2) Create dev branch from stable:
   - `git checkout -b develop/v9.1`
   - `git push -u origin develop/v9.1`

3) Add a short note in `docs/` (or README) explaining:
   - v9.1.15 is stable
   - v9.1.16–v9.1.19 happen on develop/v9.1
   - releases are tagged from release/v9.1 only

Deliver:
- commands executed and links to branches.

---

# Phase 3 — Integrate Safe Repo Cleanup via PR (NO runtime changes)
We have branch: `codex/chore/repo-cleanup-safe-v9`

## Requirements
- Must not alter ports/compose runtime entrypoints.
- Must not delete anything uncertain unless moved to `attic/` with README.
- Ensure `.gitignore` + `scripts/check_no_artifacts_tracked.sh` present and PASS.

## Steps
1) Push cleanup branch (if not already):
   - `git checkout codex/chore/repo-cleanup-safe-v9`
   - `git push -u origin codex/chore/repo-cleanup-safe-v9`

2) Open PR into `develop/v9.1` (NOT directly into stable branch):
   - `gh pr create --base develop/v9.1 --head codex/chore/repo-cleanup-safe-v9 --title "Chore: safe repo cleanup (ignore artifacts + attic)" --body "<body below>"`

PR body must include:
- what changed (.gitignore, check script, attic move, cleanup report)
- what did NOT change (runtime/ports/compose)
- checks: docs check PASS, syntax PASS, artifact guard PASS

3) After merge, confirm:
- `develop/v9.1` contains cleanup changes
- stable branch `release/v9.1` remains untouched

Deliver:
- PR link, merge status, final checks.

---

# Phase 4 — Set v9.1.16–v9.1.19 as DEV (no tags/releases yet)
## Policy
- Do NOT create tags/releases for v9.1.16–v9.1.19 until they pass:
  - docs check
  - ui smoke
  - ws regression
  - manual 2-min browser proof

## Steps
1) For each version v9.1.16…v9.1.19:
   - create a placeholder milestone/issue list (GitHub)
   - ensure each has:
     - codex task file
     - tests produce artifacts under v9/artifacts/... (not committed)
     - a test log
2) Add a label convention:
   - `stable`
   - `dev`
   - `needs-manual-proof`
   - `ready-to-tag`

Deliver:
- list of planned dev versions with links to GH issues/milestones.

---

# Phase 5 — Release Notes Template Automation (DE/EN)
Ensure future releases always generate:
- `release_notes.de.md`
- `release_notes.en.md`
- And update:
  - User Guide (DE/EN)
  - Demo Guide (DE/EN)
  - Admin Docs (DE/EN)
  - Release Notes history section

For languages:
- if UI language = DE → show DE docs
- if UI language = EN → show EN docs
- else → show EN docs

Deliver:
- verification that doc generation rule is present in your dev workflow/checks.

---

# Final Deliverables (Codex must output)
1) A concise report:
   - Stable branch name + commit
   - Dev branch name + commit
   - PR link + merge result for cleanup
   - Confirm: v9.1.15 remains stable
2) Command log (copy/paste) of what was executed.
3) Checklist results:
   - artifact guard PASS
   - docs check PASS
   - syntax PASS

---

# PR Body Template (for Phase 3)
## Summary
- Professionalize .gitignore to prevent artifacts/logs/exports from being tracked
- Add guard script to fail if artifacts are tracked
- Move uncertain legacy docs into attic/ with README
- Add cleanup report

## Safety
- No runtime behavior changes
- No compose/ports changes
- No code-path changes

## Checks
- scripts/check_no_artifacts_tracked.sh: PASS
- v9/scripts/check_docs.py: PASS
- python -m py_compile v9/docker/api/app.py: PASS