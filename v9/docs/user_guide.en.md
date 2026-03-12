# User Guide (EN, Agent View) - V9.1.11

## What does Voice Agent do?
Voice Agent keeps customer and agent conversations in sync across languages:
1. Customer speaks or types.
2. System detects customer language.
3. Agent works in the agent's own language.
4. System translates back to customer language.
5. Customer hears the answer with matching voice profile.

Goal: both sides work in their own language without losing context.

## UIs (Agent flow)
- Customer UI: `http://localhost:8086`
- Agent UI: `http://localhost:8087`

## Agent language at the top of Agent UI
Top controls in Agent UI:
- `Demo User` (dropdown for quick demo-agent selection)
- `Agent ID`
- `Agent Sprache` (`de`, `en`, `no`, `sv`, `fi`)
- `Play incoming on agent` (on/off)
- `Play customer output on agent` (on/off, default OFF)
- `Customer output lang`

### What does `Agent Sprache` do?
It is the agent's native working language.
- Incoming customer content is delivered to the agent in this language.
- Agent voice playback uses this language.
- Setting is persisted per agent user ID.

Example:
- Agent `agenten-02` sets `Agent Sprache = en`.
- Customer writes German.
- Agent sees/hears English.

## Original + translation in Agent window
The agent now sees both:
- `Original`: source text in original language.
- `Translation`: text in agent language.

This makes message validation easy during live operations.

## Customer output lang (Agent UI)
`Customer output lang` controls what the customer receives.

Options:
- `auto (detected customer profile)`
  - Recommended.
  - Uses detected customer language + voice profile stored in session.
- Manual (`de`, `en`, `no`, `sv`, `fi`)
  - Forces a fixed customer output language.

### Auto-mode rule
If customer language is detected, the response language and customer voice profile follow that detected customer language.

## Translation pipeline (simple)
1. Customer sends language A.
2. System stores language A as customer profile.
3. Agent works in language B (selected agent language).
4. Agent message is translated to language A before delivery.
5. Customer receives text + speech in language A.

## Listen Mode (customer)
- Auto start/stop/send based on silence.
- Default silence threshold: `1300 ms`.

## Three practical examples

### Example 1: Customer DE, Agent EN
- Customer speaks German.
- Agent language: `en`.
- Customer output lang: `auto`.
- Result:
  - Agent works in English.
  - Customer gets German text + German voice.
  - Agent sees both Original (DE) and Translation (EN) in chat.

### Example 2: Customer EN, Agent DE
- Customer speaks English.
- Agent language: `de`.
- Customer output lang: `auto`.
- Result:
  - Agent receives translated German.
  - Customer gets English text + English voice.

### Example 3: Manual override
- Customer starts in German.
- Agent sets `Customer output lang = en`.
- Result:
  - Customer gets English output and English voice.

## Troubleshooting
- Wrong customer language output:
  - Check `Customer output lang` in Agent UI.
  - For automatic matching, set it to `auto`.
- Agent does not hear own language:
  - Verify `Agent Sprache`.
  - Turn on `Play incoming on agent`.
- No audio:
  - Allow browser autoplay.
  - Escalate to technical support if backend audio services are unavailable.
- Two voices at the same time:
  - Keep `Play customer output on agent` OFF (default).

## New in V9.1.0: Dual-lane routing (Original + Target)
- Each incoming customer message in Agent UI now has two blocks:
  - `Original (lang_original)`
  - `Translation (Agent language)`
- Agent-side playback now uses only `tts.agent_text`.
- Customer-side playback now uses only `tts.customer_text`.
- This prevents cases where source text is spoken in the wrong voice/language.

## New in V9.1.1: TTS Cleanup
- TTS now strips markdown formatting symbols (e.g., `*`, `**`, backticks) before speech output.
- This affects audio output only, not stored or displayed text.

## New in V9.1.2: Agent inbox auto-refresh + display cleanup
- Agent UI now provides `Auto-Refresh` for inbox updates (default: on, 5 seconds).
- New activity appears in inbox without manual refresh.
- New toggle: `Display cleanup (hide formatting symbols)`.
  - This is display-only in chat.
  - Routing, translation, stored data, and TTS fields are unchanged.

## New in V9.1.5-fix-voice-duallane: Voice = Chat parity fix
- Voice input now emits the same live `message.created` contract as chat input.
- When languages differ, the agent reliably gets translated agent-lane text.
- TTS remains strictly lane-bound:
  - Agent side speaks only `tts.agent_*`
  - Customer side speaks only `tts.customer_*`
- Debug payload now exposes effective source-language hints for faster diagnostics.

### 2-minute parity check
1. Agent: language `en`, Incoming Speak `ON`.
2. Customer: language `de`, speak the wallbox sentence.
3. Expected:
   - Agent sees `Original (DE)` + `Translation (EN)` live.
   - Agent hears EN.
4. Agent replies EN.
5. Customer sees/hears DE.

## New in V9.1.7: Auto-upload + faster default model
- Customer UI now includes `Auto-send after recording` (default: ON).
- When recording stops and this toggle is ON, upload/send starts automatically (no extra `Send Audio` click).
- Default model is now `qwen2.5:3b` (fallback to `qwen2.5:7b` if 3b is unavailable).
- TTS remains lane-bound and still removes markdown/control characters only for spoken output.

### Example
1. Customer speaks in German and stops recording.
2. Auto-send is ON.
3. Upload starts automatically.
4. Agent receives live agent-lane text (for example English), customer receives response in customer language.

## New in V9.1.8: More stable operations behind the scenes
- User flow stays the same.
- In the background, admins can now enable/disable diagnostics and find sessions faster.
- User-facing benefit:
  - faster troubleshooting
  - fewer interruptions during live operation.

## New in V9.1.11: Clean Agent/Admin separation
- Agent now has a consistent top header:
  - connection status + version
  - always-visible search (`q` + mode)
  - `Agent Settings ⚙︎`
- Search is always available and now uses `/api/agent/search` (no admin endpoint in agent view).
- Drawer now contains only agent-scoped controls:
  - backend/model (local agent behavior)
  - agent language
  - incoming speak, customer-speak-on-agent, debug/metrics, auto-refresh
- Compact performance strip shows local summary:
  - `STT avg/p95`
  - `LLM avg/p95`
  - `Total avg/p95`

### Example
1. Agent enters `fe774f*` in search and keeps mode `auto`.
2. Result list shows session id, snippet, and timestamp.
3. Clicking a result opens that session directly.
4. Agent opens `Agent Settings ⚙︎` to adjust and save settings.

## New in V9.1.14: Better performance observability (admin-side)
- Agent/Customer workflow stays the same.
- Admin can now enable/disable performance logging on demand.
- User-facing value:
  - faster incident analysis
  - less trial-and-error during live support
  - exportable evidence package for team debugging

## New in V9.1.15: Performance dashboard (admin only)
- Admin can now see directly in the Admin client:
  - summary cards
  - worst spikes
  - perf search
- This does not change normal customer or agent workflows.

## Patch V9.1.15-p1: More stable chat view for the agent
- When a customer types a chat message, the agent now gets the same clear dual-lane view as with voice:
  - `Original`
  - `Translation`
- This also remains correct after reloading the Agent client.
- `Backend/Model` are no longer editable in Agent UI, so agent and admin settings do not drift apart.

## Patch V9.1.15-p3: WS RTT + display invariants
- The header in Admin, Agent, and Customer now also shows `WS RTT: <ms>`.
- This number shows the approximate WebSocket round-trip time.
- If the connection is down, it shows `WS RTT: -`.
- The agent view is now stricter about customer messages:
  - If languages differ, `Original` and `Translation` must both be visible.
  - If incoming speak is ON, only the agent-language lane is spoken.

### 2-minute proof
1. Set Agent language to `en`.
2. Set Customer language to `de` and send a German chat or voice message.
3. Check:
   - Agent sees `Original (de)` + `Translation (en)`.
   - `WS RTT` shows a millisecond value within a few seconds.
4. Agent replies in English.
5. Customer sees/hears the German output.
