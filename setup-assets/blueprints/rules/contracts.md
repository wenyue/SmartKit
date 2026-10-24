# Contracts

## Purpose and evidence

For an independent request to create or revise `.agents/rules/contracts.md`, use `write-rules-and-skills` to produce one target-owned Rule titled `Contracts` that defines what makes a change valid.

Establish the target repository from the accepted request and current evidence. The Author discovers and qualifies relevant target evidence: entry guidance and applicable Rules; accepted Issues, Specs, and ADRs; APIs, schemas, events, domain models, implementation, and behavioral tests; and ownership and delivery relationships in registries, synchronizers, manifests, packages, loaders, and documentation routes. Reuse qualified caller-supplied evidence and discover missing facts directly; the caller need not prepare an evidence packet. Qualify sources by owner and provenance. Existing Rule text is preservation and regression evidence, not design authority; visibility, historical text, machine-local state, and write access confer no authority.

Classify each obligation as preserve, change, add, retire, or non-goal. Changes, additions, retirements, exceptions, and compatibility requirements need accepted intent and qualified evidence. Otherwise preserve supported behavior, or stop if its disposition would change an outcome.

## Policy to establish

For each evidenced policy, make its activating condition, observable outcome, exact exceptions, precedence, and decision owner clear, including the nearest included and excluded cases. Cover:

- **Consumer contracts:** state, compatibility, lifecycle, concurrency, cancellation, migration, persistence, and cleanup.
- **Canonical ownership:** the input owner and the distinct transformation, adapter, transport, installation, and delivery consequences of changing that input.
- **Managed state:** claim, preservation, conflict, replacement, and retirement of owned files, structured fields, digests, and managed configuration.
- **Documentation:** authority and exposure of public versus contributor material and canonical versus derived language.
- **Evaluation:** structural, executable, and natural-language boundaries, and the evidence change that invalidates an earlier verdict.
- **Contract evolution:** coherent changes to implementation, documentation, tests, validation, persisted state, and callers; compatibility and recovery remain only when current correctness requires them.
- **Distribution:** direction of delivery, hard dependencies, visibility, and public/private exposure.

Installed SmartKit governance determines Rule precedence. Material alternatives in activation, applicability, outcomes, exceptions, precedence, ownership, preservation, or retirement require a decision; unsupported facts cannot select or silently omit policy.

Tools and Skills retain command discovery, preparation, mutation, synchronization, testing, and verification procedures. The structure owner retains placement advice. Include live-owner facts only when their omission changes policy; inventories, implementation recipes, and generic architecture guidance add no contract meaning.

## Refresh focus

Treat accepted project contracts and their reasons as durable. Recheck their current owners in API and schema definitions, behavioral tests, delivery boundaries, and accepted architectural decisions. Change the Rule when those sources establish a changed obligation, supported exception, ownership boundary, or compatibility decision; a new wording preference alone does not warrant rewriting it.

Concentrate on consequential included and excluded cases, such as whether a change preserves a consumer contract or requires a migration. Preserve still-valid project additions and exceptions. When an obligation changes, replace its affected definition and reconcile neighboring references instead of keeping both versions. With unchanged meaning, retain the complete existing Rule.

## Authoring boundary and acceptance

The Author may inspect target evidence, run owner-supported read-only or non-fixing checks, and create or replace `.agents/rules/contracts.md` beneath the Candidate root authorized for this request. Settle that root, exact path and operation through the public writer before writing. No fixed staging directory is required. Deletion, moves, live-target writes, unrelated mutation, and external effects require separate accepted authority.

The public writer owns authoring, review, and terminal results. Acceptance for this Rule requires every supported predicate, obligation, and affected surface to have an evidenced policy outcome: each supported input selects exactly one outcome without invented facts. Required checks must pass; omitting a check needs evidence that it is not applicable.

Include target and evidence owners, obligation dispositions, check results, preserved constraints, and uncertain or untested surfaces in the writer's handoff. For an unresolved access, evidence, or authority gap, identify the blocker, its owner and consequence, and what would enable continuation. The handoff must be independently usable by the caller and grants no downstream installation, publication, commit, or push.
