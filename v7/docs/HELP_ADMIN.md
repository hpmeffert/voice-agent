# Admin Guide (DEV phase, V6.9.0)

## Current admin mode
- `ADMIN_DEV_MODE=1` means every user is treated as admin.
- This is temporary for development and demo testing.
- Planned replacement in V9: real role model and admin authentication.

## Admin-relevant controls
- User preferences:
  - `GET /api/user/prefs?user_id=...`
  - `POST /api/user/prefs` with `{user_id, crm_export_enabled}`
- Session and user cleanup:
  - `POST /api/session/delete`
  - `POST /api/user/delete`
- Metrics:
  - `GET /api/metrics/recent?user_id=...&limit=20`
- Protocol export v1:
  - `GET /api/export/protocol?user_id=...&session_id=...`

## Telemetry logs (V6.8.1)
- Collection: `telemetry_logs`
- One log entry per `/api/voice` call (`ok` and `error`)
- Includes:
  - IDs: `user_id`, `session_id`
  - runtime: `backend`, `model`, `lang`
  - metrics: `audio_read_ms`, `stt_ms`, `llm_ms`, `tts_ms`, `total_ms`
  - content snippets: `transcript`, `answer`
  - error context: `status`, `error_code`, `error_detail`
- TTL retention via `TELEMETRY_RETENTION_DAYS` (default `30`)

## Templates and docs
- Transcript template:
  - `v6/templates/transcript_default.md.tpl`
- Protocol template:
  - `v6/templates/crm_protocol_default.md.j2`
  - `v6/templates/protocol_template.md` (v1 placeholder template, MIT-owned)
- Runtime override:
  - env `PROTOCOL_TEMPLATE_PATH` (for mounted custom template file)
- Telemetry admin doc:
  - `v6/docs/ADMIN.md`
- Help menu documents:
  - `v6/docs/HELP_USER.md`
  - `v6/docs/HELP_DEMO_GUIDE.md`
  - `v6/docs/HELP_ADMIN.md`
  - `v6/docs/HELP_ADMIN_TESTING.md`
  - `v6/docs/RELEASE.md`
