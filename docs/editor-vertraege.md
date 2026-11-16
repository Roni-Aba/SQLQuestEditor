# Datenverträge: Welche Namen und Formate bleiben zusammen?

Stand: 08. November 2026, Branch `8-level-erstellung-absichernx`.

Zum Einstieg empfehlen wir [Zweck und Grundbegriffe](verstehen.md) und die
[Code-FAQ](code-faq.md). Dieses Dokument ist das technische Nachschlagewerk.

Dieses Dokument hält die **beobachtbaren Verträge des aktuellen Editors** fest. Bei Änderungen an Views und Services müssen Schlüssel, Steuerwerte, Datentypen, Weiterleitungen und Exportergebnisse gleich bleiben. Ein lokaler Python-Variablenname darf sich ändern. Eine bewusste Änderung eines hier beschriebenen Vertrags braucht dagegen einen eigenen Auftrag und passende Tests.

Der Editor ist für lokale Erstellung und Bearbeitung gedacht. **Import und Export sind die dauerhaften Übergabepunkte.** Die Wiederherstellung einer Session nach einem Serverneustart ist kein Ziel dieses Refactorings.

## 1. URL- und Ablaufvertrag

Die Namen in `backend/editor/urls.py` werden von Templates und `reverse()` verwendet. Für den geführten Ablauf gelten:

```text
start -> new_game oder upload_json -> level -> create_level
create_level -> create_level1 -> create_level2 -> create_level3
create_level3 -> create_level31 -> create_level3table | create_level3hint | create_level3exit
-> create_level4 -> create_level5 -> create_level51 -> create_level6
create_level6 -> create_level61 -> create_level62 -> create_level7
create_level61 -> create_level7, wenn keine Fehlversuchhinweise aktiviert sind
create_level6 -> create_level7, wenn kein Passwort erforderlich ist
create_level7 -> create_level8 -> create_level3 | gegenstandVerwaltung | auswahl_view
```

Die Bearbeitung verwendet zusätzlich `edit_level`, `levelGrunddaten`, `sql_grunddaten_view`, `messages_grunddaten`, `gegenstandVerwaltung`, `edit_item`, `edit_item_section`, `cancel_item_edit`, `delete_item`, `save_level`, `delete_level` und `export_game`. URL-Namen, erwartete Request-Methoden und Weiterleitungsziele bleiben beim internen Umbau erhalten.

`new_game` und `upload_json` nehmen POST entgegen; `save_level`, `delete_item` und `delete_level` speichern beziehungsweise löschen nur nach POST. `export_game` liefert per GET ein ZIP oder bei fehlenden erforderlichen Dateien einen Fehler.

| Steuerung | Zulässige Werte und derzeitige Bedeutung |
|---|---|
| `item_type` | `table`, `hint`, `exit`; bestimmt die Detailseite. |
| `hint_type` | `text`, `image`, `text_image`; bestimmt Text- und Bildinhalt. |
| `requires_password`, `show_hints` | Formwerte `true` und `false` als **Strings**; im Entwurf daraus boolesche Werte. |
| `next_action` | `more_items` → `create_level3`; `item_management` → `gegenstandVerwaltung`; `level_management` → `auswahl_view`. |
| GET-Parameter `return_to` | `items` → Gegenstandsverwaltung, `summary` → Gegenstandszusammenfassung. Intern kommt `level8` als Rücksprungwert hinzu. |
| `edit_item_section`-Parameter `section` | `grunddaten`, `passwort`, `position`, `typ`, `table`, `hint`, `exit`. |

## 2. Formular- und Template-Vertrag

Die folgenden `name`-Attribute sind Eingaben für die Views. Bei einer Service-Auslagerung dürfen sie weder umbenannt noch anders interpretiert werden.

| Bereich | Feldnamen |
|---|---|
| Import | `game_files`, dazu positionsgleich `game_relative_paths`; `json_file` ist der vorhandene ältere Einzeldatei-Eingang. |
| Levelgrunddaten | `level_name`, `levelPicture`, `level_greeting`. |
| SQL-Beschränkungen | `max_columns`, `max_rows`, `too_many_rows_message`, `too_many_columns_message`, `too_many_rows_columns_message`. |
| Gegenstand und Freischaltung | `item_type`, `item_name`, `unlocked_items` als JSON-Array, `requires_password`, `item_passwords`, `password_hint`, `success_message`, `show_hints`, `hint_attempts[]`, `hint_texts[]`. |
| Typdetails | Tabelle: `column_ids[]`, `column_types[]`, `rows_json`; Hinweis: `hint_type`, `hint_text`, `hint_image`; Ausgang: `exit_success_message`, `next_level_id`. |
| Position | `image_x`, `image_y`, `image_width`, `image_height`, `icon_x`, `icon_y`, `icon_width`, `icon_height`. |
| Abschluss | `next_action`. |

`column_types[]` verwendet `text`, `number`, `date` und `boolean`. `rows_json` ist ein JSON-Array von Zeilenobjekten; die Schlüssel der Zellen entsprechen den Spaltennamen. Die Koordinaten werden im Entwurf als Zahlen gespeichert.

Die Systemnachrichten werden unter den zehn Feldnamen `wrong_password`, `wrong_password_new_hint`, `not_a_table`, `unknown_table`, `locked_table`, `sql_error`, `no_result`, `row_restriction`, `col_restriction` und `row_and_col_restriction` übermittelt. Ihre aktuellen Standardtexte stehen in `DEFAULT_MESSAGES` in `backend/editor/services/game_messages.py`; leere POST-Werte werden wieder durch den jeweiligen Standardtext ersetzt.

Die vorhandenen Templates erwarten unter anderem die Kontextschlüssel `form_values`, `saved_level`, `steps`, `summary`, `error_message`, `is_item_edit`, `editing_item_id`, `return_to_item_overview` und `return_to_item_summary`. Die **Kontextschlüssel** bleiben stabil; gleichnamige lokale Python-Variablen sind frei umbenennbar.

Die Tabellenoberfläche verbindet `rows_json` mit den JSON-Script-IDs `saved-table-columns`, `saved-table-rows` und `table-type-options`. Die Positionsseite verwendet unter anderem `image-area`, `level-background-image`, `selection-box`, `start-image-selection`, `start-icon-selection` und `continue-button`. Diese DOM-IDs und die Array-Feldnamen sind auch JavaScript-Verträge.

## 3. Session- und Entwurfsvertrag

`request.session["game_json"]` enthält das Spiel. `new_game` legt zunächst `{"id": "SQLSpellQuest", "messages": ..., "level": []}` an. `request.session["new_level"]` ist dagegen der **bearbeitbare Entwurf**. Beim Start eines neuen Levels hat er diese Form:

```python
{
    "id": "",
    "levelPicture": "",
    "databaseName": "",
    "startDialog": "",
    "queryRestriction": {},
    "items": [],
}
```

Während der Bearbeitung kommen `item`, `unlockCondition` und `position` hinzu. `item` verwendet unter anderem `id`, `type`, `unlockedItems` sowie typabhängig `tableName`, `columns`, `rows`, `hintType`, `text`, `imageLink`, `exitSuccessMessage` und `nextLevelId`. `unlockCondition` verwendet `requiredItems`, `requiresPassword`, `passwords`, `passwordHint`, `successMessage`, `showHintsOnFailure` und `failureHints` mit `attempts`/`message`. `position` enthält `boundingBoxImage` und `boundingBoxIcon`, jeweils mit `x`, `y`, `width`, `height`.

Weitere gemeinsam genutzte Session-Schlüssel:

| Schlüssel | Rolle |
|---|---|
| `editing_level_id` | Identität des ursprünglich geöffneten Levels; wichtig bei Umbenennung und Abbrechen. |
| `editing_item_id`, `item_edit_mode`, `editing_item_section` | Identität und Abschnitt des bearbeiteten Gegenstands. |
| `guided_level_creation`, `item_creation_return_to`, `reset_item_draft_on_create_level3` | Navigation und Zurücksetzen des Gegenstandsentwurfs. |
| `game_workspace`, `game_root` | Arbeitsverzeichnis und Wurzel importierter Dateien. |
| `import_sources`, `import_manifest`, `import_json_path` | Quellen, relative Pfade und Dateiliste für den verlustfreien Export. |

Im Entwurf verknüpfen `_new_asset_sources` und `_import_table_sources` neu hochgeladene und importierte Dateien mit dem Export. `database.EDITOR_LEVEL_DRAFT_KEY` hat aktuell den Wert `_editor_table_rows_key`; `database.EDITOR_TABLE_DRAFT_KEY` hat den Wert `_editor_table_rows_table_key`. Die Tabellenzeilen liegen zusätzlich in `.editor-table-rows.json` im Arbeitsverzeichnis. **Abbrechen** verwirft die zugehörigen Entwurfszeilen; **Speichern** übernimmt sie. Diese Schlüssel und die Reihenfolge der Zustandsübergänge dürfen während des Refactorings nicht auseinanderlaufen.

## 4. Exportiertes Datenformat

Die Datei `SQLSpellQuest.json` hat auf oberster Ebene `id`, `messages` und `level`. `messages` gehört zum Spiel, nicht zum einzelnen Level. Ein exportiertes Level hat `id`, `levelPicture`, `databaseName`, `startDialog`, `queryRestriction` und `items`.

`queryRestriction` verwendet gegebenenfalls:

```text
rowRestriction.maxNumber
rowRestriction.violationMessages[]
columnRestriction.maxNumber
columnRestriction.violationMessages[]
colAndRowViolationMessages[]
```

Die Übersetzung vom Entwurf in den exportierten Gegenstand ist ein zentraler Vertrag:

| Entwurf | Export-JSON |
|---|---|
| `item.unlockedItems` / `unlockCondition.requiredItems` | `neededItems` |
| `unlockCondition.requiresPassword` | `unlocked` mit umgekehrtem booleschem Wert |
| `unlockCondition.passwords`, `passwordHint` | `password.unlockPasswords`, `password.passwordHint` |
| `unlockCondition.failureHints[].attempts/message` | `unlockHints[].numWrongAttempts/hint` |
| `unlockCondition.successMessage`, `afterQuery` | `nextDialog.afterUnlock`, `nextDialog.afterQuery` |
| `position.boundingBoxImage`, `position.boundingBoxIcon` | `boundingBoxImage`, `boundingBoxIcon` |
| Tabelle: `columns[].id/type` | `tableName`, `description[]`; Typen werden zu `varchar`, `int`, `date`, `bool` übersetzt. |
| Hinweis: `text`, `imageLink` | `text`, `imageLink` |
| Ausgang: `exitSuccessMessage`, `nextLevelId` | `nextDialog.afterUnlock`, gegebenenfalls `nextLevelId` |

Beim erneuten Speichern importierter Gegenstände müssen auch nicht im Formular bearbeitete Zusatzfelder erhalten bleiben. Bei Umbenennungen werden `neededItems`, Exit-Verweise `nextLevelId`, Tabellenname und Datenbankname konsistent angepasst.

Das ZIP enthält `SQLSpellQuest.json`, Bilder unter `<level>/assets/<datei>` sowie die Leveldatenbank unter `<level>/databases/<levelname>.db`. `databaseName` wird mit `database_name_for_level()` aus der Level-ID gebildet; unzulässige Dateinamenzeichen werden dabei ersetzt. Ein identischer relativer Uploadpfad ist ein Fehler. Fehlt ein referenziertes Bild, meldet der Export einen Fehler, statt ein unvollständiges ZIP auszugeben.

## 5. Prüfpunkte vor und nach dem Umbau

Die 46 Tests in `backend/editor/tests.py` sind am dokumentierten Refactoring-Stand
vorhanden und erfolgreich geprüft. Sie decken unter anderem geführte Erstellung,
Rückwege, SQL-/Nachrichten-Shortcuts, Bearbeiten/Abbrechen, Umbenennungen und
Import/Export mit Bildern und SQLite-Inhalten ab. Auch der Verlust von Zeilen,
IDs, NULL-Werten oder importierten Datenbankstrukturen wird in ausgewählten Fällen
geprüft. Die genaue Auswahl steht in [Testen und Fehler finden](testen.md).

Django-Tests mit `self.client` führen kein JavaScript aus. Tabellenbedienung,
Bildpositionierung und tatsächliche Browsernavigation müssen zusätzlich im
Browser geprüft werden. Die Tests decken nicht jeden denkbaren Fall ab.

Für jeden Umbauabschnitt gilt: **erst den fehlenden Verhaltenstest ergänzen und grün bekommen, dann Logik verschieben, danach dieselben Tests erneut ausführen**. Wenn ein gewünschter Test bereits am Ausgangsstand scheitert, ist das eine getrennte Fehlerkorrektur und keine verdeckte Refactoring-Änderung.
