# V9.1.7 — Release Notes (DE) — 2026-03-10

## Highlights
- **Auto-Upload nach Recording-Ende (Customer UI)**: Nach Stop/Ende des Recordings startet das Upload/Senden automatisch (ohne extra “Send”-Klick).
- **Default Model = qwen2.5:3b**: Standardmodell ist nun `qwen2.5:3b` (UI-Default + Backend-Fallback konsistent).
- **Stabilität/UX**: Verbesserte Statusanzeigen und Fehlertexte für Upload/Transcribe/LLM/TTS.

## Änderungen im Detail
### UI (Customer / Agent)
- Customer: Auto-Upload Trigger nach `mediaRecorder.onstop` (oder nach Silence-Stop, falls aktiv).
- Default Model Dropdown: `qwen2.5:3b` als bevorzugter Default (wenn verfügbar); sonst fallback auf `qwen2.5:7b`.
- Optional: “Auto-send after recording” Toggle (default: ON im Customer-Client; OFF/optional im Agent-Client).

### Backend
- Default Model Fallback: Wenn kein `model` übergeben wird → `qwen2.5:3b` (falls vorhanden) sonst `OLLAMA_MODEL`.
- Logging/metrics: Keine Änderung an Dual-Lane/Translation-Routing (wenn v9.1.6 stabil ist, darf hier nichts brechen).
- **Ergänzung**: TTS-Sanitizer am TTS-Boundary (nur Ausgabepfad) entfernt Markdown-/Control-Formatierung vor Audioausgabe, ohne gespeicherten Text oder Dual-Lane-Routing zu verändern.

## Dokumentation (Pflicht)
- Update der Dokumente in **DE und EN**:
  - User Guide (DE/EN)
  - Demo Guide (DE/EN, min. 3 Story-Szenarien)
  - Admin Guide (DE/EN, Start/Tests/Parameter/Verzeichnisse/Checks)
  - Release Notes Historie (DE/EN, ab V7.0.0 bis aktuell)
- Sprachlogik Doku:
  - UI language = DE → DE Docs
  - UI language = EN → EN Docs
  - alle anderen Sprachen → EN Docs

## Tests (Pflicht, 2-Minuten Proof)
### Smoke (Browser)
1) Customer öffnen (DE), Agent öffnen (EN)
2) Customer spricht → Aufnahme stoppt → **Auto-Upload startet**
3) Agent sieht LIVE: Original + Übersetzung, optional Incoming Speak korrekt
4) Agent antwortet (EN) → Customer sieht/hört (DE)
5) Ergebnis: **PASS**

### Automatisierte Tests (Script)
- `run_v9_ws_duallane_tests.sh` ausführen + Testlog schreiben:
  - `v9/artifacts/<timestamp>/test-log-v9.1.7.txt`
  - `v9/artifacts/<timestamp>/SUMMARY.md`
  - `v9/artifacts/<timestamp>/events-agent.jsonl`, `v9/artifacts/<timestamp>/events-customer.jsonl`
- Erwartung: alle Scenarios PASS.

## Known Issues / Notes
- Performance hängt stark von STT/LLM Hardware ab (MacBook Pro M1 / 16 GB kann limitieren). Default 3B soll LLM-Latenz senken.

## License & Commercialization Guardrails
- Nur permissive OSS bevorzugen (MIT/Apache/BSD).
- GPL/AGPL im Core vermeiden; Copyleft nur als externer Sidecar.
- Lizenzrisiken aktiv markieren.

## Artifact Policy (Tests)
- Alle Testläufe schreiben ihre Artefakte nach `v9/artifacts/<timestamp>/`.
- Retention default: letzte 10 Runs (über `v9/scripts/cleanup_artifacts.sh`).
- `v9/artifacts/` niemals in Git committen (`.gitignore` aktiv).
- Optionales Sharing: nur release-relevante ZIPs als GitHub Release Asset hochladen.
