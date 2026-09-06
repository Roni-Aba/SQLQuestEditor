› $speckit-plan


• Ich verwende speckit-plan und prüfe den bestehenden Django-Bestand sowie die Figma-Analyse. Im aktuellen Planmodus erstelle ich keine Dateien; ich liefere den vollständigen, umsetzungsreifen Plan.

• Explored
  └ Read SKILL.md (speckit-plan skill), spec.md, figma-analysis.md, constitution.md, setup-plan.sh, plan-template.md

• Ran git status --short
  │ if [ -f .specify/extensions.yml ]; then sed -n '1,240p' .specify/extensions.yml; else echo 'No extension hooks registered'; fi
  │ sed -n '1,300p' backend/editor/templates/editor/auswahl.html
  │ … +6 lines
  └ D  log.md
    ?? .agents/
    … +487 lines (ctrl + t to view transcript)
    backend/editor/templates/editor/components/navbar/navbar.html:10:      href="{% url 'auswahl_view' %}"
    backend/editor/templates/editor/components/navbar/navbar.html:17:      href="{% url 'auswahl_view' %}"

───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Ein Punkt ist fachlich entscheidend: Das Figma zeigt „Level speichern“, während die neue Figma-Seite laut Vorgaben keine neue POST- oder Persistenzlogik erhalten darf. Ich prüfe noch die bestehenden Bild- und Routenverträge,
  bevor ich diese Entscheidung mit dir festhalte.

• Ran sed -n '740,790p' backend/editor/views.py
  │ sed -n '3180,3225p' backend/editor/views.py
  │ sed -n '1,160p' backend/editor/templates/editor/components/navbar/navbar.html
  │ … +4 lines
  └     request.session["new_level"] = {
            "id": "",
    … +215 lines (ctrl + t to view transcript)
    backend/editor/static/editor/img/figma/figma_createlevel1agent_497_1698_step_active.svg
    backend/editor/static/editor/img/figma/figma_createlevel1agent_497_1698_step_inactive.svg

• Questions 1/1 answered
  • Wie soll „Level speichern“ auf der neuen, reinen Figma-Renderseite funktionieren?
    answer: Nur Anzeige

• Proposed Plan


  # Figma-Levelübersicht implementieren

  ## Zusammenfassung

  Neue, additive Django-Renderseite für die Figma-Ansicht overview (Node 45:1891). Sie zeigt die drei Bereiche mit direkten Bearbeitungslinks, Cosmo-Erklärung, einem rein visuellen Speichern-Button und dem geführten
  Erstellungslink.

  ## Umsetzung

  - Figma-Cosmo-Export unverändert als figma_overview_45_1891_cosmo.png unter backend/editor/static/editor/img/figma/ speichern; keine temporäre MCP-URL verwenden.
  - Neues Template figma_overview_45_1891.html anlegen, das editor/base.html erweitert:
      - Bestehende Button- und Helper-Komponenten unverändert einbinden; nur deren bestehende CSS-Dateien laden.
      - Bootstrap-Grid: auf Desktop links vier Bearbeitungsaktionen, mittig Cosmo, Erklärung und „Level speichern“, rechts die geführte Erstellung; auf kleinen Viewports logisch untereinander.
      - Direkte Links verwenden: levelGrunddaten, sql_grunddaten_view, messages_grunddaten, gegenstandVerwaltung und create_level.
      - „Level speichern“ ausschließlich als deaktivierte, visuelle Schaltfläche rendern: kein Formular, kein POST und keine neue Persistenzlogik.
      - Semantisches <main>, visuell verstecktes <h1>, sprechende Bereichslabels und Alt-Text für Cosmo.

  - Additive Render-View figma_overview_45_1891_view in views.py ergänzen; sie rendert ausschließlich das neue Template ohne Kontext-, Session- oder POST-Logik.
  - Genau eine Route ergänzen: figma/overview-45-1891/ mit URL-Namen figma_overview_45_1891.

  ## Verträge und Abweichungen

  - Vorhandene Templates, Komponenten, CSS-Dateien, Views, Routen und Fachlogik bleiben unverändert.
  - Die bestehende Navbar wird unverändert aus base.html übernommen. Ihre zusätzlichen Links sowie das fehlende „Anleitung“ sind die dokumentierte, akzeptierte Figma-Abweichung.
  - Es gibt keine neuen Datenmodelle, Migrationen, API- oder externen Schnittstellen. Die neue öffentliche Oberfläche ist ausschließlich die GET-Route der Renderseite.

  ## Validierung

  - python manage.py check ausführen.
  - Die neue Route im Browser aufrufen und auf Desktop sowie bei 320 px Breite prüfen: sechs sichtbare Aktionen, lesbare Erklärung, keine horizontale Scrollbarkeit.
  - Sicherstellen, dass die fünf Navigationsaktionen ihre bestehenden Ziele verwenden und „Level speichern“ keinen Request auslöst.
  - Diff auf ausschließlich die neue Seite, den Figma-Export, die eine View und die eine Route prüfen; jede Handlung in log.md protokollieren.

  ## Annahmen

  - Der bestehende Cosmo-Helper ist für die zentrale Bild- und Textdarstellung passend.
  - „Level speichern“ bleibt gemäß deiner Entscheidung bewusst reine Anzeige und weicht damit absichtlich vom in Figma aktiv wirkenden Button ab.


─ Worked for 1m 56s ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

