# CODEX TASK — V9.1.12 — Admin Logging System + Manual Test Plan + Search Wildcards

## Goal
1) Add an Admin-controlled performance/logging system:
   - Toggle ON/OFF from Admin UI (must not block runtime when OFF).
   - Writes to a separate logging database/collection (NOT conversation DB).
   - Retention configurable (default 30 days; max 12 months active).
   - Ability to export/archive logs older than retention into ZIP (readable files) with date range in filename.
2) Improve Admin Search:
   - Single search field supports:
     - exact match (session_id/user_id)
     - wildcard suffix with `*` (prefix search): e.g. `fe77*`, `wallbox*`
     - text fragment search (contains)
   - Filter dropdown: auto | session_id | user_id | text
3) Provide a comprehensive manual test plan to execute after v9.1.12 release.
4) Ensure Help markdown is properly rendered (not a single-line blob), in both DE/EN docs.

## Critical Guardrails (Licensing & Commercialization)
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core repo.
- Keep copyleft components as isolated sidecars.
- No new risky deps.

## Functional Spec

### A) Logging/Perf measurement (Admin-controlled)
#### A1) What is logged (per event/request)
Store a log record containing at least:
- timestamp (UTC + local optional)
- user_id
- session_id
- direction (customer->agent / agent->customer / system)
- audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms
- lang_for_agent, lang_for_customer
- transcript (optional, configurable), answer (optional, configurable)
- model/backend used
- flags: crm_export_enabled, translation_enabled, etc. (if available)

#### A2) Where it is stored
- Separate DB/collection/table (e.g., `admin_perf_logs`).
- Must not mix with conversation messages DB.

#### A3) Performance mode toggle
- Admin UI toggle: `Performance Logging: ON/OFF`
- When OFF:
  - Do not write to perf log db (or write minimal counters only).
  - Must not introduce noticeable overhead.
- When ON:
  - write full record.

#### A4) Retention policy
- Configurable:
  - `PERF_LOG_RETENTION_DAYS` default 30
  - hard cap: keep max 365 days active (12 months)
- Implement TTL index (preferred).
- Provide an archive job endpoint or admin action:
  - Export logs older than retention into ZIP:
    - inside: JSONL and/or CSV and a README.md
    - filename: `perf-logs_YYYYMMDD-YYYYMMDD.zip`
  - After successful export: delete exported records from DB (optional toggle).

### B) Admin Search with wildcard `*`
- One input field:
  - If ends with `*`: do prefix match (e.g., `fe77*` => regex `^fe77`)
  - Else:
    - if looks like full UUID => exact match
    - else text fragment search (contains)
- Filter dropdown controls interpretation; `auto` decides based on pattern.
- Results list:
  - sessions + context snippet (show matching text fragment)
  - click result -> open session in Agent view + load history

### C) Markdown rendering in Help
- Ensure Help content renders true Markdown (headers, lists, paragraphs).
- No “serialized single-line” output.
- Use safe renderer:
  - Basic Markdown subset (headings, lists, code blocks).
  - Escape HTML to prevent XSS.
- Works for DE/EN switching:
  - UI language=DE => show DE docs
  - UI language=EN => show EN docs
  - otherwise EN

### D) Version visibility
- Admin/Agent/Customer headers show same version string.
- Help menu also shows version + release tag.
- Silence threshold default remains 1300 ms.

## Documentation Rules (MUST)
Help menu structure must ALWAYS be:
1) Admin Token speichern
2) Help (User Guide) — user documentation ONLY
3) Demo Guide — at least 3 story-driven scenarios (customer/agent/admin)
4) Admin Docs — install/start/config/tests/components checks + performance logging + archive
5) Release Notes — history from V7.0.0 -> current

Docs must be updated for new features in this release.

## Manual Test Plan (Deliver as docs + runbook)
Create `v9/docs/MANUAL_TEST_PLAN_V9.1.12.md` including:
- Quick Setup
- 10–15 test cases:
  - Dual-lane (voice + chat) across DE/EN and at least one additional language
  - Verify TTS speaks correct lane only
  - Verify admin toggle logging ON/OFF changes DB writes
  - Verify wildcard search `fe77*`, `wallbox*`
  - Verify archive ZIP created and contains correct date range data
  - Verify TTL retention effective (can simulate by lowering retention to 1 minute in test env)
- Define PASS criteria + what screenshots/logs to capture.

## Tests (Automated + Artifacts)
- Extend automated scripts to:
  - Toggle performance logging ON
  - Send at least one voice + one chat scenario
  - Verify perf log DB has entries (count > 0)
  - Toggle OFF and verify no new entries
  - Run admin search with wildcard and verify results non-empty
  - Create archive ZIP and verify file exists and has non-zero size (store in artifacts dir, not committed)

## Artifacts Policy (Must)
- All test outputs go to: `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- Include: docker logs, env snapshot, summary.md, test-log.txt, generated archive zip (optional).
- Do NOT commit large artifacts. Commit only:
  - SUMMARY.md (short)
  - test-log.txt (short)
  - docs updates

## Deliverables
- Branch: `codex/feature/v9.1.12-admin-logging-retention-archive`
- Updated API + DB indexes
- Updated Admin UI (toggle + search)
- Updated docs (DE/EN) + Manual Test Plan doc
- Automated test scripts updated and passing