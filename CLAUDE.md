# SQL Spell Quest Editor – Frontend-Refactoring-Kontext

## Zweck dieser Datei

Diese Datei dient als verbindlicher Arbeitskontext für die schrittweise Überarbeitung des Frontends im Projekt **SQL Spell Quest Editor**.

Das zentrale Ziel lautet:

> Bestehende eigene CSS-Klassen sollen, soweit technisch und gestalterisch sinnvoll, durch Bootstrap-5-Klassen ersetzt werden, ohne die Backend-Logik, Formulardaten, Django-Abläufe oder Spiellogik zu verändern.

Die Anwendung verwendet derzeit Bootstrap 5.3.3, Bootstrap Icons und zahlreiche eigene Stylesheets. Das Refactoring soll diesen Mix systematisch reduzieren. Eigenes CSS bleibt nur dort bestehen, wo Bootstrap die benötigte Darstellung oder Interaktion nicht sinnvoll abbilden kann.

---

## 1. Verbindlicher Arbeitsbereich

### Erlaubte Änderungen

Primär dürfen folgende Dateien bearbeitet werden:

```text
backend/editor/templates/editor/**/*.html
backend/editor/static/editor/**/*.css
```

Frontendbezogenes JavaScript befindet sich momentan teilweise direkt in den Django-Templates. Dieses darf nur angepasst werden, wenn eine HTML- oder Klassenänderung dies zwingend erforderlich macht und das bestehende Verhalten unverändert bleibt.

### Nicht erlaubte Änderungen

Die folgenden Bereiche dürfen im Rahmen des Bootstrap-Refactorings grundsätzlich nicht verändert werden:

```text
backend/editor/views.py
backend/editor/urls.py
backend/editor/models.py
backend/editor/utils.py
backend/editor/sqlParser.py
backend/editor/admin.py
backend/editor/apps.py
backend/editor/migrations/**
backend/config/**
```

Ebenfalls nicht zu verändern sind:

- Session-Strukturen und Session-Schlüssel
- Django-View-Abläufe
- URL-Namen und Weiterleitungen
- Spiellogik
- JSON-Strukturen
- Exportlogik
- Upload- und Dateispeicherlogik
- Formularverarbeitung im Backend
- Namen von POST-Feldern
- Template-Kontextvariablen
- Bedingungen und Schleifen in Django-Templates, sofern sie nicht rein darstellerisch umgebaut werden

Eine Backendänderung darf nicht nebenbei vorgenommen werden, auch wenn sie sinnvoll erscheint. Solche Probleme sollen lediglich dokumentiert werden.

---

## 2. Projektstruktur

Der für das Refactoring relevante Teil des Projekts ist wie folgt aufgebaut:

```text
sql-quest-editor/
├── backend/
│   ├── config/
│   ├── editor/
│   │   ├── static/editor/
│   │   │   ├── components/
│   │   │   │   ├── button/
│   │   │   │   ├── chatBox/
│   │   │   │   ├── dropdown/
│   │   │   │   ├── navbar/
│   │   │   │   ├── statusBar/
│   │   │   │   ├── tableItem/
│   │   │   │   └── tag/
│   │   │   └── css/
│   │   │       ├── pages/
│   │   │       ├── base.css
│   │   │       ├── forms.css
│   │   │       ├── layout.css
│   │   │       ├── tokens.css
│   │   │       ├── createLevelShared.css
│   │   │       └── zahlreiche seitenspezifische CSS-Dateien
│   │   ├── templates/editor/
│   │   │   ├── components/
│   │   │   ├── base.html
│   │   │   ├── start.html
│   │   │   ├── auswahl.html
│   │   │   ├── level.html
│   │   │   └── createLevel*.html
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── weitere Backend-Dateien
│   └── manage.py
└── docs/
```

Zum Zeitpunkt der Analyse enthält der Frontendbereich:

- **28 HTML-Templates**
- **36 CSS-Dateien**
- ungefähr **2.700 Zeilen eigenes CSS**

---

## 3. Aktuelle Frontend-Architektur

### Globale Basis

`backend/editor/templates/editor/base.html` lädt:

```text
Bootstrap 5.3.3
Bootstrap Icons 1.11.3
editor/css/tokens.css
editor/css/base.css
editor/css/layout.css
editor/css/forms.css
editor/components/navbar/navbar.css
```

Weitere Stylesheets werden über den Block `additional_css` seitenweise eingebunden.

Die meisten Seiten erweitern `base.html`. Dadurch sollen globale Layout- oder Typografieentscheidungen möglichst zentral getroffen werden.

### Wiederverwendbare Template-Komponenten

Aktuell existieren Komponenten für:

- Navbar
- Statusbar
- Buttons
- Chatboxen
- Dropdowns
- Tags
- Tabellen-Items

Diese Komponenten sollen erhalten bleiben, sofern sie Wiederverwendung oder Django-Template-Logik kapseln. Eine Komponente muss nicht entfernt werden, nur weil ihre Darstellung künftig fast vollständig aus Bootstrap-Klassen besteht.

### Seiten des Level-Assistenten

Der geführte Level-Erstellungsprozess ist auf viele Templates und Stylesheets verteilt:

```text
createLevel.html
createLevel1.html
createLevel2.html
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
```

Nahezu alle diese Seiten verwenden zusätzlich `createLevelShared.css`.

---

## 4. Bekannte strukturelle Auffälligkeiten

### Doppelte oder möglicherweise veraltete Stylesheet-Strukturen

Neben den aktiv eingebundenen Stylesheets existieren derzeit nicht referenzierte Dateien:

```text
editor/css/app.css
editor/css/utilities.css
editor/css/pages/start.css
editor/css/pages/createLevel.css
editor/css/pages/levelPreview.css
```

Diese Dateien dürfen nicht ungeprüft gelöscht werden. Vor einer Entfernung ist zu prüfen:

1. ob sie dynamisch oder außerhalb der untersuchten Templates verwendet werden,
2. ob sie Überreste eines früheren Refactorings sind,
3. ob ihre Regeln bereits in anderen Dateien dupliziert wurden.

### Unterschiedliche Groß-/Kleinschreibung

Im Projekt kommen unter anderem folgende Varianten vor:

```text
components/statusBar/statusBar.html
components/statusbar/statusbar.html

components/chatBox/chatBox.html
components/chatbox/chatbox.html
```

Auf standardmäßig case-insensitiven Dateisystemen kann dies unbemerkt funktionieren, auf Linux oder in CI jedoch fehlschlagen. Beim Refactoring soll eine einheitliche Schreibweise verwendet werden. Vor einer Pfadänderung müssen sämtliche Referenzen gemeinsam aktualisiert werden.

### Sehr große seitenspezifische Stylesheets

Besonders umfangreich sind unter anderem:

```text
createLevel6table.css
createLevel51.css
createLevel6.css
createLevel4-2.css
createLevel5.css
createLevel7.css
createLevel1.css
```

Diese Dateien besitzen hohes Refactoring-Potenzial, sollten aber erst nach den globalen Grundlagen bearbeitet werden.

### Inline-JavaScript in Templates

Frontend-Interaktionen befinden sich unter anderem in:

```text
createLevel1.html
createLevel3.html
createLevel4-2.html
createLevel51.html
createLevel6hint.html
createLevel6table.html
```

Das JavaScript greift teilweise über IDs oder Klassen auf DOM-Elemente zu. Beim Austausch eigener Klassen dürfen deshalb keine Selektoren entfernt oder umbenannt werden, ohne alle betroffenen Skripte zu prüfen.

---

## 5. Unveränderliche Frontend-Verträge

Die visuelle Struktur darf umgebaut werden. Die folgenden Eigenschaften gelten jedoch als funktionale Schnittstellen und müssen erhalten bleiben.

### Formulare

Nicht verändern:

- `action`
- `method`
- `enctype`
- `{% csrf_token %}`
- Namen von Inputs über `name="..."`
- notwendige `value`-Werte
- Hidden Inputs
- Submit-Button-Verhalten
- Button-Namen und Button-Werte, die im Backend ausgewertet werden

Beispiele für geschützte Feldnamen sind:

```text
level_name
levelPicture
level_greeting
max_columns
max_rows
too_many_rows_message
too_many_columns_message
too_many_rows_columns_message
item_name
unlocked_items
password_hint
item_passwords
success_message
show_hints
column_ids[]
column_types[]
next_action
json_file
```

Diese Liste ist nicht vollständig. Grundsätzlich ist jedes vorhandene `name`-Attribut als Backend-Vertrag zu behandeln.

### Django-Template-Logik

Erhalten bleiben müssen insbesondere:

```django
{% extends ... %}
{% load static %}
{% csrf_token %}
{% url ... %}
{% include ... %}
{% if ... %}
{% for ... %}
{{ variable }}
```

Template-Ausdrücke dürfen beim Umbau der HTML-Struktur verschoben werden, wenn ihr semantischer und funktionaler Zusammenhang erhalten bleibt.

### IDs und JavaScript-Hooks

IDs dürfen nur geändert werden, wenn alle zugehörigen JavaScript-Zugriffe gleichzeitig und verhaltensneutral angepasst werden.

Beispiele für vorhandene Hooks:

```text
level-picture-input
level-picture-feedback
item-select
selected-tags
unlocked-items-input
hint-rows
add-hint-row
image-area
selection-box
hint-type
hint-text-area
hint-image-area
hint-image
hint-image-name
column-rows
add-column-row
```

### Navigation

Nicht verändern:

- Django-URL-Namen
- Zielseiten der Vor- und Zurück-Navigation
- Reihenfolge des Assistenten
- Submit- gegenüber Link-Verhalten

Ein `<a>` darf nicht allein aus optischen Gründen in einen `<button>` umgewandelt werden, wenn dadurch die Navigation oder Formularübermittlung verändert wird.

---

## 6. Refactoring-Zielbild

### Grundsatz

Bootstrap soll für Standardlayout und Standardkomponenten zuständig sein.

Eigenes CSS soll nur noch verwendet werden für:

- projektspezifische Farben oder Design-Tokens
- spezielle Illustrationen und Bildpositionierung
- komplexe Auswahlflächen oder Bounding-Box-Funktionen
- nicht durch Bootstrap abbildbare Komponenten
- wenige konsistente Designanpassungen
- Zustände, die Bootstrap nicht semantisch ausdrücken kann

### Bootstrap zuerst

Vor jeder neuen oder verbleibenden eigenen CSS-Regel ist zu prüfen, ob dieselbe Wirkung mit Bootstrap erreichbar ist.

Typische Zuordnung:

| Eigener CSS-Zweck | Bevorzugte Bootstrap-Lösung |
|---|---|
| `display: flex` | `d-flex` |
| horizontale/vertikale Ausrichtung | `justify-content-*`, `align-items-*` |
| Grid-Spalten | `container`, `row`, `col-*` |
| Abstände | `m-*`, `p-*`, `gap-*` |
| Breite/Höhe | `w-*`, `h-*`, `min-vh-100` |
| Textausrichtung | `text-start`, `text-center`, `text-end` |
| Schriftgewicht | `fw-*` |
| Schriftgröße | `fs-*` |
| Farben | `text-*`, `bg-*` |
| Rahmen | `border`, `border-*` |
| Rundungen | `rounded`, `rounded-*`, `rounded-pill` |
| Schatten | `shadow`, `shadow-sm`, `shadow-lg` |
| Sichtbarkeit | `d-none`, `d-*-block`, `visually-hidden` |
| Positionierung | `position-relative`, `position-absolute`, `top-*`, `start-*` |
| Buttons | `btn`, `btn-primary`, `btn-outline-*`, `btn-link` |
| Eingaben | `form-control`, `form-select`, `form-check` |
| Karten | `card`, `card-body`, `card-title` |
| Hinweise | `alert`, `text-muted`, `form-text`, `invalid-feedback` |
| Navigation | `navbar`, `nav`, `nav-link` |
| Gruppen | `btn-group`, `input-group`, `list-group` |

Eigene Klassen dürfen weiterhin als semantische oder JavaScript-Hooks bestehen, auch wenn sie keine oder nur wenige CSS-Regeln besitzen.

---

## 7. Regeln für eigenes CSS

### Erlaubt

Eigene CSS-Regeln sind akzeptabel, wenn mindestens einer der folgenden Punkte zutrifft:

1. Bootstrap besitzt keine passende Utility oder Komponente.
2. Die Regel bildet ein projektspezifisches Designmerkmal ab.
3. Mehr als fünf bis sechs Bootstrap-Utilities würden dasselbe Element unlesbar machen und eine kleine semantische Klasse ist klarer.
4. Die Regel wird an vielen Stellen konsistent wiederverwendet.
5. Die Regel steuert eine komplexe Interaktion, etwa die grafische Auswahl einer Bounding Box.
6. Eine Bootstrap-Variable oder eine kleine zentrale Überschreibung ist die sauberere Lösung.

### Nicht erwünscht

Nicht als eigenes CSS behalten oder neu anlegen:

```css
display: flex;
justify-content: center;
align-items: center;
margin-top: ...;
padding: ...;
text-align: center;
font-weight: 600;
border-radius: ...;
width: 100%;
```

sofern die Wirkung direkt und verständlich über Bootstrap-Utilities erreichbar ist.

### Keine Utility-Kopie

Dateien wie `utilities.css` sollen nicht Bootstrap nachbauen. Eigene Hilfsklassen wie `.mt-20`, `.flex-center`, `.rounded-large` oder `.full-width` sind zu vermeiden, wenn Bootstrap bereits eine gleichwertige Utility anbietet.

### Design-Tokens

`tokens.css` kann als zentrale Quelle für projektspezifische Werte bestehen bleiben, beispielsweise:

```css
:root {
  --sqe-primary: ...;
  --sqe-surface: ...;
  --sqe-text: ...;
}
```

Dabei sollen möglichst Bootstrap-CSS-Variablen überschrieben oder ergänzt werden, statt dieselben Eigenschaften seitenweise zu wiederholen.

---

## 8. Empfohlene Reihenfolge des Refactorings

### Phase 1: Sicherheitsnetz und Inventar

Für jede Seite dokumentieren:

- eingebundene CSS-Dateien
- verwendete Komponenten
- Formulare und Feldnamen
- IDs und JavaScript-Hooks
- Vor-/Zurück-Navigation
- visuell besondere Bereiche
- responsive Zustände

Vor jeder Änderung sollte die aktuelle Ansicht mindestens für Mobilgerät und Desktop festgehalten werden.

### Phase 2: Globale Grundlagen

Zuerst prüfen und bereinigen:

```text
base.html
tokens.css
base.css
layout.css
forms.css
navbar.html
navbar.css
```

Ziele:

- globale Standardabstände reduzieren
- allgemeine Formularregeln durch Bootstrap ersetzen
- Seitencontainer vereinheitlichen
- Navbar auf Bootstrap-Struktur ausrichten
- doppelte globale Regeln entfernen
- Bootstrap-kompatible Design-Tokens definieren

### Phase 3: Kleine Komponenten

Danach bearbeiten:

```text
button
tag
dropdown
chatBox
statusBar
tableItem
```

Ziel ist, dass Komponenten hauptsächlich Bootstrap-Markup verwenden und nur projektspezifische Reststyles behalten.

### Phase 4: Einfache Seiten

Empfohlene Reihenfolge:

```text
start.html
auswahl.html
createLevel.html
createLevel2.html
createLevel8.html
level.html
```

### Phase 5: Level-Assistent

Anschließend die Seiten schrittweise bearbeiten:

```text
createLevel1
createLevel3
createLevel4
createLevel4-1
createLevel4-2
createLevel5
createLevel6
createLevel61
createLevel6exit
createLevel6hint
createLevel6table
createLevel7
```

### Phase 6: Spezialseite mit Bildauswahl

`createLevel51.html` und `createLevel51.css` zuletzt bearbeiten.

Diese Seite enthält eine benutzerdefinierte grafische Auswahlfunktion. Positionierung, Maße und JavaScript-Verhalten dürfen nicht durch eine aggressive Utility-Umstellung beschädigt werden.

### Phase 7: Bereinigung

Erst nach erfolgreicher Umstellung:

- nicht mehr verwendete Selektoren entfernen
- leere CSS-Dateien entfernen
- doppelte Regeln zusammenführen
- nicht referenzierte Stylesheets prüfen
- Pfadschreibweisen vereinheitlichen
- veraltete Dateien dokumentiert löschen

---

## 9. Vorgehen pro Datei

Bei jeder HTML-/CSS-Kombination ist folgender Ablauf einzuhalten.

### 1. Funktionale Schnittstellen identifizieren

Vor dem Umbau notieren:

- Formularaktion
- Input-Namen
- IDs
- Django-Ausdrücke
- Include-Parameter
- JavaScript-Selektoren
- Navigationsziele

### 2. CSS klassifizieren

Jede Regel einer Kategorie zuordnen:

- durch Bootstrap ersetzbar
- projektspezifisch und erforderlich
- doppelt
- veraltet
- JavaScript- oder Zustands-Hook
- responsive Sonderregel

### 3. HTML auf Bootstrap umstellen

Bevorzugt Bootstrap verwenden für:

- Grid
- Flexbox
- Abstände
- Typografie
- Buttons
- Formulare
- Karten
- Hinweise
- responsive Sichtbarkeit

### 4. Rest-CSS reduzieren

Nur Regeln behalten, die nachweislich noch benötigt werden.

### 5. Selektoren prüfen

Nach Änderungen suchen nach:

```text
entfernten Klassennamen
geänderten IDs
nicht mehr verwendeten CSS-Selektoren
JavaScript-Verweisen auf alte DOM-Strukturen
```

### 6. Seite testen

Mindestens prüfen:

- Seite lädt ohne Templatefehler.
- Vor- und Zurück-Navigation funktioniert.
- Formular wird korrekt übermittelt.
- Bereits gespeicherte Werte werden angezeigt.
- Dynamische Felder funktionieren.
- Uploadfelder funktionieren.
- Responsive Layouts brechen nicht.
- Fokus- und Tastaturbedienung bleiben möglich.

---

## 10. Responsive Design

Das bestehende Projekt nutzt bereits Bootstrap-Breakpoints wie:

```text
col-12
col-md-4
col-md-8
```

Diese Strategie soll beibehalten werden.

Grundregeln:

- Mobile-first arbeiten.
- Keine festen Seitenbreiten für Standardformulare.
- `container` oder `container-fluid` bewusst wählen.
- Spalten auf kleinen Displays stapeln.
- Große horizontale Abstände nicht auf Mobilgeräte übertragen.
- Buttons auf kleinen Displays bei Bedarf mit `w-100` darstellen.
- Bilder mit `img-fluid` absichern.
- Tabellen oder breite dynamische Inhalte mit `table-responsive` beziehungsweise kontrolliertem Overflow versehen.

---

## 11. Barrierefreiheit und Semantik

Das Refactoring darf die Zugänglichkeit nicht verschlechtern.

Beibehalten oder verbessern:

- korrekt verknüpfte `<label for="...">`
- eindeutige IDs
- passende Button-Typen
- semantische Bereiche wie `main`, `nav`, `aside`, `section`
- Alternativtexte für Bilder
- `aria-label` nur dort, wo sichtbarer Text fehlt
- sichtbare Fokuszustände
- ausreichende Kontraste
- Fehlermeldungen in der Nähe des jeweiligen Feldes
- keine rein farbliche Zustandskommunikation

Bootstrap-Klassen ersetzen keine korrekte HTML-Semantik.

---

## 12. Qualitätskriterien

Eine Seite gilt als erfolgreich refactort, wenn alle folgenden Punkte erfüllt sind:

- Die Backenddateien wurden nicht verändert.
- Alle bisherigen Django-Template-Variablen funktionieren weiterhin.
- Alle Formularfeldnamen sind unverändert.
- URL-Namen und Navigationsziele sind unverändert.
- JavaScript-Interaktionen funktionieren weiterhin.
- Standardlayout wird überwiegend mit Bootstrap umgesetzt.
- Das seitenspezifische CSS wurde deutlich reduziert.
- Verbleibendes CSS besitzt einen klaren projektspezifischen Zweck.
- Mobile und Desktop-Ansicht funktionieren.
- Es gibt keine unnötigen Inline-Styles.
- Es wurden keine Bootstrap-Utilities als eigene Klassen nachgebaut.
- Entfernte CSS-Regeln werden nicht mehr referenziert.
- Die Seite bleibt optisch konsistent mit dem restlichen Assistenten.

---

## 13. Definition of Done für das Gesamtprojekt

Das gesamte Frontend-Refactoring ist abgeschlossen, wenn:

1. alle produktiv verwendeten HTML-Templates geprüft wurden,
2. alle produktiv verwendeten CSS-Dateien geprüft wurden,
3. Standardlayout, Abstände, Typografie, Buttons und Formulare überwiegend Bootstrap verwenden,
4. eigenes CSS auf projektspezifische Gestaltung reduziert wurde,
5. ungenutzte CSS-Dateien und Selektoren nachweislich entfernt wurden,
6. Komponenten konsistente Benennungen und Pfade verwenden,
7. der komplette Level-Erstellungsprozess weiterhin funktioniert,
8. Upload, Export und dynamische Frontend-Funktionen unverändert arbeiten,
9. keine Backend- oder Spiellogik verändert wurde,
10. jede Refactoring-Etappe klein genug für einen nachvollziehbaren Review oder Commit war.

---

## 14. Arbeitsanweisung für zukünftige Änderungen

Bei jeder neuen Aufgabe in diesem Projekt gilt:

> Analysiere zuerst das betroffene Template, sein Stylesheet, seine Includes, seine Formulare und seine JavaScript-Hooks. Ersetze anschließend ausschließlich darstellerische eigene CSS-Regeln durch Bootstrap-5-Klassen. Verändere keine Backenddateien, POST-Feldnamen, URL-Namen, Sessionwerte, Django-Logik oder Spiellogik. Behalte eigenes CSS nur für projektspezifische oder mit Bootstrap nicht sinnvoll umsetzbare Gestaltung. Arbeite pro Seite oder Komponente in kleinen, überprüfbaren Schritten und nenne nach jeder Änderung, welches CSS entfernt beziehungsweise bewusst beibehalten wurde.

---

## 15. Wichtige Priorität

Funktionalität hat Vorrang vor maximaler CSS-Reduktion.

Eine komplexe, funktionierende eigene Regel soll nicht erzwungen durch eine schwer verständliche Kombination aus Bootstrap-Klassen ersetzt werden. Das Ziel ist kein Frontend ohne eigenes CSS, sondern ein Frontend, in dem Bootstrap konsequent für seine vorgesehenen Aufgaben eingesetzt wird und eigenes CSS nur noch einen klaren Mehrwert besitzt.
