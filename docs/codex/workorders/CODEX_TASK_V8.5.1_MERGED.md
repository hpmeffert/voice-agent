# CODEX_TASK_V8.5.1_MERGED

**Purpose:** Single “source of truth” wrapper for Codex/CODY so nothing is missed.  
**Rule:** V8.5.1 includes **all** requirements from:
- `CODEX_TASK_V8.5.0.md` (base features)
- `CODEX_TASK_V8.5.x_UPDATED.md` (extensions / fixes / contracts)

This merged task is a *wrapper* and does not replace detailed steps inside the two originals; it **defines precedence, integration rules, and acceptance criteria**.

---

## 0) Scope & Guardrails

### Scope
- Target tree: **`v8/` only** (no changes to V7/V6 runtime trees)
- Implement V8.5.1 as a patch release that:
  1) Keeps all V8.5.0 deliverables (Readable transcript + Metrics panel + perf_logs + TTL)
  2) Adds V8.5.x Updated deliverables (Admin Conversation Search + doc/tests hardening)

### Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS: **MIT/Apache-2.0/BSD**.
- Avoid GPL/AGPL in core. If unavoidable, isolate as **external sidecar**.
- **Piper remains a sidecar**; do not embed Piper binaries/source/models in repo.
- If any dependency is copyleft or ambiguous → flag explicitly in PR notes and propose an alternative.

### Stability Guardrails (no “Orphan/Ports/Compose” traps)
- Compose must use unique container names via project scoping; avoid hard-coded names that collide.
- Ports must be configurable via env vars and documented.
- Add a “clean reset” make target or doc snippet to remove stale containers/ports.

---

## 1) Precedence / Merge Rules

1. **No regression**: everything required by V8.5.0 must still work.
2. If instructions conflict:
   - Prefer `V8.5.x_UPDATED` for API/UI contracts and doc/testing expectations.
   - Prefer `V8.5.0` for existing endpoints/data structures if already shipped, unless Updated explicitly supersedes.

---

## 2) Deliverables Checklist (what must exist after merge)

### A) UI: Readable transcript + clean output
- The main output area must not show raw JSON with `\n`, internal fields, etc.
- Show:
  - Transcript (human-readable)
  - Answer (human-readable)
- Show **metrics/perf** in a separate panel/section (not mixed into transcript).
- Ensure **wrap/line-break** styling so long text is readable.

### B) Mongo: perf logs (separate from conversation data)
- Implement/keep `perf_logs` (or equivalent) as separate collection/table.
- Fields include at least: timestamp, user_id, session_id, audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms, transcript, answer (+ backend/model used if available).
- TTL retention (configurable) for perf logs.
- Must not break existing sessions/messages TTL.

### C) Admin Conversation Search (Updated)
- API endpoint: `GET /api/admin/conversations/search`
  - Requires `X-Admin-Token` header.
  - Requires **at least one filter**; otherwise return 400 with helpful error.
  - Filters: session_id, user_id, text query (transcript/answer), date range.
  - Paginated results with defaults and max limits.
- Admin UI panel:
  - Search form (filters)
  - Results list with key metadata + link/button to view session details.

### D) Documentation Quality Contract (non-empty, always updated)
- Help menu structure must remain:
  1) Admin Token speichern
  2) Help (User documentation, no release notes)
  3) Demo Guide (story-based)
  4) Admin Docs (install/start/tests/parameters/dirs/component checks)
  5) Release Notes (history)
- Ensure docs are **not empty**; add a test that fails if any required doc section is missing.

### E) Tests / Validation
- Include a repeatable test routine:
  - Health endpoints
  - Models endpoint
  - Voice flow happy path (Ollama)
  - Piper TTS health
  - Mongo ping + TTL indexes existence
  - Admin search endpoint auth + filter validation
- Add a lightweight script or make target that runs the checks (or documented curl commands).

---

## 3) Implementation Steps (High Level)

1. Start from current V8 tree.
2. Implement/verify **UI readable transcript + metrics panel + wrap**.
3. Implement/verify **perf_logs** write path + TTL + indexes.
4. Implement **Admin search endpoint** + token validation + pagination.
5. Add Admin UI search panel wired to endpoint.
6. Update docs + add doc completeness tests.
7. Add/verify make targets / scripts to avoid orphan/port issues.
8. End-to-end manual test + record acceptance evidence in PR.

---

## 4) Acceptance Criteria (must pass)

- UI shows transcript/answer cleanly (no raw JSON dump in main view).
- Metrics shown separately and look clean.
- `perf_logs` collection exists, receives entries, TTL works.
- Admin search works with token; fails without token; fails with no filters.
- Help menu sections exist and are not empty; tests enforce this.
- No changes outside `v8/` except shared tooling/docs if explicitly permitted by the task.
- Licensing guardrails satisfied; any risk is clearly flagged.

---

## 5) Original Task Files (embedded for reference)

> Below are the originals included verbatim to preserve all detail. If any duplication exists, follow the precedence rules above.

---

## 5.1 `CODEX_TASK_V8.5.0.md`

# CODEX_TASK_V8.5.0

> Target: **V8.x** (Major: V8) — Start from latest stable V7 tag/branch.
> Scope: Create/extend **v8/** isolated tree. Do not break v7.

## Title
Admin view: realtime metrics panel + clean transcript display

## Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer permissive OSS licenses: **MIT / Apache-2.0 / BSD**.
- **Avoid GPL/AGPL in core** (API, web UI, shared libs). If a needed component is GPL/AGPL/copy-left, isolate it as an **external sidecar/service** (separate process/container) with clear boundaries.
- Explicitly mark any license risk in PR description and docs.
- Do **not** commit secrets/keys. `.env` stays ignored.

## Help / Documentation Contract (MUST FOLLOW EACH RELEASE)
The UI **must** keep this Help menu structure (and content must NOT be empty):
1) **Admin Token speichern**
2) **Help** (User documentation — *no release notes here*)
3) **Demo Guide** (story-driven demo flows)
4) **Admin Docs** (install/start/tests/params/dirs/component checks; admin-only)
5) **Release Notes** (history from **V7.0.0** to current)

Additional rules:
- **Version/Release** must be visible in **header** and **Help**.
- Default **Silence Threshold = 1300 ms**.
- Every release must add/adjust docs + include an automated test that docs are not empty.

## Goals
- Fix transcript display readability: no `\n`/raw JSON clutter.
- Show metrics in a separate panel below, and log metrics to separate collection.

## Deliverables
- UI: transcript+answer rendered nicely; metrics panel below with latency breakdown.
- Mongo: new collection `perf_logs` with TTL index (configurable retention).
- API includes `metrics` but UI renders cleanly.

## Implementation Steps
1. UI: render transcript and answer as paragraphs/bullets; escape control characters.
2. API: keep response JSON for dev, but UI should parse and display fields.
3. Mongo: store `perf_logs`: `{ts, user_id, session_id, audio_read_ms, stt_ms, llm_ms, tts_ms, total_ms, model, backend}` with TTL `PERF_LOG_RETENTION_DAYS`.
4. Add endpoint `/admin/perf/query` (admin-only MVP: demo user).

## Tests / Verification
- Metrics visible and readable; no raw JSON in main transcript view.
- Perf logs can be queried; TTL index exists.

## Notes
Ensure perf_logs is separate from conversation data (compliance).


---

## 5.2 `CODEX_TASK_V8.5.x_UPDATED.md`

# CODEX TASK V8.5.x (Updated)

## Scope
- Nur V8 (`v8/`), keine Regression in V7.
- Fokus: Admin-Konsole und durchgaengige Doku-Qualitaet.

## Erweiterung (verbindlich)
- Admin-Konversationssuche muss verfuegbar sein:
  - nach `user_id` (`search_user_id`)
  - nach `session_id`
  - nach Inhalt (`q`, Wort oder Textabschnitt)
- Admin-UI muss diese Suche als nutzbares Panel anzeigen.
- API muss den Suchvertrag stabil liefern.

## API Contract
- `GET /api/admin/conversations/search`
- Query:
  - `user_id` (Admin-Identitaet)
  - optional `search_user_id`
  - optional `session_id`
  - optional `q`
  - optional `limit` (1..500)
- Header:
  - `X-Admin-Token: <token>`
- Verhalten:
  - ohne Filter -> HTTP 400
  - mit gueltigem Filter -> Trefferliste + Session-Zusammenfassung

## UI Contract
- `v8/web/index.html` enthaelt:
  - Admin-Panel `Conversation Search`
  - Eingaben fuer `search_user_id`, `session_id`, `q`, `limit`
  - Aktionen: `Search Conversations`, `Clear`
  - Ergebnisbereich mit Count/Session-Count und JSON-Ausgabe

## Dokumentationsvertrag (pro Release Pflicht)
- Help-Menue Reihenfolge:
  1. Admin Token speichern
  2. Benutzer Dokumentation
  3. Demo Guide
  4. Admin Docs
  5. Release Notes
- Inhalte:
  - `HELP_USER.md`: Funktionen und Wirkungen fuer Endnutzer
  - `DEMO_GUIDE.md`: Story-basierte Demoablaeufe mit Spannungsbogen
  - `HELP_ADMIN.md`: Setup, Parameter, Testreihenfolge, Verzeichnisse, Uebersetzungen
  - `RELEASE.md`: Verlauf von `V7.0.0` bis aktuelle Version
- Standardwert:
  - Silence Threshold = `1300 ms`

## Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
curl -s http://localhost:8082/api/health
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&q=test&limit=20" -H "X-Admin-Token: <TOKEN>"
```

