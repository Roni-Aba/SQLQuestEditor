# Feature Specification: Level Creation Overview

**Feature Branch**: `001-level-overview`
**Created**: 2026-09-06
**Status**: Draft
**Input**: GitHub issue [#1](https://github.com/Roni-Aba/SQLQuestEditor/issues/1): Figma overview (45:1891)

## Design Reference

The visual and interaction reference is documented in [figma-analysis.md](figma-analysis.md). It is binding for the visible page content, hierarchy, and known deviations.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open an editing area (Priority: P1)

As a level author, I want to open the central overview and clearly see the four individual editing areas so that I can continue work on the part of a level I need.

**Why this priority**: Direct access to individual editing areas is the main purpose of the overview and is required to make the authoring workflow usable.

**Independent Test**: Open the overview and verify that Levelgrunddaten, SQL Beschränkungen, Systemnachrichten, and Gegenstände are all visible and selectable.

**Acceptance Scenarios**:

1. **Given** a level author opens the overview, **When** the page is displayed on a desktop-sized screen, **Then** all four individual editing actions are visible in a dedicated left-hand area.
2. **Given** a level author selects an individual editing action, **When** the action is activated, **Then** the author is taken to the corresponding existing editing area without changing the level data as part of this navigation.

---

### User Story 2 - Choose guided creation (Priority: P2)

As a level author, I want a prominent guided-creation option and a short explanation so that I can choose between step-by-step guidance and direct editing.

**Why this priority**: The guided flow reduces uncertainty for authors who do not know the creation sequence.

**Independent Test**: Open the overview and verify that the explanation, the character image, and the guided-creation action are visible together and that the action opens the existing guided flow.

**Acceptance Scenarios**:

1. **Given** a level author opens the overview, **When** the central explanation is read, **Then** it explains both the guided and the direct-editing paths.
2. **Given** a level author chooses “Geführte Levelerstellung”, **When** the action is activated, **Then** the existing guided creation flow opens.

---

### User Story 3 - Use the overview on a small screen (Priority: P3)

As a level author using a small screen, I want the overview content to remain readable and reachable so that I can choose an editing path without horizontal scrolling.

**Why this priority**: Mobile access is secondary to the desktop authoring experience, but the feature must remain usable across supported screen sizes.

**Independent Test**: Display the overview at a narrow viewport and verify that its action groups stack in a readable order with every action reachable.

**Acceptance Scenarios**:

1. **Given** the overview is shown on a narrow screen, **When** the layout changes from the desktop arrangement, **Then** the action groups stack in a logical reading order.
2. **Given** the overview is shown on a narrow screen, **When** an author scrolls through the page, **Then** all six visible actions remain reachable without horizontal scrolling.

### Edge Cases

- When a narrow viewport cannot retain three columns, the page presents the action groups in reading order rather than clipping or overlapping them.
- When an author opens the page after returning from an existing editing flow, the overview does not alter their previously entered level information.
- When a navigation target is temporarily unavailable, the visible overview labels and explanatory content still remain understandable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated level-creation overview that authors can open independently of the existing editing pages.
- **FR-002**: The overview MUST visibly present the individual actions “Levelgrunddaten”, “SQL Beschränkungen”, “Systemnachrichten”, and “Gegenstände”.
- **FR-003**: The overview MUST visibly present “Geführte Levelerstellung” and “Level speichern”.
- **FR-004**: The overview MUST provide a plain-language explanation that distinguishes the guided path from direct editing.
- **FR-005**: Selecting any visible editing or guided-creation action MUST lead to its corresponding existing workflow and MUST NOT itself modify level information.
- **FR-006**: The overview MUST present its content as three clearly distinguishable groups on desktop-sized screens: individual editing actions, explanation with character image and save action, and guided creation.
- **FR-007**: The overview MUST adapt to narrow screens so that every visible action and explanatory text remains readable and reachable without horizontal scrolling.
- **FR-008**: The overview MUST preserve existing authoring, navigation, and data-entry behavior outside this new entry page.
- **FR-009**: The overview MUST expose meaningful labels for interactive controls and provide meaningful alternative text for the character image.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a desktop-sized screen, a reviewer can identify all six required actions and the explanatory text within 10 seconds of opening the overview.
- **SC-002**: In a manual navigation check, 100% of the five navigation actions open their intended existing workflow without modifying level data before the target workflow is used.
- **SC-003**: At 320 px viewport width, all six required actions and the explanatory text can be reached with vertical scrolling only.
- **SC-004**: In an accessibility review, 100% of interactive controls have an accessible name and the character image has non-empty alternative text.

## Assumptions

- The existing individual-editing, guided-creation, and save destinations remain available and retain their current behavior.
- This feature introduces an overview only; it does not introduce new level fields, permissions, persistence rules, or authoring steps.
- The supplied Figma node is the approved visual reference for the desktop arrangement.
- The existing global navigation remains unchanged even though the Figma navigation includes “Anleitung”; the accepted deviation is recorded in the design analysis.
