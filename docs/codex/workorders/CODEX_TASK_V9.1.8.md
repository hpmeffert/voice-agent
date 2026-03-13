# CODEX TASK — V9.1.8 — Admin Console: Performance Toggle + Search (Sessions/Messages)
Project: voice-agent (V9 tree)
Target: Patch release V9.1.8 (no breaking changes)
Branch: feature/v9.1.8-admin-search-perf

## 0) Non-Negotiables (Guardrails)
### Licensing & Commercialization Guardrails (MUST)
- Prefer permissive OSS (MIT/Apache/BSD). Avoid GPL/AGPL in core.
- If any copyleft tool is needed (e.g., Piper), keep it as isolated sidecar only.
- DO NOT add dependencies with unclear/commercially restrictive licensing.
- Flag any license risk explicitly in PR notes.

### Stability Guardrails (MUST)
- No regressions in dual-lane routing (customer/agent lanes + correct TTS language).
- No regressions in existing endpoints and UIs (agent/customer).
- Admin features must be optional and off by default where they add overhead.

### Docs Guardrails (MUST)
- Help menu must ALWAYS have the following structure (and content must not be empty):
  1) "Save Admin Token"
  2) "Help" => User Documentation (NOT release notes)
  3) "Demo Guide" (>=3 story-driven scenarios)
  4) "Admin Docs" (install/start/config/test routines; all admin parameters)
  5) "Release Notes" (history from V7.0.0 to current)
- Docs must be written for a 16-year-old (clear, step-by-step).
- DE/EN requirement: if UI language is DE => show DE docs; if EN => show EN docs; otherwise show EN.
- Update docs to include ALL new features of this release.

### Global Defaults (MUST)
- Silence threshold default: 1300 ms (where applicable).

### Artifact Policy (MUST)
- Test artifacts go into `artifacts/` with timestamp folder name, e.g. `artifacts/2026-03-10_v9.1.8/`
- Always generate:
  - `SUMMARY.md` (PASS/FAIL table + links to logs)
  - `ENV_SNAPSHOT.txt`
  - `docker-logs-*.txt`
  - `test-log-v9.1.8.txt`
- Keep artifacts out of git by default:
  - Add `artifacts/` to `.gitignore`
  - Provide a small helper script to zip artifacts for sharing (not committed outputs)
- Only commit small text logs if explicitly requested; otherwise keep them local.

---

## 1) Goal
Add an Admin-controlled ability to:
1) Toggle performance/latency measurement & logging ON/OFF (to avoid overhead when not needed).
2) Search across sessions and messages:
   - by session_id (supports partial, e.g. "fe774f*")
   - by user_id (supports partial)
   - by text search (word/fragment search; best-effort)
3) Show results in a minimal Admin UI page (or Admin section) with clickable session open.

This release should be usable for operations:
- turn metrics logging on for a demo window (e.g., 10 minutes)
- later turn it off again
- search for a conversation using partial ids or text fragment
- open the session and view history

---

## 2) Scope & Architecture

### 2.1 Data model additions (MongoDB)
Add a separate collection for performance/admin logs (NOT the conversation messages collection):
- `admin_perf_logs`
Fields:
- ts (datetime)
- user_id (string)
- session_id (string)
- direction (enum: "customer_to_agent" | "agent_to_customer" | "system")
- audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms (numbers; optional)
- transcript (string; optional)
- answer (string; optional)
- model_backend, model_name (string)
- agent_lang_ui, customer_lang_ui (string)
- flags: { voice: bool, chat: bool, translation_used: bool }
Indexes:
- ts descending
- session_id
- user_id
TTL index (optional, controlled by env): `expires_at` with `LOG_RETENTION_DAYS` default 30

### 2.2 Admin settings persistence
Introduce a dedicated collection:
- `admin_settings`
Key/value style, example document:
- _id: "global"
- perf_logging_enabled: bool (default false)
- perf_logging_sample_rate: float (0.0..1.0; default 1.0)
- perf_logging_retention_days: int (default 30)
- search_max_results: int (default 50)
- allow_text_regex_fallback: bool (default true; safer limits)
- updated_at

Also add a simple in-memory cache with short TTL (e.g., 5s) to avoid DB hit per request.

### 2.3 API additions
Add endpoints under `/admin` (protected by existing admin token mechanism if present; if none exists yet, keep it accessible but document that it is “demo-admin only” until user mgmt in V14).

Required:
- `GET /admin/settings` -> returns current settings
- `POST /admin/settings` -> updates settings (validate ranges; persist to DB)
- `GET /admin/search` -> search sessions/messages
  Query:
  - q=string
  - mode=auto|session_id|user_id|text
  - limit=1..N (default from settings; max hard cap 200)
Returns:
  - matches: [{session_id, user_id, last_ts, snippet, match_type, score?}]
  - meta: {mode_used, limit, took_ms}

Search logic:
- session_id/user_id:
  - treat `*` as wildcard; internally convert to regex safely:
    - escape input except `*`
    - `*` => `.*`
    - anchor by default as substring match, not full string, but limit complexity
- text:
  - Prefer Mongo `$text` if text index exists on messages (create index)
  - Fallback to case-insensitive regex on `transcript` + `answer` with limit + timeouts
  - Always cap scan: use recent window default (e.g., last 7 days) unless specified.
Add `since_days` optional param for text search.

### 2.4 Performance logging integration
Where metrics already exist (audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms):
- Only write to `admin_perf_logs` if `perf_logging_enabled == true`
- Apply sampling: if sample_rate < 1.0, log only some requests
- Logging must not break request; failures are swallowed and recorded to server log.

---

## 3) UI changes (Admin Console)
Add an Admin page/panel (existing admin UI area is OK):
- Section A: Performance toggle
  - Switch ON/OFF
  - Sample rate slider (1.0 default)
  - Retention days (default 30)
  - Save / Cancel
- Section B: Search
  - Search bar
  - Filter dropdown: auto | session_id | user_id | text
  - Results list (session_id, user_id, timestamp, snippet)
  - Click result => open/load session in Agent View (reuse existing behavior)
- Show small “took_ms” and “results count”.

Also ensure:
- Output window wraps text (pre-wrap) where applicable in admin views.
- Version + release is visible in header AND in help menu.

---

## 4) Documentation Updates (DE/EN)
Update:
- User Docs DE/EN (mention nothing too admin-heavy; keep user focused)
- Demo Guide DE/EN:
  - Minimum 3 story-based demos (“Kennen Sie das auch…?” / “Have you ever…?”)
  - Include at least one demo showing admin turning on perf logging briefly and searching a session.
- Admin Docs DE/EN:
  - How to start stack
  - How to verify components in order (DB, Whisper, Ollama/OpenAI, Piper, Web)
  - What parameters exist (including perf logging + search settings)
  - How to run tests and where logs/artifacts are
- Release Notes DE/EN:
  - Add V9.1.8 entry and keep full history from V7.0.0

Language switching:
- If UI language is DE => render DE docs
- If EN => render EN docs
- Else => EN

---

## 5) Tests (Must automate + produce test log)
### 5.1 Automated smoke tests (script)
Create `scripts/run_v9_1_8_admin_tests.sh` that:
1) Starts stack (compose)
2) Calls `/api/health`, `/api/models`
3) Sets perf_logging_enabled=true via `/admin/settings`
4) Sends one chat message (customer->agent) and one agent reply
5) Asserts at least 1 perf log inserted (query Mongo)
6) Runs `/admin/search?q=<partial_session_id>&mode=session_id`
7) Runs `/admin/search?q=<known_word>&mode=text`
8) Sets perf_logging_enabled=false again
9) Writes `artifacts/.../test-log-v9.1.8.txt` + `SUMMARY.md` with PASS/FAIL

### 5.2 Browser 2-minute proof checklist (manual)
Generate `docs/TEST_CHECKLIST_V9.1.8.md` (DE/EN sections):
- Toggle perf logging ON
- Run 1 short conversation
- Search by partial session_id
- Search by word fragment
- Open session
- Toggle perf logging OFF

---

## 6) Definition of Done (DoD)
- Perf logging toggle works; no logging when OFF.
- Search works for partial session_id/user_id and for text (best-effort with limits).
- No regressions in dual-lane translation/TTS routing.
- Docs not empty; help menu structure correct; DE/EN switching works.
- Artifacts generated; `SUMMARY.md` + `test-log-v9.1.8.txt` show PASS.
- No new license risk.

---

## 7) Deliverables
- PR-ready branch + commits
- Updated docs (DE/EN)
- New/updated scripts for tests + artifacts
- Release note snippets (DE/EN) prepared