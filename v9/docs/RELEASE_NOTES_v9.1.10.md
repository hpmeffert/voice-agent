# V9.1.10 — Release Notes (DE) — 2026-03-11

## Highlights
- Agent- und Admin-Rolle in der UI klar getrennt.
- Agent-Client zeigt nur noch agentenspezifische Einstellungen.
- Admin-Client hat Header-Perf-Badges (avg/p95) und zentrale Admin-Suche.
- Dual-Lane bleibt stabil: Original + Uebersetzung in Live-Events und Verlauf (wenn Lane-Daten vorhanden).

## Was wurde geaendert?
- Agent-Client:
  - Button `Agent Settings ⚙︎` statt vollwertigem Admin-Panel.
  - Keine globalen Admin-Controls mehr im Agenten (kein `/admin/settings`, kein Admin-Token, kein `/admin/search`).
  - Suche nutzt neuen Endpoint `/api/agent/search`.
  - Performance im Agenten bleibt lokal nutzbar (aus `/api/metrics/recent`).
- Admin-Client:
  - Header mit einheitlicher Suche (`q` + `mode`) und Perf-Badges fuer STT/LLM/TTS/Total.
  - Suche oeffnet Sessions aus Trefferliste wie bisher.
  - Globale Admin-Settings bleiben nur im Admin-Client.
- Version:
  - Alle Clients und Help-Version zeigen `v9.1.10`.

## 2-Minuten Test
1. Agent (`/web-agent`) oeffnen: pruefen, dass nur `Agent Settings` vorhanden sind.
2. Admin (`/`) oeffnen: Header-Suche + Perf-Badges sichtbar.
3. Suche im Admin testen: `fe774f*` und `Wallbox`.
4. Dual-Lane testen: Customer DE (Voice) -> Agent EN, Agent EN -> Customer DE.

## Lizenz-/Security-Hinweis
- Keine neuen externen Dependencies hinzugefuegt.
- Core bleibt ohne neue GPL/AGPL-Abhaengigkeiten.
