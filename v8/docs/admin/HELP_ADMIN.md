# Admin Handbuch - V8.10.2

## Ziel dieses Handbuchs
Dieses Dokument erklaert alle admin-relevanten Funktionen in V8: wofuer sie gut sind, welche Parameter gesetzt werden koennen, wie du die Installation startest und wie du die Betriebsfaehigkeit Schritt fuer Schritt testest.

## 1) Projektstruktur und wichtige Verzeichnisse
- API: `v8/docker/api/`
- Admin UI: `v8/web/`
- Customer UI: `v8/web-customer/`
- Agent UI: `v8/web-agent/`
- Compose: `v8/docker/compose.dev.yml`
- Templates: `v8/templates/`
- Doku User: `v8/docs/ui/HELP_USER.md`
- Doku Demo: `v8/docs/ui/DEMO_GUIDE.md`
- Doku Admin: `v8/docs/admin/HELP_ADMIN.md`
- Security Checklist: `v8/docs/SECURITY_BASELINE_MAC.md`
- Channel-Spec: `v8/docs/transport_channels.md`

## 2) Installation und Start als Admin
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml ps
```

Stop/Clean:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## 3) Komponenten-Checks in korrekter Reihenfolge
1. API Health
```bash
curl -s http://localhost:8082/api/health
```
2. Modellverfuegbarkeit (Whisper/Ollama sichtbar)
```bash
curl -s http://localhost:8082/api/models
```
3. EventBus/Valkey
```bash
curl -s http://localhost:8082/api/eventbus/health
```
4. Piper TTS
```bash
curl -s -X POST http://localhost:5004/tts -H 'Content-Type: application/json' -d '{"text":"Systemtest","lang":"de"}' >/dev/null
```
5. Mongo
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```
6. Valkey
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec valkey valkey-cli ping
```

## 4) Admin-Funktionen (Wofuer gut, Parameter, Test, Release-Verweis)

### Funktion: Session-Liste fuer Agenten
- Wofuer gut: aktive Sessions fuer Support-Team filtern.
- Endpoint: `GET /api/agent/sessions`
- Parameter:
  - `status` (`active`)
  - `limit` (`1..200`)
  - optional `user_id`
  - optional `session_id`
  - optional `q` (Freitext)
- Test:
```bash
curl -s "http://localhost:8082/api/agent/sessions?status=active&limit=50"
```
- Release-Verweis: V8.2.0 (Basis), V8.3.0 (Suche erweitert).

### Funktion: Admin-Konversationssuche
- Wofuer gut: Konversationen nach Kunde, Session oder Inhalt finden.
- Endpoint: `GET /api/admin/conversations/search`
- Parameter:
  - `user_id` (Admin-Identitaet)
  - optional `search_user_id`
  - optional `session_id`
  - optional `q` (Wort/Textabschnitt)
  - `limit` (`1..500`)
  - optional Header `X-Admin-Token`
- Test:
```bash
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN>&q=stichwort&limit=50" -H "X-Admin-Token: <TOKEN>"
```
- Release-Verweis: V8.5.0.

### Funktion: Handoff Request/Accept
- Wofuer gut: Uebergabe von Self-Service an menschlichen Agenten.
- Endpoints:
  - `POST /api/handoff/request`
  - `POST /api/handoff/accept`
- Parameter:
  - Request: `session_id`, `user_id`, optional `reason`
  - Accept: `session_id`, `agent_id`
- Test:
```bash
curl -s -X POST http://localhost:8082/api/handoff/request \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","user_id":"<UID>","reason":"customer_request"}'

curl -s -X POST http://localhost:8082/api/handoff/accept \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","agent_id":"agent-01"}'
```
- Release-Verweis: V8.7.0.

### Funktion: Security Baseline (neu)
- Wofuer gut: Schutz vor oversized Requests, Spam-Bursts und unsicheren Browser Defaults.
- Relevante Parameter:
  - `MAX_AUDIO_BYTES`
  - `MAX_REQUEST_BYTES`
  - `MAX_TEXT_CHARS`
  - `RATE_LIMIT_WINDOW_SEC`
  - `RATE_LIMIT_MAX_REQUESTS`
- Test:
```bash
# Header
curl -I http://localhost:8082/

# Rate limit (429 erwartet)
for i in $(seq 1 35); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/api/models; done
```
- Release-Verweis: V8.8.0.

### Funktion: V7 -> V8 Migration
- Wofuer gut: sicherer Umstieg von V7 auf V8 ohne Port-/Compose-Konflikte.
- Dokument: `v8/docs/MIGRATION_V7_TO_V8.md`
- Enthaltene Parameter:
  - Ports (`8002`, `8082`, `8083`, `8084`, `5004`, `27019`, `6381`)
  - Kern-ENV (`MONGO_URL`, `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`, `UI_VERSION`)
  - Limits/Security (`MAX_AUDIO_BYTES`, `MAX_REQUEST_BYTES`, `RATE_LIMIT_*`)
- Test:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
curl -s http://localhost:8082/api/health
```
- Release-Verweis: V8.9.0.

### Funktion: Agent -> Kunde Translation (neu)
- Wofuer gut: Agent schreibt in eigener Sprache, Kunde bekommt Nachricht in Ziel-/Kundensprache.
- Endpoint: `POST /api/agent/message`
- Parameter:
  - `session_id` (Pflicht)
  - `agent_id` (Pflicht)
  - `text` (Pflicht, Agent-Originaltext)
  - `tts_lang` (optional, Zielsprache fuer Kunden-Ausgabe)
  - `speak` (optional, Text per TTS ausgeben)
- Response:
  - `source_lang`
  - `answer_original`
  - `answer_translated`
  - `translation_ms`
- Test:
```bash
# 1) Session erzeugen
curl -s -X POST http://localhost:8082/api/chat/text \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"admin-test-agent-translate","text":"Hallo, ich spreche Deutsch.","tts_lang":"de"}'

# 2) Agent schreibt EN, Kunde bekommt DE
curl -s -X POST http://localhost:8082/api/agent/message \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","agent_id":"agent-01","text":"Hello, I can help you now.","tts_lang":"de","speak":true}'
```
- Erwartung:
  - `answer_original` ist Englisch
  - `answer_translated` ist Deutsch
  - `translation_ms` > 0 bei echter Uebersetzung
- Release-Verweis: V8.10.2.

## 5) Alle admin-einstellbaren Parameter (Compose/API)
- Plattform/Betrieb:
  - `UI_VERSION`, `UI_BUILD`
  - `ADMIN_DEV_MODE`, `ADMIN_UI_TOKEN`
- Modelle:
  - `WHISPER_MODEL`, `WHISPER_COMPUTE`
  - `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_NUM_PREDICT`, `OLLAMA_TEMPERATURE`, `OLLAMA_NUM_CTX`
  - `OPENAI_API_KEY`, `OPENAI_MODEL`
- Limits/Sicherheit:
  - `MAX_AUDIO_BYTES`, `MAX_REQUEST_BYTES`, `MAX_TEXT_CHARS`
  - `RATE_LIMIT_WINDOW_SEC`, `RATE_LIMIT_MAX_REQUESTS`
- Storage/Retention:
  - `MONGO_URL`, `MESSAGE_RETENTION_DAYS`, `SESSION_RETENTION_DAYS`, `METRICS_RETENTION_DAYS`
- Export/Protocol:
  - `CRM_EXPORT_ENABLED`, `CRM_EXPORT_DEFAULT_ENABLED`, `CRM_EXPORT_MODE`, `CRM_EXPORT_WEBHOOK_URL`
  - `CRM_EXPORT_FORMAT`, `CRM_EXPORT_TEMPLATE_MD`, `CRM_EXPORT_INCLUDE_TIMESTAMPS`, `CRM_EXPORT_TIMEZONE`
  - `MAX_EXPORT_MESSAGES`, `MAX_EXPORT_BYTES`
  - `CRM_PROTOCOL_ENABLED`, `CRM_PROTOCOL_TEMPLATE`, `CRM_PROTOCOL_FORMAT`, `CRM_PROTOCOL_TIMEZONE`, `PROTOCOL_TEMPLATE_PATH`
- EventBus/Realtime:
  - `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`
- UI/Sprachen:
  - `DEFAULT_UI_LANG`, `SUPPORTED_UI_LANGS`, `SUPPORTED_TTS_LANGS`
  - `LISTEN_MODE_DEFAULT`, `LISTEN_SILENCE_MS_DEFAULT`, `LISTEN_THRESHOLD_DEFAULT`

## 6) Uebersetzungstabelle und neue Sprachen
- Uebersetzungen werden in Mongo Collection `ui_translations` gespeichert.
- Seed-Quelle in Code: `v8/docker/api/app.py` in `seed_ui_translations()`.
- Vorgehen fuer neue Sprache:
  1. Sprachcode in `SUPPORTED_UI_LANGS` aufnehmen (Compose/API env).
  2. In `seed_ui_translations()` pro Key die neue Sprachspalte hinterlegen.
  3. API neu starten (`docker compose ... up -d --build api`).
  4. In UI `Sprache` testen und Menue/Labels pruefen.

## 7) Pflichtchecks vor jedem Release
```bash
python3 v8/scripts/check_docs.py
make v8-lint
make v8-test
```

Zusatz:
- User-Handbuch darf keine Release-Notes enthalten.
- Menuepunkt muss `Benutzer Handbuch` heissen.
