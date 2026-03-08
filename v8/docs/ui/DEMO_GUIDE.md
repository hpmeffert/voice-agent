# Demo Guide (V8.5.0)

## Story-Flow 1: "Vom ersten Satz bis zur Loesung ohne Bruch"
Stell dir vor, ein Kunde ruft an und spricht einfach los. Kein Button-Stress, kein Technikfrust. Der Dialog fliesst wie ein echtes Gespraech.

1. Customer UI (`8083`) oeffnen und `Listen Mode` aktivieren.
2. Kunde sagt sein Anliegen in zwei bis drei Teilen.
3. Zeige, wie Stille erkannt wird (Default `1300 ms`) und die Antwort automatisch folgt.
4. Oeffne Agent UI (`8084`) und suche die aktive Session per `user_id` oder Stichwort.
5. Agent uebernimmt live und beantwortet den konkreten Fall.

## Story-Flow 2: "Service mit Gedächtnis"
Ein Zuschauer sagt: "Das klingt gut, aber findet ihr auch einzelne Aussagen wieder?"

1. Im Agent UI nach einem markanten Wort suchen.
2. Treffer zeigen (Session + Turn).
3. Danach im Admin UI dieselbe Unterhaltung ueber die neue Admin-Suche finden:
   - nach `user_id`
   - nach `session_id`
   - nach Textausschnitt
4. Ergebnis: Nachvollziehbarkeit fuer Support, QA und CRM.

## Spannungsbogen fuer Praesentationen
- Einstieg: "Ein Kunde spricht frei, ohne Bedienungsanleitung."
- Mitte: "System reagiert automatisch und Agent steigt nahtlos ein."
- Finale: "Admin findet jede wichtige Stelle in Sekunden wieder."
