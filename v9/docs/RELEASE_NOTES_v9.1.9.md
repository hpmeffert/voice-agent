# V9.1.9 — Release Notes (DE) — 2026-03-10

## Highlights
- Agent UI aufgeraeumt: sticky Header, Status + Version sichtbar, Suche immer oben.
- Admin-Einstellungen in einem Drawer/Popup statt verteilter Freitextfelder.
- Einheitliche Suche mit `q` + Mode (`auto|session_id|user_id|text`) gegen `/api/admin/search`.
- Performance-Header zeigt `STT/LLM/Total avg + p95` aus `/api/admin/metrics/summary?window=10m`.

## Details
### Agent UI
- Header (immer sichtbar):
  - Links: Verbindungsstatus + Version
  - Mitte: Suchfeld + Mode
  - Rechts: `Admin ⚙︎` und Benutzer Handbuch
- Search Results sind klickbar und oeffnen direkt die Session im Agent-View.
- Admin Drawer ist standardmaessig verborgen und bietet sichere Controls:
  - Backend/Model Dropdown
  - Agent language
  - Customer language preview (readonly)
  - Toggles fuer Incoming Speak, Customer Output on Agent, Debug, Metrics, Auto-Refresh, Perf Metrics
  - Token-Feld (lokal gespeichert)
  - Danger Zone: localStorage loeschen, Session-View resetten, Admin Docs oeffnen

### Backend/API
- `APP_VERSION` auf `v9.1.9` gesetzt.
- `admin/settings` akzeptiert jetzt zusaetzlich:
  - `perf_metrics_enabled` (Alias kompatibel zu `perf_logging_enabled`)
  - `default_backend`, `default_model`
- `GET /api/admin/metrics/summary` erweitert:
  - neues Fenster `10m`
  - liefert jetzt `avg_ms` und `p95_ms`

### Version-Konsistenz
- Konsistente Version in:
  - Agent Header
  - Customer Header
  - Admin Help-Menue

## Tests
- Neues Script: `scripts/run_v9_1_9_ui_smoke.sh`
  - prueft `/config` (Version), `/admin/settings` Roundtrip,
  - `/admin/search` Treffer,
  - `/admin/metrics/summary?window=10m` numerische Werte.

## Lizenzhinweis
- Keine neuen externen Runtime-Abhaengigkeiten hinzugefuegt.
- Kommerzialisierungs-Guardrails unveraendert:
  - permissive OSS bevorzugt
  - kein GPL/AGPL-Zuwachs im Core
  - Sidecar-Isolation bleibt bestehen.
