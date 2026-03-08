# Benutzer Handbuch (Help) - V8.7.0

## Wichtig
- Diese Seite ist das **Benutzer Handbuch**.
- Historische Versionslisten stehen in einer separaten Release-Dokumentation.

## Oberflaechen
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`

## Funktion: Listen Mode (Customer UI)
- Wofuer: Freisprech-Dialog ohne staendiges Klicken.
- So funktioniert es: Aufnahme startet, Stille wird erkannt, Anfrage wird gesendet, Antwort wird abgespielt, dann startet die Aufnahme erneut.
- Beispiel:
  1. `Listen Mode` einschalten.
  2. Du sagst: "Ich brauche Hilfe bei meiner Bestellung."
  3. Nach kurzer Stille sendet das System automatisch und antwortet.
- Release-Verweis: verbessert/ausgebaut seit `V8.4.0`.

## Funktion: Silence Threshold
- Wofuer: Legt fest, wie lange Stille gewartet wird, bevor die Aufnahme stoppt.
- Standard: `1300 ms`.
- Beispiel:
  - Bei laengeren Denkpausen: Wert erhoehen.
  - Bei schneller Turn-Uebergabe: Wert senken.
- Release-Verweis: Standardwert festgelegt und vertraglich gesichert seit `V7.x`/`V8.x`.

## Funktion: Menschlichen Agenten anfordern
- Wofuer: Uebergabe von Self-Service an einen realen Agenten.
- So funktioniert es: Klick auf `Menschlichen Agenten anfordern` setzt den Handoff auf `requested`.
- Beispiel:
  1. Kunde klickt den Button.
  2. Agent UI zeigt Badge `handoff requested`.
  3. Agent uebernimmt.
- Release-Verweis: eingefuehrt in `V8.7.0`.

## Funktion: Agent-Suche (Agent UI)
- Wofuer: Aktive Kunden-Sessions schnell finden.
- So funktioniert es: Suche nach `session_id`, `user_id` oder Freitext.
- Beispiel:
  - Sucheingabe: `test-user-870`
  - Ergebnis: passende Session in der Inbox.
- Release-Verweis: eingefuehrt in `V8.3.0`, erweitert in spaeteren Releases.

## Funktion: Handoff annehmen (Agent UI)
- Wofuer: Uebernahme einer vom Kunden angeforderten Uebergabe.
- So funktioniert es: In der aktiven Session `Handoff annehmen` klicken.
- Beispiel:
  1. Session hat Badge `handoff requested`.
  2. Agent klickt `Handoff annehmen`.
  3. Kunde sieht Status `accepted`.
- Release-Verweis: eingefuehrt in `V8.7.0`.
