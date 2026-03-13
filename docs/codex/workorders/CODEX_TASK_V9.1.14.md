# CODEX TASK: V9.1.14 — Performance Logging (toggleable) + Log-DB + TTL + Archive ZIP
Project: voice-agent (Cody planning / Codex implementation)
Target: v9.x
Version: v9.1.14 (skip 9.1.13)

## Non-negotiables (must be enforced every release)
### Licensing & Commercialization Guardrails
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core. If a copyleft component is needed, isolate as an external sidecar and document the license risk.
- Explicitly flag any dependency/license risk in PR and docs.

### Help/Docs Quality Rules (must always hold)
Help menu structure must be exactly:
1) Admin token speichern
2) Help = User documentation (NOT release notes)
3) Demo Guide (>= 3 story scenarios starting with “Kennst du das auch …?” / “Have you ever …?”)
4) Admin Docs (install/start/config/tests/health checks; Whisper/Piper/DB/Ollama checks; troubleshooting)
5) Release Notes (history from v7.0.0 to current)
- Docs must be readable for a 16-year-old.
- Version + release must be visible in header + help menu on Admin/Agent/Customer.
- Default silence threshold = 1300ms.
- Every release must update docs to include new features and tests.
- Docs must exist and must not be empty.

### Artifact Policy (must always hold)
- Artifacts (logs/zips/jsonl) must NOT be committed to git.
- Store under: v9/artifacts/<YYYYMMDD-HHMMSS>/
- Keep last N runs locally; CI/automation may attach artifacts to GitHub Release if needed, but never commit.
- Provide a SUMMARY.md per run.

## Context / Current Ports
- Admin client: http://localhost:8085
- Customer client: http://localhost:8086
- Agent client: http://localhost:8087

## Goal
Implement performance logging that can be enabled/disabled at runtime by Admin settings, stored in its own MongoDB database (separate from conversation DB), with TTL retention and an archive export (ZIP of readable logs for a selected time window).

## Requirements
### A) Toggleable Performance Logging
- Add an admin setting `perf_logging_enabled` (default OFF in production, ON in dev allowed).
- If OFF: negligible overhead (no heavy aggregation, no blocking I/O).
- If ON: store per-request and per-event timing metrics:
  - ts (UTC), user_id, session_id
  - audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms
  - lang_customer_ui, lang_agent_ui, tts_lang_customer, tts_lang_agent
  - backend used (ollama/openai/…)
  - model used
  - message direction (customer->agent, agent->customer)
  - message_id / correlation_id
  - error fields if any (error_type, error_message, stack_hash)
- Must also support logging for automated tests (same pipeline).

### B) Separate Log DB + TTL
- Use MongoDB database name: `voice_agent_logs` (configurable via env `MONGO_LOG_DB`, default voice_agent_logs).
- Collections:
  - `perf_events` (raw events)
  - optionally `perf_daily_rollups` (if needed later; for V9.1.14 keep minimal, no heavy rollup)
- TTL:
  - `PERF_RETENTION_DAYS` default 30 in dev; allow 365 or 730 etc.
  - TTL index on `expires_at` (preferred) or on `ts` with expireAfterSeconds.
- Ensure TTL indexes are created idempotently on startup.

### C) Archive Export (ZIP)
- Provide API endpoint (Admin-only / guarded by “demo admin mode”):
  - `GET /admin/perf/export?from=<iso>&to=<iso>&format=jsonl|csv|md`
  - Responds with a `.zip` containing:
    - `perf_events_<from>_<to>.jsonl` (one JSON per line)
    - `README.md` describing fields
    - optional `stats_summary.json` (counts, min/avg/p95 for key timings) computed on demand for that export only
- Export must not block the API for long:
  - Stream response or build in temp file with progress-safe approach
  - Bound max export window via config `PERF_EXPORT_MAX_DAYS` (default 7) unless explicitly overridden.

### D) Admin Settings Persistence
- Persist admin settings in DB (not only localStorage):
  - collection: `admin_settings`
  - store versioned schema and last_updated_ts
- Provide endpoints:
  - `GET /admin/settings`
  - `POST /admin/settings` (partial update)
- Settings include:
  - perf_logging_enabled
  - PERF_RETENTION_DAYS
  - PERF_EXPORT_MAX_DAYS
  - optionally “sample_rate” (0..1) to reduce volume
- Add safe defaults.

### E) Minimal UI changes in Admin Client (no dashboard yet)
- In Admin client header/area, add a small toggle + retention fields:
  - “Perf logging: ON/OFF”
  - “Retention days”
  - “Export (from/to)”
- Keep it ergonomic and not wider than Agent view.
- No charts yet (that’s V9.1.15). Only simple controls + success/error toast.

### F) Security / Privacy
- Do not log full transcripts/answers by default in perf logs.
- If we ever log text: add `perf_log_text_enabled` default OFF, and redact obvious secrets (best-effort).
- Ensure API does not expose perf endpoints to non-admin (demo user counts as admin until real user mgmt in v14.x).

## Implementation Guidance (Performance)
- Logging must be non-blocking:
  - Option 1: in-process queue + background worker thread writing batches to Mongo.
  - Option 2: async fire-and-forget with bounded buffer; drop on overload but increment a counter.
- Provide counters:
  - dropped_events_count
  - queue_depth
- Expose `GET /admin/perf/health` returning queue stats.

## Tests (must produce artifacts)
Create script: `v9/scripts/run_v9_1_14_perf_logging_tests.sh`
It must:
1) Start stack
2) Enable perf logging via API
3) Run 3 synthetic interactions:
   - customer chat -> agent
   - agent reply -> customer
   - voice path if available (or skip with clear reason)
4) Verify perf_events created in log DB
5) Verify TTL index exists
6) Call export endpoint for last 5 minutes and verify zip contains expected files
7) Disable perf logging again
8) Write artifacts:
   - v9/artifacts/<ts>/SUMMARY.md (PASS/FAIL)
   - v9/artifacts/<ts>/admin_settings.json
   - v9/artifacts/<ts>/export_test.zip (do not commit)
   - v9/artifacts/<ts>/docker-logs-*.txt

Also update docs:
- Admin Docs: how to enable perf logging, what it does, how to export archive, how to validate it.
- Demo Guide: add a short story scenario demonstrating “Performance spike investigation”.

## Deliverables
- Code changes (API + Admin UI + scripts)
- Updated docs (DE+EN):
  - user_guide
  - demo_guide (>= 3 scenarios)
  - admin_docs
  - release_notes (append)
- Test artifacts + test log in v9/artifacts/<ts>
- No artifacts committed.

## Definition of Done (DoD)
- Perf logging toggle works (ON/OFF) without breaking voice/chat.
- Perf logs go to separate Mongo DB with TTL.
- Export zip works for a bounded window.
- Admin settings persist in DB.
- Tests PASS and produce artifacts.
- Docs updated (DE+EN) and rendered correctly in UI.
- License guardrails upheld (no new copyleft in core).