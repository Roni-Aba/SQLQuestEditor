<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles: Delivery Workflow expanded with mandatory Figma MCP evidence.
- Added sections: none.
- Removed sections: none.
- Follow-up TODOs: TODO(RATIFICATION_DATE): The original adoption date is not recorded.
-->
# SQL Quest Editor Constitution

## Core Principles

### I. Preserve Functional Contracts
Existing Django views, URL names, form field names, session formats, JSON structures, and JavaScript
DOM hooks MUST remain compatible unless a change is explicitly requested and all affected contracts
are updated together. Regressions in the level-authoring flow take priority over visual refinements.

Rationale: the editor's multi-step workflow depends on server-side and client-side contracts that
are shared across templates and form handlers.

### II. Design-Driven, Server-Rendered Delivery
Figma is the visual reference for design work, while Django templates remain the delivery mechanism.
New Figma implementations MUST use a new root template, a new pure render view, and exactly one new
route; existing templates, components, partials, and routes MUST NOT be repurposed or changed for
that request. Views created for Figma rendering MUST NOT add persistence, session, upload, or POST
logic without a separate backend mandate.

Rationale: independent render pages protect the working editor flow while making design work
traceable to its source mockup.

### III. Bootstrap-First and Component-Safe UI
New frontend markup MUST use Bootstrap 5 utilities and semantic HTML. Existing reusable Django
components and partials MUST be included unchanged when their documented contracts fit; otherwise,
new Bootstrap markup belongs in the new template. New CSS files, changes to existing CSS, inline
styles, CSS variables, custom utility classes, and frontend build systems are prohibited for
design-driven work.

Rationale: this keeps the UI consistent with the project stack and prevents isolated styling from
overriding protected, completed components.

### IV. Accessibility and Responsive Behaviour Are Requirements
Every new or materially changed user interface MUST provide semantic landmarks and heading order,
visible labels for controls, meaningful alternative text, appropriate button types, and relevant
ARIA attributes. Layouts MUST be mobile-first and use Bootstrap containers, grids, spacing, and
responsive utilities rather than device-specific custom styling.

Rationale: the editor must remain usable with assistive technology and across the supported desktop
and mobile contexts.

### V. Evidence-Based Quality and Traceability
Each completed work action MUST be recorded immediately in `log.md` using
`scripts/log_agent_step.sh`, excluding the logging call itself. Changes MUST be proportionately
validated: run `python manage.py check` for Django changes, exercise relevant tests where present,
and visually inspect user-facing design work. Failures or unavoidable Bootstrap-versus-Figma
differences MUST be documented rather than concealed.

Rationale: traceable decisions and repeatable validation make a design-driven application safer to
evolve.

## Technical Constraints

The application MUST remain a Django 4.2 server-rendered project. Bootstrap 5.3.3 and Bootstrap
Icons are the standard frontend dependencies; React, Vue, Tailwind, npm build pipelines, and a
replacement frontend architecture are out of scope unless the constitution is amended first.

For Figma work, new templates MUST extend `editor/base.html`. Static Figma exports MUST be stored
under `backend/editor/static/editor/img/figma/`; temporary design-tool URLs MUST NOT be committed.
Protected backend modules, migrations, configuration, existing CSS, and completed component layouts
MUST NOT be changed without an explicit, scoped request.

## Delivery Workflow

Work MUST begin with a read-only inspection of the applicable project guidance, affected templates,
contracts, and current worktree state.

For every Figma-based feature, a GitHub work item or equivalent work item MUST exist before
specification begins. It MUST contain the Figma file URL, node ID, confirmed semantic page name,
intended outcome, and high-level acceptance criteria. The Figma node MUST NOT be loaded before the
page name has been confirmed.

The Figma Design-to-Code skill and the Figma-MCP integration MUST be used before specification,
before implementation, and during the final convergence check. The analysis MUST be stored as
`figma-analysis.md` in the active Spec Kit feature directory. It MUST record the Figma reference,
layout, visible content, components, states, interactions, assets, open questions, and accepted
deviations.

The specification MUST link to the Figma analysis. The implementation plan MUST map Figma elements
to existing Django components or new Bootstrap markup and MUST document all contract-sensitive
decisions. Implementations MUST follow the analysis, specification, plan, and all protected project
contracts. Temporary Figma URLs MUST NOT be committed.

Before handoff, contributors MUST review the diff for unrelated changes, preserve existing user
work, and report validation results and any intentional deviations. Documentation changes MUST keep
`mkdocs build --strict` viable when documentation tooling is available.

## Governance

This constitution governs project practices and overrides conflicting informal conventions. An
amendment MUST document the affected principles, rationale, migration impact, and semantic version
bump in the Sync Impact Report. MAJOR versions are required for incompatible removals or
redefinitions, MINOR versions for new principles or material expansions, and PATCH versions for
clarifications that do not change obligations.

Every code review and task handoff MUST check compliance with these principles, including contract
preservation, Bootstrap-only frontend changes, action logging, and proportionate validation.
Exceptions require an explicit user-approved scope and MUST be documented with their risk and
follow-up work. Operational guidance in `AGENTS.md` is the runtime companion to this constitution.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date is not recorded | **Last Amended**: 2026-09-06
