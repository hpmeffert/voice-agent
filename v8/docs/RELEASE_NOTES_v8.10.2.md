# V8.10.2 - Multi-language TTS translation + bilingual docs

## What changed
- Added TTS output translation pipeline in `/api/voice` and `/api/chat/text`.
- Added Agent->Customer translation behavior in `/api/agent/message`:
  - Agent can send original text in source language.
  - Customer receives translated delivery text based on `tts_lang`.
  - Response includes `source_lang`, `answer_original`, `answer_translated`, `translation_ms`.
- Added response fields:
  - `answer` (original)
  - `answer_translated` (nullable)
  - `answer_tts_lang`
  - `translation_ms`
- Added persistence fields in messages/telemetry:
  - `answer_original`, `answer_translated`, `answer_tts_lang`, `metrics.translation_ms`
- Admin UI:
  - `TTS output language` control (`auto`, `de`, `en`, `fr`, `it`, `es`, ...)
  - Split answer panes (original + translated)
  - Translation latency shown in metrics card
- Help docs now bilingual (DE/EN) with runtime switching:
  - DE if UI language is `de`
  - EN fallback for `en` and all other languages (`fr`, `it`, `es`, ...)

## Voice support
- FR/IT/ES voice mapping remains enabled in Piper sidecar:
  - `PIPER_VOICE_FR`, `PIPER_VOICE_IT`, `PIPER_VOICE_ES`

## Why this is useful
- Users can listen to answers in their preferred output language without losing original content.
- Agent teams can reply in their working language while customers still receive localized responses.
- Agents/admins can audit translation impact via stored fields and `translation_ms`.
- Demo/readiness improves for multilingual scenarios.

## Verification
```bash
python3 v8/scripts/check_docs.py
make v8-lint
make v8-smoke
```

## Licensing/commercialization
- No new dependency added in core path.
- Piper remains sidecar-style and host-mounted voices stay outside repo runtime source tree.
