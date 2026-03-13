# CODEX_TASK_V9.1.15 — Admin Analytics Page (Perf Dashboard v1)

## Goal
Add an **Admin analytics page** that reads from the perf logging DB (v9.1.14) and shows:
- headline KPIs (avg/p95 for total_ms, stt_ms, llm_ms, tts_ms, translate_ms)
- last N minutes/hours/day selectors
- simple filters: user_id/session_id/text search (supports wildcard `*` for prefix)
- basic tables: slowest 20 requests, most frequent errors, counts per backend/model
- export buttons:
  - create archive zip for selected range
  - download existing archive

This is v1: keep UI clean and fast.

---

## Requirements
- Must work even if perf logging is OFF (show "logging disabled" banner + link to settings).
- Must not block the system: use aggregation queries with limits and indexes.
- Search must support:
  - `wallbox*` (prefix)
  - `fe77*` (prefix)
  - `*fragment*` optional (if implemented, warn about cost; OK to limit to prefix only in v1)

---

## UI
Admin client:
- Keep header clean: status + version + search.
- Add a "Perf" tab/page.
- Show KPIs at top (cards/boxes).
- Show table below (paginated or limited).
- Provide “Refresh” + auto-refresh toggle (default off).

---

## API additions (if needed)
- GET `/admin/perf/summary?start=...&end=...&filters...`
- GET `/admin/perf/events?start=...&end=...&limit=...&cursor=...`
- GET `/admin/perf/errors?start=...&end=...`
- Reuse v9.1.14 archive endpoints.

---

## Tests
- Automated UI smoke:
  - logging ON
  - load perf page, verify KPIs present (not empty)
  - run a quick /voice cycle
  - refresh perf page; counts increase
- Produce `test-log-v9.1.15.txt` + artifacts folder.

---

## Documentation
Update Admin Docs (DE/EN):
- How to use Perf dashboard
- How to interpret p95 spikes
- How to export archives and where they go

Release Notes: DE + EN.

---

## Guardrails + Help structure + Silence threshold + Artifact policy
Same as in v9.1.14, mandatory.