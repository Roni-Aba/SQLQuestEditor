# Research: Level Basics Display

## Decision 1: Keep the page visual-only

- **Decision**: Render the two text fields as read-only visual controls and render the image and navigation actions as non-submitting display controls.
- **Rationale**: Figma shows their appearance but supplies no evidence for POST targets, uploads, persistence, sessions, validation, or navigation destinations. The governing issue and constitution prohibit inferring that backend behaviour.
- **Alternatives considered**: Reuse the existing level-basics multipart form; rejected because it would connect the page to existing upload, submit, session, and JavaScript contracts outside the requested scope.

## Decision 2: Reuse protected status and helper components

- **Decision**: Include the existing status-bar and helper components unchanged and provide only their documented context values from the new view/template.
- **Rationale**: Both map directly to the progress and Cosmo guidance in Figma, retaining project styling and accessibility contracts.
- **Alternatives considered**: Recreate progress circles and Cosmo markup in the new page; rejected because it duplicates protected project components and risks visual/semantic drift.

## Decision 3: Use responsive Bootstrap layout instead of absolute positioning

- **Decision**: Translate Figma's desktop arrangement to a responsive container and grid with semantic sections in reading order.
- **Rationale**: The Figma node is absolutely positioned but has no mobile design. The project requires Bootstrap-only, mobile-first behaviour without custom CSS.
- **Alternatives considered**: Copy Figma coordinates through inline styling or a page stylesheet; rejected because both violate project rules and do not provide responsive behaviour.

## Decision 4: Handle the Cosmo image without temporary URLs

- **Decision**: First use the existing helper-supported Cosmo asset if it matches the reference sufficiently; otherwise download the exact Figma export as a permanent static asset before implementation uses it.
- **Rationale**: Figma MCP URLs expire and cannot be committed. The helper component already provides safe static image loading.
- **Alternatives considered**: Reference the temporary Figma MCP URL; rejected because it expires and violates the asset policy.

## Decision 5: Preserve the protected navigation divergence

- **Decision**: Extend the existing base template and accept its navigation as-is.
- **Rationale**: Figma shows `Anleitung`, but the protected navbar has fixed project links. Altering it would change an unrelated shared contract.
- **Alternatives considered**: Add a page-specific navigation or change the shared navigation; rejected because the base/navbar are protected and a duplicate navigation would break consistency.
