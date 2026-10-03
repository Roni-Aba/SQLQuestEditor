# Quickstart: Validate Level Basics Display

## Prerequisites

- Start from the repository root.
- Use the project Python environment with Django dependencies available.
- Confirm that the implementation has added the route described in [contracts/level-basics-display.md](contracts/level-basics-display.md).

## Validation Steps

1. Run the Django configuration check:

   ```bash
   cd backend
   python manage.py check
   ```

   Expected: Django reports no configuration errors.

2. Start the local server:

   ```bash
   cd backend
   python manage.py runserver
   ```

3. Open `/figma/levelauswahl-575-2535/` in a desktop viewport.

   Expected: Existing navigation, eight steps with only step 1 highlighted, Cosmo guidance, both `Schreibe hinein` fields, background-image action, and `Zurück`/`Weiter` are visible.

4. Reduce the viewport to 320 px width and review the page.

   Expected: Content follows a logical stacked order; every required element is reachable through vertical scrolling only; no horizontal page overflow obscures controls.

5. Use keyboard navigation through the page and inspect the rendered controls with accessibility tooling.

   Expected: Focus follows the visual reading order; all controls have accessible names; Cosmo has meaningful alternative text; the active first step is announced.

6. Enter text or activate visible controls where allowed, then inspect an existing level-authoring page or reload the display page.

   Expected: No level data, upload, session state, or authoring-flow position has changed.

## Figma Comparison

Compare the completed desktop page with [figma-analysis.md](figma-analysis.md). Record the accepted protected-navbar difference and any Bootstrap approximation; do not resolve either through new CSS or changes to protected components.
