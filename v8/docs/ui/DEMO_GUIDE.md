# Demo Guide (V8.1.0)

Ziel: In 5-7 Minuten zeigen, warum Voice Agent im Alltag und im Support wirklich hilft.

## Demo Story 1: "Der hektische Vormittag"
Stell dir vor, ein Kunde ruft an, waehrend bereits drei Tickets offen sind.
Du oeffnest die Customer UI (`8083`) und startest direkt:
1. Begruessung per Spracheingabe (`Record` -> `Stop` -> `Send`).
2. Kunde nennt Problem in eigenen Worten.
3. Agent antwortet strukturiert und ruhig.
4. Optional Textnachricht nachschieben ueber `/api/chat/text`-Flow in der UI.

Spannungsbogen:
- Anfang: Stress, unklare Lage.
- Mitte: klare, schnelle Interaktion.
- Ende: sauberer, nachvollziehbarer Gespraechsverlauf.

## Demo Story 2: "Admin rettet die Live-Demo"
"Stell dir vor, kurz vor einem Kundentermin wirkt alles instabil."
1. Admin UI (`8082`) oeffnen.
2. `api/health`, `api/models`, `eventbus/health` pruefen.
3. Kurzer Testcall in Customer UI.
4. Ergebnis live zeigen: System ist messbar gesund und einsatzbereit.

## Demo-Hinweise
- Starte mit einem klaren Use Case, nicht mit Technikdetails.
- Erklaere jede sichtbare Einstellung in einem Satz.
- Zeige am Ende immer den Mehrwert: schneller, reproduzierbar, teamfaehig.
