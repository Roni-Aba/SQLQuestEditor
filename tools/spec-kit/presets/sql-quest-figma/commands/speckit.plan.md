---
description: "Erstellt einen technischen Plan unter Einbezug der Figma-MCP-Analyse."
---

## Figma-MCP-Planungsgate

Prüfe, ob das aktuelle Feature eine Figma-Designreferenz besitzt.

Bei Figma-basierten Features:

1. Lies `figma-analysis.md`, `spec.md` und die Projektverfassung vollständig.
2. Falls `figma-analysis.md` fehlt oder Figma-Datei-URL, Node-ID oder Seitenname
   unvollständig sind, stoppe die Planung und fordere zuerst die fehlenden Angaben an.
3. Verwende bei fehlenden oder widersprüchlichen Designinformationen erneut den
   Figma-Design-to-Code-Skill und die Figma-MCP-Anbindung.
4. Dokumentiere im technischen Plan die Zuordnung von Figma-Elementen zu bestehenden
   Django-Komponenten oder neuem Bootstrap-Markup, neue Template-, View-, Route- und
   URL-Namen, mögliche Figma-Assets, relevante Verträge und bekannte Abweichungen.
5. Berücksichtige, dass bestehende Templates, Komponenten, Partials, CSS-Dateien,
   Views und Routen nur gemäß der Projektverfassung verändert werden dürfen.

{CORE_TEMPLATE}
