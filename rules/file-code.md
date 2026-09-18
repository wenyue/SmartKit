# Code Design Goals

Strength: `Default`

Scope: Writing, modifying, and reviewing code across languages, covering ownership, boundaries,
clarity, local consistency, state integrity, dependencies, abstractions, failure handling,
diagnostics, and documentation.

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

## Failure Handling

- Judge success, ordinary refusal or absence, contracted failure, and programming violations by the
  operation's promise, not representation, frequency, or retryability. Preserve failed outcomes and
  partial effects; catching a failure or restoring future usability alone does not justify defaults
  or success. Recovery must fulfill the promise or an accepted degraded or partial outcome.
- Keep infallible operations direct; language and project contracts own failure mechanisms.
  Introduce stable distinctions only for caller decisions, with translation at the owning boundary.
  Handle closed business vocabularies exhaustively when contracted; open protocols explicitly handle
  unknown outcomes, retaining failure and useful causes without disguising incidental failures as
  business refusal.
- Enforce production-required validation, control flow, side effects, and invariants independently
  of checks that can be disabled. Keep programming violations distinct from ordinary negatives.
- Handle failure only for owned recovery, cleanup, compensation, contract-required translation, or
  final handling; otherwise propagate through the accepted contract, including library-to-caller
  transfer. Give each independently initiated operation a final owner and every asynchronous or
  detached path owned completion, failure, and lifecycle. Guarantee owned cleanup across all paths,
  including cancellation and interruption.
- Consuming failure or delegating reporting retains responsibility for state, cleanup, retry, and
  feedback. Preserve observable unresolved outcomes, remaining effects, and available useful causes
  and diagnostics through final handling, distinguishing primary from recovery, cleanup, or
  compensation failures.
- Recovery needs a valid resulting state, feasible bounded action, and authority for its effects.
  Retry must address the cause and be safe across the complete path, including partial irreversible
  effects and any needed idempotency or compensation. Preserve important or sole-copy data until
  authority for the specific loss and a valid resulting state are established.
- Validate data where its syntax and meaning are understood; distinguish invalid content from failed
  I/O.
- Give each reportable incident one final report owner, allowing complementary diagnostics and
  audience feedback without propagation duplicates. Judge severity by impact, operational
  expectations, and needed response; levels and alerting are project-owned. Channel or recovery
  alone does not set severity, and recovered incidents may warrant investigation. Include useful
  context, impact, and disposition without credentials or needless private data.
- Assign remediation by actual capability and authority; specialist repair remains with qualified
  actors. The boundary responsible for product feedback distinguishes it from maintainer diagnostics,
  discloses material loss or unavailability even when users cannot repair it, and offers feasible
  actions or supported escalation when available. Remediation completion, failure, and mid-path stops
  remain owned and observable through channels appropriate to the audience and environment.
- Explain caller obligations and recovery rationale where code, types, and referenced contracts leave
  important meaning unclear, especially data-loss authority and retry safety.
- Decide whether failure-handling work is needed from these principles and the code and contract
  evidence. Following a clear existing propagation policy alone needs no separate workflow. When
  writing or materially changing a failure path, or choosing failure contracts, recovery, retry,
  data-loss, final-handling, or remediation policy, use
  [handle-operation-failure](../skills/handle-operation-failure/SKILL.md). Also use it for dedicated
  failure-handling assessment, diagnosis, or design.

## Documentation

- Keep comments accurate and useful as code changes; update or remove stale or redundant text.
- Follow the target's documentation language, syntax, and explicit formatting requirements.
- Meet applicable explicit comment-coverage requirements. Otherwise, decide whether comments are
  needed by jointly weighing purpose, actual use and sharing boundaries, behavioral and contract
  complexity, information not already clear in names, types, signatures, or code, and comparable
  local comment presence, absence, style, detail, and visual coherence. Weigh these factors without
  a fixed priority or treating local practice as the default answer; evidence can justify adding or
  omitting a comment without proving neighboring code wrong.
- Important caller obligations, invariants, lifecycle constraints, or edge cases left unclear can
  establish a need for comments. Give shared and externally consumed contracts deliberate attention
  even with one caller; public visibility alone does not require coverage. Simple, self-explanatory
  local code may remain uncommented when no explicit requirement applies.
- Decide routine comment need from these criteria and code or contract evidence alone, resolving
  material evidence gaps before deciding. Once writing or material revision is needed, use
  [write-code-comment](../skills/write-code-comment/SKILL.md). Also use it for dedicated code-comment
  or documentation-comment assessment, review, completion, cleanup, or migration.
