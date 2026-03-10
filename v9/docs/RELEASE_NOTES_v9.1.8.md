# V9.1.8 — Release Notes (DE) — 2026-03-10

## Highlights
- **Admin Performance Toggle**: Performance-/Latenz-Logging kann jetzt gezielt ein- und ausgeschaltet werden.
- **Admin Search**: Suche ueber Konversationen nach `session_id`, `user_id` oder Textfragmenten.
- **Operations-ready**: Trefferliste mit `Open Session` fuer schnellen Sprung in die passende Session.

## Aenderungen im Detail
### Backend
- Neues Logging-Ziel `admin_perf_logs` (getrennt von Konversationsdaten).
- `admin_settings` erweitert um:
  - `perf_logging_enabled`
  - `perf_logging_sample_rate` (0.0..1.0)
  - `perf_logging_retention_days`
  - `search_max_results`
  - `allow_text_regex_fallback`
- Neue Admin-Suche: `GET /api/admin/search`
  - `mode=auto|session_id|user_id|text`
  - Wildcard fuer IDs mit `*`
  - Textsuche bevorzugt `$text`, optional Regex-Fallback (gesteuert ueber Settings).
- In-memory Cache fuer Admin-Settings (5 Sekunden), um DB-Last zu reduzieren.

### Admin UI
- Admin-Settings um Performance-Felder erweitert.
- Neues Search-Panel mit Query + Mode + Since-Days + Limit.
- Treffer koennen per `Open Session` direkt in den aktiven Session-Kontext uebernommen werden.

## Tests
- Script: `scripts/run_v9_1_8_admin_tests.sh`
- Artefakte: `v9/artifacts/<timestamp>/`
  - `test-log-v9.1.8.txt`
  - `SUMMARY.md`
  - `ENV_SNAPSHOT.txt`
  - `docker-logs-*.txt`

## Lizenz- und Kommerzialisierungs-Hinweis
- Keine neuen Runtime-Abhaengigkeiten hinzugefuegt.
- Core bleibt bei permissiver OSS-Strategie; kein GPL/AGPL-Zuwachs im Core.
