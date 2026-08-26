# Shared Portability

## Declare the portable boundary

Establish the candidate's cross-project owner, applicability, public loading and discovery route,
owned resources, and every required Rule, Skill, tool, schema, environment capability, or host
behavior. Each dependency must be explicitly declared and available through a supported shared or
target-owned route.

Use accepted user decisions, Issues, Specs, ADRs, governing contracts, observable shared
implementation, and representative target evidence. Do not use source-project policy, local naming,
directory accidents, context documents, or the source repository's mere ability to execute as
portable evidence.

## Select representative targets

Use at least one supported target context. Add another only when a materially different target seam
can change applicability, dependency availability, permissions, execution, or exits. A target that
differs only in names or layout adds no evidence.

The Semantic Fidelity and Ownership Reviewer checks portable ownership, applicability, dependency
closure, and source-project-only assumptions. The Agent Executability and Behavioral Closure
Reviewer applies the candidate to each representative target. When static and machine evidence
cannot establish concrete runtime feasibility with high confidence, route the affected target case
to Executable Acceptance.

Any undeclared dependency, invented target fact, or source-project-only assumption blocks
portability PASS even when the candidate passes in its source repository.
