# Release Notes (DE) - V7.0.0 bis V9.1.5

## Historie
- V7.0.0: V7-Scaffold isoliert, eigene Ports, Admin-Demo-Defaults.
- V7.1.0: Hands-free Listen Mode mit Auto-Stop/Auto-Send/Auto-Resume.
- V7.2.0: Audio-Pipeline gehaertet, ffmpeg-Konvertierung, klare JSON-Fehler.
- V7.3.0-V7.10.0: UX-, Security-, Telemetrie- und Sprachausbau.
- V8.0.0: V8 als isolierte Schicht mit Valkey/EventBus.
- V8.1.0: Customer UI getrennt.
- V8.2.0: Agent UI mit Inbox/Join/Live-Chat.
- V8.3.0: Agent-Suche nach User/Session.
- V8.4.0: Listen Mode fuer Kunden verbessert.
- V8.5.0: Admin-Konversationssuche (`user_id`, `session_id`, `q`).
- V8.6.0: Doku-Hardening und Help-Menue-Regeln.
- V8.7.0: Handoff-Workflow via EventBus.
- V8.8.0: Security-Baseline (Headers, Limits, Rate-Limits).
- V8.9.0: Stabiles Packaging + Migration.
- V8.10.2: TTS-Output-Translation inkl. Agent->Kunde Uebersetzung.
- V9.0.0: Help System v2, bilinguale DE/EN-Doku, `/api/docs`, Version sichtbar in Header+Menue, Agent-Muttersprache (DE/EN/NO/SV/FI) mit persistierten Agent-Prefs.
- V9.1.0: Dual-Lane-Sprachrouting (`agent`-Lane + `customer`-Lane) mit expliziter TTS-Bindung (`tts.agent_*`, `tts.customer_*`), WS-Lang-Persistenz (`customer_lang_ui_last`, `agent_lang_ui_last`) und sicherer Verhinderung von falscher Sprachausgabe.
- V9.1.1: TTS-Text-Sanitizer am Ausgabepunkt; entfernt Markdown-/Control-Zeichen fuer Sprache, ohne Dual-Lane-Routing oder gespeicherte Transkripte zu veraendern.
- V9.1.2: Agent-UI Auto-Refresh (Inbox), robuster WS-Reconnect und optionaler Anzeige-Filter fuer Sonderzeichen im Chat (nur UI-Darstellung).
- V9.1.5: WS-Dual-Lane-Test-Hardening mit Artefakt-Nachweisen, robusten Eventual-Delivery-Checks (10s) und Lane-Observability-Metadaten (`event_id`, `event_ts`, `lane.*`, `text_for_*`, `lang_for_*`) fuer eindeutige Fehleranalyse.
- V9.1.5-fix-voice-duallane: Voice-Paritaetsfix, damit Voice denselben live `message.created` Dual-Lane-Vertrag wie Chat nutzt; behebt fehlende Agent-Lane-Uebersetzung bei Voice-Faellen und behaelt die strikte TTS-Lane-Bindung.
- V9.1.6: Post-fix-Hardening fuer wiederholbare WS/Voice-Tests, formale Artefakt-Policy (`v9/docs/ARTIFACT_POLICY.md`) sowie Retention/Cleanup-Automation fuer lokale Nachweise.

## Nutzen von V9.1.0
- Keine falsche Sprache mehr im Agenten- und Kunden-TTS-Pfad.
- Jede Nachricht hat klare Empfaenger-Lanes: Original, Agent-Ansicht, Kunden-Ansicht.
- TTS liest nur noch explizit vorgesehene Felder und nie versehentlich den falschen Text.

## Nutzen von V9.1.2
- Agent-Inbox aktualisiert sich automatisch, neue/veraenderte Sessions werden ohne manuelles Refresh sichtbar.
- WS-Reconnect stabilisiert Live-Updates nach kurzen Verbindungsabbruechen.
- Chat-Anzeige kann Sonderzeichen (z. B. Markdown-Marker) ausblenden, ohne TTS/Backend-Logik zu veraendern.

## Nutzen von V9.1.5
- Testlaeufe trennen jetzt `fast_delivery_ok` und `eventual_delivery_ok`, damit lokale Modell-Laufzeiten keine falschen Negativmeldungen mehr erzeugen.
- Jeder Lauf erzeugt ein vollstaendiges Artefaktpaket (`artifacts.zip`, SUMMARY, WS-Eventspuren, ENV-Snapshot, Docker-Logs) fuer reproduzierbare Analyse.
- WS-Events liefern Lane-Zusammenfassungen + IDs, damit Admins die Uebersetzungsdurchsetzung pro Empfaengerrolle eindeutig nachweisen koennen.

## Release Gate - V9.1.5-fix-voice-duallane (Finale Verifikation)
- Gate-Resultat: **PASS** (automatisierte WS-Suite + Voice-Pfad-Nachweis).
- Kernnachweis aus den aufgezeichneten Events:
  - Customer-Voice (DE) bleibt als `text_original=Meine Wallbox geht aus.` erhalten und wird in die Agent-Lane als `text_for_agent=My wallbox is out.` mit `lang_for_agent=en` und `tts_lang_agent=en` geroutet.
  - Agent-Antwort (EN) wird in die Customer-Lane als deutscher Text mit `lang_for_customer=de` und `tts_lang_customer=de` geroutet.
- Artefakte fuer Review:
  - `artifacts/SUMMARY.md`
  - `artifacts/test-log-v9.1.5-ws.txt`
  - `artifacts/test-log-v9.1.5.txt`
  - `artifacts/ws_agent_events.jsonl`
  - `artifacts/ws_customer_events.jsonl`
  - `artifacts-v9.1.5-final.zip`

### 2-Minuten Browser-Checkliste (manuell)
1. Agent UI: Sprache `en`, Incoming Speak `AN`.
2. Customer UI: Sprache `de`.
3. Kunde sendet/spricht einen deutschen Text.
4. Pruefen: Agent sieht Original + englische Lane und hoert nur die englische Lane.
5. Agent antwortet auf Englisch.
6. Pruefen: Kunde erhaelt/hoert nur die deutsche Lane.

### Lizenzhinweis
- In diesem Release-Gate-Lauf wurden keine neuen Runtime-Abhaengigkeiten eingefuehrt.
- Kommerzialisierungs-Guardrails unveraendert:
  - permissive OSS in Core bevorzugt
  - kein GPL/AGPL-Zuwachs im Core Runtime
  - copyleft-Komponenten bleiben als Sidecar isoliert.

## Nutzen von V9.1.6
- Standardisierte Testskripte unter `v9/scripts/tests/` machen V9-Laeufe auf jedem Rechner reproduzierbar.
- Jeder Testlauf schreibt jetzt in einen klaren Ordner `v9/artifacts/<timestamp>/`.
- Die Cleanup-Routine begrenzt lokalen Speicherverbrauch durch Aufbewahrung nur der neuesten Laeufe.
