# Demo Guide (2-5 minutes)

## 1) Warmup check
- Open UI: `http://localhost:8080`
- Confirm API status:
  - `GET /api/health`
  - `GET /api/models`

## 2) Fast first answer
- Ask a short question (for example: "What can you do in one sentence?").
- Show transcript and answer in the Result box.

## 3) Memory follow-up
- Ask a follow-up that depends on previous answer.
- Confirm the assistant keeps context in the same `session_id`.

## 4) Model switch demo
- Switch model (for example `qwen2.5:3b` vs `qwen2.5:7b`).
- Ask the same question and compare speed/quality.

## 5) Transcript export
- Click `Download Transcript` and show generated file.
- Optional API call:
  - `GET /api/session/<session_id>/export?user_id=<user_id>&format=md`

## 6) Data controls
- Demonstrate delete endpoints if needed:
  - `POST /api/session/delete`
  - `POST /api/user/delete`

## Maintenance rule (from V6.5 onward)
- Every new feature must update:
  1) UI help text (`v6/docs/help_user.md`)
  2) Demo guide (`v6/docs/demo_guide.md`)
