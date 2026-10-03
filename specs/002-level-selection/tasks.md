---

description: "Actionable task list for the level-basics display feature"
---

# Tasks: Level Basics Display

**Input**: Design documents from `specs/002-level-selection/`

**Prerequisites**: `plan.md`, `spec.md`, `figma-analysis.md`, `research.md`, `data-model.md`, `contracts/level-basics-display.md`, and `quickstart.md`

**Tests**: No automated tests are requested by the specification. Validation tasks use the prescribed Django check and manual route, responsive, accessibility, and state-preservation reviews.

**Organization**: Tasks are grouped by user story so each delivery increment remains independently reviewable.

## Phase 1: Setup (Reference and Scope)

**Purpose**: Protect existing work and establish the approved visual and contract boundaries before editing code.

- [X] T001 [P] Review `specs/002-level-selection/figma-analysis.md`, `specs/002-level-selection/plan.md`, and `specs/002-level-selection/contracts/level-basics-display.md`; record every completed action in `log.md` via `scripts/log_agent_step.sh`.
- [X] T002 [P] Inspect the protected `backend/editor/templates/editor/base.html`, `backend/editor/templates/editor/components/statusBar/statusBar.html`, `backend/editor/templates/editor/components/helper/helper.html`, and `backend/editor/templates/editor/partials/levelGrunddatenForm.html` without modifying them.
- [X] T003 Review the active worktree with `git status --short` and preserve unrelated changes in `backend/editor/templates/editor/figma_overview_45_1891.html` and `log.md`.

---

## Phase 2: Foundational (Additive Route Contract)

**Purpose**: Create the isolated route and pure render boundary required by every user story.

**⚠️ CRITICAL**: Complete this phase before relying on the page in any user-story review.

- [X] T004 Add pure render view `figma_levelauswahl_575_2535_view` with a local eight-step, step-1-active presentation context in `backend/editor/views.py`; do not read or mutate session, POST, uploads, or level data.
- [X] T005 Add exactly one additive `figma/levelauswahl-575-2535/` route named `figma_levelauswahl_575_2535` in `backend/editor/urls.py` for `figma_levelauswahl_575_2535_view`.

**Checkpoint**: The isolated GET route contract in `specs/002-level-selection/contracts/level-basics-display.md` is available for page rendering.

---

## Phase 3: User Story 1 - View level basics (Priority: P1) 🎯 MVP

**Goal**: Provide the independently accessible level-basics display with the active progress step, Cosmo guidance, visible controls, and no authoring side effects.

**Independent Test**: Open `/figma/levelauswahl-575-2535/` and verify that the eight-step indicator, character guidance, two text-entry displays, background-image action, and `Zurück`/`Weiter` controls appear together.

### Implementation for User Story 1

- [X] T006 [US1] Create `backend/editor/templates/editor/figma_levelauswahl_575_2535.html` extending `editor/base.html`, loading only existing status-bar and helper component CSS, and including each protected component once with its documented context.
- [X] T007 [US1] Build the new visual-only level-basics controls in `backend/editor/templates/editor/figma_levelauswahl_575_2535.html` with semantic Bootstrap markup, read-only text inputs, and non-submitting background-image/back/continue buttons; do not add a form, file input, POST action, or navigation target.
- [X] T008 [US1] Compare the Figma Cosmo export against the helper-compatible existing asset in `backend/editor/templates/editor/figma_levelauswahl_575_2535.html`; add an unchanged export only under `backend/editor/static/editor/img/figma/` if the existing asset cannot faithfully serve the reference.

**Checkpoint**: The P1 page is independently renderable and displays the complete first-stage hierarchy without modifying authoring data.

---

## Phase 4: User Story 2 - Understand required level information (Priority: P2)

**Goal**: Make every requested piece of level information unambiguous through the exact visible copy, placeholder text, and accessible labels.

**Independent Test**: Review `backend/editor/templates/editor/figma_levelauswahl_575_2535.html` in the new route and confirm both Figma prompts, both `Schreibe hinein` placeholders, the background-image label, and `Zurück`/`Weiter` appear with accessible names.

### Implementation for User Story 2

- [X] T009 [US2] Apply the exact Figma labels, `Schreibe hinein` placeholders, guidance copy, meaningful Cosmo alternative text, and accessible names for all display controls in `backend/editor/templates/editor/figma_levelauswahl_575_2535.html`.
- [X] T010 [US2] Verify in `backend/editor/templates/editor/figma_levelauswahl_575_2535.html` that the visible controls remain read-only or non-submitting and cannot invoke existing `levelPicture`, level-save, session, upload, or authoring-flow behaviour.

**Checkpoint**: The screen independently communicates the expected level name, background image, and greeting without suggesting unsupported functionality.

---

## Phase 5: User Story 3 - Access the screen on narrow displays (Priority: P3)

**Goal**: Preserve content readability, keyboard order, and reachability on a 320 px viewport using Bootstrap-only responsive layout.

**Independent Test**: At 320 px, inspect `/figma/levelauswahl-575-2535/` and confirm required content is reachable through vertical scrolling only and that keyboard focus follows the visible reading order.

### Implementation for User Story 3

- [X] T011 [US3] Apply responsive `container`, `row`, `col-*`, spacing, flex, and overflow Bootstrap utilities in `backend/editor/templates/editor/figma_levelauswahl_575_2535.html` so the desktop guidance/form columns stack logically without inline styles, new CSS, or custom classes.
- [X] T012 [US3] Confirm the included status-bar configuration in `backend/editor/templates/editor/figma_levelauswahl_575_2535.html` preserves an identifiable active first step and no clipped active state at narrow widths.

**Checkpoint**: The page is usable and understandable on both desktop and narrow displays while retaining the protected component behaviour.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Verify route integrity, visual fidelity, accessibility, contract preservation, and traceability before handoff.

- [X] T013 Run `python manage.py check` from `backend/manage.py` after the additive template, view, and route changes.
- [X] T014 Execute the desktop, 320 px, keyboard, accessibility, and data-preservation checks in `specs/002-level-selection/quickstart.md` against `/figma/levelauswahl-575-2535/`.
- [X] T015 Compare the rendered page against `specs/002-level-selection/figma-analysis.md` and record accepted protected-navbar and Bootstrap approximation deviations in `log.md` via `scripts/log_agent_step.sh`.
- [X] T016 Review `git diff --check` and `git status --short`; confirm only `backend/editor/templates/editor/figma_levelauswahl_575_2535.html`, `backend/editor/views.py`, `backend/editor/urls.py`, any required exact Figma asset, `specs/002-level-selection/`, and `log.md` changed for this feature.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately and establishes the protected scope.
- **Foundational (Phase 2)**: Depends on T001–T003; blocks rendered-route validation.
- **User Story 1 (Phase 3)**: Depends on T004–T005 and delivers the MVP.
- **User Story 2 (Phase 4)**: Depends on T006–T007 because it refines the same new template's information hierarchy.
- **User Story 3 (Phase 5)**: Depends on T006–T007 because it applies responsive behaviour to the same new template.
- **Polish (Phase 6)**: Depends on all desired user-story tasks.

### User Story Dependencies

- **US1 (P1)**: Depends only on the new isolated route and view; it is the recommended MVP.
- **US2 (P2)**: Refines the new template created by US1; it does not alter existing authoring forms or data contracts.
- **US3 (P3)**: Refines the new template created by US1; it does not alter existing components or CSS.

### Parallel Opportunities

- T001 and T002 can run in parallel because they are read-only reviews of different documentation and protected template areas.
- T003 can run alongside T001 and T002 after the worktree review is initiated.
- After T006–T007, US2's copy/accessibility review (T009–T010) and US3's responsive review (T011–T012) should be coordinated sequentially because they edit the same new template.
- T013 can run in parallel with manual validation preparation, but T014–T016 require the final page state.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T005 to create the isolated display route.
2. Complete T006–T008 to render the protected progress and helper components with visual-only controls.
3. Open the route and confirm the P1 independent-test criteria before refining content or responsiveness.

### Incremental Delivery

1. Deliver the P1 visual hierarchy with no side effects.
2. Deliver P2 exact labels and accessible control names without adding functional form behaviour.
3. Deliver P3 responsive stacking while retaining the protected components' existing mobile behaviour.
4. Complete cross-cutting validation and document intentional Figma differences.

## Notes

- Every task uses the required checklist format, task ID, and exact file path.
- `[P]` marks only tasks that can safely run in parallel.
- No automated test task is included because neither the specification nor the user requested TDD; T013–T016 provide the required validation coverage.
