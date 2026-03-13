# CODEX_TASK_V9.1.11 — Admin UI Layout + Ergonomics + Metrics Wrap (NO core behavior change)

## 0) Mission
Improve the **Admin Client UI** ergonomics and layout consistency:
- Admin page width/layout should match Agent page (no horizontal scrolling for primary controls).
- Admin parameters should appear via a **drawer/panel** similar to the Agent UI (toggle show/hide).
- Keep controls left-aligned; do NOT push important buttons to the far right.
- Admin Metrics panel (`admin_perf_logs`) must wrap long lines and display nicely without sideways scrolling.

**Hard rule:** Do NOT change Dual-Lane routing logic, translation behavior, WS semantics, or API contracts except UI-visible formatting/structure needed for admin view.

## 1) Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS (MIT/Apache/BSD/ISC). Avoid GPL/AGPL in the core.
- If a copyleft component is unavoidable, isolate as an external sidecar (like Piper).
- Do not add new runtime dependencies without license check + note in docs.
- Do not copy external assets into the repo unless clearly permissive and documented.

## 2) Documentation Quality Rules (MANDATORY EACH RELEASE)
Help menu structure must ALWAYS be correct and non-empty:
1) **Admin Token speichern**
2) **Help** = User Documentation (NOT release notes)
3) **Demo Guide** = story-based (min. 3 scenarios) + Admin demo scenario
4) **Admin Docs** = install/start/config/tests/checks (Whisper/Piper/DB/Ollama/etc.)
5) **Release Notes** = full history from V7.0.0 → current

- All docs must be understandable for a **16-year-old**.
- Version must be visible in:
  - page header AND help menu (all clients: admin/agent/customer)
- Default Silence Threshold remains **1300 ms** (do not change here).

## 3) Artifact Policy for Tests (MANDATORY)
- Write test artifacts under: `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- MUST include:
  - `SUMMARY.md` (PASS/FAIL + key timings)
  - `ENV_SNAPSHOT.txt`
  - `docker-logs-*.txt` (api/web-agent/web-customer/web-admin/piper as applicable)
  - `events-*.jsonl` or `ws_*_events.jsonl` if WS tests run
  - `test-log-v9.1.11-ui-smoke.txt` (human readable)
- Keep only the latest 3 runs locally; older ones may be zipped and removed.
- Do not commit large artifacts; commit only small SUMMARY/test-log samples if needed.

## 4) Scope (What to implement)

### 4.1 Admin Client layout parity with Agent Client
Target: Admin UI width, containers, and visual grid match the Agent UI.
- Use same max-width and responsive layout as agent.
- Remove/avoid horizontal scroll.
- Ensure primary controls are **left-aligned** and visible without scrolling.

### 4.2 Admin Parameters Drawer/Panel (like Agent)
Currently, admin parameters may be in the wrong place or too wide.
Implement:
- A visible header with:
  - Left: **“Admin Client” label + Version badge + WS/API status**
  - Middle/Right: Search bar (single field) + filter dropdown (auto|session_id|user_id|text)
  - Right: **Admin ⚙︎** button toggles drawer/panel visibility
- Drawer default:
  - For now: **visible** (demo user is admin). Later releases can lock by roles.
- Drawer content:
  - Admin settings controls (dropdowns/toggles), but **do not move to far right**.
  - Group controls into sections:
    - “Runtime”
    - “Translation & TTS”
    - “Logging/Performance”
    - “Danger Zone” (reset local storage, clear session, etc.)

**Important:** In V9.1.11 we only adjust layout + rendering. Do not refactor data model.

### 4.3 Admin Metrics panel: wrap and readable
Admin metrics (`admin_perf_logs`) must:
- Wrap long text (CSS: `white-space: pre-wrap; word-break: break-word;`)
- Render metrics in a readable stacked layout (key/value table or cards).
- Keep it inside the standard width container.
- Avoid rendering raw JSON as a single unwrapped line; pretty-print with wrapping.

### 4.4 Button placement ergonomics
- Buttons/dropdowns should be left/top aligned.
- Never require horizontal scrolling to click “Save / Cancel / Apply”.
- If needed, stack controls vertically on small widths.

### 4.5 Consistent version display everywhere
Ensure all three clients show the same version string:
- Admin client header + Help menu
- Agent client header + Help menu
- Customer client header + Help menu

Version string should come from a single source (prefer: API `/version` or config injection).
If a version endpoint already exists, use it; otherwise add a minimal one:
- `GET /version` → `{ "version": "v9.1.11", "release": "..." }`
BUT only if it’s truly minimal and won’t break anything. Otherwise keep current mechanism but make it consistent.

## 5) Tests (MUST be automated as far as possible)

### 5.1 UI Smoke Test (Admin ergonomics)
Create/update script:
- Start stack
- Probe endpoints
- Confirm Admin UI loads (HTTP 200)
- Confirm no horizontal scroll is required for:
  - header controls
  - admin drawer open/close
  - save button visibility
Log results in: `test-log-v9.1.11-ui-smoke.txt`

### 5.2 Browser 2-minute proof checklist (manual)
Write a short checklist in `SUMMARY.md`:
- Open Admin client, confirm header label+version visible.
- Toggle Admin drawer, confirm settings visible without scrolling.
- Check metrics panel wrapping.
- Run search field with:
  - session_id prefix (e.g. `fe774f*`)
  - user_id prefix
  - text fragment
Confirm results list visible and clickable.

### 5.3 Regression Guard
Run existing v9.1.x smoke tests and confirm:
- Dual-lane still works
- WS still connects
- No translation behavior changes
- Voice and chat still functional (basic probe)

## 6) Files to touch (expected)
- `v9/web-admin/index.html` (or equivalent admin client entry)
- Shared CSS or layout components used by agent/admin
- Optional: small helper for version display consistency
- Docs:
  - `Help` user doc (update: mention admin UI changes)
  - `Admin Docs` (update: where to find admin drawer + metrics panel)
  - `Release Notes` v9.1.11 (DE/EN)

## 7) Release Notes (DE/EN)
Create:
- `release_notes.en.md`
- `release_notes.de.md`

Include:
- Highlights: Admin UI width parity, drawer, metrics wrap, consistent version display
- No core behavior changes statement
- Test evidence summary and artifacts path
- Known limitations (if any)

## 8) Definition of Done (DoD)
- Admin UI width matches agent; no horizontal scrolling needed for controls.
- Admin drawer toggles reliably; controls remain visible and left-aligned.
- Admin metrics wraps; readable without sideways scroll.
- Version is consistent across admin/agent/customer header + help menu.
- All docs updated and non-empty; Help menu structure correct.
- Test artifacts generated; summary shows PASS; regression tests pass.
- No new license risks.

## 9) Implementation constraints
- Keep changes minimal and UI-focused.
- Avoid breaking API contracts.
- Avoid adding dependencies.

--- END OF TASK ---