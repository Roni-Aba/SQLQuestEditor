# FAQ: Wo ändere ich was im Code?

Alle Pfade beginnen am Projektordner. Nutze die Dateisuche deiner IDE und suche
anschließend nach dem genannten Funktionsnamen. Die Einstiegspunkte unten
entsprechen dem Stand nach der Service-Bündelung.

## Wie finde ich schnell die richtige Datei?

Die Dateipfade dieser Übersicht liegen unter `backend/editor/`.

| Ich möchte … | Datei und Einstiegspunkt |
|---|---|
| einen Text auf der Startseite ändern | `templates/editor/start.html` — Sichtbarer Text des betreffenden Elements |
| Levelname, Begrüßung oder Bild verarbeiten | `services/level_service.py` — `update_level_basics`, `update_level_picture` |
| SQL-Beschränkungen ändern | `services/level_service.py` — `query_restriction_from_post`, `level2_form_values` |
| eine Standardnachricht ändern | `services/game_messages.py` — `DEFAULT_MESSAGES` |
| den Gegenstandstyp verarbeiten | `services/item_service.py` — `item_type_and_next_view` |
| Hinweistext oder Hinweisbild ändern | `services/item_service.py` — `update_hint_field`, `update_hint_image` |
| einen Ausgang verarbeiten | `services/item_service.py` — `update_exit_fields` |
| Voraussetzungen oder Passwörter ändern | `services/item_service.py` — `set_item_requirements`, `update_password_details` |
| Koordinaten übernehmen | `services/item_service.py` — `position_from_post` |
| Tabellenwerte prüfen | `services/table_service.py` — `parse_table_columns`, `parse_table_rows` |
| SQLite-Dateien erstellen | `database.py` — `create_level_database` |
| den Import ändern | `services/game_import.py` — `import_game` |
| den Export ändern | `services/game_export.py` — `build_game_export` |
| Bearbeiten oder Abbrechen nachvollziehen | `view_handlers/item_management.py` — `edit_item_view`, `cancel_item_edit_view` |

## Gibt es ein vollständiges Beispiel für einen Button und eine neue Seite?

Ja: [Button und neue Seite ergänzen](seiten-erweitern.md) zeigt die genaue
Einfügestelle in `createLevel2.html`, eine kleine View, ihren Import und die
URL-Registrierung. Dort steht auch, welche zusätzlichen Schritte nötig sind,
wenn die neue Seite Teil des geführten Editors werden soll.

## Wo ändere ich einen Text oder Button?

**Hier anfangen:** `backend/editor/templates/editor/start.html`, wenn es um die
Startseite geht. Für andere Seiten suche nach dem aktuell sichtbaren Text:

```bash
rg -n 'Neues Spiel beginnen' backend/editor/templates/editor
```

**Das passiert dort:** Ein Template ist HTML mit Django-Platzhaltern. Die View
liefert die Werte für diese Platzhalter. Wiederverwendete Elemente werden per
`include` eingebunden und liegen unter `templates/editor/components/` oder
`templates/editor/partials/`.

**Beispiel:** Du kannst den sichtbaren Text „Neues Spiel beginnen“ umformulieren.
Erhalte dabei Formularziel, `method`, Feldnamen und CSRF-Token. Ein sichtbarer
Text ist etwas anderes als das `name`-Attribut, das Python auswertet.

**Das hängt daran:** `partials/levelGrunddatenForm.html` wird beispielsweise sowohl
im geführten Editor als auch im Grunddaten-Shortcut verwendet. Eine Änderung dort
betrifft beide Seiten. Beachte außerdem die Projektregeln in `AGENTS.md`: Bootstrap
verwenden, geschützte Komponenten erhalten und bei Figma-Aufgaben neue Seiten anlegen.

**So prüfen:** Betroffene Seiten öffnen, Text und Formularaktion kontrollieren.
Bei gemeinsamen Partials beide Einstiege prüfen.

## Wo ändere ich SQL-Beschränkungen?

**Hier anfangen:** `query_restriction_from_post` in
`backend/editor/services/level_service.py`.

**Das passiert dort:** Die Funktion liest `max_rows`, `max_columns` und drei
Meldungen aus den Formulardaten. Daraus baut sie `queryRestriction` für den
Levelentwurf. `level2_form_values` übersetzt gespeicherte Werte zurück ins Formular.

**Beispiel:** Soll eine neue Eingaberegel gelten, untersuche zuerst die bestehende
Umwandlung: Ziffern werden zu einer Zahl, andere Eingaben zu `None`. Lege das
gewünschte Verhalten in einem Test fest, bevor du die Umwandlung änderst.

**Das hängt daran:** `view_handlers/create_level2.py` und
`view_handlers/shortcut.py` verwenden denselben Service. Das Formular liegt in
`templates/editor/partials/sqlGrunddatenForm.html`. Die Prüfung einer SQL-Abfrage
im Spiel ist eine andere Aufgabe als das Speichern dieser Einstellungen im Editor.

**So prüfen:** Geführten Schritt und SQL-Shortcut absenden, erneut öffnen und den
Export kontrollieren. Der vorhandene Test
`test_sql_shortcut_speichert_und_zeigt_restriktionen` ist ein guter Einstieg.

## Wo ändere ich die Reihenfolge oder das Ziel eines Schritts?

**Hier anfangen:** In der betreffenden View unter `backend/editor/view_handlers/`.
`create_level2_view` steht beispielsweise in `create_level2.py` und leitet nach
dem Speichern auf `create_level3` weiter. `urls.py` verbindet URL-Namen mit Views;
`views.py` stellt die View-Funktionen zentral bereit.

**Das hängt daran:** Rückwege stehen teilweise im Template. Die gemeinsame
Bearbeitungsnavigation liegt in `view_handlers/shared.py`. Ein Schritt kann im
geführten Ablauf und als Abschnitt einer Gegenstandsbearbeitung aufgerufen werden.

**So prüfen:** Hinweg, Rückweg, erneutes Öffnen und Einstieg über die Verwaltung.
Ändere URL-Namen nicht beiläufig: Templates und `reverse()` verwenden sie.

## Welche HTML-Seite gehört zu welcher View?

| Oberfläche | View-Modul unter `backend/editor/view_handlers/` | Hauptservice unter `backend/editor/services/` |
|---|---|---|
| `start.html` | `game_start.py`, `game_import_export.py` | `game_messages.py`, `game_import.py` |
| `createLevel1.html`, `createLevel2.html` | `create_level1.py`, `create_level2.py` | `level_service.py` |
| `createLevel3*.html` | `create_level3.py` | `item_service.py`, `table_service.py` |
| `createLevel4.html` | `create_level4.py` | `item_service.py` |
| `createLevel5.html`, `createLevel51.html` | `create_level5.py` | `item_service.py` |
| `createLevel6*.html` | `create_level6.py` | `item_service.py` |
| `createLevel7.html`, `createLevel8.html` | `create_level7.py`, `create_level8.py` | `item_service.py`, `level_service.py` |
| `levelGrunddaten.html`, `sqlGrunddaten.html`, `messagesGrunddaten.html` | `shortcut.py` | `level_service.py`, `game_messages.py` |
| `gegenstandVerwaltung.html`, `editItem.html` | `item_management.py` | `item_service.py`, `level_service.py` |
| `level.html` | `level_management.py`; auch Exportfehler in `game_import_export.py` | `level_service.py`, `game_export.py` |

`createLevel.html` ist der Einstieg in einen neuen Entwurf (`create_level.py`).
`auswahl.html` gehört zu `shortcut.py`. Die Kontaktseite und gesonderte Vorschauen
liegen in `testingScratchView.py`.

Die HTML-Seite ruft einen Service nicht direkt auf. Ein Formular wird an eine
URL gesendet; Django ruft die View auf, und diese verwendet den Service.

## Wo ändere ich dynamisches Verhalten im Browser?

**Hier anfangen:** Unter `backend/editor/static/editor/js/`.

| Datei | Aufgabe |
|---|---|
| `start.js` | Relative Pfade des hochgeladenen Spielordners übermitteln |
| `levelGrunddatenForm.js` | Bildauswahl und Freigabe des Formularbuttons |
| `createLevel3table.js` | Spalten/Zeilen im Tabellenformular und `rows_json` |
| `createLevel3hint.js` | Eingabefelder passend zur Hinweisart anzeigen |
| `createLevel4.js` | Ausgewählte Voraussetzungen verwalten |
| `createLevel51.js` | Bild- und Iconrechtecke auswählen und umrechnen |
| `createLevel6-2.js` | Fehlversuchhinweise hinzufügen und entfernen |
| `confirmDelete.js` | Löschbestätigungen für Formulare mit `data-confirm` |

**Das hängt daran:** IDs, Feldnamen und `data-*`-Attribute verbinden HTML und JS.
Prüfe bei Änderungen beide Dateien. Das Script der alten `tableEditor`-Komponente
ist nicht der Tabelleneditor des geführten Ablaufs.

**So prüfen:** Im Browser tatsächlich klicken, Zeilen verändern oder Rechtecke
ziehen. Django-Tests führen kein JavaScript aus.

## Wo ändere ich das Exportformat oder die Speicherung?

**Hier anfangen:** `build_item_for_json` in `item_service.py` und
`build_level_for_json` in `level_service.py` erzeugen die Exportdaten eines
Gegenstands beziehungsweise Levels. `game_export.py` stellt das ZIP zusammen.
`database.py` verarbeitet SQLite und die zwischengespeicherten Tabellenzeilen.

**Das hängt daran:** Import und Spiel müssen dasselbe Format verstehen. Bewahre
unbekannte Zusatzfelder importierter Gegenstände und Bildreferenzen. Interne
Entwurfsfelder müssen nicht genauso heißen wie exportierte Felder.

**So prüfen:** Beispielspiel importieren, gezielt verändern, exportieren und erneut
importieren. JSON, Tabelleninhalte und Bilder vergleichen. Details stehen in den
[Datenverträgen](editor-vertraege.md) und unter [Testen](testen.md).
