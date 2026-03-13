# CODEX_TASK_V6.6.1 — Help Menu Split + Version Label + Admin Test Guide (DEV Admin ON)

**Project:** voice-agent (V6 isolated under `v6/`)  
**Base branch (golden):** `release/v6.6.0` (or latest `release/v6.x` you use)  
**Target branch:** `feature/v6.6.1-help-menu-split`  
**Release tag:** `v6.6.1`  
**Scope:** UI/Docs/Admin UX + Testing documentation (no breaking API changes)

---

## 0) Non‑Negotiables (Guardrails)

### 0.1 Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer **permissive OSS**: **MIT / Apache-2.0 / BSD**.
- **Avoid GPL/AGPL in core** (API, web UI, shared libs).  
- If a copyleft component is unavoidable (e.g., a TTS engine like Piper), keep it as an **external sidecar** or isolated process boundary.  
- **Do not copy** GPL/AGPL code into core.  
- Add a short **License Risk Note** in PR description if any dependency license is uncertain.

### 0.2 No Compose / Port / Orphan Regressions
- V6 must remain isolated under `v6/`.
- Do not modify V5 runtime files.
- Any new docker services/ports must be **namespaced** and documented.
- No hidden bind collisions: if adding ports, make them configurable via env vars.

---

## 1) Goal Summary

### 1.1 UI Help Menu Improvements
- Help should be accessible via a **menu (top right)**.
- Help content must be split into **separate menu items**, not one giant page:
  - **User Help**
  - **Demo Guide**
  - **Admin Guide** (visible only to admin; see DEV override below)
  - **Release Notes / Version**
- Show **Version + Release label** in the menu (e.g., `v6.6.1` + git short SHA if available).

### 1.2 Admin Testing Documentation
- Create an **Admin documentation page/section** that describes how to test the environment end-to-end:
  - Startup checks
  - Health checks
  - Model availability
  - Mongo persistence checks
  - TTL behavior notes
  - Transcript export checks
  - Error cases & expected messages
- This testing doc must be a **separate help menu entry**.

### 1.3 DEV Mode: Everyone is Admin (Temporary)
- While testing, the user should be treated as admin by default:
  - `ADMIN_DEV_MODE=1` makes **all users appear as admin**.
- This is temporary and should be clearly marked as DEV-only.

---

## 2) Deliverables (What must be produced)

### 2.1 UI
- Add a **Help / Menu** control in `v6/web/index.html` (top right).
- Split help content into multiple pages/sections selectable via menu items.
- Add **Version display line** inside menu.

### 2.2 Docs (Repo files)
Create/Update these files under `v6/docs/`:
- `HELP_USER.md` — end-user UI explanation (short, practical)
- `HELP_DEMO_GUIDE.md` — “wow” demo flow and tips
- `HELP_ADMIN.md` — admin-only configuration and templates overview (existing and upcoming)
- `HELP_ADMIN_TESTING.md` — **how to test the environment** (new requirement)
- `RELEASE.md` — release/version notes for the currently running build (or link to release notes)

> All help content must be **text only** (Markdown/JSON). No external assets.

### 2.3 API (Minimal)
- Ensure API provides the UI with:
  - `ui.admin` boolean (true for admins; in DEV mode always true)
  - `ui.version` string (e.g., `v6.6.1`)
  - optional `ui.build` (git short SHA) if easy

If you already have an endpoint returning UI flags (e.g. `/models`), extend it. Otherwise add a lightweight:
- `GET /config` (or similar) returning `ui` info.

### 2.4 Config / Env
- Add env var:
  - `ADMIN_DEV_MODE` default `"0"` in compose
- In `v6/docker/compose.dev.yml`, set it to `"1"` **for now** (testing phase).

---

## 3) Implementation Plan (Step-by-step)

### 3.1 UI Menu + Routing (No framework)
In `v6/web/index.html`:
- Add a **top-right menu button** (three dots / “Help”).
- When clicked, show dropdown with:
  1) User Help  
  2) Demo Guide  
  3) Admin Guide *(admin only)*  
  4) Admin Testing *(admin only)*  
  5) Release / Version  
- When selecting an item:
  - Show content in a modal or side panel (simple, readable).
  - Do not load everything into DOM at once; load on demand.

### 3.2 Loading Help Content
Two acceptable approaches:
- **Option A (recommended):** ship Markdown files in web container and fetch them:
  - Add `v6/docs/help/*.md` → copied into `v6/web/help/` during build (or directly serve from `/help/...`).
  - UI uses `fetch('/help/HELP_USER.md')` etc.
- **Option B:** API serves help content from `v6/docs/` via endpoints.
  - Must be safe and read-only.

Pick **Option A** unless you have a strong reason.

### 3.3 Version line in menu
- Provide `v6.6.1` statically in UI for now, plus:
  - Optionally read from `/api/config` if implemented.
- Display: `Version: v6.6.1 (build abc1234)`.

### 3.4 DEV Admin Override
In `v6/docker/api/app.py` (or central config):
- Add:
  - `ADMIN_DEV_MODE = os.getenv("ADMIN_DEV_MODE","0") == "1"`
- In `is_admin_user(user_id)`:
  - If `ADMIN_DEV_MODE` → return `True`
  - Else → use real role logic (placeholder for future V9)

### 3.5 Admin Testing Documentation
Create `v6/docs/HELP_ADMIN_TESTING.md` covering:
- Start stack: `docker compose -f v6/docker/compose.dev.yml up -d --build`
- Health checks:
  - `curl http://localhost:8080/api/health`
  - `curl http://localhost:8080/api/models`
  - `docker compose ... exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`
- Conversation test:
  - record → stop → send
  - verify session persists
- Persistence test:
  - fetch session endpoint
  - delete session endpoint
  - delete user endpoint
- Transcript export test:
  - generate transcript/protocol file
  - ensure correct format and includes required header metadata (timestamp/session/user)
- Failure tests:
  - simulate Ollama down
  - simulate OpenAI quota
  - verify UI fallback messaging
- Notes on startup delay and warmup.

### 3.6 Update Demo Guide on every new feature
In `HELP_DEMO_GUIDE.md`, add a “What’s new in v6.6.1” section and keep a running list.

---

## 4) Acceptance Criteria

### 4.1 UI
- Menu appears top right.
- Help content is split into separate menu items.
- Admin-only items are hidden when not admin.
- In DEV mode (ADMIN_DEV_MODE=1), admin items are visible.
- Version line is visible and correct.

### 4.2 API
- `ui.admin` and `ui.version` (and optionally `ui.build`) available to UI.
- No breaking changes to `/voice` behavior.

### 4.3 Docs
- All help files exist and are readable in UI.
- Admin testing guide is present, linked in menu, and useful.

### 4.4 Ops/Regression
- `docker compose -f v6/docker/compose.dev.yml up -d --build` works from repo root.
- No new orphan container issues.
- No port collisions introduced.

---

## 5) Files to Touch (Expected)

- `v6/web/index.html` (menu + help modal/panel + version line)
- `v6/docker/api/app.py` (admin dev override + ui flags output)
- `v6/docker/compose.dev.yml` (add `ADMIN_DEV_MODE: "1"`)
- `v6/docs/HELP_USER.md` (new or update)
- `v6/docs/HELP_DEMO_GUIDE.md` (update)
- `v6/docs/HELP_ADMIN.md` (update)
- `v6/docs/HELP_ADMIN_TESTING.md` (new)
- `v6/docs/RELEASE.md` (update)

---

## 6) Tests (Must Run)

### 6.1 Local quick checks
```bash
docker compose -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

### 6.2 Mongo ping
```bash
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

### 6.3 UI smoke
- Open `http://localhost:8080`
- Verify menu items load help docs
- Verify version line shows

---

## 7) PR & Release Checklist

- [ ] Ensure only V6 paths were changed.
- [ ] Confirm no GPL/AGPL libs added to core.
- [ ] Add/Update docs under `v6/docs/`.
- [ ] Update `v6/docs/RELEASE.md` and mention new help menu split.
- [ ] Create tag `v6.6.1` after merge.

### 7.1 PR Description must include
- Summary
- Screenshots (optional)
- License notes (if any)
- How to test

---

## 8) Notes for Later Versions
- V9: Real roles/admin (OTP via RCS/SMS), replace DEV override.
- V7.x: “Listening mode” / auto-continue voice loop after TTS ends.

