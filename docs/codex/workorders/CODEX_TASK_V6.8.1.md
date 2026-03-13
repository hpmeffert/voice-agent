# CODEX_TASK_V6.8.1 — UI Output Formatting + Metrics Panel + Telemetry Log (Admin)  
**Project:** voice-agent (V6 isolated under `v6/`)  
**Base branch:** `origin/release/v6.8.0` (or latest `origin/release/v6.x` if 6.8.0 not present)  
**Target branch:** `feature/v6.8.1-output-formatting-telemetry`  
**Release tag:** `v6.8.1`  

---

## 0) Non‑negotiables (Guardrails)
### Licensing & Commercialization Guardrails (MUST)
- Prefer **permissive OSS** licenses: **MIT / Apache‑2.0 / BSD**.
- **Avoid GPL/AGPL** inside the core product. If a GPL component is unavoidable, isolate it as an **external sidecar** (separate container/service) with clean boundaries.
- Actively **flag license risks** in PR description and release notes.
- Any new UI/template assets must be **our own** (MIT) or permissively licensed.

### Repo / Versioning Guardrails
- V6 remains isolated under `v6/`.
- Do **not** break V5/V4 runtime.
- No “orphan/ports/compose” footguns: compose files must be explicit and self-contained.

---

## 1) Goal
Improve readability of the UI output:
- Show **transcript + answer** as normal text (no JSON escape sequences like `\n`).
- Show **metrics/latency** in a separate section under the text output.
- Optionally allow viewing **raw JSON** in a collapsible debug panel.

Additionally, implement **telemetry logging** to MongoDB (separate from conversation data):
- Store per-request metrics + transcript/answer + user/session IDs.
- Add TTL-based retention for telemetry logs.
- Prepare the ground for later analytics features.

---

## 2) Scope
### In scope (V6.8.1)
**UI (`v6/web/index.html`):**
- Replace “dump JSON into `<pre>`” with:
  - A **Transcript** block (text)
  - An **Answer** block (text)
  - A **Metrics** panel below (table or key-value grid)
  - A **Debug** accordion (raw JSON)
- Ensure output wraps nicely:
  - Use `white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;`
  - Keep code-like formatting only for debug JSON.

**API (`v6/docker/api/app.py`):**
- Add a dedicated telemetry collection, e.g. `telemetry_logs`.
- On every `/voice` call (success and failure), write a telemetry record:
  - `created_at` (datetime UTC)
  - `expires_at` (datetime UTC) for TTL
  - `user_id`, `session_id`
  - `backend`, `model`
  - metrics: `audio_read_ms`, `stt_ms`, `llm_ms`, `tts_ms`, `total_ms`
  - `lang`
  - `transcript` (if available)
  - `answer` (if available)
  - `status` ("ok" | "error")
  - `error_code` (optional)
  - `error_detail` (optional)
- Add TTL index on `telemetry_logs.expires_at`.
- Add env var:
  - `TELEMETRY_RETENTION_DAYS` (default: 30)
- Ensure telemetry logging does not block the main flow:
  - Fail-safe: if telemetry write fails, continue responding.

**Docs (Admin-facing):**
- Update `v6/docs/ADMIN.md` (or create if missing) with:
  - How to inspect telemetry logs in Mongo
  - Retention settings
  - Example queries (last 50 logs, slowest calls, errors)

### Explicitly out of scope
- Full analytics dashboards (planned later, e.g. V7.x)
- Authentication/roles UI (planned later)

---

## 3) Detailed Requirements
### 3.1 UI Output Layout
Replace current JSON-only output with something like:
- **Transcript** (rendered text)
- **Answer** (rendered text; preserve line breaks)
- **Metadata row**: user_id, session_id, lang, backend/model
- **Metrics panel** (small table):
  - audio_read_ms
  - stt_ms
  - llm_ms
  - tts_ms
  - total_ms
- **Debug (collapsed by default)**: raw JSON (pretty-printed)

### 3.2 Remove “escaped newline” confusion
- Display `answer` via `textContent` in a block that uses `white-space: pre-wrap`.
- Do not show JSON escapes in the main view.

### 3.3 Telemetry DB
- Mongo collections remain:
  - `users`, `sessions`, `messages` (existing)
  - Add: `telemetry_logs`
- Create TTL index:
  - `telemetry_logs.expires_at` with `expireAfterSeconds: 0`
- Compute `expires_at = created_at + TELEMETRY_RETENTION_DAYS`.

### 3.4 API Response shape
Keep the current response JSON stable (don’t break callers), but:
- Ensure `metrics` object is present and authoritative.
- Avoid duplicating metrics fields at top-level if possible; if currently duplicated, deprecate duplicates but keep for compatibility.

---

## 4) Implementation Steps
1) **API: Telemetry init**
   - Add env var `TELEMETRY_RETENTION_DAYS`.
   - Add `telemetry_col` handle.
   - On startup ensure TTL index exists.

2) **API: Write telemetry**
   - After audio read / STT / LLM / TTS, collect timing.
   - Write one telemetry record per request.
   - On exceptions, write telemetry with `status="error"` and `error_detail`.

3) **UI: New output renderer**
   - Parse API JSON.
   - Render transcript/answer blocks.
   - Render metrics panel.
   - Store debug JSON in `<details>`.

4) **Docs: Admin telemetry**
   - Add Mongo queries examples.

---

## 5) Acceptance Criteria
- UI shows transcript + answer as readable text (no `\n` sequences displayed).
- Metrics visible under the text output (not mixed into main output).
- Raw JSON available via a collapsed debug section.
- Telemetry logs are written to Mongo on each `/voice` request.
- TTL retention works: telemetry docs expire after configured days.
- No new GPL/AGPL dependencies in core; license risks flagged.

---

## 6) Test Plan
### 6.1 Local run
```bash
docker compose -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
```

### 6.2 UI smoke test
- Record a short utterance.
- Verify:
  - Transcript block shows plain text
  - Answer block shows plain text with line breaks
  - Metrics panel populates
  - Debug JSON present

### 6.3 Telemetry verification
```bash
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh
use voice_agent

db.telemetry_logs.find().sort({created_at:-1}).limit(5).pretty()
```

### 6.4 TTL check (index exists)
```javascript
db.telemetry_logs.getIndexes()
```

---

## 7) Deliverables
- PR on branch `feature/v6.8.1-output-formatting-telemetry`
- Updated files:
  - `v6/docker/api/app.py`
  - `v6/web/index.html`
  - `v6/docs/ADMIN.md` (or equivalent)
- Release notes snippet for `v6.8.1`

---

## 8) Release Notes (draft)
**V6.8.1 — Output Formatting + Telemetry**
- UI: clean transcript/answer rendering + metrics panel + debug JSON view
- API: telemetry logging to Mongo with TTL retention (admin-ready)
- Admin docs: how to inspect telemetry logs and retention controls

