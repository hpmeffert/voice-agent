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
