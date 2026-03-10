# Demo Guide (EN) - V9.0.0

## Demo goal
Show how international support works when customers and agents keep their own language while the platform handles translation and voice routing.

## Story Flow 1: "Have you seen this?" Customer DE, Agent EN
Imagine: customer speaks German, but the available agent is English-native.

### Setup
1. Open Customer UI (`8086`).
2. Open Agent UI (`8087`).
3. In Agent UI set:
   - `Demo User = agenten-02 (EN)`
   - `Agent ID = agenten-02`
   - `Agent Sprache = en`
   - `Play incoming on agent = ON`
   - `Play customer output on agent = OFF`
   - `Customer output lang = auto`

### Demo steps
1. Customer says/types: "Ich brauche Hilfe mit meiner Rechnung."
2. Agent receives the message in English.
3. Agent replies in English.
4. Customer receives German text + German voice.
5. Agent chat shows both:
   - `Original: ...`
   - `Translation: ...`

### Audience takeaway
- Agent does not need German.
- Customer experience remains local and natural.

## Story Flow 2: Customer EN, Agent DE
Imagine: your team is German-speaking, but an English customer contacts support.

### Setup
1. Set agent:
   - `Demo User = agent-de-01 (DE)`
   - `Agent ID = agent-de-01`
   - `Agent Sprache = de`
   - `Customer output lang = auto`
2. Customer speaks/types English.

### Demo steps
1. Agent receives translated German content.
2. Agent replies in German.
3. System translates back to English.
4. Customer hears English voice output.

### Audience takeaway
- Local teams can support global customers without language switching stress.

## Story Flow 3: Manual override in a live case
Imagine: supervisor wants to force a specific output language for verification.

### Demo steps
1. Customer starts in German.
2. Agent sets `Customer output lang = en`.
3. Agent replies in own language.
4. Customer receives English text + English voice.

### Audience takeaway
- Auto mode for production.
- Manual override for edge cases, QA, and controlled workflows.

## Admin demo (required)
1. Open Admin UI (`8085`).
2. Verify Help menu order:
   1. Save Admin Token
   2. User Guide
   3. Demo Guide
   4. Admin Docs
   5. Release Notes
3. Show version in header and Help.
4. Run quick checks:
   - `/api/health`
   - `/api/models`
   - agent language test with `agenten-02`.

## Presenter tip (build a narrative arc)
- Start with pain: language mismatch in support.
- Show the live language bridge in <2 minutes.
- End with impact: faster handling, less misunderstanding, better global scalability.

## V9.1.0 stage focus
- In Agent UI, show clearly separated blocks:
  - `Original`
  - `Translation`
- Turn on `Play incoming on agent`:
  - Only translated agent-lane audio should be spoken.
- Let the agent reply:
  - Customer must see/hear only customer-lane output in customer language.

## V9.1.1 Demo Focus
- Use a sentence with markdown markers (e.g., `**Important**: *Please* check`).
- Expected: display unchanged, speech output without formatting artifacts.

## V9.1.2 Demo Focus
- Show that new sessions appear in inbox without clicking `Refresh Inbox` (auto-refresh enabled).
- Simulate a short connection drop and show the return to `WS: online`.
- Toggle `Display cleanup` on/off to demonstrate the Agent-side text rendering difference.

## V9.1.7 Demo Focus
- Turn `Auto-send after recording` ON in Customer UI.
- Speak one short sentence and stop recording.
- Show the audience that upload starts immediately without an extra click.
- Explain the value:
  - fewer clicks
  - fewer operator errors
  - faster live conversation flow.

## V9.1.8 Demo Focus
- Admin enables `Perf logging enabled` only for a short demo window.
- Run one short conversation.
- Open Admin Search:
  - first partial session id (`*`)
  - then text fragment search.
- Open a hit using `Open Session` and show direct navigation.
- Turn logging OFF again after the demo.

## V9.1.9 Demo Focus: Clean Agent Desk
1. Show the new Agent layout with always-visible sticky header.
2. Enter `fe774f*` in search (mode `auto`) and run search.
3. Open one result directly from the result list.
4. Open `Admin ⚙︎` and walk through the Drawer:
   - safe controls (dropdowns/toggles) instead of free text
   - Save/Cancel flow
   - quick link to Admin Docs
5. Point to the performance strip (`STT/LLM/Total avg+p95`) and explain why it helps during live support.
