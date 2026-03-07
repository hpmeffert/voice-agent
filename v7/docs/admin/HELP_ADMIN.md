# Admin Docs (V7.0.0)

## Demo admin model
- New users are persisted with role `admin` by default (V7 testing mode).
- Role is stored in Mongo `users.role`.

## Identity endpoint
- `GET /api/whoami?user_id=...`
- Returns:
  - `user_id`
  - `role`
  - `is_admin`

## Admin docs endpoint
- `GET /api/admin/docs/help`
- Intended for admin-only doc retrieval in UI.

## Security caveat
- This admin model is demo/testing scope for V7 scaffold.
- It is not production-grade authorization.
- Roadmap still targets stronger auth/roles in future major versions.
