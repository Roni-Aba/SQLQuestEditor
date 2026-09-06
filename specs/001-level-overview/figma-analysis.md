# Figma Analysis: Level Creation Overview

**Figma file**: https://www.figma.com/design/isyoakVzVVVEsS6lHxnbzP/SQL-Spell-Quest-Editor?node-id=45-1891&m=dev
**Node ID**: `45:1891`
**Confirmed page name**: `overview`
**Analyzed**: 2026-09-06
**Source work item**: [GitHub issue #1](https://github.com/Roni-Aba/SQLQuestEditor/issues/1)

## Layout

- Desktop frame with a white background and a full-width purple navigation bar.
- Three desktop content areas: four direct-editing actions in the left area; character image, explanation, and save action in the centre; guided-creation action in the right area.
- The character image is visually central above the explanatory copy. The save action appears beneath the central content.
- The Figma reference is absolutely arranged; the target experience must instead retain this hierarchy with a responsive, stacked narrow-screen layout.

## Visible Content

- Brand text: `SQL SPELL QUEST EDITIOR` (spelling as displayed in Figma).
- Navigation labels: `Kontakt`, `Unser Team`, `Anleitung`.
- Explanation: `Du befindest dich in der Übersicht zur Levelerstellung.` It explains that authors can choose the guided creation option or directly choose the editing area they want to work on.
- Actions: `Levelgrunddaten`, `SQL Beschränkungen`, `Systemnachrichten`, `Gegenstände`, `Geführte Levelerstellung`, and `Level speichern`.

## Components and Visual Language

- Purple full-width navigation bar with white or near-white text.
- White background, dark body text, and medium-sized semi-bold headline-style copy.
- Purple, rounded rectangular action buttons with semi-bold white labels.
- One character illustration (Cosmo) at the centre of the page.
- Existing reusable base layout, navigation, button, and helper components are applicable only where their protected contracts and visible structure match the design intent.

## States and Interactions

- No error, loading, selection, or disabled state is shown in the Figma node.
- The four left-side actions are direct entry points to individual editing areas.
- The right-side action is an entry point to the guided creation flow.
- The central save action is visible; the work item explicitly excludes inventing new save or form behavior.
- On small screens, the three content areas must stack in a readable, reachable order.

## Assets

- One exported character image is referenced by the Figma design context: `https://www.figma.com/api/mcp/asset/bc3ea127-97d3-47cd-ab1f-dfa5bd576152.png`.
- The URL is temporary and must not be committed. If implementation needs it, the exact export must first be saved as a local project asset.
- The exact export is stored for this implementation as `backend/editor/static/editor/img/figma/figma_overview_45_1891_cosmo.png`.

## Accessibility

- The page needs a clear heading hierarchy, named interactive controls, and alternative text for the character image.
- The responsive stacked layout must preserve logical reading and focus order.

## Open Questions

- None blocking specification. The Issue confirms the required page name, Figma reference, visible actions, and scope.

## Known Deviations

- The Figma navigation includes `Anleitung`, while the existing protected navigation has fixed links and cannot be altered for this feature. The implementation must reuse the protected navigation unchanged and document this visible difference.
- Exact Figma dimensions, spacing, and colour values may be approximated by the project’s established presentation conventions rather than duplicated as page-specific styling.
- The Figma save button appears enabled. By confirmed product decision, the new pure render page displays it as a disabled visual control and adds no save form or POST behaviour.
