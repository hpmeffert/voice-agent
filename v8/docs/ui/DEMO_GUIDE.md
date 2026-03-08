# Demo Guide - V8.6.0

## Story-Flow 1: Self-Service mit Wow-Effekt
Stell dir vor, ein Kunde spricht einfach los. Keine Klick-Orgie, kein Bruch. Der Assistent reagiert automatisch wie in einem echten Gespraech.

1. Customer UI (`8083`) oeffnen.
2. `Listen Mode` aktivieren.
3. Kunde spricht 2-3 kurze Anliegen.
4. Zeigen, dass bei Stille (`1300 ms`) automatisch gesendet wird.
5. Antwort wird abgespielt, danach geht es automatisch weiter.

## Story-Flow 2: Call-Center Handoff mit Nachvollziehbarkeit
Jetzt kommt der spannende Teil: der Agent uebernimmt ohne Informationsverlust.

1. Agent UI (`8084`) oeffnen.
2. Session ueber `user_id` oder Stichwort finden.
3. Session uebernehmen und live antworten.
4. Admin UI (`8082`) oeffnen und dieselbe Konversation suchen:
   - mit `search_user_id`
   - mit `session_id`
   - mit `q` (z. B. Schluesselwort aus dem Gespraech)
5. Ergebnis zeigen: vom Kundendialog bis zum Admin-Audit alles durchgaengig nachvollziehbar.

## Praesentationsbogen
- Einstieg: "Kunde spricht frei, das System fuehrt sauber durch den Turn."
- Mitte: "Agent steigt nahtlos ein, ohne neue Session."
- Finale: "Admin findet jede relevante Passage sofort wieder."
