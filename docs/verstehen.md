# Wofür ist der Editor da?

## Was kann ich mit dem Editor erstellen?

Du kannst Spielinhalte für SQL Spell Quest zusammenstellen: ein Spiel mit Leveln,
Hintergrundbildern und Gegenständen. Manche Gegenstände stehen für Tabellen,
andere liefern Hinweise oder beschreiben einen Ausgang. Die Tabellen werden als
SQLite-Datenbanken exportiert. So kannst du Inhalte für SQL-Aufgaben vorbereiten,
ohne das Exportformat von Hand schreiben zu müssen.

Das Spiel selbst ist eine separate Anwendung. Diese Dokumentation beschreibt das
Verhalten des Editors und die von ihm erzeugten Daten. Wie das Spiel etwa einen
Ausgang ohne Ziel behandelt, muss in der Spielanwendung geprüft werden.

## Was ist ein Spiel, ein Level und ein Gegenstand?

| Begriff | Bedeutung | Beispiel |
|---|---|---|
| Spiel | Sammlung von Leveln und gemeinsamen Systemnachrichten | Ein SQL-Rätsel mit mehreren Räumen |
| Level | Ein Abschnitt mit Hintergrundbild, Begrüßung, SQL-Grenzen und Gegenständen | Ein Arbeitszimmer |
| Gegenstand / Item | Ein Eintrag in einem Level mit Typ, Name und Einstellungen | Tabelle `Geschaefte`, Hinweis `Notiz`, Ausgang `Tuer` |
| Datenbank | Datei mit den Tabellen und ihren Zeilen | `Arbeitszimmer.db` |
| Systemnachricht | Gemeinsamer Text des Spiels, etwa bei falschem Passwort | „Versuche es noch einmal.“ |

Ein Table-Item beschreibt die Tabelle im Spiel-JSON; die eigentlichen Zeilen liegen
in der Datenbank. Ein Hintergrundbild gehört zum Level. Ein zusätzliches
Hinweisbild gehört zum jeweiligen Hint-Item.

## Wie könnte ein kleines Rätsel aussehen?

Eine Tabelle `Geschaefte` enthält Namen von Geschäften. Eine `Notiz` erklärt,
welche Informationen gesucht werden. Eine `Tuer` bekommt ein Passwort und eine
Erfolgsmeldung. Du entscheidest, wie diese Inhalte zusammenpassen.

Der Editor leitet kein Passwort automatisch aus einer SQL-Abfrage ab. Du trägst
Passwörter und Hinweise selbst ein und überprüfst anschließend im Spiel, ob das
Rätsel sinnvoll lösbar ist.

## Was bedeuten JSON und SQLite?

**JSON** ist eine Textdatei mit benannten Datenfeldern. `SQLSpellQuest.json`
beschreibt unter anderem Level, Bilder, Gegenstände und Freischaltbedingungen.

**SQLite** speichert Tabellen in einer einzelnen `.db`-Datei. Jedes exportierte
Level erhält eine Datenbank mit einem aus dem Levelnamen gebildeten Namen.
Für `Arbeitszimmer` lautet er `Arbeitszimmer.db`.

## Muss ich programmieren können, um Level zu erstellen?

Für Formulare, Bilder und Hinweise brauchst du keine Django-Kenntnisse. Für
Table-Items helfen Kenntnisse über Tabellen, Spalten, Datentypen und SQL.
Wenn du das Verhalten des Editors verändern möchtest, führt dich die
[Code-FAQ](code-faq.md) zu den richtigen Dateien.
