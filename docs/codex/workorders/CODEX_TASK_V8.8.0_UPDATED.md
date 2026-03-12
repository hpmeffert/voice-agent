# CODEX TASK V8.8.0 (Updated)

## Zusätzliche Dauerregeln (verbindlich ab V8.8.0)

### 1) Menütext im Admin-Client
- Untermenüpunkt 2 muss heißen: **Benutzer Handbuch**
- Der Text `Help` darf dort nicht mehr als Menülabel verwendet werden.

### 2) Benutzer Handbuch Inhalt
- Für jede Nutzerfunktion muss dokumentiert sein:
  - Funktionsweise
  - Konkretes Beispiel
  - ggf. Release-Verweis (wann eingeführt)
- Release-Notes-Inhalte gehören nicht in das Benutzer Handbuch.

### 3) Admin Handbuch Inhalt
- Für jede Admin-Funktion muss dokumentiert sein:
  - Wofür gut?
  - Welche Parameter erwartet?
  - Wie testbar (API/CLI/UI)?
  - Mit welchem Release eingeführt/erweitert?

### 4) Release Notes Qualität
- Für jede neue funktionale Erweiterung muss beschrieben werden:
  - Was ist neu?
  - Wofür ist es gut?
  - Was ist der konkrete Vorteil für Admin/Agent/Kunde?
  - Welche Parameter, Flags oder Endpoints gehören dazu?

### 5) Agent-Client Hilfe
- Agent-Client enthält Hilfe nur mit dem Benutzer Handbuch.
- Keine Demo Guide/Admin Docs/Release Notes im Agent-Help.
