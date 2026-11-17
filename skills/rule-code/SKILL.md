---
name: rule-code
description: Use for work involving code in any language, including requested code-policy assessment.
---

# Code Design

Treat code quality as part of the outcome, not optional polish. Aim for elegant, well-crafted implementations: clear intent and direct control flow that solve the actual problem with the minimum necessary machinery. Favor maintainable clarity over cleverness; preserve correctness and keep improvements within the requested scope.

Keep behavior understandable through its owners. Choose structure for the work needed to understand and change it, rather than for shorter callers or more reusable-looking interfaces.

## Choose a boundary that earns its cost

Give every behavior, state, invariant, and lifecycle one clear owner. Keep owner-local logic and the reasoning needed to understand and change it together.

Keep short, straightforward, single-use logic in its caller by default. Extract only when the result materially reduces the total effort needed to understand and change the behavior. Useful reasons include:

- A distinct responsibility, invariant, or domain concept.
- Actual production reuse.
- Substantial branching, state, or lifecycle complexity.
- Dependency isolation.

Weigh the benefit against the added functions, types, files, APIs, and navigation. Use the smallest boundary that realizes it; a private helper in the same file may be enough. Retain enough cohesive control flow in the caller to make the operation understandable.

Shortening a caller, naming a small block, line counts, and hypothetical reuse do not by themselves justify extraction. Exercise private logic through its owning behavior. A test seam needs a responsibility or dependency boundary justified by the production design, independently of the wish to test private logic directly.

### Keep failure handling and public APIs with their owners

Keep failure handling with its owning operation. Catch/log/default repetition alone does not justify a callback wrapper, even across callers. Require a coherent responsibility beyond the template, such as cleanup, transaction completion, required failure-contract translation, or substantive recovery; judge that responsibility rather than function length.

Align public interfaces with stable product or domain capabilities. Meet test and call-site needs through the owning contract rather than widening APIs, moving owner-local logic, or adding indirection solely for convenience.

## Make state, effects, and lifetimes visible

Provide dependencies through visible owners and keep state placement consistent with that ownership. Give each unit only the capabilities it needs, with dependency direction and cross-layer boundaries explicit.

Keep state mutation and lifecycle transitions predictable from creation through cleanup. Preserve valid dependency lifetimes across asynchronous work and callbacks.

Keep side effects, failure modes, retries, fallbacks, and lifecycle transitions visible in the contract or control flow.

## Align implementation style with comparable code

Keep code of the same kind consistent in organization and style. Use the codebase's existing implementations and project conventions as references for clarity, cohesion, and visual appeal.

If comparable implementations are inconsistent or absent, follow an established project convention where one exists; otherwise choose a cohesive style that fits the surrounding code. A more specific rule or an explicitly approved design can justify deliberate departures.

## Resolve diagnostics before considering suppression

Do not suppress compiler, analyzer, or linter diagnostics at the configuration level. Use an inline or file-wide suppression only when resolving the diagnostic would violate the approved design or produce a materially worse result.

Before each suppression, state its exact diagnostic, scope, and necessity, and obtain explicit user confirmation covering that suppression. Reuse an existing confirmation that covers the same diagnostic, scope, and necessity. General approval or approval of another suppression does not authorize a new or broader one.
