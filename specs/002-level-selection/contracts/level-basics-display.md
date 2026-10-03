# UI Contract: Level Basics Display

## Public Route

| Property | Contract |
|----------|----------|
| Path | `/figma/levelauswahl-575-2535/` |
| URL name | `figma_levelauswahl_575_2535` |
| HTTP method | `GET` only |
| Response | Independently renderable visual-only level-basics page |

## View Contract

| Property | Contract |
|----------|----------|
| View name | `figma_levelauswahl_575_2535_view` |
| Template | `editor/figma_levelauswahl_575_2535.html` |
| Input | Request only; no path parameters, form values, session state, or uploaded files |
| Output context | Static presentation context including eight progress steps with only step 1 active |
| Side effects | None |

## User Interface Contract

- The page extends the protected global base layout and therefore retains its existing navigation.
- It includes the protected status-bar once and exposes eight labelled steps with step 1 active.
- It includes the protected helper once with a meaningful Cosmo alternative text and the Figma guidance copy.
- It visibly includes the required two labelled text-entry displays, background-image action, and separate `Zurück` and `Weiter` controls.
- Display fields and actions must not submit, upload, navigate, store, or change level data.
- All controls must have accessible names; content must stack in reading order at narrow widths.

## Non-Goals

- No POST endpoint, file upload, validation, persistence, session mutation, or authoring-flow navigation is part of this contract.
- No existing form fields, DOM IDs, JavaScript hooks, components, templates, views, routes, or CSS files are modified.
