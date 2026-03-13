# CODEX_TASK_V6.4.1 — Transcript Export Templates (Delta)

**Version:** V6.4.1  
**Base:** `origin/release/v6.4.0` (or the last V6.4.x tag/branch you use)  
**Goal:** Add a **configurable, MIT-safe transcript export template system** (Markdown/JSON only) that can later be edited/replaced by an Admin (file-based now; DB-based later).

---

## 0) Operating Rules (MANDATORY)

### 0.1 Licensing & Commercialization Guardrails (must follow)
- Prefer **permissive OSS**: **MIT/Apache-2.0/BSD/ISC**.
- **Avoid GPL/AGPL** (and strong copyleft) in the **core**.  
- If a copyleft component is unavoidable, it MUST be isolated as an **external sidecar/service** with clear boundaries (no linking/embedding).
- If you propose any new dependency, you must:
  1) name the license,  
  2) justify why it is safe for commercial distribution,  
  3) offer a fallback that avoids it if possible.
- **Do not** introduce a dependency solely for templating if a small in-house implementation suffices.

### 0.2 Delta-only scope
This task is a **delta** on top of V6.4.0: implement only what is required for configurable transcript templates and export output. Do not refactor unrelated parts.

---

## 1) User Story

As a developer/demo operator, I want the system to export a session transcript for CRM/demo purposes as:
- a **standardized conversation protocol document** with header metadata (date/time, caller/user_id, session_id),
- using a **configurable template** that is:
  - **text-based only** (Markdown/JSON) – no external assets,
  - **owned by us** (repo content, MIT safe),
  - **replaceable/editable later** by an Admin (file now; DB later in V9).

---

## 2) Deliverables

### 2.1 Files to add
Create a new directory:
- `v6/templates/`

Add template(s) and schema doc:
- `v6/templates/transcript_default.md.tpl`  (Markdown template)
- `v6/templates/transcript_default.json.schema.json` (optional: schema reference doc)
- (Optional) `v6/templates/README.md` explaining placeholders and usage

**Important:** templates must contain only original text, no copied third-party content.

### 2.2 API changes (v6/docker/api/app.py)
Add support for template-based transcript export:

#### New env/config keys
- `CRM_EXPORT_ENABLED` (default: `"true"`)
- `CRM_EXPORT_FORMAT` (default: `"md"`, allowed: `md|json|both`)
- `CRM_EXPORT_TEMPLATE_MD` (default: `v6/templates/transcript_default.md.tpl`)
- `CRM_EXPORT_INCLUDE_TIMESTAMPS` (default: `"true"`)
- `CRM_EXPORT_TIMEZONE` (default: `"Europe/Berlin"`)

#### New endpoint(s)
1) `GET /session/{session_id}/export`
   - Query:
     - `user_id` (required)
     - `format` optional (`md|json`) overrides default
   - Behavior:
     - Verify session belongs to user_id (same as existing ownership checks).
     - Load messages from Mongo.
     - Produce export output:
       - **Markdown** using template
       - **JSON** using the established session/message schema (no templating needed)
     - Return as downloadable file:
       - `Content-Type: text/markdown` for md
       - `Content-Type: application/json` for json
       - `Content-Disposition: attachment; filename="transcript_<session_id>.<ext>"`

2) (Optional) `GET /templates`
   - Returns which templates are available + current active config (no template contents).

### 2.3 Web UI changes (v6/web/index.html)
Add a button:
- “⬇️ Download Transcript”
- Visible when `session_id` exists.
- Calls:
  - `/api/session/<session_id>/export?user_id=<user_id>&format=md` (default)
- If `CRM_EXPORT_FORMAT=both`, optionally show a small dropdown:
  - “Markdown” / “JSON”

### 2.4 Docs update
Update:
- `v6/docs/TEAM_QUICKSTART_V6_MAC.md`
Add:
- How to configure export format + template path
- Example curl:
  - `curl -OJ "http://localhost:8080/api/session/<id>/export?user_id=<uid>&format=md"`

---

## 3) Template Requirements (Markdown)

### 3.1 Placeholder set (minimum)
Your Markdown template must support these placeholders:
- `{{date}}` (YYYY-MM-DD)
- `{{weekday}}` (Mon/Tue… or localized)
- `{{start_time}}` (HH:MM:SS)
- `{{end_time}}` (HH:MM:SS)
- `{{user_id}}`
- `{{session_id}}`
- `{{backend}}`
- `{{model}}`
- `{{lang}}`
- `{{messages}}` (rendered conversation body)

### 3.2 Messages rendering format
`{{messages}}` should be generated as blocks like:

```
### 10:14:03 User
...

### 10:14:11 Assistant
...
```

If timestamps are disabled, omit `10:14:03` and just render `### User`.

### 3.3 Implementation rule (no heavy template engine)
Implement a small safe replacement utility:
- Load template as text
- Replace placeholders via a strict whitelist mapping
- Never execute code from template
- If template is missing: fallback to a built-in default template string

---

## 4) Mongo Data Usage

Use existing collections:
- `users`, `sessions`, `messages`

Ensure:
- Export uses message ordering by timestamp/created_at ascending.
- Export includes session metadata (created_at, last_updated, backend/model if stored).

If some fields aren’t stored today:
- derive best-effort, but do **not** break existing data.

---

## 5) Security / Abuse Controls
- Enforce ownership: session must belong to `user_id`
- Rate-limit not required yet, but:
  - enforce `MAX_EXPORT_MESSAGES` (default 200)
  - enforce `MAX_EXPORT_BYTES` (default 1–2 MB)
- Return clear errors (400/403/404).

---

## 6) Tests / Verification (manual checklist)
1) Start stack:
   ```bash
   docker compose -f v6/docker/compose.dev.yml up -d --build
   ```
2) Create a short conversation.
3) Export Markdown:
   - UI button downloads `transcript_<session>.md`
   - Header fields present (date/time/user/session)
4) Export JSON:
   - `curl -OJ ".../export?format=json"`
   - JSON parses and includes messages array.
5) Change template path to a custom template:
   - export reflects the changes
6) Verify ownership:
   - wrong user_id cannot export someone else’s session.

---

## 7) Git / PR expectations
- Branch: `feature/v6.4.1-transcript-template-config`
- Commit message style:
  - `V6.4.1: configurable transcript templates (md/json)`
- No changes outside `v6/` unless absolutely necessary.

---

## 8) Notes for V9 (Admin module later)
Do **not** implement now, just keep design-friendly:
- Later, admin can store templates in DB and select active template per tenant.
- Current file-based approach must be cleanly swappable.
