# Wie ergänze ich einen Button oder eine neue Seite?

Diese Anleitung zeigt kleine Änderungen an `createLevel2`, der Seite für
SQL-Beschränkungen. Alle Dateipfade beginnen am Projektordner. Die Beispiele
sind zum selbst Ausprobieren gedacht; diese Dokumentation fügt dem Editor
noch keine Hilfeseite hinzu.

## Welche Dateien brauche ich dafür?

| Aufgabe | Betroffene Dateien unter `backend/editor/` |
|---|---|
| Button zu einer vorhandenen Seite | Das betreffende Template |
| Eigene Seite anzeigen | Neues Template, passender View-Handler, `views.py`, `urls.py` |
| Eingaben verarbeiten | Zusätzlich der passende Service und Verhaltenstests |
| Nur im Browser etwas ein-/ausblenden | Template und zugehörige externe JavaScript-Datei |

Öffne in PyCharm den Projektordner. Über die Dateisuche findest du beispielsweise
`createLevel2.html`. Über „In Dateien suchen“ findest du `create_level2_view` und
alle Aufrufer. Lies vor einer Änderung auch die lokalen Regeln in `AGENTS.md`.
Die Beispiele hier beschreiben normale, ausdrücklich beauftragte Codeänderungen.
Für Figma-Aufträge gelten zusätzlich die dort festgelegten Regeln zur Neuanlage
von Templates und Render-Views.

## Wie füge ich auf createLevel2 einen Button ein?

### 1. Entscheide, was beim Klick passieren soll

| Gewünschte Wirkung | HTML | Was macht der Browser? |
|---|---|---|
| Andere Seite öffnen | `<a href="…">` | Ruft die Zielseite per GET auf |
| Formular absenden | `<button type="submit">` | Sendet die Felder des zugehörigen Formulars |
| Lokale JavaScript-Aktion auslösen | `<button type="button">` | Führt nur die angeschlossene Browseraktion aus |

Ein Link kann wie ein Button aussehen. Entscheidend sind das HTML-Element und
seine Attribute. Ein normaler Link speichert keine neu eingetippten Formulardaten.

### 2. Ergänze einen Link zur vorhandenen Kontaktseite

Öffne `backend/editor/templates/editor/createLevel2.html`.
Füge **innerhalb von `create-page__content`, direkt nach dem schließenden
`</section>` der Fortschrittsanzeige**, diesen Block ein. Die folgenden
`{% url … %}`-Zeilen und der Formular-Include bleiben erhalten.

```html
<div class="mb-3">
  <a class="btn btn-outline-primary" href="{% url 'kontakt' %}">
    Kontakt öffnen
  </a>
</div>
```

- `<div class="mb-3">` gruppiert den Link und gibt ihm mit Bootstrap Abstand nach unten.
- `<a>` ist der Navigationslink. `btn btn-outline-primary` lässt ihn wie einen Button aussehen.
- `{% url 'kontakt' %}` sucht den vorhandenen URL-Namen in `urls.py` und erzeugt den Pfad.
- `Kontakt öffnen` ist der sichtbare Text. Du kannst ihn ändern, ohne das Ziel zu ändern.
- Die schließenden Tags beenden Link und Gruppe.

Du brauchst dafür keine neue View und keinen Service: Die Kontaktseite existiert
bereits. Verwende den URL-Namen statt eines fest eingetragenen Pfades.

### 3. Prüfe den Button

Starte den Editor wie in [Projekt starten](starten.md) beschrieben. Beginne ein
Level und gehe zu den SQL-Beschränkungen. Der Button soll die Kontaktseite öffnen.
Prüfe den bisherigen „Weiter“-Button ebenfalls. Er soll die Eingaben weiterhin
übernehmen und zu `create_level3` führen.

Beim Verlassen per Link werden noch nicht abgesendete Eingaben nicht in der
Session gespeichert. Für eine Hilfe, die während des Ausfüllens offen bleiben
soll, wäre ein zusätzlicher Tab eine mögliche bewusste UI-Entscheidung.

## Warum ändere ich dafür nicht einfach das gemeinsame Formular?

`createLevel2.html` bindet `partials/sqlGrunddatenForm.html` ein. Dieses Partial
enthält bereits ein vollständiges `<form>` und wird auch von `sqlGrunddaten.html`
für den Shortcut verwendet.

```text
createLevel2.html ────┐
                     ├── include → partials/sqlGrunddatenForm.html
sqlGrunddaten.html ──┘
```

Ein Button im Seitentemplate erscheint nur dort. Eine Änderung am gemeinsamen
Partial kann beide Einstiege betreffen. Ein Submit-Button muss dem Formular
zugeordnet sein; einfach außerhalb eingefügt sendet er es nicht ab. Verschachtele
niemals ein zusätzliches `<form>` um dieses Partial.

Für einen ausdrücklich gewünschten neuen Speicherbutton klärst du zuerst die
Aktion, ergänzt den Submit-Button im passenden Formular und behandelst seine
Aktion in der View. Bestehende `action`, `method`, Feldnamen und `{% csrf_token %}`
bleiben erhalten. Fachliche Verarbeitung gehört in den zuständigen Service.
Ein zweiter Submit-Button allein erzeugt noch kein anderes Speicherverhalten.

## Wie füge ich eine eigene Seite hinzu?

Beispiel: Eine Hilfeseite erklärt die SQL-Beschränkungen. Sie zeigt nur Text an
und verändert keine Spieldaten. Wir verwenden den Namen `sql_hilfe` durchgehend
für die URL und `sql_hilfe_view` für die Python-Funktion.

### 1. Lege das Template an

Erstelle `backend/editor/templates/editor/sqlHilfe.html` mit diesem Inhalt:

```html
{% extends "editor/base.html" %}

{% block title %}SQL-Hilfe | SQL Spell Quest Editor{% endblock %}

{% block content %}
<main class="container py-4">
  <h1>{{ page_title }}</h1>
  <p>
    Die Zeilengrenze bestimmt, wie viele Ergebniszeilen eine SQL-Abfrage
    maximal liefern darf. Die Spaltengrenze begrenzt die Ergebnisspalten.
  </p>
  <a class="btn btn-outline-primary" href="{% url 'create_level2' %}">
    Zurück zu den SQL-Beschränkungen
  </a>
</main>
{% endblock %}
```

`extends` übernimmt das bestehende Grundlayout samt Navigation und Bootstrap.
Die beiden `block`-Bereiche liefern Seitentitel und Inhalt. `{{ page_title }}`
ist ein Platzhalter: Seinen Wert liefert gleich die View. Die Bootstrap-Klassen
regeln Breite und Abstände; eine neue CSS-Datei ist dafür nicht nötig.

### 2. Ergänze die View im passenden vorhandenen Modul

Öffne `backend/editor/view_handlers/create_level2.py`. Ergänze diese Funktion
**unterhalb** der bestehenden Funktion, ohne deren Inhalt zu ersetzen:

```python
def sql_hilfe_view(request):
    return render(request, "editor/sqlHilfe.html", {
        "page_title": "SQL-Beschränkungen verstehen",
    })
```

- `def` definiert die Funktion. Django übergibt die Browseranfrage als `request`.
- `render` lädt das Template und erzeugt eine HTML-Antwort. Der Import von `render`
  ist in diesem Modul bereits vorhanden.
- Das Dictionary ordnet `page_title` den Text zu, den das Template einsetzen soll.
- `return` gibt die fertige Antwort an Django zurück.

Für dieses Beispiel liegt die Hilfe neben der zugehörigen Level-2-View.
Eine rein darstellende Seite braucht keinen neuen Service.

### 3. Mache die Funktion über views.py erreichbar

In `backend/editor/views.py` ersetzt du die bisherige Importzeile für Level 2
mit diesem Import:

```python
from .view_handlers.create_level2 import create_level2_view, sql_hilfe_view
```

`views.py` dient hier als zentraler Zugang zu den ausgelagerten Funktionen.
Die URL-Konfiguration verwendet `views.sql_hilfe_view`. Die Funktion wird dabei
nicht kopiert und auch noch nicht ausgeführt.

### 4. Registriere die URL

In `backend/editor/urls.py` ergänzt du **innerhalb von `urlpatterns`** eine Zeile:

```python
path("sql-hilfe/", views.sql_hilfe_view, name="sql_hilfe"),
```

- `"sql-hilfe/"` ist der Pfad im Browser, lokal also `http://127.0.0.1:8000/sql-hilfe/`.
- `views.sql_hilfe_view` ist die Funktion für diese Anfrage. Dahinter stehen keine Klammern.
- `name="sql_hilfe"` ist der Name, den Templates und `reverse()` verwenden.

`path` und `views` sind bereits importiert. `backend/config/urls.py` bindet die
Editor-URLs bereits ein und braucht für diese Seite keine Änderung.

### 5. Verlinke die neue Seite

Im Button aus dem ersten Beispiel ersetzt du Ziel und Beschriftung:

```html
<div class="mb-3">
  <a class="btn btn-outline-primary" href="{% url 'sql_hilfe' %}">
    Hilfe zu SQL-Beschränkungen
  </a>
</div>
```

Dieser Link funktioniert erst, wenn die neue Route registriert ist.
Der Ablauf ist nun:

```text
createLevel2.html: Klick auf Hilfe
    → GET /sql-hilfe/
    → urls.py: Name sql_hilfe
    → views.py: importierte Funktion sql_hilfe_view
    → view_handlers/create_level2.py: render(...)
    → sqlHilfe.html + page_title
    → HTML im Browser
```

### 6. Prüfe die fertige Änderung

Führe mit aktivierter Python-Umgebung im Ordner `backend/` aus:

```bash
python manage.py check
python manage.py test
```

Öffne anschließend den Editor. Kontrolliere den Hilfebutton, die Überschrift und
den Rücklink. Prüfe auch, dass das ursprüngliche Absenden der SQL-Beschränkungen
weiterhin funktioniert. Die bisherigen Tests decken eine neu hinzugefügte Hilfe
nicht automatisch ab; für ihre neue Route kannst du in `editor/tests.py` einen
gezielten Test für Status 200, Template und Inhalt ergänzen.

## Was ist anders, wenn die Seite ein neuer geführter Schritt werden soll?

Eine registrierte Seite wird nicht automatisch Teil des Assistenten. Der aktuelle
Ablauf wird durch Form-Actions, POST-Weiterleitungen und Rücklinks bestimmt.
Für einen neuen Schritt zwischen Level 2 und Level 3 prüfst du gemeinsam:

1. **Vorheriger Schritt:** `create_level2_view` speichert aktuell die Einschränkungen
   und leitet bei POST zu `create_level3` weiter. Diese Weiterleitung müsste zum
   neuen Schritt führen; das Speichern davor muss erhalten bleiben.
2. **Neue View:** GET zeigt den Entwurf. POST verarbeitet die neuen Eingaben,
   übernimmt sie in den Entwurf und leitet zu `create_level3` weiter.
3. **Rücknavigation:** Die neue Seite braucht einen Rückweg. In `createLevel3.html`
   ist der Rücklink vom Bearbeitungsmodus abhängig. Nur der passende geführte
   Rückweg darf auf den neuen Schritt zeigen; die anderen Ziele bleiben erhalten.
4. **Fortschritt:** `get_steps()` in `view_handlers/shared.py` erzeugt derzeit die
   Nummern 0 bis 8. Bei einem zusätzlichen nummerierten Schritt müssen auch die
   `active_step`-Angaben der betroffenen Views zur neuen Reihenfolge passen.
5. **Gemeinsame Logik:** Wenn der Schritt Daten bearbeitet, wähle den vorhandenen
   Level-, Gegenstands- oder Tabellenservice. Prüfe auch die Shortcut-Aufrufer.
6. **Prüfung:** Teste beide Übergänge mit derselben Client-Session, die gespeicherten
   Werte, Zurück/Vorwärts sowie gegebenenfalls Bearbeiten, Abbrechen und Export.

Neue gespeicherte Felder können außerdem Änderungen an Import, Export und Spiel
verlangen. Kläre das Format anhand der [Datenverträge](editor-vertraege.md), bevor
du einen neuen Session- oder JSON-Schlüssel einführst.

## Was bedeutet eine typische Fehlermeldung?

| Meldung oder Verhalten | Wo zuerst nachsehen? |
|---|---|
| `NoReverseMatch` | Stimmt der Name in `{% url … %}` mit `name=…` in `urls.py` überein? |
| `TemplateDoesNotExist` | Liegt die Datei unter `templates/editor/` und stimmt `editor/sqlHilfe.html` in `render`? |
| `AttributeError` bei `views.sql_hilfe_view` | Ist die Funktion in `views.py` importiert und richtig geschrieben? |
| 404 beim Öffnen | Ist die Route in `urlpatterns`, und stimmt der eingegebene Pfad? |
| Neue Eingaben fehlen nach einem Klick | Wurde das Formular per POST abgesendet oder nur ein Link geöffnet? |
| Button erscheint auch im Shortcut | Wurde ein gemeinsames Partial statt nur des Seitentemplates geändert? |

Weitere Einstiegspunkte stehen in der [Code-FAQ](code-faq.md). Den Datenweg und
die Zuständigkeiten erklärt die [Architekturübersicht](architektur.md).
