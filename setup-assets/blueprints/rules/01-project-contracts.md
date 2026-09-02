# Project Contracts

Strength: `Mandatory`

Scope: Setup Authoring Contract for the target repository's persistent change-validity policy
across APIs, capability ownership, installation, documentation, evaluation, contract evolution,
distribution, hard dependencies, and exposure.

## Contract frame

When `setup-project-agents` requests `.agents/rules/01-project-contracts.md`, author that one
target-owned Mandatory Rule titled `Project Contracts`. It applies when a change affects any concern
in this contract's Scope and owns the persistent conditions that make the change valid.

Use accepted project intent and evidence qualified by its target-repository owner and provenance.
Relevant evidence includes entry guidance and narrower Rules; accepted Issues, Specs, and ADRs;
public APIs, schemas, events, domain models, implementation, and behavioral tests; canonical-source
and delivery relationships in registries, synchronizers, manifests, ownership records, packages,
loaders, and documentation routes. The existing target Rule is preservation and regression evidence,
not design authority. Visibility, historical text, machine-local state, or write access grants no
meaning or permission.

Classify every inherited or proposed obligation as preserve, change, add, retire, or non-goal. A
change, addition, retirement, exception, or compatibility requirement needs accepted intent and
qualified evidence; otherwise preserve the supported current behavior or stop when its disposition
would change an outcome.

## Required policy

For every supported condition and its nearest included and excluded cases, state the activating
predicate, required observable outcome, exact exception, precedence, and decision owner. Include all
evidenced mappings for:

- consumer-facing contracts, including state, compatibility, lifecycle, concurrency, cancellation,
  migration, persistence, and cleanup behavior;
- canonical input ownership and the distinct transformation, adapter, transport, installation, and
  delivery outcomes that follow when that input changes;
- setup-managed claim, preservation, conflict, replacement, and retirement outcomes for owned files,
  structured fields, digests, and managed state;
- documentation authority and exposure, including public versus contributor material and canonical
  versus derived language;
- structural, executable, and natural-language evaluation boundaries, including the evidence change
  that invalidates a prior verdict;
- coherent contract evolution across implementation, documentation, tests, validation, persisted
  state, and callers, retaining compatibility or recovery only when current correctness requires it;
  and
- distribution direction, hard dependency, visibility, and public/private exposure boundaries.

The narrowest current authority governs a supported conflict. Materially different supported
activation, applicability, outcome, exception, precedence, ownership, preservation, or retirement
policies require a decision stop; unsupported facts cannot silently select or omit a policy.

Keep command discovery, setup mechanics, mutation, synchronization, testing procedure, and
verification procedure with their owning tools and Skills. Keep placement advice with the project
structure owner. Exclude inventories, implementation recipes, generic architecture guidance, and
facts recoverable from a live owner unless omission would change a policy outcome.

## Author grant and terminal result

The future Author may inspect target evidence, run owner-supported read-only or non-fixing checks,
and create or replace only `GENERATED/.agents/rules/01-project-contracts.md`, where `GENERATED` is
the request root supplied by `setup-project-agents`. The Author may not delete or move that
Candidate, write the live target, mutate unrelated target state, or create an external effect
without separate accepted authority.

Return exactly one terminal result; the first matching discriminator has precedence:

1. `ACCESS_REQUIRED` when necessary evidence or validation cannot be accessed within the grant.
2. `CONTEXT_REQUIRED` when access exists but a necessary fact cannot be discovered from qualified
   evidence.
3. `HUMAN_DECISION_REQUIRED` when qualified evidence permits materially different policies or a
   required operation, effect, owner, comparison point, exception, or obligation disposition lacks
   accepted authority.
4. `VALIDATION_FAILED` when a required check remains failed or any supported predicate, obligation,
   affected surface, or Author operation lacks one evidenced outcome or grant.
5. `READY` when the Candidate contains every required mapping, each supported input selects exactly
   one observable policy outcome, no conclusion requires an unsupported project fact, and all
   applicable owner-supported deterministic checks pass or are recorded `NOT_REQUIRED`.

Every stop identifies the blocker, owner, consequence, and condition for a fresh attempt. `READY`
reports the Candidate, target owner, evidence owners, obligation dispositions, checks, preserved
constraints, and uncertain or untested surfaces. It is ready input only for
`setup-project-agents` and grants no downstream installation, publication, commit, or push.
