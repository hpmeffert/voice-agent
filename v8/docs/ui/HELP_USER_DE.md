# Benutzer Handbuch (DE) - V8.10.2

## Was kann diese App?
Du kannst mit dem Voice Agent sprechen, Antworten bekommen, die Sprache fuer die Audio-Ausgabe waehlen und Sitzungen exportieren.

## Funktion: Record / Stop / Send
- So funktioniert es:
  1. `Record` startet die Aufnahme.
  2. `Stop` beendet die Aufnahme.
  3. `Send` schickt Audio an `/api/voice`.
- Beispiel:
  - Du sagst: "Ich brauche Hilfe bei meiner Wallbox." Danach sendest du und bekommst eine Antwort.

## Funktion: Listen Mode
- Zweck: Freisprechen ohne dauerndes Klicken.
- Wirkung:
  - App erkennt Sprache, stoppt bei Stille und sendet automatisch.
- Wichtige Einstellung:
  - `Silence threshold` Standard: `1300 ms`.

## Funktion: TTS Output Language
- Zweck: Antwort in einer anderen Sprache vorsprechen lassen.
- Werte: `auto`, `de`, `en`, `fr`, `it`, `es`, ...
- Beispiel:
  - Du sprichst Deutsch, waehle `en`.
  - UI zeigt:
    - `Answer (original)` auf Deutsch
    - `Answer (translated)` auf Englisch
  - Piper spricht die englische Version.

## Funktion: Session Memory
- `user_id` identifiziert den Benutzer.
- `session_id` identifiziert den Verlauf.
- Wirkung: Kontext bleibt in der Session erhalten.

## Funktion: Transcript/Protocol Export
- Zweck: Dokumentation fuer CRM, Support, Demo.
- Export-Formate: Markdown/JSON (je nach Einstellung).

## Datenschutz / Aufraeumen
- `Clear Session` leert den Verlauf der aktuellen Session.
- Admin kann Sessions/User serverseitig loeschen.

## Release-Verweise
- TTS-Output-Translation erweitert in `V8.10.2`.
