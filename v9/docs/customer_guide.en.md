# Customer Guide (EN) - Voice Agent V9

## What does the Customer Client do?
The customer client is the end-user page. You can:
- talk with **voice** (Record / Listen Mode),
- write via **chat**,
- receive answers as **text + audio**.

Goal: use the system without technical setup knowledge.

## UI overview
- URL: `http://localhost:8086`
- Header:
  - `Voice Agent Customer <Version>`
  - status (`idle`, `recording`, `uploading`, `speaking`)
  - `UI` dropdown for interface language (`de`/`en`)
  - `?` button = this help
- Input area:
  - `User` and `Session`
  - `Record`, `Stop`, `Send Audio`
  - `Auto-send after recording`
  - `Listen Mode`
  - `Customer language`
  - `TTS`
- Chat area:
  - text input
  - `Send Text`

## Step by step: Voice flow
1. Open the customer client.
2. Check `Customer language`:
   - `auto` (recommended) or fixed `de/en/no/sv/fi`.
3. Click `Record`.
4. Speak clearly.
5. Click `Stop` (or use Listen Mode auto-stop).
6. If `Auto-send after recording = ON`, upload starts automatically.
   - Otherwise click `Send Audio`.
7. Wait for the answer:
   - text appears in chat history,
   - audio plays in the player.

## Step by step: Chat flow
1. Type text into `Text eingeben und senden...`.
2. Click `Send Text`.
3. Read the answer and optionally listen to TTS output.

## Key settings in simple words
- `UI`:
  - changes only customer UI labels/text.
  - does **not** change detected input language or TTS lane behavior.
- `Customer language`:
  - `auto` = language is detected automatically.
  - manual = fixed output language.
- `TTS`:
  - controls spoken output language.
  - `auto` uses the detected profile.
- `Auto-send after recording`:
  - ON = faster flow without extra click.
- `Listen Mode`:
  - continuous mode: record, stop on silence, send.
  - default silence threshold is `1300 ms`.

## Typical example
1. Customer speaks German.
2. System processes the input.
3. Agent works in agent language internally.
4. Customer receives the answer back in customer language (text + voice).

## Troubleshooting (quick)
- No microphone:
  - allow browser microphone permission.
- No sound:
  - check volume and autoplay.
- No response:
  - check status line and try a new session.
- Wrong language:
  - check `Customer language` and `TTS`.
