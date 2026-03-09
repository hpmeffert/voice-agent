# Admin Docs (EN) - V9.0.0

## Purpose
This admin guide explains:
- how to start the stack,
- which parameters matter,
- how to test agent/customer language routing,
- how to troubleshoot in a repeatable way.

## Directories (admin map)
- API: `v9/docker/api/`
- Admin web: `v9/web/`
- Customer web: `v9/web-customer/`
- Agent web: `v9/web-agent/`
- Compose: `v9/docker/compose.dev.yml`
- Templates: `v9/templates/`
- Scripts: `v9/scripts/`
- Test logs: `v9/output/testlogs/` and `v9/test-logs/`

## Start as admin
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml ps
```

## Required component checks (order)
1. API
```bash
curl -s http://localhost:8085/api/health
```
2. Model catalog
```bash
curl -s http://localhost:8085/api/models
```
3. Piper (TTS sidecar)
```bash
curl -s -X POST http://localhost:5005/tts -H 'Content-Type: application/json' -d '{"text":"Test","lang":"en"}' >/dev/null
```
4. Mongo
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```
5. Valkey
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml exec valkey valkey-cli ping
```

## Agent <-> Customer language routing logic
### Target behavior
- Agent always works in selected `Agent Sprache`.
- Customer always receives customer language + customer voice profile.
- `Customer output lang = auto` follows detected customer profile.

### Core technical fields
- Session meta:
  - `meta.customer_lang_last`
  - `meta.customer_voice_lang_last`
- Agent request:
  - `agent_lang`
  - `tts_lang` (empty = auto)
- Event payload:
  - `source_lang`
  - `customer_lang`
  - `customer_voice_lang`

## Detailed admin test routine

### Test A: Customer DE, Agent EN (`agenten-02`)
1. Open Agent UI (`8087`).
2. Set:
   - Demo User: `agenten-02 (EN)`
   - Agent ID: `agenten-02`
   - Agent Sprache: `en`
   - Play incoming on agent: ON
   - Play customer output on agent: OFF
   - Customer output lang: `auto`
3. Customer in `8086` sends German speech/text.
4. Expected:
   - Agent sees/hears English.
   - Agent sees `Original + Translation` in the chat panel.
   - Agent replies in English.
   - Customer receives German + German voice.

### Test B: Customer EN, Agent DE (`agent-de-01`)
1. Set agent:
   - Agent ID: `agent-de-01`
   - Agent Sprache: `de`
   - Customer output lang: `auto`
2. Customer sends English speech/text.
3. Expected:
   - Agent sees/hears German.
   - Agent replies in German.
   - Customer receives English + English voice.

### Test C: Manual override
1. Customer starts in German.
2. Agent sets `Customer output lang = en`.
3. Agent replies in own language.
4. Expected:
   - Customer receives English text + voice, even though session started in German.

## Key parameters (admin-settable)
- `DEFAULT_UI_LANG`
- `SUPPORTED_UI_LANGS`
- `SUPPORTED_TTS_LANGS`
- `LISTEN_SILENCE_MS_DEFAULT` (must be 1300)
- `LISTEN_THRESHOLD_DEFAULT`
- `ADMIN_UI_TOKEN`
- `MONGO_URL`
- `VALKEY_URL`
- `PIPER_BASE_URL`
- `OLLAMA_BASE_URL`
- `OPENAI_API_KEY` (optional)
- `UI_VERSION`, `UI_BUILD`

## Required Help menu order
1. Save Admin Token
2. User Guide
3. Demo Guide
4. Admin Docs
5. Release Notes

## Permanent rule for future releases
Every release must keep language-flow docs updated in User Guide, Demo Guide, and Admin Docs:
- agent language
- customer output lang (auto/manual)
- translation back from agent to customer
- customer voice profile mapping

## Troubleshooting
- `API upstream unavailable`:
  - check `http://localhost:8003/health`,
  - then retry through web proxy.
- Wrong customer language output:
  - verify Agent UI `Customer output lang`,
  - set to `auto` for profile-based routing.
- Wrong agent-side language:
  - verify `Agent Sprache`,
  - reload session.
- Two voices at once:
  - disable `Play customer output on agent`.

## New in V9.1.0: Lane + TTS contract
- WebSocket events now carry explicit fields:
  - `text_original`, `lang_original`
  - `agent.text`, `agent.lang`
  - `customer.text`, `customer.lang`
  - `tts.agent_text`, `tts.agent_lang`, `tts.customer_text`, `tts.customer_lang`
- Session meta persists:
  - `meta.customer_lang_ui_last`
  - `meta.agent_lang_ui_last`
- Customer client now has a `Customer language` dropdown and sends `customer_lang` on WS connect.
