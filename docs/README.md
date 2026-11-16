# SQL Spell Quest Editor: verstehen, benutzen, verändern

Mit diesem lokalen Editor erstellst und bearbeitest du Level für SQL Spell Quest.
Du legst Bilder, Gegenstände, Tabellen und Freischaltbedingungen fest. Am Ende
exportierst du das Spiel als ZIP mit JSON, SQLite-Datenbanken und Bildern.

Diese Dokumentation richtet sich an Student\*innen und Programmierer\*innen mit
wenig Projekterfahrung. Du musst die Architektur nicht kennen, um anzufangen.

## Was möchtest du tun?

| Ich möchte … | Hier geht es weiter |
|---|---|
| verstehen, wofür der Editor da ist | [Zweck und Grundbegriffe](verstehen.md) |
| Table-, Hint- und Exit-Items unterscheiden | [Gegenstände verstehen](gegenstaende.md) |
| den Editor auf meinem Rechner starten | [Projekt starten](starten.md) |
| den geführten Editor mit Screenshots durchgehen | [Bebilderter Durchlauf](gefuehrter-editor.md) |
| mein erstes Level erstellen | [Schritt-für-Schritt-Anleitung](erstes-level.md) |
| ein bestehendes Level ändern | [Geführter Editor oder Shortcuts?](bedienen.md) |
| einen Button oder eine eigene Seite ergänzen | [Praktische Code-Anleitung](seiten-erweitern.md) |
| Texte, Logik oder Tabellen im Code ändern | [FAQ: Wo ändere ich was?](code-faq.md) |
| einen Fehler untersuchen oder eine Änderung testen | [Testen und Fehler finden](testen.md) |
| den Weg vom Formular zum Service verstehen | [Architektur erklärt](architektur.md) |
| Feldnamen und Exportformat nachschlagen | [Datenverträge](editor-vertraege.md) |
| die Projektdokumentation ergänzen | [Dokumentation pflegen](dokumentieren.md) |

## Was ist die wichtigste Unterscheidung?

**Der Editor erstellt die Spieldaten; das Spiel verwendet sie.** Eine erfolgreiche
Erstellung im Editor ist deshalb noch kein vollständiger Spieltest.

**Speichern ist außerdem nicht Exportieren.** Speichern übernimmt eine Bearbeitung
in den aktuellen Editorzustand. Erst der heruntergeladene Export ist dein
transportierbares Ergebnis. Bewahre ihn auf, bevor du deine Arbeit beendest.

## Wie lese ich die Code-Anleitungen?

Dateipfade in den Anleitungen beginnen am Projektordner, in dem `mkdocs.yml`
liegt. Öffne diesen Ordner in deiner IDE. Suche anschließend nach dem angegebenen
Funktionsnamen. Zeilennummern verwenden wir bewusst nicht, weil sie sich ändern.

[Historische Auswertungen, Mockups und weitere Unterlagen](unterlagen.md)
