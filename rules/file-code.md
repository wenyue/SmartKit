# Code Design Goals

Strength: `Default`

Scope: Writing, modifying, and reviewing code across languages, covering ownership, boundaries,
clarity, local consistency, state integrity, dependencies, abstractions, diagnostics, and
documentation.

## Ownership And APIs

- Give every behavior, state, invariant, and lifecycle one clear owner.
- Keep owner-local logic cohesive with its owner; move logic only when its reuse or boundary is real.
- Keep public interfaces minimal and aligned with stable product or domain capabilities.
- Meet test and call-site needs through the owning contract rather than widening APIs, moving
  owner-local logic, or adding indirection solely for convenience.

## Clarity And Abstraction

- Before editing code, inspect the target file and nearby implementations for comparable work.
  Follow their established naming, structure, control flow, and API patterns unless a more
  specific rule or an explicitly approved design requires a deliberate departure.
- Use names, types, and structure to make responsibilities, valid states, and the main decision path
  understandable locally.
- Keep side effects, failure modes, retries, fallbacks, and lifecycle transitions visible in the
  contract or control flow.
- Introduce an abstraction only when it represents a real concept, protects an invariant, or removes
  meaningful duplication while reducing maintenance cost.
- Avoid helpers, adapters, and generic layers that obscure ownership or serve only one trivial use.

## Diagnostics And Suppressions

- Do not suppress compiler, analyzer, or linter diagnostics at the configuration level. Use an
  inline or file-wide suppression only when resolving the diagnostic would violate the approved
  design or produce a materially worse result. Before each suppression, state its exact diagnostic,
  scope, and necessity, then obtain explicit user confirmation. General or prior approval does not
  authorize a later suppression.

## State And Dependencies

- Keep state mutation and lifecycle transitions predictable from creation through cleanup.
- Preserve valid dependency lifetimes across asynchronous work and callbacks.
- Give each unit only the capabilities it needs, with dependency direction and cross-layer
  boundaries explicit.
- Provide dependencies through visible owners and keep state placement consistent with that
  ownership.

## Documentation

- Decide whether to comment, what kind of comment to use, and how much detail to include by jointly
  weighing its purpose, the code's actual sharing and use boundaries, behavioral or contract
  complexity, information value, and comparable nearby code. Give local comment presence or
  absence, style, detail, and visual coherence real weight without making any factor the fixed
  priority or local practice the default answer. A well-grounded judgment may favor adding or
  omitting a comment without proving neighboring code wrong.
- Follow applicable explicit documentation syntax and formatting requirements; distinguish these
  requirements from observed habits, which inform the judgment above.
- Give shared and externally consumed interfaces deliberate documentation attention. Assess the
  actual contract: one caller can still consume a shared contract, language-level public visibility
  alone does not require documentation, and simple local functions need no blanket coverage.
  Document important caller constraints and behavior that names, types, and signatures do not make
  clear, including relevant invariants, lifecycle obligations, external requirements, and edge cases.
- Distinguish API documentation, which explains the caller's contract, from internal comments,
  which help readers understand the implementation, by purpose rather than placement. Keep internal
  comments concise, adding detail when understanding requires it. They may explain rationale,
  constraints, or tradeoffs, or briefly label logical sections when that improves reading and visual
  organization, inside or outside functions. A useful section label need not reveal hidden knowledge.
- Keep comments accurate and useful as code changes; update or remove stale or redundant text.
  Use section labels sparingly enough to preserve the flow of the code. Avoid line-by-line
  narration, repeated names, and edit history; when design is unclear, improve the design instead
  of explaining around it.
