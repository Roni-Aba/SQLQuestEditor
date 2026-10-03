# Feature Specification: Level Basics Display

**Feature Branch**: `002-level-selection`
**Created**: 2026-09-12
**Status**: Draft
**Input**: GitHub issue [#3](https://github.com/Roni-Aba/SQLQuestEditor/issues/3): Figma: levelauswahl (575:2535)

## Design Reference

The visual and interaction reference is documented in [figma-analysis.md](figma-analysis.md). It is binding for the visible page content, hierarchy, and known deviations.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View level basics (Priority: P1)

As a level author, I want to view the level-basics screen with its prompts and progress indicator so that I understand which information belongs at the first stage of level creation.

**Why this priority**: The screen’s primary value is making the first level-creation stage understandable through its visible hierarchy and prompts.

**Independent Test**: Open the new screen and verify the eight-step indicator, character guidance, two labelled text-entry areas, background-image action, and navigation actions are visible together.

**Acceptance Scenarios**:

1. **Given** a level author opens the screen, **When** it is displayed at desktop width, **Then** the progress indicator, guidance area, and level-basics controls are clearly visible without overlapping.
2. **Given** a level author views the progress indicator, **When** the screen is first displayed, **Then** it visibly identifies step 1 as the active stage and shows steps 2 through 8 as subsequent stages.

---

### User Story 2 - Understand required level information (Priority: P2)

As a level author, I want clear prompts for a level name, a background image, and a user greeting so that I know the information expected in this stage.

**Why this priority**: Clear labels and guidance reduce uncertainty before authors enter the next creation step.

**Independent Test**: Review the screen text and confirm that each of the three requested pieces of information is named and that both text-entry areas show the visible placeholder.

**Acceptance Scenarios**:

1. **Given** a level author reads the main controls, **When** the form area is visible, **Then** it includes the prompts “Verrate mir doch bitte wie das Level heißen soll” and “Wie soll der Nutzer des Levels begrüßt werden?”.
2. **Given** a level author views either text-entry area, **When** no text has been supplied, **Then** it displays “Schreibe hinein”.
3. **Given** a level author views the background-image area, **When** the action is visible, **Then** its purpose is communicated as uploading a desired background image.

---

### User Story 3 - Access the screen on narrow displays (Priority: P3)

As a level author on a narrow display, I want the guidance and controls arranged in a readable order so that I can review every visible part of the screen without horizontal scrolling.

**Why this priority**: The desktop arrangement is the supplied reference, while basic readability and reachability must be retained on smaller screens.

**Independent Test**: Display the screen at a 320 px viewport width and verify that its visible sections can be reached by vertical scrolling only.

**Acceptance Scenarios**:

1. **Given** the screen is shown on a narrow display, **When** the desktop columns cannot fit, **Then** the guidance and control areas stack in logical reading order.
2. **Given** the screen is shown on a narrow display, **When** an author moves through its controls, **Then** the focus order follows the visible reading order.

### Edge Cases

- When a narrow viewport cannot show all eight progress steps at once, each step remains identifiable without clipping the active step.
- When no level information is available, both text-entry areas retain their visible placeholder text.
- When the background-image action is unavailable for interaction on this display-only screen, its label still communicates the intended action without changing level data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated, independently accessible screen for the Figma reference in issue #3.
- **FR-002**: The screen MUST visibly present an eight-step level-creation indicator and distinguish step 1 from steps 2 through 8.
- **FR-003**: The screen MUST visibly present the character illustration and the accompanying guidance text shown in the Figma reference.
- **FR-004**: The screen MUST visibly present prompts for the level name and user greeting, each with the placeholder “Schreibe hinein”.
- **FR-005**: The screen MUST visibly present an action for uploading a desired background image.
- **FR-006**: The screen MUST visibly present “Zurück” and “Weiter” as separate navigation actions.
- **FR-007**: The screen MUST preserve the visual reading order and full reachability of its required content on narrow displays without horizontal page scrolling.
- **FR-008**: The screen MUST provide an accessible name for every visible interactive control and meaningful alternative text for the character illustration.
- **FR-009**: Opening or interacting with this new display-only screen MUST NOT alter existing level data, start uploads, submit information, or change established authoring workflows.
- **FR-010**: The feature MUST leave all existing screens, shared components, navigation behaviour, and established level-authoring contracts unchanged.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a desktop-sized display, a reviewer can identify the active first step, the two text prompts, background-image action, and both navigation actions within 15 seconds of opening the screen.
- **SC-002**: In a manual review, 100% of the required visible labels match the Figma reference, including the two prompts, “Schreibe hinein”, “Zurück”, and “Weiter”.
- **SC-003**: At a 320 px viewport width, 100% of required visible content is reachable with vertical scrolling only.
- **SC-004**: In an accessibility review, 100% of visible interactive controls have accessible names and the character illustration has non-empty alternative text.
- **SC-005**: In a navigation and data-preservation check, opening and using the display-only controls causes 0 changes to existing level information.

## Assumptions

- The confirmed semantic page name remains `levelauswahl`, although the supplied Figma node visibly depicts level basics; this naming discrepancy is recorded as an open question in the design analysis.
- The new screen is visual-only and does not introduce level creation, upload, save, or navigation behaviour beyond what is already established elsewhere.
- The supplied Figma node is the approved desktop reference; narrow-screen behaviour follows its visible hierarchy rather than an additional mobile mockup.
- The existing global navigation remains unchanged even though the Figma navigation visibly includes “Anleitung”; the accepted deviation is recorded in the design analysis.
