# Release Notes (DE) - V7.0.0 bis V9.1.0

## Historie
- V7.0.0: V7-Scaffold isoliert, eigene Ports, Admin-Demo-Defaults.
- V7.1.0: Hands-free Listen Mode mit Auto-Stop/Auto-Send/Auto-Resume.
- V7.2.0: Audio-Pipeline gehaertet, ffmpeg-Konvertierung, klare JSON-Fehler.
- V7.3.0-V7.10.0: UX-, Security-, Telemetrie- und Sprachausbau.
- V8.0.0: V8 als isolierte Schicht mit Valkey/EventBus.
- V8.1.0: Customer UI getrennt.
- V8.2.0: Agent UI mit Inbox/Join/Live-Chat.
- V8.3.0: Agent-Suche nach User/Session.
- V8.4.0: Listen Mode fuer Kunden verbessert.
- V8.5.0: Admin-Konversationssuche (`user_id`, `session_id`, `q`).
- V8.6.0: Doku-Hardening und Help-Menue-Regeln.
- V8.7.0: Handoff-Workflow via EventBus.
- V8.8.0: Security-Baseline (Headers, Limits, Rate-Limits).
- V8.9.0: Stabiles Packaging + Migration.
- V8.10.2: TTS-Output-Translation inkl. Agent->Kunde Uebersetzung.
- V9.0.0: Help System v2, bilinguale DE/EN-Doku, `/api/docs`, Version sichtbar in Header+Menue, Agent-Muttersprache (DE/EN/NO/SV/FI) mit persistierten Agent-Prefs.
- V9.1.0: Dual-Lane-Sprachrouting (`agent`-Lane + `customer`-Lane) mit expliziter TTS-Bindung (`tts.agent_*`, `tts.customer_*`), WS-Lang-Persistenz (`customer_lang_ui_last`, `agent_lang_ui_last`) und sicherer Verhinderung von falscher Sprachausgabe.

## Nutzen von V9.1.0
- Keine falsche Sprache mehr im Agenten- und Kunden-TTS-Pfad.
- Jede Nachricht hat klare Empfaenger-Lanes: Original, Agent-Ansicht, Kunden-Ansicht.
- TTS liest nur noch explizit vorgesehene Felder und nie versehentlich den falschen Text.
