# Release Notes (V7 -> V8)

## Historie
- V7.0.0 bis V7.10.0: stabile V7-Linie (Admin UI, Listen Mode, i18n, Metrics).
- V8.0.0: neues isoliertes V8-Scaffold mit Valkey-Sidecar + EventBus-Skeleton.

## V8.0.0
### Highlights
- Isolierter `v8/` Baum erstellt.
- Neues Compose mit `valkey` Service.
- EventBus-Transportabstraktion (`publish/subscribe`) im API-Layer.
- Help-Menue-Struktur bleibt verbindlich und wird automatisiert geprueft.
