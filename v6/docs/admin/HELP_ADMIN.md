# Admin Docs (V6.10.0)

## Admin token gate (Option A)
- API endpoint: `GET /api/whoami?user_id=...`
- Header: `X-Admin-Token: <token>`
- `is_admin=true` only if header token matches `ADMIN_UI_TOKEN`.
- If `ADMIN_UI_TOKEN` is empty, admin mode is effectively disabled.

## UI behavior
- Admin Docs menu item is hidden unless `/api/whoami` returns `is_admin=true`.
- UI stores optional admin token in browser localStorage.

## Server-side enforcement
- Admin documentation endpoint is gated:
  - `GET /api/admin/docs/help`
- Missing/wrong token returns `403`.

## Security caveat
- This is a demo-grade gate for development and demos.
- It does not replace full auth/role systems.
- Real auth/roles (OTP/RCS/SMS path) are planned for V9+.
