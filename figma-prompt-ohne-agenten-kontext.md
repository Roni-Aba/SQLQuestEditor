# Was passiert bei einem Figma-Prompt ohne Agenten-Kontext?

Dieses Dokument beschreibt den Ablauf, wenn ein Nutzer einen Figma-Prompt an eine LLM wie ChatGPT, Claude oder Gemini übergibt, ohne dass die LLM automatisch den Projekt-Workspace kennt.

## 1. Der Nutzer sendet den Prompt

Beispiel:

```text
Implement this design from Figma.
https://www.figma.com/design/...?...node-id=78-725
```

Die LLM erkennt daraus:

- Es gibt eine Figma-URL.
- Ein bestimmter Figma-Node soll umgesetzt werden.
- Der Nutzer erwartet vermutlich generierten Code.
- Das Ziel-Framework ist zunächst unbekannt.

## 2. Die LLM prüft ihren Figma-Zugriff

Eine reine LLM ohne Figma-Plugin, MCP oder Connector kann die URL nicht wirklich auslesen. Sie sieht nur den Link, nicht den Inhalt des Designs.

In diesem Fall müsste sie:

- den Nutzer um einen Screenshot bitten,
- Designwerte wie Farben und Abstände anfordern,
- oder eine Umsetzung auf Basis von Annahmen erzeugen.

Mit einer Figma-Integration kann die LLM dagegen einen Tool-Request an Figma senden.

## 3. Die URL wird analysiert

Aus einer URL wie dieser:

```text
https://www.figma.com/design/isyoakVzVVVEsS6lHxnbzP/Untitled?node-id=78-725
```

werden typischerweise folgende Werte extrahiert:

```text
fileKey: isyoakVzVVVEsS6lHxnbzP
nodeId: 78:725
```

Die Schreibweise `78-725` aus der URL wird dabei in `78:725` umgewandelt.

## 4. Die LLM sendet einen Figma-Request

Der Request sieht sinngemäß so aus:

```json
{
  "fileKey": "isyoakVzVVVEsS6lHxnbzP",
  "nodeId": "78:725"
}
```

Je nach Integration können zusätzlich Angaben zum Ziel-Framework oder zur Programmiersprache übertragen werden.

## 5. Figma liefert Designinformationen zurück

Die Antwort kann unter anderem enthalten:

- Referenzcode, häufig React mit Tailwind CSS
- einen Screenshot des ausgewählten Nodes
- Textinhalte
- Positionen und Größen
- Farben
- Typografie
- Abstände
- Border-Radien
- Node-IDs
- Bild- und Asset-URLs
- Komponenteninformationen
- Design-System- oder Token-Informationen

Der gelieferte React-/Tailwind-Code ist normalerweise Referenzcode und nicht automatisch fertiger Code für das eigentliche Projekt.

## 6. Die LLM interpretiert das Design

Die LLM versucht aus den gelieferten Informationen eine Seitenstruktur abzuleiten. Bei dem konkreten Design könnte sie beispielsweise erkennen:

- einen Header mit Navigation,
- einen Titel,
- einen Stepper mit acht Schritten,
- Eingabefelder,
- einen Upload-Button,
- einen Zurück-Button,
- einen Weiter-Button,
- Farben wie `#7749F8`,
- die Schriftart Inter,
- feste Desktop-Positionen.

## 7. Der Ziel-Stack muss bestimmt werden

Ohne Projektkontext weiß die LLM nicht automatisch, welche Technologie verwendet werden soll. Sie kennt beispielsweise nicht:

- ob React oder Django verwendet wird,
- ob Vue oder Angular verwendet wird,
- ob CSS, Tailwind oder Bootstrap eingesetzt wird,
- welche Komponenten bereits existieren,
- welche Routing-Struktur verwendet wird,
- wie Formulare verarbeitet werden,
- wohin ein Upload gespeichert werden soll.

Wenn diese Informationen fehlen, muss die LLM Annahmen treffen. Zum Beispiel:

```text
Ich nehme an, dass es sich um eine React-Anwendung mit Tailwind CSS handelt.
```

## 8. Die LLM erzeugt Code

Auf Basis der Figma-Informationen erzeugt sie anschließend Code. Dazu müsste sie:

1. die Figma-Struktur in Komponenten übersetzen,
2. Assets einbinden,
3. Layout und Typografie übernehmen,
4. Interaktionen ergänzen,
5. responsive Regeln hinzufügen,
6. gegebenenfalls Tailwind-Klassen verwenden.

Ohne Zugriff auf das Projekt entsteht dabei meist eine isolierte Beispielimplementierung.

## 9. Die Grenzen ohne Projektkontext

Ohne Workspace-Zugriff kann die LLM nicht zuverlässig prüfen:

- ob passende Komponenten bereits vorhanden sind,
- welche CSS-Tokens verwendet werden,
- welche Templates angepasst werden müssen,
- wie die Django-Views funktionieren,
- ob die angegebenen URLs erreichbar sind,
- wie Formulare serverseitig verarbeitet werden,
- wohin ein Bild-Upload gespeichert werden soll,
- ob der erzeugte Code kompiliert oder gerendert werden kann.

Die erzeugte Lösung kann daher visuell plausibel, aber technisch unpassend sein.

## 10. Ergebnis einer normalen LLM-Unterhaltung

Am Ende gibt die LLM meistens Codeblöcke oder vorgeschlagene Dateien zurück. Der Nutzer muss diese anschließend selbst:

- in das Projekt übertragen,
- an die Projektstruktur anpassen,
- mit vorhandenen Komponenten verbinden,
- testen,
- und visuell prüfen.

## 11. Vergleich: normale LLM und Agent mit Projektkontext

| Normale LLM-Unterhaltung | Agent mit Projektkontext |
|---|---|
| Kennt nur den Prompt | Kennt Prompt und Workspace |
| Kann Figma nur mit Connector lesen | Kann Figma-MCP direkt aufrufen |
| Muss das Framework annehmen | Erkennt das Framework aus dem Projekt |
| Erzeugt meist isolierten Beispielcode | Passt den Code an die vorhandene Struktur an |
| Kann Dateien nicht unbedingt ändern | Kann Dateien lesen und bearbeiten |
| Kann Assets oft nur verlinken | Kann Assets herunterladen und integrieren |
| Keine zuverlässige Projektvalidierung | Kann Tests und Build ausführen |
| Nutzer muss Code manuell übertragen | Agent kann Änderungen direkt durchführen |

## 12. Sequenz ohne Agenten-Kontext

```text
Figma-Prompt
    ↓
LLM interpretiert die Anfrage
    ↓
Figma-Zugriff wird geprüft
    ↓
URL wird in fileKey und nodeId zerlegt
    ↓
Figma-Connector liefert Designinformationen
    ↓
LLM interpretiert Screenshot, Code und Tokens
    ↓
Ziel-Stack wird angenommen oder vom Nutzer ergänzt
    ↓
LLM erzeugt Beispielcode
    ↓
Nutzer überträgt und integriert den Code manuell
    ↓
Nutzer testet und validiert die Umsetzung
```

## 13. Sequenz mit Agenten-Kontext

```text
Figma-Prompt
    ↓
LLM liest Figma über MCP
    ↓
LLM analysiert zusätzlich den Workspace
    ↓
Vorhandene Komponenten, Templates und Tokens werden geprüft
    ↓
Figma-Referenzcode wird in den echten Ziel-Stack übersetzt
    ↓
Dateien und Assets werden integriert
    ↓
Tests und visuelle Prüfung werden ausgeführt
    ↓
Ergebnis wird an den Nutzer übergeben
```

## 14. Konkreter Unterschied beim Django-Projekt

Beim konkreten SQL-Spell-Quest-Projekt liefert Figma zwar React-/Tailwind-Referenzcode. Der Workspace verwendet jedoch Django mit HTML, CSS und JavaScript.

Eine LLM ohne Agenten-Kontext würde deshalb wahrscheinlich React-/Tailwind-Code ausgeben. Dieser Code könnte optisch ähnlich aussehen, wäre aber nicht automatisch in die Django-Anwendung integrierbar.

Ein Agent mit Workspace-Kontext würde dagegen:

1. die vorhandenen Django-Templates untersuchen,
2. bestehende Header-, Button- und Formularstrukturen suchen,
3. vorhandene CSS-Tokens wiederverwenden,
4. die React-Struktur in Django-Templates übersetzen,
5. die Interaktionen an Django-Views und URLs anbinden,
6. Assets in die statischen Dateien integrieren,
7. die Seite ausführen und prüfen.

## 15. Kurzfassung

Ohne Agenten-Kontext lautet der Ablauf:

```text
Figma-Prompt → LLM → Figma-Connector → Designinformationen → Interpretation → angenommener Ziel-Stack → generierter Code
```

Mit Agenten-Kontext lautet der Ablauf:

```text
Figma-Prompt → LLM → Figma-MCP + Workspace → Design analysieren → Komponenten prüfen → Ziel-Stack anpassen → Dateien ändern → testen → validieren
```

Der entscheidende Unterschied ist nicht nur der Zugriff auf Figma. Entscheidend ist, ob die LLM auch den tatsächlichen Projektkontext, die vorhandenen Konventionen und die ausführbare Umgebung kennt.

