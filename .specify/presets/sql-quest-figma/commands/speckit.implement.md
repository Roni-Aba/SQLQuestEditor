---
description: "Implementiert Figma-basierte Features mit erneuter Figma-MCP-Prüfung."
---

## Figma-MCP-Implementierungsgate

Prüfe vor jeder Implementierung, ob das aktuelle Feature eine Figma-Designreferenz besitzt.

Bei Figma-basierten Features:

1. Lies `spec.md`, `plan.md`, `tasks.md`, `figma-analysis.md` und die
   Projektverfassung.
2. Prüfe, ob Seitenname, Figma-Datei-URL und Node-ID dokumentiert sind. Falls nicht,
   stoppe und fordere die fehlenden Angaben an.
3. Verwende den Figma-Design-to-Code-Skill und lade den dokumentierten Figma-Node über
   die Figma-MCP-Anbindung erneut.
4. Vergleiche die aktuelle Figma-Ansicht mit `figma-analysis.md` und dokumentiere
   relevante Änderungen oder Abweichungen.
5. Implementiere ausschließlich gemäß Spezifikation, Plan und Projektverfassung.
   Eine visuelle Übereinstimmung darf niemals bestehende Django-, Formular-, URL-,
   JSON- oder JavaScript-Verträge gefährden.
6. Speichere Figma-Assets dauerhaft unter `backend/editor/static/editor/img/figma/`.
   Temporäre Figma-URLs dürfen nicht in den Quellcode übernommen werden.

{CORE_TEMPLATE}
