# Demo Guide (V7.2.0)

Ziel: Interesse wecken, einen klaren Spannungsbogen aufbauen und die Kernfunktionen in 5-8 Minuten zeigen.

## Storyline mit Spannungsbogen
Stellen Sie sich mal vor, ein Kunde ruft an und erwartet sofortige, natuerliche Unterstuetzung - ohne Klick-Marathon, ohne technische Huerden.

1. **Einstieg (Neugier)**
- Starten Sie mit: "Was waere, wenn unser Agent einfach zuhoert, versteht und nahtlos antwortet?"
- Zeigen Sie das UI und die Klarheit von Transcript/Answer.

2. **Momentum (Aha-Moment)**
- Aktivieren Sie `Listen Mode`.
- Sprechen Sie eine Frage, machen Sie dann bewusst eine Pause.
- Zeigen Sie live:
  - Auto-Stop bei Stille
  - Auto-Send
  - Antwortwiedergabe
  - automatisches Weiterhoeren danach

3. **Vertrauen (Robustheit)**
- Erklaeren Sie kurz die Audio-Haertung in V7.2.0:
  - Browser-Opus/WebM
  - ffmpeg-Konvertierung nach WAV vor STT
- Zeigen Sie einen Fehlerfall (ungultige Datei) und dass die UI strukturierte JSON-Fehler bekommt statt HTML.

4. **Kontrolle (Betriebssicherheit)**
- Zeigen Sie Session/User-Pills und dass Verlauf in derselben Session erhalten bleibt.
- Optional: Transcript/Protocol Download als Nachweis fuer Dokumentation und Nachvollziehbarkeit.

5. **Abschluss (Nutzen klar machen)**
- Formulierungsvorschlag:
  - "Wir zeigen nicht nur einen Voice-Chat, sondern einen robusten Gespraechsfluss, der fuer echte Nutzung vorbereitet ist."

## Konkreter Demo-Ablauf
1. `http://localhost:8081` oeffnen.
2. Frage 1 manuell senden (`Record -> Stop -> Send`).
3. Folgefrage im selben Kontext stellen.
4. `Listen Mode` aktivieren und einen kompletten hands-free Turn zeigen.
5. Optional fehlerhafte Datei senden und JSON-Fehlerformat zeigen.
6. Seite neu laden und persistierte User-Settings pruefen.

## Wirkungstexte fuer Praesentation
- "Stellen Sie sich vor, der Agent reagiert wie ein echter Dialogpartner."
- "Kein Medienbruch: vom Zuhoren bis zur Antwort in einem kontinuierlichen Loop."
- "Selbst im Fehlerfall bleibt die Integration stabil und maschinenlesbar."

## Checkliste vor Publikum
- `/api/health` ist `ok`.
- Mikrofonfreigabe im Browser aktiv.
- Modell ist geladen (erste Anfrage kann laenger dauern).
- Ein Test-User bleibt waehrend der Demo konstant fuer reproduzierbaren Verlauf.
