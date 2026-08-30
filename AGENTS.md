# Codex-Arbeitskontext für SQL Spell Quest Editor

Stand: 2026-07-27, nach vollständiger Analyse aller Django-Templates, Komponenten, Partials und Frontend-Hooks.

Diese Datei ist der verbindliche Projektkontext für Codex in diesem Repository. Bei jedem neuen Figma-MCP-Request zuerst diese Datei lesen, danach den betroffenen Projektbereich und erst dann das Figma-Design auswerten.

Das Projekt wird Design-Driven entwickelt: Die Mockups liegen in Figma und werden per MCP bereitgestellt. Figma beschreibt das Zielbild und die Interaktionsabsicht. Die Umsetzung bleibt aber eine serverseitige Django-Anwendung mit Bootstrap 5 und bestehenden, wiederverwendbaren Django-Template-Komponenten.

## 0. Verbindliches Arbeitsprotokoll

Jede ausgeführte Arbeitshandlung ist unmittelbar nach ihrem Abschluss in `log.md` zu protokollieren. Das umfasst insbesondere Analyse, Toolaufrufe, Entscheidungen, Dateiänderungen, Prüfungen und Sichtprüfungen. Ausschließlich der Log-Aufruf selbst wird nicht erneut geloggt, damit keine Endlosschleife entsteht.

Aus dem Projektstamm ist dafür dieses Skript zu verwenden:

```bash
./scripts/log_agent_step.sh <kategorie> "<kurze Aktion>" [--duration-ms <ms>] [--tokens-estimated <anzahl>]
```

Zulässige Kategorien sind `analyse`, `tool`, `entscheidung`, `implementierung`, `validierung` und `sichtpruefung`. Kategorie, Aktion, exakter ISO-8601-Timestamp und Tokenverbrauch sind Pflichtfelder jedes Eintrags. Die beobachtete Laufzeit ist eine optionale Zusatzangabe und wird in Millisekunden übergeben, sobald sie zuverlässig messbar ist. Die sichtbare Textnutzlast von Request und Response darf näherungsweise als Zeichenanzahl geteilt durch vier erfasst werden; sie wird ausdrücklich nur als Schätzung markiert und darf nicht als tatsächlicher Modell-Tokenverbrauch ausgegeben werden. Ist der sichtbare Umfang nicht zuverlässig messbar, bleibt der Tokenverbrauch transparent `nicht verfügbar`.

## 1. Zielbild

Der SQL Spell Quest Editor soll visuell möglichst nah an den Figma-Mockups bleiben, ohne die bestehende Django-Struktur unnötig umzubauen.

Prioritäten:

1. Bestehende Funktionalität erhalten.
2. Für jedes Figma-Design eine neue Django-Seite anlegen; bestehende HTML-Dateien niemals verändern.
3. Bootstrap 5 für Layout, Spacing, Typografie, Formulare, Buttons, Cards, Alerts, Tabellen und Responsive-Verhalten verwenden.
4. Eigene Komponenten beibehalten und wiederverwenden, wenn sie Django-Logik, Wiederverwendung oder projektspezifisches Verhalten kapseln.
5. Frontend ausschließlich mit Bootstrap-Klassen umsetzen. Keine neuen CSS-Dateien erstellen und keine bestehenden CSS-Dateien für eine Designänderung bearbeiten.
6. Projektstruktur beibehalten.

### Verbindliche Neuanlage bei jedem Figma-Prompt

Bei jedem Prompt, der ein Figma-Design implementieren, übertragen oder nachbauen lässt, gilt ausnahmslos:

1. Keine bestehende `.html`-Datei ändern. Sämtliche vorhandenen Templates und Partials sind für Figma-Aufgaben schreibgeschützt, auch wenn bereits eine fachlich oder visuell ähnliche Seite existiert.
2. Immer eine neue, eindeutig benannte `.html`-Datei direkt unter `backend/editor/templates/editor/` anlegen. Auch bei einem späteren Prompt zum selben Figma-Node eine weitere neue Seite erzeugen, statt die zuvor erzeugte Seite zu ändern.
3. In `backend/editor/views.py` immer eine neue View-Funktion ergänzen, die ausschließlich das neue Template rendert. Darstellungsdaten dürfen als neuer lokaler Kontext übergeben werden; die View darf keine Session-, Upload-, Persistenz- oder POST-Logik erhalten. Bestehende View-Funktionen nicht verändern.
4. In `backend/editor/urls.py` immer genau eine neue `path(...)`-Zeile mit einem neuen, eindeutigen URL-Namen für diese View ergänzen. Bestehende Routen nicht verändern.
5. Vorhandene Template-Komponenten dürfen im neuen Template unverändert per `{% include %}` wiederverwendet werden. Ihre `.html`-Dateien dürfen dafür nicht angepasst werden.
6. Benötigt das Design neue Fachlogik, Session-Daten, Persistenz oder Formularverarbeitung, diese nicht in die neue reine Render-View hineininterpretieren. Dafür zuerst einen ausdrücklichen Backend-Auftrag des Nutzers einholen.

Diese Regel hat bei Figma-Prompts Vorrang vor allen allgemeinen Empfehlungen zur Wiederverwendung oder Erweiterung bestehender Templates.

Neue Figma-Seiten nachvollziehbar und kollisionsfrei benennen. Den semantischen Seitennamen und die Figma-Node-ID verwenden:

```text
Template: figma_<seitenname>_<node-a>_<node-b>.html
View:     figma_<seitenname>_<node-a>_<node-b>_view
Route:    figma/<seitenname>-<node-a>-<node-b>/
URL-Name: figma_<seitenname>_<node-a>_<node-b>
```

Beispiel für Node `78:725`:

```python
def figma_levelgrunddaten_78_725_view(request):
    return render(
        request,
        "editor/figma_levelgrunddaten_78_725.html",
    )
```

Die zugehörige Route muss als genau eine neue Zeile ergänzt werden:

```python
path("figma/levelgrunddaten-78-725/", views.figma_levelgrunddaten_78_725_view, name="figma_levelgrunddaten_78_725"),
```

Fertige Komponenten und fertige Layouts sind geschützt. Ihr Styling, ihre Abstände, Größen, Farben, Typografie, Responsive-Regeln und visuelle DOM-Struktur dürfen nicht verändert werden. Sie werden bei neuen Seiten ausschließlich unverändert wiederverwendet.

Kein Ziel:

- React, Vue, Tailwind, ein npm-Build oder eine neue Frontend-Architektur einführen.
- Figma-Details mit hart kodierten Einzelwerten oder eigenem CSS erzwingen, obwohl Bootstrap dieselbe Absicht ausdrücken kann.
- Neue `<style>`-Blöcke, `style="..."`-Attribute, CSS-Variablen oder projektspezifische Utility-Klassen einführen.
- Backend-, Session-, JSON- oder Spiellogik ändern, nur weil ein Design das nahelegt.

## 2. Technischer Rahmen

Das Projekt ist eine klassische Django-App:

```text
backend/
  manage.py
  config/
  editor/
    templates/editor/
    static/editor/
    views.py
    urls.py
    utils.py
    sqlParser.py
docs/
```

Relevante Technologie:

- Django 4.2.30
- serverseitige Django-Templates
- Bootstrap 5.3.3 via CDN in `base.html`
- Bootstrap Icons 1.11.3 via CDN in `base.html`
- vorhandene CSS-Dateien unter `backend/editor/static/editor/` als Legacy-Bestand; sie sind für neue Aufgaben nur lesbar
- kein `package.json`, kein Frontend-Build
- CI führt aktuell `python -m compileall .` und `mkdocs build --strict` aus

Lokale Standardbefehle:

```bash
cd backend
python manage.py runserver
```

```bash
cd backend
python manage.py check
```

```bash
cd backend
python manage.py test
```

Hinweis: Es sind derzeit keine aussagekräftigen Tests vorhanden. `manage.py test` prüft damit hauptsächlich, ob Django ohne Testsuite startet.

## 3. Aktuelle Frontend-Struktur

Aktueller Stand:

- 40 HTML-Templates mit insgesamt 5.776 Zeilen unter `backend/editor/templates/editor/`
- 28 Root-Templates direkt unter `templates/editor/`, einschließlich `base.html`
- 8 Komponenten unter `templates/editor/components/`
- 4 Partials unter `templates/editor/partials/`
- 15 CSS-Dateien unter `backend/editor/static/editor/`; diese sind Legacy-Bestand und werden nicht weiter ausgebaut
- 604 Zeilen vorhandenes CSS
- 1 externe JS-Datei unter `backend/editor/static/editor/components/tableEditor/tableEditor.js`
- 6 Templates mit ausführbarem Inline-JavaScript
- 9 Cosmo-Bilder unter `backend/editor/static/editor/img/cat1.png` bis `cat9.png`

Globale Basis:

```text
backend/editor/templates/editor/base.html
```

`base.html` lädt:

```text
Bootstrap 5.3.3
Bootstrap Icons 1.11.3
editor/css/tokens.css
editor/css/base.css
editor/css/layout.css
editor/css/forms.css
```

`base.html` inkludiert `components/navbar/navbar.html` automatisch. Die vorhandene Datei `components/navbar/navbar.css` wird von `base.html` nicht geladen; ihre `.navbar-custom`-Selektoren werden im aktuellen Navbar-Markup nicht verwendet.

`{% block additional_css %}` bleibt aus Kompatibilitätsgründen bestehen. In neuen Seiten darf er nur unveränderte, bereits vorhandene Komponenten-CSS für tatsächlich inkludierte Bestandskomponenten laden; nie neue, geänderte oder seitenspezifische CSS-Dateien.

## 4. Template-Inventar

Root-Templates:

```text
auswahl.html
base.html
createLevel.html
createLevel1.html
createLevel2.html
createLevel2-1.html
createLevel3.html
createLevel4.html
createLevel4-1.html
createLevel4-2.html
createLevel5.html
createLevel51.html
createLevel6.html
createLevel61.html
createLevel6exit.html
createLevel6hint.html
createLevel6table.html
createLevel7.html
createLevel8.html
editItem.html
gegenstandVerwaltung.html
level.html
levelGrunddaten.html
messagesGrunddaten.html
sqlGrunddaten.html
start.html
test.html
contact.html
```

Komponenten:

```text
components/button/button.html
components/dropdown/dropdown.html
components/helper/helper.html
components/navbar/navbar.html
components/statusBar/statusBar.html
components/tableEditor/tableEditor.html
components/tableItem/tableitem.html
components/tag/tag.html
```

Partials:

```text
partials/itemSummary.html
partials/levelGrunddatenForm.html
partials/messagesForm.html
partials/sqlGrunddatenForm.html
```

Vorhandene CSS-Dateien im Legacy-Bestand:

```text
css/base.css
css/forms.css
css/layout.css
css/level.css
css/start.css
css/tokens.css
css/createLevel51.css
components/button/button.css
components/dropdown/dropdown.css
components/helper/helper.css
components/navbar/navbar.css
components/statusBar/statusBar.css
components/tableEditor/tableEditor.css
components/tableItem/tableItem.css
components/tag/tag.css
```

Nicht in dieser Analyse vorhanden: `createLevelShared.css`, `css/pages/`, `chatBox/`, `chatbox/`, `app.css`, `utilities.css`.

## 5. Komponenten-Regeln

Vor jeder Neuentwicklung prüfen, ob eine bestehende Komponente reicht.

### Schutz fertiger Komponenten und Layouts

Die folgenden Bereiche gelten als fertiger Bestand und dürfen bei einer neuen Figma-Umsetzung nicht optisch angepasst werden:

- `base.html` und das globale Seitenlayout
- `components/navbar/navbar.html`
- `components/button/button.html`
- `components/dropdown/dropdown.html`
- `components/helper/helper.html`
- `components/statusBar/statusBar.html`
- `components/tableEditor/tableEditor.html`
- `components/tableItem/tableitem.html`
- `components/tag/tag.html`
- bereits umgesetzte Seitenlayouts und deren Bootstrap-Klassen

Nicht verändern:

- Bootstrap-Klassen, die das bestehende Styling oder Layout bestimmen
- Reihenfolge, Ausrichtung, Abstände, Breiten und Höhen fertiger Bereiche
- Farben, Schriftgrößen, Schriftgewichte, Rahmen, Rundungen und Schatten
- Responsive-Verhalten und Breakpoints
- vorhandene CSS-Dateien oder CSS-Abhängigkeiten

Bei einem neuen Figma-Request wird immer ein neues Seitentemplate angelegt. Der fertige Bestand darf darin ausschließlich unverändert eingebunden werden. Die neue Seite wird mit Bootstrap-Markup aufgebaut. Wenn Figma eine Abweichung zu einer fertigen Komponente zeigt, bleibt die bestehende Komponente unverändert; die Abweichung wird dokumentiert.

Eine bestehende Komponente oder ein bestehendes Layout darf nur geändert werden, wenn der Nutzer ausdrücklich genau diese Komponente oder dieses Layout zur Überarbeitung beauftragt.

### Verbindliche Komponentenverträge

| Komponente | Parameter und Verhalten | Vorhandene Abhängigkeit |
|---|---|---|
| `button/button.html` | `title`; optional `href`, `icon`, `type`, `name`, `value`, `disabled`. Mit `href` entsteht ein `<a>`, sonst ein `<button>`. Nicht in ein weiteres `<a>` einwickeln; für Navigation `href` direkt übergeben. | `button/button.css` |
| `dropdown/dropdown.html` | `id` und `name`; optional `label`, `placeholder`, `options` mit `value`/`label`, `selected_value`, `required`, `error`. | `dropdown/dropdown.css` |
| `helper/helper.html` | `helper_image` und `helper_text`; optional `aria_label`, `image_alt`. Lädt das Bild selbst über `{% static %}`. | `helper/helper.css` und globale `.cosmo-image`-Regeln |
| `navbar/navbar.html` | Keine Parameter. Enthält feste Links auf `auswahl_view`, `level`, `start` und `kontakt` und wird von `base.html` automatisch inkludiert. | aktuelles Markup nutzt Bootstrap; `navbar.css` wird nicht geladen |
| `statusBar/statusBar.html` | `steps`: Liste aus Objekten mit `number` und `active`. `get_steps()` markiert aktuell alle abgeschlossenen und den aktuellen Schritt als `active`. | `statusBar/statusBar.css` |
| `tableEditor/tableEditor.html` | `form_values.table_name`, `form_values.columns`, `data_type_options`; Felder `column_ids[]` und `column_types[]`. | `tableEditor.css` und explizit zu ladendes `tableEditor.js` |
| `tableItem/tableitem.html` | `title`; optional `edit_url`, `delete_url`. Löschen ist ein POST-Formular mit CSRF und Confirm-Dialog. | aktuelles Markup ist Bootstrap-basiert; die Klassen aus `tableItem.css` kommen darin nicht vor |
| `tag/tag.html` | `title`; beabsichtigte Optionen `show_remove`, `show_edit`, `edit_url`, `delete_url`. Löschen ist ein POST-Formular mit CSRF und Confirm-Dialog. | `tag/tag.css` |

Zusätzliche Regeln:

- Der teilweise übergebene Parameter `show_list` wird von `tag.html` nicht ausgewertet.
- Wegen `show_remove|default:True` und `show_edit|default:True` werden explizite `False`-Werte derzeit wieder zu `True`. Die Komponente kann die beiden Aktionen daher nicht zuverlässig ausblenden. In neuen Seiten nicht für einen Nur-Anzeige-Tag verwenden und die geschützte Komponente nicht reparieren.
- `tableEditor.html` wird aktuell von keinem Seitentemplate inkludiert und `tableEditor.js` wird nirgends geladen. `createLevel6table.html` ist ein separater Editor mit eigener Inline-Logik. Diese beiden Implementierungen nicht vermischen.
- Eine Komponente höchstens einmal pro Seite einbinden, wenn sie feste IDs oder globale DOM-Abfragen besitzt. Das betrifft insbesondere `tableEditor`.
- Beim unveränderten Wiederverwenden einer Komponente darf ihre bereits vorhandene CSS-Datei im `additional_css`-Block der neuen Seite verlinkt werden. Dies ist die einzige zulässige neue CSS-Abhängigkeit. Die CSS-Datei selbst bleibt unverändert.
- Wenn eine vorhandene Komponente das Figma-Ziel nicht passend ausdrückt, im neuen Seitentemplate direkt Bootstrap-Markup verwenden. Die bestehende Komponente nicht anpassen.

### Verbindliche Partial-Verträge

Partials sind ebenfalls bestehende HTML-Dateien und bei Figma-Aufgaben schreibgeschützt:

| Partial | Verwendet von | Vertrag |
|---|---|---|
| `partials/levelGrunddatenForm.html` | `createLevel1.html`, `levelGrunddaten.html` | Enthält ein vollständiges Multipart-POST-Formular und Inline-JS. Erwartet `form_action`, `back_url`, `helper_text`, `submit_label`, `submit_icon`, `submit_button_id`, `require_picture`, `form_values`. Felder: `level_name`, `levelPicture`, `level_greeting`. |
| `partials/sqlGrunddatenForm.html` | `createLevel2.html`, `sqlGrunddaten.html` | Enthält ein vollständiges POST-Formular. Erwartet `form_action`, `back_url`, `helper_text`, `submit_label`, `submit_icon`, `navigation_label`, `form_values`. Felder: `max_columns`, `max_rows` und drei Überschreitungsnachrichten. |
| `partials/messagesForm.html` | `createLevel2-1.html`, `messagesGrunddaten.html` | Ist nur eine Formularsektion und muss innerhalb eines POST-Formulars stehen. Erwartet `form_values`; optional `messages_column_class`. Enthält zehn Nachrichtenfelder. |
| `partials/itemSummary.html` | `createLevel7.html`, `editItem.html` | Erwartet `summary`; optional `page_title`, `item_id`. Mit `item_id` verlinkt es auf `edit_item_section`, sonst auf die geführten Create-Routen. |

Ein Partial, das bereits ein `<form>` enthält, niemals in ein weiteres Formular verschachteln. Partials nur inkludieren, wenn der neue View-Kontext ihren Vertrag vollständig erfüllt; sonst neues Bootstrap-Markup ausschließlich im neuen Seitentemplate schreiben.

Neue Komponenten nur anlegen, wenn sie wiederverwendbar sind oder eine klare Django-Template-Logik kapseln. Struktur dann analog halten:

```text
backend/editor/templates/editor/components/<name>/<name>.html
```

Für neue Komponenten wird ausschließlich ein Django-Template angelegt und Bootstrap-Markup verwendet. Eine neue `<name>.css`-Datei ist ausdrücklich verboten.

## 6. Figma-MCP-Workflow

### Verbindliche Korrekturregel für Figma-MCP-Prompts

Ein Figma-MCP-Prompt darf niemals dazu führen, dass eine bestehende HTML- oder CSS-Datei angepasst oder neues CSS angelegt wird. Das gilt auch dann, wenn die Figma-Referenz dadurch nur näherungsweise umgesetzt werden kann. Bestehende Templates, Komponenten, Layouts und ihre CSS-Abhängigkeiten bleiben unverändert und werden ausschließlich wiederverwendet.

Für die Umsetzung sind ausschließlich Bootstrap-Klassen im neuen Template zu verwenden. Zu jedem Figma-Prompt müssen eine neue Render-View in `views.py` und genau eine neue Route in `urls.py` ergänzt werden. Bestehende Views, Routen, HTML-Dateien und Verträge bleiben unverändert. Wenn das Design ohne CSS-Datei oder Änderung an fertigem Bestand nicht sinnvoll abbildbar ist, muss die Abweichung benannt und vor einer solchen Änderung beim Nutzer nachgefragt werden.

Vor jedem Figma-MCP-Call muss der Nutzer nach dem Namen der neu zu generierenden Seite gefragt werden. Der bestätigte Seitenname ist für Template-, View- und Routennamen zu verwenden; die Figma-Node-ID wird weiterhin zusätzlich zur eindeutigen Benennung angehängt.

Bei jedem Figma-Request in dieser Reihenfolge arbeiten:

1. Diese Datei lesen.
2. `git status --short` prüfen und fremde/unrelated Änderungen schützen.
3. Bestehende Django-Templates, vorhandene CSS-Dateien, Includes und JavaScript-Hooks ausschließlich lesend zur Orientierung analysieren.
4. Figma-Node per MCP laden und als Designreferenz auswerten.
5. Figma-Elemente auf vorhandene Django-Komponenten und Bootstrap-Klassen mappen; fertige Komponenten unverändert übernehmen.
6. Ein neues Seitentemplate unter `backend/editor/templates/editor/` anlegen. Keine bestehende `.html`-Datei ändern.
7. Eine neue, reine Render-Funktion in `views.py` ergänzen, ohne vorhandene View-Funktionen anzupassen.
8. Genau eine neue `path(...)`-Zeile mit eindeutigem Namen in `urls.py` ergänzen, ohne vorhandene Routen anzupassen.
9. Backend-Verträge, bestehende Formulare, bestehende URL-Namen und Session-/JSON-Strukturen unverändert lassen.
10. Änderung mit Django-Check und sinnvoller manueller/visueller Prüfung validieren.

Figma ist die visuelle Quelle, aber nicht automatisch die technische Struktur. Ein vorhandenes ähnliches Template darf als lesende Referenz dienen, darf jedoch niemals für den Figma-Prompt verändert werden. Jeder Figma-Prompt erzeugt bewusst eine neue Seite mit eigener Render-View und eigener Route.

Wenn der Figma-Entwurf neue Daten, neue Backend-Abläufe oder neue Persistenz verlangt, nicht heimlich implementieren. Dann die Frontend-Abweichung benennen und beim Nutzer Rückfrage halten oder die fehlende Backend-Erweiterung als separaten Punkt dokumentieren.

### Mindeststruktur einer neuen Figma-Seite

- Immer `{% extends "editor/base.html" %}` verwenden; Navbar, Bootstrap und globale Styles nicht erneut einbauen.
- `{% load static %}` nur verwenden, wenn die Seite statische Assets oder vorhandene Komponenten-CSS lädt.
- `title`- und `content`-Block setzen.
- `additional_css` nur für die unveränderten CSS-Dateien tatsächlich inkludierter Bestandskomponenten verwenden.
- Semantische Elemente, eindeutige Überschriftenhierarchie, Labels, `aria-*` und sinnvolle Button-Typen verwenden.
- Keine Form-Action auf eine bestehende Fach-View erfinden. Ohne ausdrücklich beauftragte Backend-Logik nur darstellende oder lokale UI-Interaktion im neuen Template implementieren.
- Für nötiges JavaScript nur das neue Template oder eine ausdrücklich neu angelegte JS-Datei verwenden; bestehende JS-Dateien nicht ändern.
- Figma-Bilder und -Icons als exakte exportierte Assets dauerhaft unter `backend/editor/static/editor/img/figma/` speichern. Temporäre MCP-URLs nicht committen und keine Ersatzgrafiken selbst zeichnen.

## 7. Design-Übertragung aus Figma

Beim Abgleich mit Figma auf diese Ebenen achten:

- Layout: Container, Grid, Spalten, Reihenfolge, responsive Verhalten.
- Komponenten: Buttons, Selects, Cards, Tags, Statusbar, Helper/Cosmo, Tabellen.
- Inhalt: sichtbare Labels, Hilfetexte, Buttontexte, Icon-Auswahl.
- Zustände: aktiv, disabled, leer, Fehler, Erfolg, Auswahlmodus.
- Interaktion: Klickziele, Formularfluss, dynamische Felder, Uploads, Bounding-Box-Auswahl.
- Responsiveness: mobile-first mit Bootstrap-Breakpoints abbilden.
- Accessibility: Labels, Fokus, `aria-*`, Kontraste, semantische Bereiche.

Figma-Maße nicht als eigenes CSS kopieren. Bevorzugte Umsetzung:

- Figma-Abstände auf Bootstrap-Utilities wie `p-*`, `m-*`, `gap-*`, `g-*` übersetzen.
- Figma-Spalten auf `container`, `container-fluid`, `row`, `col-*` übersetzen.
- Figma-Farben auf vorhandene Bootstrap-Farbklassen wie `bg-primary`, `text-body`, `text-secondary`, `text-white`, `border-secondary` und `link-*` abbilden. `tokens.css` nicht verändern.
- Figma-Buttons mit `btn`, `btn-primary`, `btn-outline-*`, `btn-lg`, `px-*` etc. bauen.
- Figma-Formulare mit `form-control`, `form-select`, `form-check`, `form-label`, `form-text` bauen.
- Figma-Cards mit `card`, `card-body`, `shadow-sm`, `border-*` bauen.
- Icons über Bootstrap Icons verwenden.

Wenn Bootstrap einen Figma-Wert nicht exakt abbilden kann, die nächstliegende Bootstrap-Klasse verwenden und die visuelle Abweichung dokumentieren. Kein eigenes CSS als Ausweichlösung schreiben.

## 8. Geschützte Backend-Bereiche

Bei Design-/Frontend-Aufgaben nicht ändern:

```text
backend/editor/models.py
backend/editor/utils.py
backend/editor/sqlParser.py
backend/editor/admin.py
backend/editor/apps.py
backend/editor/migrations/**
backend/config/**
```

`backend/editor/views.py` und `backend/editor/urls.py` sind ebenfalls geschützt. Bei einem Figma-Prompt ist ausschließlich folgende additive Änderung erlaubt und vorgeschrieben:

- in `views.py` eine neue reine Render-Funktion ergänzen,
- in `urls.py` genau eine neue `path(...)`-Zeile ergänzen.

Vorhandene Funktionen, Imports, Routen und deren Verhalten nicht ändern. Weitere Backend-Änderungen benötigen einen ausdrücklichen Auftrag des Nutzers.

Nicht beiläufig verändern:

- Session-Schlüssel und Session-Datenformate
- View-Reihenfolge und Redirects
- URL-Namen
- JSON-Import und JSON-Export
- Dateiupload- und Speicherlogik
- SQL-Parser- und Exportlogik
- Spiellogik
- Formularfeldnamen
- Template-Kontextvariablen
- `{% if %}`-/`{% for %}`-Logik, wenn sie fachliche Bedeutung hat

## 9. Geschützte URL-Namen

Diese URL-Namen sind Django-Verträge und dürfen in Templates nicht ohne Backend-Abgleich geändert werden:

```text
start
kontakt
level
upload_json
component_test
create_level
auswahl_view
create_level1
create_level2
create_level21
create_level3
create_level4
create_level41
create_level42
create_level5
create_level51
create_level6
create_level61
create_level6hint
create_level6exit
create_level6table
create_level7
create_level8
export_game
levelGrunddaten
sql_grunddaten_view
gegenstandVerwaltung
edit_item
edit_item_section
delete_item
messages_grunddaten
edit_level
save_level
delete_level
```

Ein `<a>` nicht aus rein optischen Gründen in ein Submit-Element umwandeln und umgekehrt. Navigation und Formularübermittlung sind funktionale Verträge.

## 10. Geschützte Formularfelder

Jedes vorhandene `name`-Attribut ist ein Backend-Vertrag.

Aktuell besonders relevant:

```text
json_file
level_name
levelPicture
level_greeting
max_columns
max_rows
too_many_rows_message
too_many_columns_message
too_many_rows_columns_message
wrong_password
wrong_password_new_hint
not_a_table
unknown_table
locked_table
sql_error
no_result
row_restriction
col_restriction
row_and_col_restriction
item_name
unlocked_items
requires_password
password_hint
item_passwords
success_message
show_hints
hint_attempts[]
hint_texts[]
image_x
image_y
image_width
image_height
icon_x
icon_y
icon_width
icon_height
item_type
hint_type
hint_text
hint_image
exit_success_message
next_level_id
rows_json
column_ids[]
column_types[]
next_action
```

Bei Änderungen an Formularen immer erhalten:

- `action`
- `method`
- `enctype`
- `{% csrf_token %}`
- `name`
- relevante `value`
- Hidden Inputs
- Submit-Button-Namen und Werte
- `required` nur ändern, wenn fachlich beabsichtigt

## 11. JavaScript- und DOM-Hooks

Vor jedem Template-Umbau prüfen:

```bash
rg "getElementById|querySelector|addEventListener|closest|dataset|name=|id=" backend/editor/templates/editor backend/editor/static/editor -n
```

Inline-JavaScript sitzt aktuell in:

```text
partials/levelGrunddatenForm.html
createLevel3.html
createLevel4-2.html
createLevel51.html
createLevel6hint.html
createLevel6table.html
```

Externe JS-Datei:

```text
backend/editor/static/editor/components/tableEditor/tableEditor.js
```

### Konkrete JavaScript-Verträge

- `levelGrunddatenForm.html`: `level-picture-input`, `level-picture-feedback` und die variable `submit_button_id`. Der Upload aktiviert bei `require_picture=True` erst den Submit-Button.
- `createLevel3.html`: `item-select`, `selected-tags`, `selected-tags-empty`, `unlocked-items-input`. Der Hidden Input enthält ein JSON-Array; dynamische Tags verwenden die Klassen aus `tag.css`.
- `createLevel4-2.html`: `hint-rows`, `add-hint-row`, `.hint-row`, `.remove-hint-row`; dynamische Felder müssen weiterhin `hint_attempts[]` und `hint_texts[]` heißen.
- `createLevel51.html`: Formular-Action `create_level51`, `image-area`, `level-background-image`, `selection-box`, `start-image-selection`, `start-icon-selection`, `continue-button` sowie alle `image-*`- und `icon-*`-Koordinatenfelder. Die Logik rechnet von der angezeigten Bildgröße in natürliche Bildkoordinaten um, mutiert Inline-Styles der Selection-Box und unterstützt aktuell Mausereignisse.
- `createLevel6hint.html`: `hint-type`, `hint-text-area`, `hint-image-area`, `hint-text`, `hint-image`, `hint-image-name`. Zulässige Steuerwerte sind `text`, `image` und `text_image`; daraus werden Sichtbarkeit und `required` dynamisch abgeleitet.
- `createLevel6table.html`: `table-item-form`, `rows-json`, `columns-container`, `add-column-button`, `add-row-button`, `empty-table-message`, `table-wrapper`, `data-table-head`, `data-table-body`. Zusätzlich sind die von `json_script` erzeugten IDs `saved-table-columns`, `saved-table-rows` und `table-type-options` verbindlich. Spaltenfelder heißen `column_ids[]` und `column_types[]`; beim Submit wird `rows_json` serialisiert.
- `tableEditor.js`: `column-rows`, `add-column-row`, `data-type-options`, `.table-editor__row` und `.table-editor__remove-button`. Dieses Script gehört nur zur derzeit ungenutzten `tableEditor.html`-Komponente.

IDs, Array-Feldnamen, `data-*`-Attribute, JSON-Script-IDs, steuernde Select-Werte und die von JavaScript erwartete DOM-Hierarchie sind funktionale Verträge. In Figma-Aufgaben werden diese bestehenden Dateien ohnehin nicht verändert. Bei ausdrücklich beauftragten Nicht-Figma-Änderungen alle betroffenen Skripte und Serververträge gemeinsam prüfen.

## 12. Bootstrap-only-Frontend

Bootstrap ist für alle neuen Frontend-Elemente verbindlich. Die vorhandenen CSS-Dateien und die Styles fertiger Komponenten und Layouts sind historischer Bestand und dürfen nicht als Erweiterungspunkt verwendet werden.

Strikte Verbote bei jeder Figma-/Frontend-Aufgabe:

- Keine neue `.css`-Datei erstellen.
- Keine bestehende `.css`-Datei ändern, löschen oder umbenennen.
- Keine `<style>`-Blöcke und keine `style="..."`-Attribute in Templates schreiben.
- Keine CSS-Variablen in `tokens.css` oder einer anderen Datei ergänzen oder ändern.
- Keine eigenen Utility-Klassen wie `.contact-page`, `.flex-center` oder `.mt-20` anlegen.
- Über `{% block additional_css %}` ausschließlich bereits vorhandene Komponenten-CSS laden, wenn die zugehörige Komponente im neuen Template unverändert inkludiert wird. Keine Seiten-CSS oder unbenutzte Abhängigkeit ergänzen.
- Keine Bootstrap-Klassen in fertigen Komponenten oder Layouts ändern, nur um ein neues Figma-Mockup anzupassen.
- Keine fertigen Komponenten oder Layouts aus optischen Gründen duplizieren, umbauen oder überschreiben.

Wenn eine Figma-Ansicht bereits durch vorhandenes projektspezifisches CSS oder eine fertige Komponente funktioniert, dieses Styling nur unangetastet wiederverwenden. Neue Anpassungen erfolgen ausschließlich in neuem HTML-Markup durch Bootstrap-Klassen.

Einige geschützte Legacy-Templates besitzen bereits `style="..."`-Attribute (`sqlGrunddatenForm`, `createLevel4-1`, `createLevel6exit`, `createLevel6hint`, `createLevel8`). Das ist Bestand und keine Vorlage für neue Seiten.

Direkt mit Bootstrap lösen:

| Zweck | Bootstrap |
|---|---|
| Grid/Layout | `container`, `container-fluid`, `row`, `col-*` |
| Flexbox | `d-flex`, `flex-*`, `justify-content-*`, `align-items-*` |
| Abstände | `m-*`, `p-*`, `gap-*`, `g-*` |
| Typografie | `h*`, `display-*`, `fs-*`, `fw-*`, `text-*` |
| Buttons | `btn`, `btn-primary`, `btn-outline-*`, `btn-lg`, `btn-sm` |
| Formulare | `form-control`, `form-select`, `form-check`, `form-label`, `form-text` |
| Cards | `card`, `card-body`, `card-title`, `shadow-sm` |
| Alerts | `alert`, `alert-*` |
| Tabellen | `table`, `table-bordered`, `table-responsive`, `align-middle` |
| Sichtbarkeit | `d-none`, `d-*-block`, `visually-hidden` |
| Position | `position-*`, `top-*`, `start-*`, `end-*` |

Für Figma-Maße, die Bootstrap nicht exakt anbietet, wird die nächstliegende Bootstrap-Klasse gewählt. Eine kleine visuelle Abweichung ist zulässig und muss gegenüber dem Nutzer benannt werden; eigenes CSS ist keine Ausweichlösung.

Eigene Klassen sind nur erlaubt, wenn sie bereits im bestehenden Markup und Legacy-CSS vorhanden sind. Für neue Markup-Strukturen bevorzugt Klassenkombinationen aus Bootstrap verwenden, zum Beispiel `container d-flex flex-column gap-4 mx-auto`, statt eine neue semantische CSS-Klasse zu erfinden.

## 13. Tokens und Branding

`tokens.css` enthält bestehende Projektwerte, ist aber schreibgeschützt für neue Frontend-Aufgaben.

Aktuelle Basis:

```text
--color-primary: #6f42c1
--color-primary-soft: #ebe5fc
--color-text: #212529
--color-text-muted: #68717a
--color-border: #d9d9d9
--color-background: #ffffff
--content-max-width: 980px
--navbar-height: 56px
```

Bootstrap-Variablen werden dort bereits angepasst:

```text
--bs-primary
--bs-primary-rgb
--bs-body-color
--bs-body-bg
--bs-body-font-family
--bs-border-color
--bs-secondary-color
--bs-link-color
--bs-link-hover-color
--bs-focus-ring-color
```

Wenn Figma neue Farben oder Abstände vorgibt, auf die vorhandenen Bootstrap-Utilities und Bootstrap-Variablen im unveränderten Bestand abbilden. Keine neuen Tokens und keine Seitencss ergänzen.

## 14. Seitenspezifische Hinweise

### Tatsächlicher Seiten- und Assistentenfluss

```text
start.html
  -> JSON-Upload

createLevel.html
  -> createLevel1.html
  -> createLevel2.html
  -> createLevel2-1.html
  -> createLevel3.html
  -> createLevel4.html
     -> ohne Passwort: createLevel5.html
     -> mit Passwort: createLevel4-1.html
        -> ohne Fehlversuchhinweise: createLevel5.html
        -> mit Fehlversuchhinweisen: createLevel4-2.html
  -> createLevel5.html
  -> createLevel51.html
  -> createLevel6.html
  -> createLevel61.html
     -> createLevel6table.html | createLevel6hint.html | createLevel6exit.html
  -> createLevel7.html
  -> createLevel8.html
```

Verwaltungsseiten:

```text
auswahl.html
level.html
levelGrunddaten.html
sqlGrunddaten.html
messagesGrunddaten.html
gegenstandVerwaltung.html
editItem.html
contact.html
test.html
```

Die übrigen 27 Root-Templates erweitern `base.html`. Komponenten und Partials erweitern `base.html` nicht selbst.

`createLevel51.html` und die dazugehörige vorhandene CSS-Datei sind besonders sensibel. Diese Seite enthält die Bounding-Box-Auswahl für Bild- und Iconbereiche. `image-area`, `selection-box`, Positionsinputs und Mauslogik nicht verändern, sofern die Aufgabe nicht ausdrücklich fachlich darauf zielt. Die aktuelle Auswahl unterstützt `mousedown`, `mousemove` und `mouseup`, aber keine Touch- oder Pointer-Events. Neue CSS-Regeln sind verboten.

`createLevel6table.html` enthält eine umfangreiche Inline-Tabellenlogik mit dynamischen Spalten, Zeilen, JSON-Skripten und Hidden Input `rows_json`. Hier sind DOM-Hooks wichtiger als optische Klassen.

`components/tableEditor/tableEditor.html` ist nicht die Implementierung von `createLevel6table.html`. Die Komponente ist derzeit ungenutzt; ihr externes Script wird von keiner Seite geladen.

`partials/levelGrunddatenForm.html`, `partials/sqlGrunddatenForm.html` und `partials/messagesForm.html` werden mehrfach verwendet. Änderungen daran wirken auf geführte Erstellung und Bearbeitungsseiten.

`partials/itemSummary.html` wird sowohl in `createLevel7.html` als auch in `editItem.html` verwendet und wechselt seine Ziele abhängig von `item_id`.

`auswahl.html`, `level.html`, `gegenstandVerwaltung.html` und `editItem.html` sind Navigations- und Verwaltungsseiten. Links, Formulare und Delete/Save-Flows erhalten.

`test.html` ist eine Komponenten-Testseite. Vor Löschung oder Umbau prüfen, ob sie noch manuell für Komponentenprüfung genutzt wird.

## 15. Vorgehen pro Änderung

Vor der Änderung:

```bash
git status --short
rg --files backend/editor/templates/editor -g '*.html'
rg --files backend/editor/static/editor
rg "additional_css|include|static 'editor/|<script|name=|id=" backend/editor/templates/editor -n
```

Dann:

1. Ähnliche bestehende Templates und passende Includes ausschließlich lesend analysieren.
2. Vorhandene CSS-Dateien bei Bedarf nur lesen; sie dürfen nicht geändert werden.
3. JavaScript-Hooks identifizieren.
4. Figma-Node laden und Zielbild erfassen.
5. Mapping notieren: Figma-Element -> vorhandenes Template/Komponente/Bootstrap.
6. Ein neues Seitentemplate anlegen.
7. Eine neue Render-View ergänzen.
8. Genau eine neue URL-Route ergänzen.
9. Prüfen, dass keine bestehende `.html`-Datei verändert wurde.
10. Prüfen, dass keine CSS-Datei verändert oder angelegt wurde.
11. Keine fremden Dateien oder unbezogene Änderungen anfassen.

Nach der Änderung:

```bash
git diff --check
```

```bash
cd backend
python manage.py check
```

Alle Templates syntaktisch laden:

```bash
cd backend
python manage.py shell -c "from pathlib import Path; from django.template.loader import get_template; root = Path('editor/templates'); [get_template(str(path.relative_to(root))) for path in root.rglob('*.html')]; print('Templates: OK')"
```

Tests:

```bash
cd backend
python manage.py test
```

Bei Figma-Aufgaben zusätzlich im Diff prüfen:

- Unter den bereits vorhandenen `.html`-Dateien gibt es keine Änderung.
- Genau ein neues Seitentemplate wurde angelegt.
- `views.py` enthält nur die neue additive Render-Funktion.
- `urls.py` enthält nur eine neue einzeilige `path(...)`-Definition.
- Keine `.css`-Datei ist neu, geändert, gelöscht oder umbenannt.
- Das neue Template enthält weder `<style>` noch `style="..."`.
- Der neue URL-Name lässt sich mit Django `reverse()` auflösen.

Wenn visuelle Änderungen aus Figma umgesetzt wurden, relevante Ansichten mindestens in Desktop- und Mobilbreite prüfen. Wenn ein Devserver nötig ist, lokal über `python manage.py runserver` starten.

## 16. Definition of Done

Eine Figma-Umsetzung ist fertig, wenn:

- das betroffene Figma-Zielbild erkennbar umgesetzt ist,
- ein neues Seitentemplate angelegt wurde,
- keine bereits vorhandene `.html`-Datei verändert wurde,
- eine neue reine Render-Funktion in `views.py` ergänzt wurde,
- genau eine neue, eindeutig benannte `path(...)`-Zeile in `urls.py` ergänzt wurde,
- vorhandene Django-Struktur und Komponenten weiterverwendet wurden,
- fertige Komponenten und Layouts unverändert wiederverwendet wurden,
- Bootstrap Layout, Spacing, Typografie, Formulare, Komponenten und Responsive-Verhalten trägt,
- keine `.css`-Datei neu erstellt, geändert, gelöscht oder umbenannt wurde,
- keine `<style>`-Blöcke, `style="..."`-Attribute oder neuen CSS-Variablen vorhanden sind,
- keine geschützten Backend-Verträge verändert wurden,
- Formularfeldnamen, URL-Namen und JS-Hooks erhalten oder konsistent angepasst wurden,
- mobile und Desktop-Layout nicht brechen,
- `python manage.py check` erfolgreich läuft,
- relevante manuelle Flows weiterhin funktionieren.

Funktionalität hat Vorrang vor visueller Exaktheit. Wenn Bootstrap einen Figma-Wert nicht exakt abbildet, bleibt die Umsetzung bei der nächstliegenden Bootstrap-Lösung und dokumentiert die Abweichung, statt CSS nachzurüsten.
