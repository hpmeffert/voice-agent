# Release Notes (DE) - V7.0.0 bis V9.1.15

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
- V9.1.7: Customer Auto-Upload nach Recording-Ende, Default-Modell auf `qwen2.5:3b` vereinheitlicht und TTS-Sanitizer-Regressionstest unter `v9/scripts/tests/test_tts_sanitize.py`.
- V9.1.8: Admin-Performance-Toggle + neue Suche (`/api/admin/search`) mit Mode `auto|session_id|user_id|text`, Wildcard `*` fuer IDs und klickbarem Session-Open im Admin-UI.
- V9.1.9: Agent-UI aufgeraeumt (sticky Header), einheitliche Suche (`q` + `mode`) immer sichtbar, Admin-Einstellungen in Drawer mit sicheren Controls, und Performance-Header mit `avg/p95` aus `window=10m`.
- V9.1.11: Klare Rollentrennung: Agent-Client nur mit agentenspezifischen Settings, Admin-Client mit globalem Admin-Panel + Header-Perf-Badges + zentraler Admin-Suche; Agent-Suche ueber `/api/agent/search`.
- V9.1.14: Togglebares Performance-Logging in separater Log-DB (`voice_agent_logs.perf_events`) mit TTL, Queue-Health und ZIP-Export.
- V9.1.15: Admin Performance Dashboard mit Summary Cards, Worst-Spikes-Tabelle, Prefix-Suche und Export-/Delete-Workflow.

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

## Nutzen von V9.1.7
- Kunden muessen nach Sprachaufnahme keinen zusaetzlichen Send-Klick mehr machen (weniger Bedienfehler).
- `qwen2.5:3b` als Default senkt typischerweise Latenz auf schwacherer Hardware.
- TTS-Markdown-Bereinigung bleibt abgesichert durch einen dedizierten Test im offiziellen Testpfad.

## Nutzen von V9.1.8
- Admin kann Performance-Logging nur in benoetigten Zeitfenstern aktivieren (weniger Dauer-Overhead).
- Suche nach Konversationen ist deutlich schneller: Teil-`session_id`, Teil-`user_id` oder Textfragment.
- Trefferliste erlaubt direktes Oeffnen der Session im Agent-Client fuer schnelle Analyse.

## Nutzen von V9.1.9
- Agenten sehen eine klarere Arbeitsflaeche: Verbindungsstatus + Version links, Suche zentral, Admin-Controls nur bei Bedarf.
- Suchworkflow ist konsistent: ein Feld `q`, Mode-Dropdown (`auto|session_id|user_id|text`), Wildcard `*` und direkter Session-Sprung aus Treffern.
- Admin-Drawer reduziert Bedienfehler (Dropdowns/Toggles statt Freitext) und speichert relevante Defaults in DB (`/api/admin/settings`).
- Performance-Werte sind live sichtbar (`STT/LLM/Total avg+p95`), mit schonender Polling-Strategie (10s offen, 30s geschlossen).

## Nutzen von V9.1.11
- Agenten sehen keine globalen Admin-Einstellungen mehr und koennen weniger versehentlich falsch konfigurieren.
- Admins erhalten die globale Steuerung zentral im Admin-Client (Settings, Suche, Metrics).
- Dual-Lane bleibt stabil fuer Live + Verlauf; bei alten Nachrichten ohne Lane-Daten bleibt die Anzeige robust (Best-Effort).

## Nutzen von V9.1.12
- Kunden haben jetzt eine eigene Hilfe im Customer-Client (`?` Button) mit klaren Schritt-fuer-Schritt-Anleitungen.
- Voice- und Chat-Ablauf sind fuer Endnutzer einfacher nachvollziehbar (DE/EN).
- Kunden-Hilfe wird als formatiertes Markdown gerendert (keine Rohtext- oder Einzeilen-Darstellung).
- Kunden koennen die Oberflaechensprache (`UI`) direkt im Header zwischen DE/EN umstellen.
- UI-Strings kommen DB-basiert aus `ui_i18n_strings`, damit neue Sprachen spaeter ohne Frontend-Code eingefuegt werden koennen.
- Die UI-Sprachpraeferenz wird pro Benutzer in `user_prefs` gespeichert und beim Laden wiederhergestellt.

## Nutzen von V9.1.14
- Performance-Logs sind jetzt getrennt von den Konversationsdaten in `voice_agent_logs.perf_events`.
- Logging ist kontrollierbar (ON/OFF, Sample-Rate, Retention, Export-Max-Tage).
- Admin kann ZIP-Archive fuer ein Zeitfenster exportieren (`jsonl|csv|md` + `README.md` + `stats_summary.json`).
- Perf-Health zeigt Queue-Tiefe und verworfene Events, damit Lastspitzen sichtbar werden.

## Nutzen von V9.1.15
- Admin sieht sofort, ob STT, LLM, Translate oder TTS den Engpass verursacht.
- `Worst Spikes` macht langsame Sessions sichtbar, bevor jemand in Rohlogs suchen muss.
- Prefix-Suche mit `*` beschleunigt die Analyse nach `user_id`, `session_id` oder `error_code`.

## Nutzen von V9.1.15-p1
- Customer-Chat verhaelt sich fuer den Agenten jetzt genauso stabil wie Voice: Original + Uebersetzung bleiben auch im Verlauf erhalten.
- Agent Runtime `Backend/Model` ist klar an Admin gebunden, damit kein Konfigurationsdrift im Agent-Client entsteht.

## Nutzen von V9.1.15-p3
- Admin, Agent und Customer zeigen jetzt einen einfachen `WS RTT`-Wert im Header und machen Leitungslatenz sichtbar.
- Die Agent-Ansicht haelt die Dual-Lane-Invariante strenger ein: Kundennachrichten sollen bei Sprachunterschied immer `Original + Uebersetzung` zeigen.
- Der Smoke-Test prueft jetzt Health, WS-Ping/Pong, nicht-leere Help-Dokumente und einen Chat-Dual-Lane-Nachweis in einem Lauf.
