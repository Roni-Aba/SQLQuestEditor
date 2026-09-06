---
name: figma-sdd
description: "Liest einen Figma-Node, analysiert lokale Django-Bausteine und erstellt ein GitHub-Issue im Repository Roni-Aba/SQLQuestEditor. Verwenden für Figma-zu-GitHub-Workitem; nicht für Implementierung."
---

# Figma zu GitHub-Workitem

Lies den Figma-Node als Designquelle, ermittle die tatsächlich passenden lokalen
Django-Templates und -Komponenten und erstelle daraus ein klar abgegrenztes
GitHub-Workitem. Figma beschreibt die Oberfläche, aber keine erfundene Fachlogik.

## Geltungsbereich

- Das Ergebnis ist genau ein GitHub-Issue im festen Repository
  [`Roni-Aba/SQLQuestEditor`](https://github.com/Roni-Aba/SQLQuestEditor).
- Verwende immer GitHub und das Repository `owner=Roni-Aba`, `repo=SQLQuestEditor`.
  Andere Repository-Ziele sind nicht zulässig.
- Erstelle keine Spec-Kit-Artefakte, lokalen SDD-Dateien, Unteraufgaben oder Code.
- Dieser Skill ändert weder Figma noch das lokale Projekt. Eine spätere Implementierung
  ist ein separater, ausdrücklicher Auftrag.

## Eingang und Preflight

Vor dem ersten Figma-MCP-Aufruf muss der Nutzer den semantischen Namen der neu zu
generierenden Seite bestätigt haben. Fordere außerdem einen Figma-Frame- oder Node-Link
an, falls er nicht vorliegt.

1. Lies `AGENTS.md`, prüfe `git status --short` und schütze alle fremden Änderungen.
2. Analysiere den lokalen Bestand ausschließlich lesend. Prüfe mindestens die passenden
   Dateien unter `backend/editor/templates/editor/`, die Komponenten unter
   `backend/editor/templates/editor/components/`, die verwendeten `{% include %}`-
   Beziehungen, CSS-Abhängigkeiten und die für den Node relevanten JavaScript-Hooks.
   Öffne die tatsächlich in Frage kommenden Dateien und halte die konkrete
   Wiederverwendung fest; nenne keine Komponente nur aufgrund ihres Namens.
3. Lade einen verfügbaren GitHub-Connector oder eine GitHub-Skill. Das Ziel ist fest
   `Roni-Aba/SQLQuestEditor`; frage nicht nach einem anderen Repository und leite keine
   Zielwerte aus dem lokalen Git-Remote ab.
4. Protokolliere jede Arbeitshandlung mit `./scripts/log_agent_step.sh`, sofern das
   Projekt diesen verpflichtenden Workflow bereitstellt.

Wenn `get_design_context` verwendet wird, lade davor zwingend die Skill
`figma:figma-design-to-code` und befolge ihre Anweisungen.

## Designkontext aus Figma

Lies den angegebenen Figma-Node per MCP und erfasse nur belegbare Informationen:

- Figma-Link, Node-ID, Abrufdatum und bestätigter Seitenname
- sichtbare Texte, Informationshierarchie, Layout, Responsive-Hinweise und Zustände
- vorhandene Komponenten, Variablen, Assets und Interaktionshinweise
- Mapping auf bestehende Django-Komponenten, Bootstrap und geschützte Verträge
- Abweichungen, technische Risiken und offene fachliche Fragen

Erfinde aus visuellen Elementen keine Persistenz, Session-Daten, POST-Logik,
API-Verträge oder Validierungsregeln. Temporäre MCP-Asset-URLs dürfen nicht als
dauerhafte Referenz gespeichert werden.

## GitHub-Workitem erstellen

Die GitHub-Skill beziehungsweise der GitHub-Connector prüft im Repository
`Roni-Aba/SQLQuestEditor` auf ähnliche offene Issues und erstellt das Issue über den
verbundenen GitHub-Zugriff. Nenne vor der Schreibaktion nochmals das feste Ziel
`github.com/Roni-Aba/SQLQuestEditor` und den konkreten Issue-Titel. Bei einem
wahrscheinlichen Duplikat nenne den Fund und erstelle kein zweites Issue ohne Zustimmung.

Erstelle das Issue nur, wenn der Nutzer die externe Erstellung ausdrücklich beauftragt
hat. Bei einer vollständigen, ausdrücklichen Anfrage darf es ohne weiteren
Freigabeschritt erstellt werden.

Verwende diese kompakte Beschreibung:

```markdown
## Figma-Quelle
- Link: <Figma-URL>
- Node: <Node-ID>
- Seite: <bestätigter Seitenname>

## Ziel
<belegbares, kurzes Ziel der Oberfläche>

## Designanforderungen
- <sichtbare Hierarchie, Komponenten und Zustände>
- <relevante Layout- und Responsive-Anforderungen>
- <Assets oder Design-System-Hinweise>

## Projektvorgaben
- Neue Figma-Seite nur additiv: neues Template, neue Render-View, neue Route.
- Bestehende Templates, Komponenten und CSS-Dateien nicht ändern.
- Bootstrap verwenden; keine neue CSS-Datei und keine erfundene Backend-Logik.

## Lokale Bestandsanalyse
- Wiederzuverwendende Templates und Komponenten: <konkrete, geprüfte Repository-Pfade>
- Relevante Includes, CSS-Abhängigkeiten und JavaScript-Hooks: <konkrete, geprüfte Repository-Pfade>
- Abgeleitete Umsetzung: <welche Bestandsteile unverändert wiederverwendet werden und welches neue Template, welche View und welche Route erforderlich wären>

## Akzeptanzkriterien
- [ ] <aus Figma belegbarer, überprüfbarer Punkt>
- [ ] <aus Figma belegbarer, überprüfbarer Punkt>

## Offene Fragen / Risiken
- <nur tatsächliche Lücken oder Risiken>
```

Formuliere einen präzisen Titel als `Figma: <Seitenname> (<Node-ID>)`. Übernimm
Labels, Assignee, Meilenstein oder Projekt nur, wenn sie angefordert wurden oder eindeutig
als Projektnorm vorliegen.

## Abschluss

Melde das Ziel `github.com/Roni-Aba/SQLQuestEditor`, die Issue-URL beziehungsweise
Issue-Nummer, den Figma-Node und offene Fragen. Falls kein GitHub-Zugriff besteht,
melde ausschließlich den konkreten Blocker.
