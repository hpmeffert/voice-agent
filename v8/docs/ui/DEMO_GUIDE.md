# Demo Guide - V8.9.0

## Story-Flow 1: Self-Service bis zum Handoff-Moment
Stell dir vor, ein Kunde startet im Self-Service. Alles laeuft automatisch, bis die Anfrage menschliche Unterstuetzung braucht.

1. Customer UI (`8083`) oeffnen.
2. Listen Mode aktivieren, 2-3 Turns sprechen.
3. Kunde klickt `Menschlichen Agenten anfordern`.
4. Im Chat erscheint der Handoff-Status `requested`.

## Story-Flow 2: Call-Center Uebernahme in Echtzeit
Jetzt steigt das Agententeam ein.

1. Agent UI (`8084`) oeffnen.
2. Session in der Inbox mit Badge `handoff requested` finden.
3. `Handoff annehmen` klicken.
4. Im Customer UI wird `accepted` angezeigt.
5. Agent antwortet live, Konversation laeuft ohne Neustart weiter.

## Spannungsbogen fuer die Demo
- Einstieg: "Kunde bedient sich selbst, ohne Technikbarriere."
- Konflikt: "Die Anfrage wird komplexer, Handoff wird angefordert."
- Aufloesung: "Agent uebernimmt nahtlos, volle Nachvollziehbarkeit bleibt erhalten."

## Story-Flow 3: Security sichtbar machen (V8.8.0)
Stell dir vor, ein Stoer-Client sendet in Sekunden viele Requests. Das System bleibt trotzdem stabil.

1. Admin UI (`8082`) geoeffnet lassen.
2. Terminal: mehrere schnelle Requests auf `/api/models` senden.
3. Beobachtung: API antwortet mit `429`, statt ungebremst Last aufzunehmen.
4. Danach normale Requests erneut testen (`/api/health`) und Verfuegbarkeit zeigen.
