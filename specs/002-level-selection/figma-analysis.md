# Figma Analysis: Level Basics Display

**Figma file**: https://www.figma.com/design/isyoakVzVVVEsS6lHxnbzP/SQL-Spell-Quest-Editor?node-id=575-2535&m=dev
**Node ID**: `575:2535`
**Confirmed page name**: `levelauswahl`
**Analyzed**: 2026-09-12
**Source work item**: [GitHub issue #3](https://github.com/Roni-Aba/SQLQuestEditor/issues/3)

## Layout

- White desktop frame with a full-width purple navigation bar.
- A horizontal row of eight numbered progress circles below the navigation; the first circle is purple and the remaining circles are light pink.
- Desktop content is split into a left guidance column and a right form column.
- The left column displays the Cosmo illustration above a short bold explanation.
- The right column stacks the level-name prompt and field, background-image upload action, user-greeting prompt and field, and the two navigation actions.
- The Figma reference uses absolute positioning. The target must instead preserve the hierarchy through a responsive stacked narrow-screen layout.

## Visible Content

- Brand text: `SQL SPELL QUEST EDITIOR` (spelling as displayed in Figma).
- Navigation labels: `Kontakt`, `Unser Team`, `Anleitung`.
- Progress labels: `1` through `8`.
- Level-name prompt: `Verrate mir doch bitte wie das Level heißen soll`.
- Both text-entry placeholders: `Schreibe hinein`.
- Guidance text: `Hier legen wir die Grundsteine unseres Levels fest. Du kannst mir beschreiben was du dir vorstellst und ich zaubere dir ein schönes Hintergrundsbild`.
- Background-image action: `Lade dein gewünschtes Hintergrundsbild hoch`.
- Greeting prompt: `Wie soll der Nutzer des Levels begrüßt werden?`.
- Navigation actions: `Zurück` and `Weiter`.

## Components and Visual Language

- Purple navigation bar and saturated purple primary actions with white semi-bold labels.
- White background, dark headings, muted placeholder copy, and light-grey rounded text-entry outlines.
- The progress indicator uses a filled active circle and muted inactive circles.
- Existing reusable base layout, navigation, status-bar, and helper components have directly relevant protected contracts. The existing level-basics partial has relevant form and upload hooks, but it must not be altered and can be included only if its complete context contract is met.

## States and Interactions

- Step 1 is the only visible active progress state.
- No validation, error, loading, selected-file, or completion state is shown in the Figma node.
- The node depicts text entry, a background-image upload action, and back/continue actions, but does not evidence submission, upload processing, data persistence, or destination behaviour.
- For this new visual-only screen, no existing submit, upload, session, or level-authoring behaviour may be attached or inferred.

## Assets

- The Figma design context returns one Cosmo image asset and two SVG progress-circle assets.
- All returned MCP asset URLs are temporary and must not be committed.
- If implementation requires the exact Cosmo export, it must be downloaded unchanged and stored under `backend/editor/static/editor/img/figma/` before it is referenced.
- The existing status-bar and helper components may satisfy the design intent with their protected assets and styling; no asset decision is required during specification.

## Accessibility

- The screen requires a clear main heading hierarchy, named navigation and display controls, and visible labels for both text-entry areas.
- The Cosmo image requires meaningful alternative text.
- Responsive stacking must retain visual reading order and keyboard focus order.
- The progress indicator must expose the active first step to assistive technologies.

## Open Questions

- The confirmed semantic page name is `levelauswahl`, but the Figma node depicts level basics. The issue records this discrepancy; implementation planning must retain the required additive name while treating the visible node as the design reference.
- The Figma reference does not define functional handling for image selection, text entry, back navigation, or continue navigation. Any functional behaviour requires a separate explicit backend mandate.

## Known Deviations

- The Figma navigation includes `Anleitung`, whereas the existing protected navigation has different fixed links. The implementation must reuse the protected navigation unchanged and document the visible difference.
- At narrow widths, the protected navigation's fixed inline links can widen the document beyond the viewport. The new page keeps its own content in a Bootstrap-responsive, overflow-contained main region, but the shared navbar is not altered.
- Exact Figma dimensions, spacing, and colour values may be approximated using existing project presentation conventions rather than page-specific styling.
- The Figma node makes the upload and navigation actions look active, but the new pure render page cannot invent their functional targets or persistence behaviour.
