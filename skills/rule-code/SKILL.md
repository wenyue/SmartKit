---
name: rule-code
description: Apply shared code policy when writing, modifying, or reviewing code in any language, including ownership, APIs, local patterns, abstractions, diagnostics, state, dependencies, failure outcomes, and comment decisions; also use for requested code-policy assessment.
---

# Code Design Goals

Strength: `Default`

Scope: Writing, modifying, and reviewing code across languages, covering ownership, boundaries,
clarity, local consistency, state integrity, dependencies, abstractions, and diagnostics, and
requested assessment of those concerns.

Apply this policy within the current code task. For a requested assessment, cover the requested
code and report supported findings and material evidence gaps within that request.

Before deciding comment coverage or whether a comment is needed, read
[rule-code-comment](../rule-code-comment/SKILL.md), including when omission may be appropriate.
Before deciding operation outcomes, failure propagation, or handling, read
[rule-error-handling](../rule-error-handling/SKILL.md), including routine existing propagation.
Those Skills own their policies and the conditions for loading their supporting resources.

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
