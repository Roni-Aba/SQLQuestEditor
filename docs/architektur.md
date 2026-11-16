# Wie ist der Code aufgebaut?

## Beschreibt diese Architektur das Spiel oder den Editor?

Dieses Repository enthält den **Editor**. Er erzeugt die Daten, die das separate
Spiel später verwendet. Ein Button auf einer `createLevel`-Seite gehört zur
Django-Oberfläche des Editors. Ein Table-Item, Hint-Item oder Exit-Item gehört
dagegen zu den erzeugten Spieldaten.

```text
Editor im Browser
    → Django verarbeitet die Eingaben
    → Level-/Gegenstandsentwürfe in der Session, Arbeitsdateien im Workspace
    → Export als ZIP mit JSON, SQLite-Datenbanken und Bildern
    → separates Spiel lädt und verwendet die exportierten Daten
```

Eine Änderung am Editorlayout verändert nicht automatisch die Darstellung im
Spiel. Eine Änderung am Exportformat muss dagegen zum lesenden Spiel passen.
Die [Gegenstandsarten](gegenstaende.md) erklären die fachlichen Begriffe.

## Wie beginne ich als neue Person mit einer Änderung?

| Dein Vorhaben | Dein Einstieg |
|---|---|
| Text oder Navigationsbutton ergänzen | Seitentemplate unter `templates/editor/` |
| Neue Seite erreichbar machen | Template, `view_handlers/`, Import in `views.py`, Route in `urls.py` |
| Bestimmen, wohin „Weiter“ führt | POST-Zweig der betreffenden View und Rücklink der Folgeseite |
| Festlegen, wie Eingaben gespeichert werden | Zuständiger Service, aufgerufen von der View |
| Browserinteraktion ändern | Template und passende Datei unter `static/editor/js/` |

Die Anleitung [Button und neue Seite ergänzen](seiten-erweitern.md) führt diese
Schritte am echten Aufbau von `createLevel2` vor. Du brauchst nicht für jede neue
Seite einen neuen Service: Ein Service bündelt eine fachliche Aufgabe, etwa die
Levelverarbeitung, und kann von mehreren Seiten verwendet werden.

## Was passiert, wenn ich auf „Weiter“ klicke?

Beispiel: Du schickst die SQL-Beschränkungen im geführten Editor ab.

1. Das HTML-Formular sendet die Werte an die URL `create_level2`.
2. `backend/editor/urls.py` ordnet die URL der View `create_level2_view` zu.
3. Die View in `view_handlers/create_level2.py` liest den Levelentwurf aus der Session.
4. `query_restriction_from_post` in `services/level_service.py` verarbeitet die Werte.
5. Die View schreibt den Entwurf zurück und leitet zur nächsten Seite weiter.

Ein GET-Aufruf zeigt dagegen das Formular mit seinen gespeicherten Werten an.
Am Beispiel von Level 2 sind das zwei verschiedene Wege:

```text
Seite öffnen (GET)
  create_level2_view
    → new_level aus der Session lesen
    → level2_form_values: gespeicherte Daten in Formularwerte übersetzen
    → render mit steps, saved_level und form_values
    → createLevel2.html bindet sqlGrunddatenForm.html ein

„Weiter“ anklicken (POST)
  Formularfelder → create_level2_view
    → query_restriction_from_post: Eingaben in queryRestriction übersetzen
    → new_level in die Session zurückschreiben
    → redirect("create_level3")
    → Browser öffnet die Folgeseite per GET
```

Das Template ruft den Service also nicht selbst auf. Es zeigt die Werte an, die
die View im **Kontext-Dictionary** übergibt. Ein Formular sendet die Eingaben an
eine URL; erst deren View ruft die passende Python-Verarbeitung auf.

`new_level` ist der aktuelle Levelentwurf. Seine Übernahme in `game_json` und der
anschließende ZIP-Export sind weitere Schritte. Speichern im Editor, Speichern
eines Tabellenentwurfs und Herunterladen eines Exports sind unterschiedliche Vorgänge.

## Was bedeuten die technischen Begriffe?

| Begriff | Einfach erklärt |
|---|---|
| Template | HTML-Vorlage, die Django mit Daten füllt |
| View | Python-Funktion, die eine Browseranfrage annimmt und eine Antwort liefert |
| Service | Funktionen für fachliche Aufgaben, etwa einen Gegenstand zusammenbauen |
| Session | Arbeitszustand der aktuellen Browsersitzung |
| Workspace | Arbeitsverzeichnis für importierte Dateien und Tabellenentwürfe |
| Redirect | Antwort, die den Browser auf eine andere URL schickt |

## Wie hängen die Teile zusammen?

Diese statische Übersicht zeigt den Hauptweg. Die Pfeile bedeuten „verwendet“
beziehungsweise „ruft auf“, keine Vererbung:

```text
Browser: HTML-Formulare und JavaScript
                    |
                    v
               urls.py
                    |
                    v
       views.py → view_handlers/
                    |
                    v
                services/
                    |
                    v
       database.py / utils.py / Dateien

View → Template → HTML-Antwort an den Browser
```

Einige Views verwenden `database.py` auch direkt. Die Services sind keine
vollständig von Django unabhängige Schicht: Mehrere Funktionen erhalten einen
Request und arbeiten mit seiner Session. Die Aufteilung bündelt Zuständigkeiten,
ohne dafür neue Klassen oder Frameworks einzuführen.

## Welche Aufgabe hat welcher Ordner?

Alle folgenden Pfade liegen unter `backend/editor/`:

| Ort | Zuständigkeit |
|---|---|
| `templates/editor/` | Seiten; gemeinsame Teile unter `components/` und `partials/` |
| `static/editor/js/` | Interaktion im Browser |
| `urls.py` | URL-Namen und Zuordnung zu Views |
| `views.py` | Zentrale Imports der ausgelagerten View-Funktionen |
| `view_handlers/` | Anfragen, Formulare, Session und Antworten |
| `services/` | Fachliche Verarbeitung |
| `database.py` | SQLite, Spaltentypen, Arbeitsverzeichnis und Tabellenentwürfe |
| `utils.py` | Allgemeine Namens-/Dateihelfer und optionale auskommentierte Diagnose |
| `tests.py` | Bestehende Verhaltenstests |

## Wofür sind die sieben Services da?

| Datei unter `backend/editor/services/` | Inhalt |
|---|---|
| `level_service.py` | Grunddaten, SQL-Grenzen, Levelentwurf, Speichern, Verweise und Löschen |
| `item_service.py` | Entwurf, Typ, Voraussetzungen, Passwort, Position, Bearbeitung und Löschen |
| `table_service.py` | Formularspalten/-zeilen prüfen, Werte umwandeln und Entwurfszeilen übernehmen |
| `game_import.py` | Spiel-JSON finden, Dateien importieren und Quellen merken |
| `game_export.py` | Export-JSON, Bilder, Datenbanken und weitere Dateien zum ZIP zusammenstellen |
| `game_messages.py` | Gemeinsame Systemnachrichten und Standardtexte |
| `assets.py` | Hochgeladene Bilder speichern |

`level_service` verwendet unter anderem `item_service`. Der Gegenstandsservice
importiert umgekehrt keinen Level-Service. Beide verwenden `database` und den
Bildhelfer `assets`. `database` verwendet allgemeine Helfer aus `utils`.
Services importieren keine View-Handler.

## Muss ich für eine kleine Änderung alle Dateien verstehen?

Nein. Beginne bei der konkreten Aufgabe in der [Code-FAQ](code-faq.md). Verfolge
nur die betroffene Kette aus Formular, View und Funktion. Ziehe die
[Datenverträge](editor-vertraege.md) hinzu, wenn du Feldnamen oder gespeicherte
Strukturen berührst.
