# Admin Docs (DE) - V9.0.0

## Ziel
Diese Admin-Doku zeigt Ihnen Schritt fuer Schritt:
- wie Sie das System starten,
- welche Parameter relevant sind,
- wie Sie die Sprachprofile Agent <-> Kunde testen,
- wie Sie Fehler reproduzierbar finden.

## Verzeichnisse (wichtig fuer Admins)
- API: `v9/docker/api/`
- Admin Web: `v9/web/`
- Customer Web: `v9/web-customer/`
- Agent Web: `v9/web-agent/`
- Compose: `v9/docker/compose.dev.yml`
- Templates: `v9/templates/`
- Skripte: `v9/scripts/`
- Testlogs: `v9/output/testlogs/` und `v9/test-logs/`

## Start als Admin
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml ps
```

## Komponenten-Test (Pflicht, Reihenfolge)
1. API
```bash
curl -s http://localhost:8085/api/health
```
2. Modelkatalog
```bash
curl -s http://localhost:8085/api/models
```
3. Piper (TTS Sidecar)
```bash
curl -s -X POST http://localhost:5005/tts -H 'Content-Type: application/json' -d '{"text":"Test","lang":"de"}' >/dev/null
```
4. Mongo
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```
5. Valkey
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml exec valkey valkey-cli ping
```

## Sprachrouting Agent <-> Kunde (Fachlogik)
### Zielzustand
- Agent arbeitet immer in `Agent Sprache`.
- Kunde bekommt immer Kundensprache + Kunden-Voice-Profil.
- `Customer output lang = auto` nutzt das erkannte Kundenprofil.

### Technische Kernfelder
- Session-Meta:
  - `meta.customer_lang_last`
  - `meta.customer_voice_lang_last`
- Agent Request:
  - `agent_lang`
  - `tts_lang` (leer = auto)
- Event-Payload:
  - `source_lang`
  - `customer_lang`
  - `customer_voice_lang`

## Admin-Testprozedur (ausfuehrlich)

### Test A: Kunde DE, Agent EN (`agenten-02`)
1. Agent UI (`8087`) oeffnen.
2. Setzen:
   - Demo User: `agenten-02 (EN)`
   - Agent ID: `agenten-02`
   - Agent Sprache: `en`
   - Empfang auf Agent sprechen: ON
   - Kunden-Ausgabe auf Agent sprechen: OFF
   - Customer output lang: `auto`
3. Kunde in `8086` spricht/schreibt Deutsch.
4. Erwartung:
   - Agent sieht/hoert Englisch.
   - Agent sieht `Original + Uebersetzung` im Chatfenster.
   - Agent antwortet auf Englisch.
   - Kunde bekommt Deutsch + deutsche Stimme.

### Test B: Kunde EN, Agent DE (`agent-de-01`)
1. Agent setzen:
   - Agent ID: `agent-de-01`
   - Agent Sprache: `de`
   - Customer output lang: `auto`
2. Kunde spricht/schreibt Englisch.
3. Erwartung:
   - Agent sieht/hoert Deutsch.
   - Agent antwortet auf Deutsch.
   - Kunde bekommt Englisch + englische Stimme.

### Test C: Manuelle Ueberschreibung
1. Kunde startet auf Deutsch.
2. Agent setzt `Customer output lang = en`.
3. Agent antwortet in eigener Sprache.
4. Erwartung:
   - Kunde bekommt Englisch (Text + Voice), trotz deutschem Start.

## Wichtige Parameter (Admin-setzbar)
- `DEFAULT_UI_LANG`
- `SUPPORTED_UI_LANGS`
- `SUPPORTED_TTS_LANGS`
- `LISTEN_SILENCE_MS_DEFAULT` (muss 1300 sein)
- `LISTEN_THRESHOLD_DEFAULT`
- `ADMIN_UI_TOKEN`
- `MONGO_URL`
- `VALKEY_URL`
- `PIPER_BASE_URL`
- `OLLAMA_BASE_URL`
- `OPENAI_API_KEY` (optional)
- `UI_VERSION`, `UI_BUILD`

## Help-Menue Pflichtstruktur
1. Admin Token speichern
2. Benutzer Handbuch
3. Demo Guide
4. Admin Docs
5. Release Notes

## Dauerregel fuer kommende Releases
Bei jeder neuen Version muessen User Guide, Demo Guide und Admin Docs den aktuellen Sprachfluss enthalten:
- Agent-Sprache
- Customer output lang (auto/manuell)
- Rueckuebersetzung Agent -> Kunde
- Voice-Profil-Zuordnung Kunde

## Troubleshooting
- `API upstream unavailable`:
  - auf `http://localhost:8003/health` pruefen,
  - dann Web-Proxy erneut pruefen.
- Kunde bekommt falsche Sprache:
  - Agent UI: `Customer output lang` pruefen,
  - fuer automatische Zuordnung auf `auto`.
- Agent bekommt falsche Sprache:
  - `Agent Sprache` pruefen,
  - Session neu laden.
- Zwei Ausgaben gleichzeitig:
  - `Kunden-Ausgabe auf Agent sprechen` deaktivieren.

## Neu in V9.1.0: Lane- und TTS-Contract
- WS-Events enthalten jetzt explizit:
  - `text_original`, `lang_original`
  - `agent.text`, `agent.lang`
  - `customer.text`, `customer.lang`
  - `tts.agent_text`, `tts.agent_lang`, `tts.customer_text`, `tts.customer_lang`
- Session-Meta speichert:
  - `meta.customer_lang_ui_last`
  - `meta.agent_lang_ui_last`
- Kunden-Client hat Dropdown `Kundensprache`; diese wird beim WS-Connect als `customer_lang` uebergeben.

## Neu in V9.1.1 (Admin)
- TTS-Sanitize laeuft nur am Audio-Ausgabepunkt.
- Persistente Daten (Messages/CRM-Exports) bleiben unveraendert.
- Regressionstest: `v9/scripts/tests/test_tts_sanitize.py`.

## Neu in V9.1.2 (Admin)
- Agent-UI hat `Auto-Refresh` fuer Inbox-Updates (Intervall 5 Sekunden, per LocalStorage steuerbar).
- WS-Reconnect im Agent-Client reduziert Aussetzer bei kurzzeitigen Netzwerkabbruechen.
- `Anzeige bereinigen` wirkt nur auf den sichtbaren Text im Agent-Chat und nicht auf persistente Daten.

## Neu in V9.1.6 (Admin): WS-Testautomation + Artefakt-Hardening
### Automatischen Nachweis-Test starten
```bash
bash v9/scripts/tests/run_v9_duallane_ws_tests.sh
```

### Was "PASS" bedeutet
Sie erhalten immer sechs Zeilen:
1. `COMMIT`
2. `RESULT`
3. `SCENARIO1` (Kunde -> Agent)
4. `SCENARIO2` (Agent -> Kunde)
5. `SCENARIO3` (zweite Kundenrunde mit Antwort)
6. `P95_MS`

Wenn `RESULT: PASS` steht, ist das Dual-Lane-Routing fuer diesen Lauf korrekt.

### Wo die Artefakte liegen
- Aktueller Lauf: `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- Optionales Lauf-ZIP: `v9/artifacts/<YYYYMMDD-HHMMSS>/artifacts.zip`
- Aufbewahrung: standardmaessig bleiben nur die neuesten `10` Laeufe.
- Pflichtdateien:
  - `test-log-v9.1.5.txt`
  - `SUMMARY.md`
  - `ws_probe_status.json`
  - `events-agent.jsonl`, `events-customer.jsonl`
  - `docker-logs-api.txt`, `docker-logs-web-agent.txt`, `docker-logs-web-customer.txt`
  - `ENV_SNAPSHOT.txt`
  - `session_dump.json`
  - `artifacts.zip` (im Laufordner)

### Release-Evidence-Regel (wichtig)
- `artifacts/` bleibt lokaler Arbeitsbereich.
- Evidence-ZIPs, Logs und Env-Snapshots werden nicht in Git versioniert.
- Fuer release-relevante Nachweise laden Sie nur 1-3 ZIPs als GitHub-Release-Assets hoch (z. B. FAIL, FIX, PASS).
- Beispiel-Upload:
  - `gh release upload v9.1.6 v9/artifacts/<run-id>/artifacts.zip`

### FAIL schnell verstehen
- `scenario*_eventual_delivery_failed`: Event kam zu spaet (>10s) oder gar nicht.
- `*_translation_not_applied_when_langs_differ`: Quell- und Zielsprache sind verschieden, aber die Ziel-Lane wurde nicht uebersetzt.
- `*_lang_*_not_*`: falsche Empfaengersprache wurde erzeugt.

### Neue WS-Debugfelder (fuer klare Analyse)
Jedes `message.created`-Event enthaelt jetzt:
- `event_id`, `event_ts`
- `text_for_agent`, `lang_for_agent`
- `text_for_customer`, `lang_for_customer`
- `lane.agent.lang`, `lane.agent.has_translation`, `lane.agent.text_preview`
- `lane.customer.lang`, `lane.customer.has_translation`, `lane.customer.text_preview`

## Neu in V9.1.5-fix-voice-duallane (Admin)
- Voice-Events verwenden jetzt denselben Live-Eventtyp wie Chat: `message.created`.
- Voice aktualisiert Session-Meta fuer Sprache robust:
  - STT-Sprache
  - textbasierte Erkennung
  - effektive Routing-Sprache

## Neu in V9.1.7 (Admin)
- Customer UI hat jetzt den Schalter `Auto-send after recording` (Standard: AN, in LocalStorage gespeichert).
- Compose/API-Defaults nutzen `qwen2.5:3b` als Standardmodell.
- Fallback bleibt aktiv:
  - wenn `qwen2.5:3b` nicht verfuegbar ist, wird auf vorhandenes Modell (typisch `qwen2.5:7b`) gewechselt.
- TTS-Sanitizer bleibt low-risk:
  - nur direkt am TTS-Ausgabepunkt,
  - keine Aenderung an gespeicherten Transkripten oder Dual-Lane-Routing.

### Admin-Kurztest V9.1.7
1. `docker compose -f v9/docker/compose.dev.yml up -d --build`
2. Customer-Client: Aufnahme starten, sprechen, stoppen.
3. Pruefen: Upload startet sofort (bei aktivem Auto-send).
4. `python3 v9/scripts/tests/test_tts_sanitize.py` ausfuehren.
5. `bash v9/scripts/tests/run_v9_duallane_ws_tests.sh` ausfuehren.
Ziel: Agent bekommt bei DE->EN im Voice-Fall dieselbe EN-Lane wie im Chat-Fall.

### Pflicht-Test \"Voice vs Chat parity\"
1. Agent `en`, Kunde `de`.
2. Einmal Chat senden (DE), einmal Voice senden (DE).
3. In beiden Faellen muss im Agent-Event gelten:
   - `text_original` DE
   - `text_for_agent` EN
   - `lang_for_agent=en`
   - `tts.agent_lang=en`

## Neu in V9.1.8 (Admin): Performance Toggle + Search
- Neue Admin-Parameter:
  - `perf_logging_enabled`
  - `perf_logging_sample_rate` (0.0 bis 1.0)
  - `perf_logging_retention_days`
  - `search_max_results`
  - `allow_text_regex_fallback`
- Neue API-Suche:
  - `GET /api/admin/search?user_id=...&q=...&mode=auto|session_id|user_id|text&since_days=7&limit=50`
- Neue Logging-Collection:
  - `admin_perf_logs` (separat von `messages`).

### Schnelltest fuer Admins
1. Admin Settings oeffnen, `perf_logging_enabled=AN`, speichern.
2. Eine kurze Unterhaltung starten.
3. Suche testen:
   - Teil-Session-ID mit `*` (z. B. `abc123*`)
   - Textfragment (z. B. `breaker`)
4. Treffer mit `Open Session` oeffnen.
5. `perf_logging_enabled=AUS` setzen.

### Automatisierter Testlauf
```bash
bash scripts/run_v9_1_8_admin_tests.sh
```
- Artefakte liegen in `v9/artifacts/<timestamp>/`.
- ZIP-Helfer:
```bash
bash v9/scripts/zip_artifacts.sh v9/artifacts/<timestamp>
```

## Neu in V9.1.9 (Admin): Agent Drawer + Perf-Header 10m
- Agent-UI wurde als Arbeitsoberflaeche aufgeraeumt:
  - Header immer sichtbar (WS-Status + Version + Suche + Admin-Button)
  - Suche ueber `/api/admin/search` mit `q` + `mode`
  - Admin-Einstellungen im Drawer statt verstreuter Freitextfelder
- Neue/erweiterte Admin-Settings:
  - `perf_metrics_enabled` (kompatibel zu `perf_logging_enabled`)
  - `default_backend`
  - `default_model`
- `GET /api/admin/metrics/summary` unterstuetzt jetzt `window=10m` und liefert `avg_ms` + `p95_ms`.

### Admin-Kurztest V9.1.9
1. Agent-UI (`8087`) oeffnen, `Admin ⚙︎` oeffnen.
2. Backend/Model und Toggles setzen, `Save` klicken.
3. Suche mit `fe774f*` (Mode `auto`) ausfuehren und Session aus Trefferliste oeffnen.
4. Pruefen, dass der Perf-Header Werte zeigt (`STT/LLM/Total avg+p95`).

### Automatisierter Smoke-Test V9.1.9
```bash
bash scripts/run_v9_1_9_ui_smoke.sh
```
- Ergebnis und Artefakte unter: `v9/artifacts/<YYYYMMDD-HHMMSS>/`

## Neu in V9.1.11 (Admin): Rollentrennung Agent/Admin
- Agent-Client:
  - hat nur noch `Agent Settings` (keine globalen Admin-Parameter mehr)
  - nutzt fuer Suche den Endpoint `/api/agent/search`
- Admin-Client:
  - bleibt zentrale Stelle fuer globale Admin-Settings (`/api/admin/settings`)
  - zeigt Header-Perf-Badges (`STT/LLM/TTS/Total avg/p95`)
  - hat zentrale Admin-Suche (`/api/admin/search`) mit `auto|session_id|user_id|text` und Wildcard `*`

### Admin-Kurztest V9.1.11
1. Admin-Client oeffnen und pruefen:
   - Header zeigt Version `v9.1.11`
   - Perf-Badges werden geladen
2. Suche im Header:
   - `fe774f*` (Session/User Fragment)
   - `Wallbox` (Text)
   - Treffer anklicken -> Session wird geladen
3. Agent-Client pruefen:
   - kein Admin-Token / keine globalen Admin-Settings sichtbar

## Neu in V9.1.12 Patch 2: Customer UI Sprache aus DB
- Neue Collection fuer UI-Texte:
  - `ui_i18n_strings`
  - Schema: `scope`, `key`, `lang`, `text`, `updated_at`
- Neue Collection fuer UI-Praeferenzen:
  - `user_prefs`
  - Schema: `user_id`, `scope`, `ui_lang`, `updated_at`

### Wo finde ich die Uebersetzungstabelle?
- In MongoDB:
  - DB: `voice_agent` (oder dein `MONGO_DB`)
  - Collection: `ui_i18n_strings`
- Scope fuer Kundenoberflaeche:
  - `scope=customer`

### Wie fuege ich eine neue Sprache hinzu?
1. Pro UI-Key einen Datensatz in `ui_i18n_strings` mit neuem `lang` anlegen.
2. API testen:
   - `GET /api/i18n?scope=customer&lang=<neu>`
3. Im Kunden-Client die UI-Sprache waehlen.
4. Falls kein Satz gefunden wird, faellt das System auf Englisch (`en`) zurueck.
