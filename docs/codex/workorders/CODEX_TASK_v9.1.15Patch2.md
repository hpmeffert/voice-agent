CODEX TASK: v9.1.15-patch2 — Fix Dual-Lane for CUSTOMER CHAT (not only Voice)

Context
- Current version: v9.1.15 (Admin 8085, Customer 8086, Agent 8087)
- Dual-lane translation works for VOICE customer input.
- Dual-lane translation FAILS for CUSTOMER CHAT input:
  - Customer types German -> Agent does NOT show EN translation.
  - LLM answer is shown only in German on Agent view (even when Agent language is EN).
  - Customer receives German answer correctly.

Goal
- Ensure Dual-Lane payload is consistently created and rendered for BOTH:
  A) customer voice input
  B) customer chat input
- Agent view MUST always show:
  - Original text (source)
  - Translation text_for_agent (agent language)
  when languages differ.
- Must work LIVE via WS and after RELOAD via session history API.

Non-goals
- Do NOT change dual-lane routing design.
- Do NOT change voice pipeline behavior that already passes.
- No new risky dependencies. Follow OSS guardrails (permissive, avoid GPL/AGPL in core).

Required Fix (Backend)
1) Identify customer chat endpoint (e.g. POST /chat or equivalent) and ensure it calls the SAME canonical function used by voice after STT (e.g. handle_customer_text(...) / build_dual_lane_event(...)).
2) For customer->agent events created from CHAT:
   - populate:
     - text_original (customer input)
     - lang_original / source_lang
     - text_for_agent (translated if needed)
     - lang_for_agent (= agent_lang_ui_last OR WS agent_lang param)
     - tts_lang_agent (= lang_for_agent)
   - Also keep customer lane fields if present.
3) Ensure session meta language handling matches voice path:
   - If customer_lang is auto and session has no persisted customer_lang_ui_last:
     - set it based on detected language of this chat message.
   - Do not overwrite customer_lang_ui_last unless explicitly set.
4) Ensure agent reply events (LLM) are consistent:
   - When agent triggers LLM reply, store event with:
     - text_original (canonical/original)
     - text_for_customer (translated to customer_lang_ui_last)
     - lang_for_customer
     - Optionally include text_for_agent if agent UI needs it.
   - Agent UI must show content in agent language (if agent_lang is EN, agent sees EN content).

Required Fix (History)
- GET /session/{id} (or equivalent) must return lane fields if stored.
- If historic customer messages exist without lane fields, do NOT create a new translation dependency.
  Prefer:
   - either backfill only for rendering using existing translate function,
   - or compute on-demand only when needed.
  Must not break existing DB or message schemas.

Required Fix (Frontend: Agent)
- Rendering rule (Agent view):
  - For any CUSTOMER message:
    - If text_original + text_for_agent exist: render two blocks (Original + Translation).
    - If only one exists, render what exists, but log a warning.
- Ensure this applies to BOTH:
  - live WS events
  - history-loaded messages

Tests (Automated + Manual)
A) Automated WS/HTTP test:
- Scenario: customer_lang=de (chat), agent_lang=en
- Inject customer chat text: "Meine Wallbox geht immer aus. Was kann ich tun?"
- Assert within <=2s agent receives event with:
  - text_original contains German
  - text_for_agent contains English (not equal to original)
  - lang_for_agent == "en"
B) Agent reply test:
- Send agent reply in EN (chat) "Please check breaker..."
- Assert customer receives DE text_for_customer and tts_lang_customer == "de"
C) Reload test:
- Reload agent UI or call session API and verify the stored message shows both lanes.

Artifacts Policy (mandatory)
- Write test artifacts to v9/artifacts/<timestamp>/...
- Include:
  - SUMMARY.md with PASS/FAIL per scenario
  - docker logs (api/web-agent/web-customer) if FAIL
  - ws event capture jsonl (agent/customer)
- Do NOT commit artifacts. Add guard in scripts if needed.

Deliverables
- Patch on a new branch: codex/bugfix/v9.1.15-chat-duallane
- Small commits:
  1) backend fix + tests
  2) agent UI render fix
  3) docs/release note snippet (DE/EN)
- Provide final command list to run tests and expected PASS output.