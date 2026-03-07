# Admin Guide (DEV phase, V6.6.1)

## Current admin mode
- `ADMIN_DEV_MODE=1` means every user is treated as admin.
- This is temporary for development and demo testing.
- Planned replacement in V9: real role model and admin authentication.

## Current admin-relevant controls
- User preferences:
  - `GET /api/user/prefs?user_id=...`
  - `POST /api/user/prefs` with `{user_id, crm_export_enabled}`
- Session and user cleanup:
  - `POST /api/session/delete`
  - `POST /api/user/delete`

## Templates and docs
- Transcript template:
  - `v6/templates/transcript_default.md.tpl`
- Protocol template:
  - `v6/templates/crm_protocol_default.md.j2`
- Help menu documents:
  - `v6/docs/HELP_USER.md`
  - `v6/docs/HELP_DEMO_GUIDE.md`
  - `v6/docs/HELP_ADMIN.md`
  - `v6/docs/HELP_ADMIN_TESTING.md`
  - `v6/docs/RELEASE.md`
