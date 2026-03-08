# Demo Guide (V8.2.0)

## Story: Call-Center Handoff in Echtzeit
Stell dir vor, ein Kunde ist im Gespraech und braucht ploetzlich einen Spezialisten.

### Flow 1: Kunde startet
1. Customer UI (`8083`) oeffnen.
2. Kunde sendet eine Sprach- oder Textnachricht.
3. Session-ID wird erstellt.

### Flow 2: Agent uebernimmt
1. Agent UI (`8084`) oeffnen.
2. Inbox zeigt aktive Sessions.
3. Agent klickt Session an (Join).
4. Agent schreibt Antwort; Kunde sieht sie live ohne Reload.

### Flow 3: Stimme als Wow-Effekt
1. Im Agent UI `Speak to customer` aktivieren.
2. Agent sendet Nachricht.
3. Customer UI spielt Antwort als Audio aus.

## Spannungsbogen fuer Praesentation
- Anfang: Kunde ohne Kontext in der Leitung.
- Mitte: Agent steigt live ein und uebernimmt sauber.
- Ende: Teamfaehiger, nachvollziehbarer Prozess mit Echtzeit-Feedback.
