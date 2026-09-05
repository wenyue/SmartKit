# Project Contracts

Strength: `Mandatory`

Scope: Setup Authoring Contract for persistent change-validity policy across APIs, capability
ownership, installation, documentation, evaluation, contract evolution, distribution, hard
dependencies, and exposure.

## Purpose and evidence

For a `setup-project-agents` request targeting `.agents/rules/01-project-contracts.md`, the Author
produces one target-owned Mandatory Rule titled `Project Contracts`. It defines what makes a
change valid whenever the change touches a concern in this Scope.

Setup must supply relevant target evidence: entry guidance and narrower Rules; accepted Issues,
Specs, and ADRs; APIs, schemas, events, domain models, implementation, and behavioral tests; and
ownership and delivery relationships in registries, synchronizers, manifests, packages, loaders,
and documentation routes. Qualify sources by owner and provenance. Existing Rule text is
preservation and regression evidence, not design authority; visibility, historical text,
machine-local state, and write access confer no authority.

Classify each obligation as preserve, change, add, retire, or non-goal. Changes, additions,
retirements, exceptions, and compatibility requirements need accepted intent and qualified
evidence. Otherwise preserve supported behavior, or stop if its disposition would change an outcome.

## Policy to establish

For each evidenced policy, make its activating condition, observable outcome, exact exceptions,
precedence, and decision owner clear, including the nearest included and excluded cases. Cover:

- **Consumer contracts:** state, compatibility, lifecycle, concurrency, cancellation, migration,
  persistence, and cleanup.
- **Canonical ownership:** the input owner and the distinct transformation, adapter, transport,
  installation, and delivery consequences of changing that input.
- **Managed state:** claim, preservation, conflict, replacement, and retirement of owned files,
  structured fields, digests, and setup-managed state.
- **Documentation:** authority and exposure of public versus contributor material and canonical
  versus derived language.
- **Evaluation:** structural, executable, and natural-language boundaries, and the evidence change
  that invalidates an earlier verdict.
- **Contract evolution:** coherent changes to implementation, documentation, tests, validation,
  persisted state, and callers; compatibility and recovery remain only when current correctness
  requires them.
- **Distribution:** direction of delivery, hard dependencies, visibility, and public/private exposure.

The narrowest current authority governs a supported conflict. Material alternatives in activation,
applicability, outcomes, exceptions, precedence, ownership, preservation, or retirement require a
decision; unsupported facts cannot select or silently omit policy.

Tools and Skills retain command discovery, setup, mutation, synchronization, testing, and
verification procedures. The structure owner retains placement advice. Include live-owner facts
only when their omission changes policy; inventories, implementation recipes, and generic
architecture guidance add no contract meaning.

## Author boundary and result

The Author may inspect target evidence, run owner-supported read-only or non-fixing checks, and
create or replace `GENERATED/.agents/rules/01-project-contracts.md` under setup's request root.
Deletion, moves, live-target writes, unrelated mutation, and external effects require separate
accepted authority.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Material policy alternatives remain, or a required operation, effect, owner, comparison point, exception, or obligation disposition lacks accepted authority. |
| `VALIDATION_FAILED` | A required check fails, or a supported predicate, obligation, affected surface, or Author operation lacks an evidenced outcome or grant. |
| `READY` | Every required mapping is present, each supported input selects exactly one observable policy outcome without invented facts, and all applicable deterministic checks pass or are evidenced as `NOT_REQUIRED`. |

A stop names the blocker, owner, consequence, and condition for a fresh attempt. A ready handoff
identifies the Candidate, target and evidence owners, obligation dispositions, checks, preserved
constraints, and uncertain or untested surfaces. It is input to `setup-project-agents`; it grants
no downstream installation, publication, commit, or push.
