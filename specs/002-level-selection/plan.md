# Implementation Plan: Level Basics Display

**Branch**: `002-level-selection` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-level-selection/spec.md`

## Summary

Add an independently accessible, display-only Figma page for node `575:2535`. The new page presents the existing protected navigation, the existing status-bar and helper components, and new Bootstrap-only level-basics display controls. It has a new root template, a pure render view, and one route; it must not connect displayed fields, upload, or navigation controls to existing authoring behaviour.

## Technical Context

**Language/Version**: Python 3 with Django 4.2.30; Django templates; browser HTML

**Primary Dependencies**: Django, Bootstrap 5.3.3, Bootstrap Icons 1.11.3

**Storage**: No new storage; the new page neither reads nor writes session, uploaded files, or persisted level data

**Testing**: `python manage.py check`; manual desktop and narrow-screen visual review; manual keyboard/accessibility review

**Target Platform**: Server-rendered web page in supported desktop and mobile browsers

**Project Type**: Django web application

**Performance Goals**: The page renders within the normal existing template-response budget and introduces no external runtime request beyond already loaded project resources

**Constraints**: New Bootstrap-only markup; no CSS changes or additions; no inline styles; no changes to protected templates, components, partials, routes, or existing view behaviour; no invented POST, upload, session, or persistence logic

**Scale/Scope**: One new visual-only page, one new view, one new URL route, and optionally one exact Figma image export only if the protected helper asset cannot faithfully represent the reference

## Constitution Check

### Pre-design Gate

| Principle | Plan response | Status |
|-----------|---------------|--------|
| Preserve Functional Contracts | The new view is read-only and adds no form action, session access, upload handling, or change to existing URLs, fields, DOM hooks, or JSON structures. | PASS |
| Design-Driven, Server-Rendered Delivery | The plan defines a new root template, pure render view, and exactly one URL route for the confirmed page name and Figma node. | PASS |
| Bootstrap-First and Component-Safe UI | Reuse protected status-bar and helper components unchanged; create only new Bootstrap markup where the existing form partial's POST contract does not fit. | PASS |
| Accessibility and Responsive Behaviour | Use semantic landmarks, heading hierarchy, labels, accessible control names, alternative text, and responsive Bootstrap grid utilities. | PASS |
| Evidence-Based Quality and Traceability | Preserve Figma analysis, record implementation actions in `log.md`, run Django validation, review the route, and visually inspect desktop and narrow layouts. | PASS |

### Post-design Gate

The research, UI contract, data model, and quickstart below preserve the same constraints. No constitution violation or exception is introduced. **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/002-level-selection/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── level-basics-display.md
└── tasks.md                 # Created later by $speckit-tasks
```

### Source Code (repository root)

```text
backend/
└── editor/
    ├── templates/editor/
    │   ├── figma_levelauswahl_575_2535.html       # New root template
    │   ├── base.html                               # Protected, reused by extension
    │   └── components/
    │       ├── helper/helper.html                  # Protected, reused unchanged
    │       └── statusBar/statusBar.html            # Protected, reused unchanged
    ├── static/editor/
    │   └── img/figma/                              # Only if an exact Figma asset is required
    ├── views.py                                    # One additive pure render view
    └── urls.py                                     # One additive path
```

**Structure Decision**: This is a single Django application. The feature changes only one new root template plus the constitution-permitted additive view and route; no new component, CSS, JavaScript, model, migration, or service is needed.

## Figma-to-Project Mapping

| Figma element | Project mapping | Contract-sensitive decision |
|---------------|-----------------|-----------------------------|
| Purple navigation bar | `editor/base.html` automatically includes `components/navbar/navbar.html` | Reuse unchanged even though Figma includes `Anleitung`, which the protected navbar does not expose. |
| Eight numbered progress circles | `components/statusBar/statusBar.html` with a new local `steps` context marking step 1 active | Reuse component and existing CSS unchanged; do not alter its active-state semantics. |
| Cosmo illustration and guidance copy | `components/helper/helper.html` with the appropriate existing Cosmo image and Figma copy | Reuse unchanged; compare the existing asset to the Figma export during implementation and download the exact export only when required. |
| Level-name and greeting display fields | New template-local Bootstrap labels and read-only text inputs | Do not include `partials/levelGrunddatenForm.html`, because its multipart POST, file input, IDs, and inline JavaScript require a functional backend contract outside scope. |
| Background-image, back, and continue actions | New template-local Bootstrap buttons with no form action or navigation target | Keep them visual-only and non-submitting; no existing URL or upload action may be inferred. |
| Desktop two-column layout and narrow stacking | New template-local `container`, `row`, responsive `col-*`, spacing, and flex utilities | Preserve reading/focus order without absolute positioning, inline styles, or new CSS. |

## Additive Names and Contracts

- **Template**: `backend/editor/templates/editor/figma_levelauswahl_575_2535.html`
- **View**: `figma_levelauswahl_575_2535_view(request)` in `backend/editor/views.py`
- **Route**: `figma/levelauswahl-575-2535/`
- **URL name**: `figma_levelauswahl_575_2535`
- **View context**: a local eight-entry `steps` collection with only step 1 active, plus any static presentation values required by the new template.
- **Protected contracts**: existing view logic, URL names, session data, form field names, upload handling, component markup and CSS, and JavaScript hooks remain unchanged.
- **Known naming risk**: the confirmed semantic name is `levelauswahl`, while the node displays level basics. Preserve the required additive names above and use the node only as the visual reference.

## Implementation Sequence

1. Re-read `figma-analysis.md` before coding and inspect the protected base, status-bar, helper, level-basics partial, views, and URLs without modifying them.
2. If needed, compare the Figma Cosmo export with the existing helper asset; place an unmodified exact export under `backend/editor/static/editor/img/figma/` only when the existing asset is not suitable.
3. Add `figma_levelauswahl_575_2535.html`, extending `editor/base.html`; load only the already existing component CSS required by the included protected components.
4. Build the new display controls with semantic Bootstrap-only markup. Use labelled, read-only text inputs and non-submitting visual buttons; do not create a form, POST action, file input, or navigation target.
5. Add `figma_levelauswahl_575_2535_view` with static presentation context only, then append exactly one corresponding path in `backend/editor/urls.py`.
6. Run `python manage.py check`, request the new route, inspect desktop and 320 px layouts, check keyboard order and accessible labels, review the diff, and record any accepted Figma deviations.

## Complexity Tracking

No constitution violations require justification.
