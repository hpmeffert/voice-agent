# CODEX_TASK_V6.5.0 — UI Wrap + Help/Demo Guide Foundation (V6-only)

**Branch:** `feature/v6.5.0-ui-wrap-demo-guide`  
**Base:** `origin/release/v6.1.0` (or the latest V6 tag/branch you currently treat as “golden”)  
**Scope:** **V6 only** — all changes must live under `v6/` (no edits to V5 runtime paths).  
**Goal:** Make the V6 UI presentation-ready by fixing long-line rendering and introducing a Help/Demo Guide system that will be **continuously updated** in future releases.

---

## 0) Non‑negotiables (Guardrails)

### 0.1 Licensing & Commercialization Guardrails (MUST)
- Prefer permissive OSS licenses: **MIT / Apache-2.0 / BSD / ISC**.
- Avoid **GPL/AGPL** in the **core** product path.
- If a useful component is copyleft (e.g., Piper), keep it **isolated as a sidecar** (separate container/process) and do **not** link/ship it as a core dependency.
- **Do not** add any dependency without explicitly checking and documenting its license in the PR summary.
- Any license risk must be called out explicitly in “Risks & Follow-ups”.

### 0.2 Version isolation (MUST)
- All V6 work stays inside `v6/`:
  - `v6/docker/...`
  - `v6/web/...`
  - `v6/docs/...`
- Do not modify root `docker/`, `web/`, `docs/` unless explicitly requested (not in this task).

### 0.3 Compose / Ports / Orphans (MUST)
- Keep V6 compose file(s) under `v6/docker/`.
- Use stable, non-conflicting ports; avoid surprises:
  - `web:8080`, `api:8000`, `piper:5002`, `mongo:27017` (or parameterize via env).
- Add/keep `--project-directory` guidance in docs to prevent “docker/docker path” issues.
- Ensure `docker compose down --remove-orphans` is documented for clean resets.

### 0.4 “Always update Demo Guide & UI Wrap”
From V6.5 onward: **every time new features are added**, update:
- the **UI Wrap behavior** (if affected),
- the **Demo Guide** (add a new step or section),
- and the **Help text** explaining the new feature.

This rule applies to V6.6+ tasks as well.

---

## 1) Deliverables

### 1.1 UI: long text wrapping in the “Result” output
**Problem:** JSON/answer gets displayed as a single long line (bad for demos).  
**Fix:** Ensure long text wraps nicely.

**Requirements:**
- Output area must wrap long lines:
  - CSS: `white-space: pre-wrap;` + `word-break: break-word;` + `overflow-wrap: anywhere;`
- Preserve readability for JSON:
  - Keep formatting, but allow wrapping.
- No horizontal scrolling unless absolutely necessary.
- Must work in Chrome/Safari.

**Where:** `v6/web/index.html` (inline styles or CSS file inside `v6/web/`).

---

### 1.2 Help Menu (foundation) + Demo Guide content block
Add a top-right menu (or small “?” button) that opens a modal/panel containing:

1) **User Help**  
- What the UI elements do
- How sessions work (user_id + session_id)
- What models/backends mean

2) **Demo Guide (effectful)**  
A short scripted walkthrough for presentations, e.g.:
- “Warmup check” → verify `/api/health` and `/api/models`
- “Short question” test (fast)
- “Memory demo” (ask follow-up that depends on previous message)
- “Transcript export” (if already in V6.1/6.2)
- “Delete session/user” demo (if enabled)
- “Switch model” demo (ollama 3b vs 7b) if present

**Rules:**
- Store the Help/Demo content in a **MIT-owned** text asset inside the repo:
  - `v6/docs/help_user.md`
  - `v6/docs/demo_guide.md`
- UI loads these files via fetch and renders as plain text/markdown (minimal).
- No external assets, no images required.

---

### 1.3 Docs
Update `v6/docs/TEAM_QUICKSTART_V6_MAC.md`:
- Mention UI wrap improvement.
- Mention Help Menu & Demo Guide.
- Include a short “Demo script” snippet and where to edit it (`v6/docs/demo_guide.md`).
- Reiterate the rule: **every new feature → update Demo Guide + Help**.

---

## 2) Acceptance Criteria

- [ ] “Result” output wraps long lines cleanly on desktop widths.
- [ ] Help menu opens/closes reliably; no console errors.
- [ ] Demo Guide is present, readable, and suitable for a 2–5 minute live demo.
- [ ] Help/Demo content is in-repo, MIT-owned, text-only (no external assets).
- [ ] Docs updated accordingly.
- [ ] No changes outside `v6/`.

---

## 3) Implementation Notes (Suggested Approach)

### 3.1 UI Wrap CSS
Apply to the result container:
```css
pre#result {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}
```

### 3.2 Help modal
- Implement a lightweight modal in plain JS (no new framework dependency).
- On open: fetch `/docs/help_user.md` and `/docs/demo_guide.md` from nginx static.
- Render into `<pre>` or simple `<div>` with `white-space: pre-wrap;`.

### 3.3 Nginx / Static serving
Make sure `v6/docs/` is copied into the web image:
- Update `v6/docker/web/Dockerfile` to copy `v6/docs/` into `/usr/share/nginx/html/docs/`.

---

## 4) Git Hygiene

1) Create branch: `feature/v6.5.0-ui-wrap-demo-guide`
2) Implement changes under `v6/`
3) Update docs
4) Commit message:
   - `V6.5: UI wrap + help menu + demo guide`
5) Push branch and open PR
6) Add release notes draft (optional) referencing:
   - UI wrap improvement
   - Help + Demo Guide and where to edit content
   - Reminder: update Demo Guide each release

---

## 5) Risks & Follow-ups
- If markdown rendering is desired later, use a permissive renderer (MIT/Apache) — but keep V6.5 minimal (text-only).
- Confirm no licensing pitfalls introduced.
