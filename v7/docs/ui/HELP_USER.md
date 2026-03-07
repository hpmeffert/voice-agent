# Voice Agent Help (V7.0.0)

## What is new in V7
- V7 runs fully isolated under `v7/` (no runtime overlap with V6).
- Dedicated dev ports:
  - Web: `http://localhost:8081`
  - API: `http://localhost:8001` (proxied as `/api`)
  - Piper: `:5003`
  - Mongo: `:27018`
- Demo users are created as `admin` by default in Mongo (testing mode).

## Main controls
- `Record`: start microphone capture.
- `Stop`: stop recording.
- `Send`: send audio to `/api/voice`.
- `Clear Session`: reset local session and start fresh.

## Conversation mode
- `Auto-stop on silence` + `Auto-send after stop` enable hands-free usage.
- `Silence threshold` and `Max recording seconds` can be tuned in UI.

## Help menu
- `Help`: this user guide.
- `Demo Guide`: presenter flow for demos.
- `Admin Docs`: visible for admins, loaded from server-gated endpoint.
- `V7 Release Notes`: V7 release summary.

## Security caveat
- Admin visibility in V7 is for demo/testing convenience.
- Full production auth/roles are planned for later major versions.
