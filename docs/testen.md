# Änderungen testen und Fehler finden

## Wie prüfe ich meine Änderung zuerst?

Führe aus dem Projektordner mit aktivierter Python-Umgebung aus:

```bash
cd backend
python manage.py check
python manage.py test --verbosity 2
```

`check` prüft die Django-Konfiguration. Die Tests prüfen konkrete erwartete
Ergebnisse. Beim dokumentierten Refactoring-Stand sind es 46 Tests in
`backend/editor/tests.py`. Ein grüner Lauf ist ein wichtiger Nachweis, aber keine
Garantie für jedes mögliche Verhalten.

## Wie starte ich nur einen passenden Test?

Zum Beispiel für die SQL-Shortcuts, ebenfalls aus `backend/`:

```bash
python manage.py test editor.tests.GuidedLevelTests.test_sql_shortcut_speichert_und_zeigt_restriktionen --verbosity 2
```

Testmethoden beginnen mit `test_`, damit der Testlauf sie findet. Jede Methode
richtet ihren eigenen Ausgangszustand ein; sie darf nicht von einem vorherigen
Test abhängen.

## Was passiert in einem solchen Test?

1. **Vorbereiten:** Ein Spiel oder Level als Ausgangszustand anlegen/importieren.
2. **Handeln:** Mit `self.client.post(...)` ein Formular absenden oder mit
   `self.client.get(...)` eine Seite anfordern.
3. **Vergleichen:** Erwartete Weiterleitung, gespeicherte Daten oder Export prüfen.

`reverse("create_level2")` sucht die URL zu ihrem Namen. `self.client` ist der
Django-Testclient. Er ruft die Anwendung ohne echten Browser auf.

## Welche Tests helfen bei welcher Änderung?

Alle genannten Tests stehen in `backend/editor/tests.py`:

| Änderung | Passender vorhandener Test |
|---|---|
| Geführte Erstellung | `test_guided_level_matches_example_export` |
| SQL-Shortcut | `test_sql_shortcut_speichert_und_zeigt_restriktionen` |
| Systemnachrichten | `test_nachrichten_shortcut_speichert_auf_spielebene` |
| Tabellenzeile löschen | `test_deleting_table_row_changes_exported_database` |
| Bearbeitung abbrechen | `test_cancel_item_edit_discards_table_row_changes` |
| Level umbenennen | `test_level_rename_updates_exit_reference_and_rejects_collision` |
| Import und Export | `test_import_export_round_trip` |
| Fehlendes Bild | `test_missing_imported_image_blocks_export` |

Die gemeinsamen Beispieldaten liegen unter
`backend/editor/tests/data/SQLSpellQuest_export-24/`. Verwende sie, statt dasselbe
Level immer wieder abzutippen. Verändere die Referenzdaten nicht nur, damit ein
fehlgeschlagener Test wieder grün wird.

## Wann brauche ich zusätzlich einen Browserdurchlauf?

Bei JavaScript, Formularbedienung und Navigation. Prüfe nach einer Änderung den
betroffenen Weg: öffnen, Werte ändern, absenden, zurückgehen, erneut öffnen,
speichern beziehungsweise abbrechen. Bei Tabellen und Uploads auch exportieren
und den Export erneut laden. Prüfe die Browserkonsole auf JavaScript-Fehler.

## Wie erkenne ich die Art eines Fehlers?

| Beobachtung | Erster sinnvoller Blick |
|---|---|
| `NameError` | Fehlt ein Import oder wurde eine Variable umbenannt? |
| `NoReverseMatch` | Stimmen URL-Name und benötigte Parameter in `urls.py`? |
| HTTP 500 | Traceback im Terminal des Django-Servers |
| Button reagiert nicht | Browserkonsole, geladenes JS und erwartete DOM-ID |
| Werte verschwinden | Wurde das Formular abgesendet? Welche View schreibt den Entwurf? |
| Exportbild fehlt | Bildreferenz und Import-/Uploadquelle; nicht nur Dateiname prüfen |
| SQLite-Inhalt stimmt nicht | Tabellenentwurf, Übernahme beim Speichern und Export prüfen |

## Wie gehe ich bei einem echten Fehler vor?

Schreibe die kleinsten Schritte auf, die ihn auslösen. Ergänze nach Möglichkeit
einen Test, der genau dieses Verhalten prüft. Bestätige, dass er vor der Korrektur
fehlschlägt und danach besteht. Führe anschließend die gesamte Testsuite aus.
Ein reines Verschieben von Code soll das Verhalten dagegen unverändert lassen.

## Wie prüfe ich Änderungen an dieser Dokumentation?

```bash
python -m mkdocs build --strict
```

Prüfe danach auch Suche, Navigation und Anleitungen im Browser. Ein erfolgreicher
HTML-Build beweist nicht, dass eine Erklärung fachlich richtig ist.

[Anleitung zum Schreiben und Pflegen der Dokumentation](dokumentieren.md)
