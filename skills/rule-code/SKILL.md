---
name: rule-code
description: Use for work involving code in any language, including requested code-policy assessment.
---

# Code Design Goals

## Ponytail Loading

Before making decisions in any coding task, read [ponytail](../ponytail/SKILL.md).

## Keep Behavior and APIs with Their Owners

Give every behavior, state, invariant, and lifecycle one clear owner. Keep owner-local logic with
its owner; move logic only when its reuse or boundary is real.

Align public interfaces with stable product or domain capabilities. Meet test and call-site needs
through the owning contract rather than widening APIs, moving owner-local logic, or adding
indirection solely for convenience.

## Make State and Dependencies Explicit

Provide dependencies through visible owners and keep state placement consistent with that
ownership. Give each unit only the capabilities it needs, with dependency direction and cross-layer
boundaries explicit.

Keep state mutation and lifecycle transitions predictable from creation through cleanup. Preserve
valid dependency lifetimes across asynchronous work and callbacks.

Keep side effects, failure modes, retries, fallbacks, and lifecycle transitions visible in the
contract or control flow.

## Use Local Evidence for Code Structure

Before editing code, inspect the target file and nearby implementations for comparable work.
Follow their established naming, structure, control flow, and API patterns unless a more specific
rule or an explicitly approved design requires a deliberate departure.

## Retain Diagnostics

Do not suppress compiler, analyzer, or linter diagnostics at the configuration level. Use an inline
or file-wide suppression only when resolving the diagnostic would violate the approved design or
produce a materially worse result.

Before each suppression, state its exact diagnostic, scope, and necessity, and obtain explicit user
confirmation covering that suppression. Reuse an existing confirmation that covers the same
diagnostic, scope, and necessity. General approval or approval of another suppression does not
authorize a new or broader one.
