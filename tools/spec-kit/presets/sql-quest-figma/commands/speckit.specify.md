---
description: "Erstellt eine Spezifikation mit verpflichtender Figma-MCP-Analyse."
---

## Figma-MCP-Gate

Prüfe, ob die Feature-Beschreibung eine Figma-Datei-URL, eine Node-ID oder eine
Figma-basierte Benutzeroberfläche betrifft.

Bei einer Figma-basierten Anfrage gelten vor der Spezifikation folgende Regeln:

1. Prüfe, ob ein semantischer Seitenname bestätigt wurde. Falls nicht, frage danach
   und lade den Figma-Node noch nicht.
2. Prüfe, ob die Figma-Datei-URL und die Node-ID vorhanden sind. Falls Informationen
   fehlen, frage gezielt danach.
3. Lies die Projektverfassung und die projektspezifischen Anweisungen.
4. Verwende vor jedem Figma-MCP-Aufruf den verfügbaren Figma-Design-to-Code-Skill.
5. Lade den Figma-Node über die Figma-MCP-Anbindung und analysiere Layout, sichtbare
   Texte, Komponenten, Zustände, Interaktionen, Assets und Barrierefreiheit.
6. Halte die Analyse während der Spezifikation als verbindliche Designreferenz vor.
   Eine visuell passende Umsetzung darf projektspezifische Verträge nicht verletzen.

{CORE_TEMPLATE}

## Figma-Analyseartefakt

Nach dem Erstellen der Spezifikation wird bei Figma-basierten Features:

1. `.specify/feature.json` gelesen, um das aktuelle Feature-Verzeichnis zu ermitteln.
2. Im Feature-Verzeichnis die Datei `figma-analysis.md` erstellt.
3. Darin Figma-Datei-URL, Node-ID, bestätigter Seitenname, Analysedatum, Layout,
   Inhalte, Komponenten, Zustände, Interaktionen, Assets, offene Fragen und bekannte
   Abweichungen dokumentiert.
4. In `spec.md` auf `figma-analysis.md` verwiesen.

Bei einer Anfrage ohne Figma-Bezug wird dieser Zusatzschritt übersprungen.
