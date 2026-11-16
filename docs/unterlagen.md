# Weitere Unterlagen und historische Auswertungen

Der Einstieg für neue Leser\*innen ist die [Startseite](README.md). Für die aktuelle
Struktur siehe [Architektur erklärt](architektur.md).

Der produktive Editor liegt in `backend/editor`. Der geführte Ablauf und die
Bearbeitungsseiten sind über `backend/editor/urls.py` erreichbar. Die wichtigen
URL-, Formular-, Session- und Exportverträge stehen in
[`editor-vertraege.md`](editor-vertraege.md).

## Weitere Projektunterlagen

- `grundlagen/` und `mockups/` enthalten Grundlagen und Entwurfsunterlagen.
- `uml/` beschreibt die aktuelle Struktur und die Editorabläufe.
- `evaluation/` enthält Messwerkzeuge und historische Auswertungen. Diese
  Messwerte ersetzen keine Django-Tests oder manuelle Browserprüfung.
- [`pylint-report.md`](pylint-report.md) dokumentiert den Stand vom 26. August
  2026 und ist keine aktuelle Qualitätsmessung.

## Vorschau- und Testseiten

Die Routen für `auswahl3`, Agent-, Plugin-, Figma- und SDD-Ansichten in
`backend/editor/view_handlers/testingScratchView.py` sind separate Vorschauen
und Evaluationsstände. Auch `/components/` ist eine Komponenten-Testseite.
Diese Seiten bleiben erreichbar; sie sind nicht Teil des geführten
Editorablaufs. Die historischen `*Old.html`-Templates werden von
`docs/evaluation/crr.py` ausgewertet und bleiben deshalb im Repository.
