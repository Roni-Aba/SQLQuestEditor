# Data Model: Level Basics Display

## Persistence Scope

This feature introduces **no persisted entity, database field, session value, uploaded file, or JSON structure**. It is a visual-only page.

## Presentation Data

| Presentation value | Shape | Source | Validation / transition |
|--------------------|-------|--------|-------------------------|
| Progress steps | Eight ordered values with a number and active state | Static local view context | Step 1 is active; steps 2–8 are inactive. No transition occurs on this page. |
| Level-name display | Empty read-only text input with visible placeholder | New template | Never submitted or stored. |
| Greeting display | Empty read-only text input with visible placeholder | New template | Never submitted or stored. |
| Background-image action | Visible non-submitting control | New template | Does not open an upload flow or create a file. |
| Back and continue actions | Visible non-submitting controls | New template | Do not navigate or alter authoring state. |

## Existing Data Boundaries

- Existing level data, `new_level` session data, form fields, uploads, and JSON exports are explicitly outside the feature boundary.
- No state on the display page may be used as input to any existing authoring view.
