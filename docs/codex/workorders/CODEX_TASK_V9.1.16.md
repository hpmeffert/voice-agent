# CODEX Workorder — V9.1.16 “Search Fixes + Better Tests”
**Project:** Voice Agent  
**Date:** 2026-03-12 (DE local time)  
**Target branch:** `develop/v9.1.x` (based on `origin/develop/v9.1.x`)  
**Scope:** Fix search reliability across Admin/Agent, harden automated tests, and produce repeatable artifacts without committing them.

---

## 0) Non‑negotiable Guardrails (must follow)
### Licensing & Commercialization Guardrails
- Prefer permissive OSS (MIT/Apache/BSD).  
- Avoid GPL/AGPL in **core/runtime**.  
- If a copyleft component is unavoidable, isolate it as an external “sidecar” (separate container/process), and **document license risk**.  
- Do not introduce new dependencies without explicitly stating license and why it is safe.

### Documentation Quality Rules (must never regress)
Help menu structure is fixed and must be validated every release:
1. **Admin token speichern**
2. **Help** → User Documentation (NOT release notes)
3. **Demo Guide** → at least **3** story-driven demos (“Kennst du das auch…?”)
4. **Admin Docs** → install/start/config/tests/paths/components checks
5. **Release Notes** → cumulative from **V7.0.0 → current**
Also:
- Version + release is visible in **Header + Help** in **Admin/Agent/Customer**.
- Default Silence Threshold remains **1300 ms**.
- Docs are written for a ~16-year-old (clear, examples, step-by-step).
- Docs are updated whenever features change.

### Artifact Policy (critical)
- **Never commit** artifacts/logs/exports/zips to git.
- Store test outputs under: `v9/artifacts/runs/<run-id>/...`
- Ensure `.gitignore` covers: `v9/artifacts/**`, `*.zip`, `*test-log*`, `docker-logs*.txt`, `export*.zip`, etc.
- Run `bash scripts/check_no_artifacts_tracked.sh` before commit → must PASS.

---

## 1) Goal (what V9.1.16 must deliver)
Search currently “sometimes finds nothing” when searching by:
- full `user_id` / `session_id`
- partial fragments like `fe77*` / `wallbox*`
- text fragments inside conversation (transcript/answer)

**V9.1.16 must:**
1. Make search deterministic and explainable:
   - `*` wildcard supported (prefix/suffix/contains) in Admin search UI and API.
   - `auto | session_id | user_id | text` modes behave correctly.
2. Ensure search results include **context** and are clickable:
   - results list → `Open session` shows full conversation under the left panel (Admin) and Agent view history.
3. Add tests that reproduce the earlier failures:
   - tests must fail if search returns empty unexpectedly.
   - tests must create their own data and not depend on existing manual sessions.

---

## 2) Expected UX after V9.1.16
### Admin (8085)
- Single search field + filter dropdown:
  - `auto` detects whether query looks like session/user id; otherwise treat as text.
  - `*` wildcard supported:
    - `fe77*` = prefix
    - `*wallbox*` = contains
    - `*c8e9` = suffix
- Results list shows:
  - session_id, user_id (shortened), last activity, hit snippet(s)
- Clicking a result:
  - loads and shows full conversation **below** the left panel (under spoken reply), scrollable.
  - shows original + translations where present.

### Agent (8087)
- Search remains visible (as now).
- Search by id fragments or text fragments behaves same as Admin.

---

## 3) Backend Work (API)
### 3.1 Search API contract
If existing endpoint exists (e.g. `/admin/search` or `/admin/search/sessions`), keep it and extend safely.

**Requirements:**
- Accept:
  - `q` (string)
  - `mode` in `{auto, session_id, user_id, text}`
  - `limit` default 20, max 100
  - optional `include_snippets=true`
- `*` wildcard:
  - Convert to safe regex (escape everything except `*`).
  - Example:
    - `fe77*` → `^fe77`
    - `*fe77*` → `fe77`
    - `*` alone should be rejected (avoid scanning entire DB)
- Return:
  - list of sessions with: `session_id`, `user_id`, `updated_at`, `hit_type`, `snippets[]`
  - and optionally `total_estimate`

### 3.2 DB indexes (performance)
Ensure indexes exist for:
- `sessions._id` (session_id)
- `sessions.user_id`
- `messages.session_id`
- `messages.user_id`
- Text search:
  - Prefer MongoDB text index on `messages.text_original`, `messages.text_for_agent`, `messages.text_for_customer`, `messages.transcript`, `messages.answer`
  - If using regex search, index fields accordingly and limit scans.
- Add minimal code to create indexes at startup (idempotent).

### 3.3 Safety limits
- Prevent full-table scans:
  - minimum query length (e.g. >= 3 chars) for `text` mode
  - disallow query patterns like `*` or `**`
  - enforce `limit`

---

## 4) Frontend Work (Admin/Agent)
### 4.1 Search field + wildcard help
- Add a tiny tooltip/help line under search:
  - Examples: `wallbox*`, `*wallbox*`, `fe77*`
- Ensure “Enter” triggers search.
- Results list: show snippets and allow click.

### 4.2 Session display
When opening a session from search:
- show full conversation panel:
  - original + translation blocks
  - timestamps if available
  - scrollable, wraps text (no endless single line)
- keep current layout stable.

---

## 5) Tests (must be automated + produce artifacts)
### 5.1 New test script
Create: `v9/scripts/run_v9_1_16_search_tests.sh`

It must:
1. Start/verify stack health (or assume already running but verify endpoints).
2. Seed data:
   - create a new `user_id` + `session_id`
   - inject at least 3 messages containing known tokens, e.g. “wallbox”, “abschlag”, “vertrag”
   - ensure both lanes exist (agent/customer) where relevant
3. Run search assertions:
   - search by exact session_id → returns session
   - search by exact user_id → returns sessions
   - search by prefix `fe77*` style (use seeded ids with known prefix) → returns session
   - search by `*wallbox*` → returns session with snippet containing wallbox
4. Export artifacts:
   - `SUMMARY.md`
   - `http_requests.log` (requests/urls/status)
   - `docker-logs-*.txt` (api/web-admin/web-agent/web-customer)
   - `seed.json` (the ids + inserted messages)
   - `results.json` (raw search results)
   - store all under: `v9/artifacts/runs/v9.1.16-search-<timestamp>/`

### 5.2 Pass/Fail criteria
- If any expected result missing → FAIL and `SUMMARY.md` explains which assertion failed.
- If search response time is very slow (>2s for these tiny seeded datasets), flag in summary (not fail, but warn).

### 5.3 Required checks before commit
- `bash scripts/check_no_artifacts_tracked.sh` → PASS
- `python3 v9/scripts/check_docs.py` → PASS
- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py` → PASS
- `bash v9/scripts/run_v9_1_16_search_tests.sh` → PASS (should be green locally)

---

## 6) Documentation updates (DE/EN)
Update these (both languages; for other UI languages show EN docs):
- `v9/docs/user_guide.(de|en).md`: mention wildcard search and how to use it.
- `v9/docs/admin_docs.(de|en).md`: explain search modes, indexing, and troubleshooting.
- `v9/docs/demo_guide.(de|en).md`: add a demo story around “Wallbox geht immer aus” showing search in Admin.
- `v9/docs/release_notes.(de|en).md`: add V9.1.16 entry (what changed + why).

---

## 7) Deliverables (Definition of Done)
✅ Search works reliably for:
- exact ids
- wildcard ids (`*`)
- text fragments (`*wallbox*`)
✅ Admin and Agent show results + session opens with full conversation (original + translations)
✅ New automated search test script passes and produces artifacts
✅ No artifacts tracked in git
✅ Docs updated DE/EN and help menu structure validated

---

## 8) Output required from Codex (paste back)
1. `git status --porcelain` (must be clean except intentional)
2. `git diff --stat`
3. Path to artifact run folder (e.g. `v9/artifacts/runs/v9.1.16-search-.../SUMMARY.md`)
4. Summary of any new dependencies + license notes (should be none if possible)
5. Commands to run tests

---

## 9) Optional (nice-to-have if low risk)
- Add “search latency ms” in results payload and show it in UI footer.
- Add `X-Request-Id` header and include it in `http_requests.log` to trace slow requests.
