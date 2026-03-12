# Admin Docs (EN) - V9.1.16

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

## New in V9.1.1 (Admin)
- TTS sanitization runs only at the audio output boundary.
- Persistent data (messages/CRM exports) remains unchanged.
- Regression test: `v9/scripts/tests/test_tts_sanitize.py`.

## New in V9.1.2 (Admin)
- Agent UI includes `Auto-Refresh` for inbox updates (5-second interval, persisted in localStorage).
- WebSocket reconnect in Agent UI improves continuity after short network drops.
- `Display cleanup` affects only visible chat text in Agent UI; stored data and routing remain unchanged.

## New in V9.1.6 (Admin): WS test automation + artifact hardening
### Run the automated proof test
```bash
bash v9/scripts/tests/run_v9_duallane_ws_tests.sh
```

### What "PASS" means
You always get six lines:
1. `COMMIT`
2. `RESULT`
3. `SCENARIO1` (customer -> agent)
4. `SCENARIO2` (agent -> customer)
5. `SCENARIO3` (second customer roundtrip)
6. `P95_MS`

If `RESULT: PASS`, dual-lane routing is correct for this run.

### Where artifacts are stored
- Current run folder: `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- Optional run ZIP: `v9/artifacts/<YYYYMMDD-HHMMSS>/artifacts.zip`
- Retention: only the newest `10` runs are kept by default.
- Required files:
  - `test-log-v9.1.5.txt`
  - `SUMMARY.md`
  - `ws_probe_status.json`
  - `events-agent.jsonl`, `events-customer.jsonl`
  - `docker-logs-api.txt`, `docker-logs-web-agent.txt`, `docker-logs-web-customer.txt`
  - `ENV_SNAPSHOT.txt`
  - `session_dump.json`
  - `artifacts.zip` (inside run folder)

### Release evidence policy (important)
- Keep `artifacts/` as local working storage only.
- Do not commit evidence ZIPs, logs, or env snapshots into Git history.
- For release-relevant runs, upload only 1-3 ZIPs as GitHub Release Assets (for example: FAIL, FIX, PASS).
- Example upload command:
  - `gh release upload v9.1.6 v9/artifacts/<run-id>/artifacts.zip`

### How to read FAIL quickly
- `scenario*_eventual_delivery_failed`: event arrived too late (>10s) or not at all.
- `*_translation_not_applied_when_langs_differ`: source/target languages differ but translated lane is still equal to original.
- `*_lang_*_not_*`: wrong receiver language lane was generated.

### New WS debug metadata (for reliable troubleshooting)
Each `message.created` event now includes:
- `event_id`, `event_ts`
- `text_for_agent`, `lang_for_agent`
- `text_for_customer`, `lang_for_customer`
- `lane.agent.lang`, `lane.agent.has_translation`, `lane.agent.text_preview`
- `lane.customer.lang`, `lane.customer.has_translation`, `lane.customer.text_preview`

## New in V9.1.5-fix-voice-duallane (Admin)
- Voice events now use the same live event type as chat: `message.created`.
- Voice updates language metadata more robustly:
  - STT language
  - text-detected language
  - effective routing language

## New in V9.1.7 (Admin)
- Customer UI now has `Auto-send after recording` (default: ON, persisted in localStorage).
- Compose/API defaults now use `qwen2.5:3b` as default model.
- Fallback remains active:
  - if `qwen2.5:3b` is unavailable, the runtime falls back to the available model (typically `qwen2.5:7b`).
- TTS sanitizer remains low-risk:
  - applied only at TTS output boundary,
  - no change to stored transcripts or dual-lane routing.

### Admin quick test for V9.1.7
1. `docker compose -f v9/docker/compose.dev.yml up -d --build`
2. Customer client: start recording, speak, stop.
3. Verify: upload starts immediately (when Auto-send is ON).
4. Run `python3 v9/scripts/tests/test_tts_sanitize.py`.
5. Run `bash v9/scripts/tests/run_v9_duallane_ws_tests.sh`.
Goal: DE->EN voice traffic produces the same EN agent lane as DE->EN chat traffic.

### Required \"Voice vs Chat parity\" check
1. Agent `en`, Customer `de`.
2. Send one chat message (DE), then one voice message (DE).
3. In both cases, agent event must contain:
   - `text_original` in DE
   - `text_for_agent` in EN
   - `lang_for_agent=en`
   - `tts.agent_lang=en`

## New in V9.1.8 (Admin): Performance Toggle + Search
- New admin parameters:
  - `perf_logging_enabled`
  - `perf_logging_sample_rate` (0.0 to 1.0)
  - `perf_logging_retention_days`
  - `search_max_results`
  - `allow_text_regex_fallback`
- New admin search API:
  - `GET /api/admin/search?user_id=...&q=...&mode=auto|session_id|user_id|text&since_days=7&limit=50`
- New logging collection:
  - `admin_perf_logs` (separate from `messages`).

### Quick admin test
1. Open Admin Settings, set `perf_logging_enabled=ON`, save.
2. Run one short conversation.
3. Test search:
   - partial session id with `*` (example: `abc123*`)
   - text fragment (example: `breaker`)
4. Open a hit using `Open Session`.
5. Set `perf_logging_enabled=OFF`.

### Automated test run
```bash
bash scripts/run_v9_1_8_admin_tests.sh
```
- Artifacts are written to `v9/artifacts/<timestamp>/`.
- ZIP helper:
```bash
bash v9/scripts/zip_artifacts.sh v9/artifacts/<timestamp>
```

## New in V9.1.9 (Admin): Agent Drawer + 10m Perf Header
- Agent UI is cleaned up as an operational workspace:
  - always-visible header (WS status + version + search + admin button)
  - search via `/api/admin/search` using `q` + `mode`
  - admin settings moved into a Drawer with safe controls
- New/extended admin settings:
  - `perf_metrics_enabled` (compatible alias with `perf_logging_enabled`)
  - `default_backend`
  - `default_model`
- `GET /api/admin/metrics/summary` now supports `window=10m` and returns both `avg_ms` and `p95_ms`.

### Admin quick test V9.1.9
1. Open Agent UI (`8087`), open `Admin ⚙︎`.
2. Adjust backend/model/toggles and click `Save`.
3. Run search with `fe774f*` (mode `auto`) and open session from results.
4. Verify performance strip shows values (`STT/LLM/Total avg+p95`).

### Automated smoke test V9.1.9
```bash
bash scripts/run_v9_1_9_ui_smoke.sh
```
- Output and artifacts: `v9/artifacts/<YYYYMMDD-HHMMSS>/`

## New in V9.1.11 (Admin): Agent/Admin role separation
- Agent client:
  - now exposes only `Agent Settings` (no global admin controls)
  - uses `/api/agent/search` for search
- Admin client:
  - remains the central place for global admin settings (`/api/admin/settings`)
  - shows header perf badges (`STT/LLM/TTS/Total avg/p95`)
  - keeps unified admin search (`/api/admin/search`) with `auto|session_id|user_id|text` and wildcard `*`

### Admin quick test V9.1.11
1. Open Admin client and verify:
   - header shows the correct release version for that build
   - perf badges are populated
2. Header search:
   - `fe774f*` (session/user fragment)
   - `Wallbox` (text)
   - click result -> session opens
3. Open Agent client:
   - no admin token / no global admin settings exposed

## New in V9.1.12 Patch 2: Customer UI language from DB
- New collection for UI strings:
  - `ui_i18n_strings`
  - Schema: `scope`, `key`, `lang`, `text`, `updated_at`
- New collection for UI preferences:
  - `user_prefs`
  - Schema: `user_id`, `scope`, `ui_lang`, `updated_at`

### Where is the translation table?
- In MongoDB:
  - DB: `voice_agent` (or your configured `MONGO_DB`)
  - Collection: `ui_i18n_strings`
- Customer UI scope:
  - `scope=customer`

### How to add another language
1. Insert rows for each UI key in `ui_i18n_strings` with the new `lang`.
2. Verify via API:
   - `GET /api/i18n?scope=customer&lang=<new>`
3. Select that UI language in customer client.
4. If a key is missing, UI falls back to English (`en`).

## New in V9.1.14: Performance logging + ZIP export
- Performance logs are now separated in a dedicated log database:
  - DB: `voice_agent_logs` (ENV: `MONGO_LOG_DB`)
  - Collection: `perf_events`
- Runtime-toggle settings:
  - `perf_logging_enabled` (on/off)
  - `perf_logging_retention_days` (TTL, e.g. 30/365/730)
  - `perf_export_max_days` (max export window)
  - `perf_logging_sample_rate` (0..1)
  - `perf_log_text_enabled` (default OFF)

### Key admin endpoints
- `GET /api/admin/settings?user_id=...`
- `POST /api/admin/settings`
- `GET /api/admin/perf/health?user_id=...`
- `GET /api/admin/perf/export?user_id=...&from=<iso>&to=<iso>&format=jsonl|csv|md`

### 2-minute admin test
1. In admin settings, set `perf_logging_enabled=ON`.
2. Run one short chat interaction (customer -> agent -> response).
3. Check `GET /api/admin/perf/health`:
   - `log_db=voice_agent_logs`
   - `has_ttl_index=true`
4. Trigger export via `/api/admin/perf/export`, download ZIP.
5. Verify ZIP contains:
   - `perf_events_*.jsonl` or `.csv`/`.md`
   - `README.md`
   - `stats_summary.json`

## New in V9.1.15: Admin Performance Dashboard
- Admin can now see directly in the performance area:
  - summary cards
  - `avg/p95` for STT, LLM, Translate, TTS, Total
  - `Worst Spikes`
  - perf search with prefix wildcard `*`
- New endpoints:
  - `GET /api/admin/perf/summary?user_id=...&window=1h|24h|7d|30d`
  - `GET /api/admin/perf/search?user_id=...&q=fe77*&from=<iso>&to=<iso>&limit=50`
  - `POST /api/admin/perf/export/delete`

### 2-minute admin test V9.1.15
1. Open Admin client (`8085`).
2. Switch `Window` between `1h`, `24h`, `7d`, `30d`.
3. In `Worst Spikes`, check which session was slowest.
4. Search in the perf field with `fe77*` or a session id.
5. Export the last 24h and optionally delete the exported range afterward.

### Note
- The header must now show `Voice Agent Admin Client v9.1.16`.
- If an older version is still visible: do a hard reload (`Cmd+Shift+R`).

## Patch V9.1.15-p1: Chat dual-lane + agent runtime scope
- Customer chat now persists the same lane metadata as voice.
- This means the agent keeps seeing both:
  - `Original`
  - `Translation`
  even after reload and in session history.
- Agent Runtime `Backend/Model` in Agent UI is now read-only and clearly marked `Admin-controlled`.

### 2-minute proof
1. Agent client: `Agent language = en`, `Incoming speak = ON`.
2. Customer client: send German chat text: `Meine Wallbox blinkt rot. Was kann ich tun?`
3. Expected in Agent:
   - `Original (de)`
   - `Translation (en)`
   - audio only in EN
4. Agent replies in EN.
5. Expected in Customer:
   - text/audio in DE.

## Patch V9.1.15-p3: WebSocket RTT + guardrails
- Admin, Agent, and Customer now show in the header:
  - `WS: connected/disconnected`
  - `WS RTT: <ms>`
- The RTT value comes from a lightweight ping/pong over the existing WebSocket connection.
- Benefit:
  - short network slowdowns become visible immediately
  - demos show not only "connected", but also whether the socket is responsive

### Admin quick check
1. Open `http://localhost:8085`, `8086`, and `8087`.
2. Wait 5-10 seconds.
3. Verify:
   - all three headers show an RTT value
   - on disconnect, the UI falls back to `WS RTT: -`

### Guardrail for agent dual-lane
- For `customer -> agent` with different languages, the agent view must show:
  - `Original`
  - `Translation`
- This applies to:
  - live WebSocket events
  - reload / session history

## New in V9.1.16: Search modes, wildcards, and repeatable proof
### Search modes in the Admin client
- `auto`: detects identifier-like queries, otherwise falls back to text search.
- `session_id`: exact or wildcard search on session ids.
- `user_id`: exact or wildcard search on user ids.
- `text`: searches conversation text, lane text, and answer fields.

### Wildcard rules
- `fe77*` = prefix
- `*wallbox*` = contains
- `*c8e9` = suffix
- `*` alone is rejected on purpose to avoid full collection scans.

### Index and troubleshooting notes
- The API creates search indexes idempotently at startup.
- If search unexpectedly returns nothing:
  1. check `curl -s http://localhost:8085/api/health`
  2. run `python3 v9/scripts/check_docs.py`
  3. run `bash v9/scripts/run_v9_1_16_search_tests.sh`
  4. inspect `v9/artifacts/runs/v9.1.16-search-.../SUMMARY.md`

### 2-minute proof for search
1. Open the Admin client.
2. Search for `*wallbox*`.
3. Review the result snippets.
4. Click `Open Session`.
5. Verify the full history shows `Original + Translation`.

## Patch V9.1.16: Voice/chat parity in the UI
- Customer client:
  - shows the customer's own transcript again after voice input
  - shows the answer in the same chat history
- Agent client:
  - still shows `Original + Translation` for customer voice input
  - now also shows the agent lane again for generated answers, including reload

### Required proof
1. Customer `de`, Agent `en`.
2. Send one voice interaction.
3. Expected in Customer:
   - transcript visible
   - answer visible
4. Expected in Agent:
   - customer text: `Original (de) + Translation (en)`
   - generated answer: `Original + Translation (en)`
5. Reload the history and verify again.
