---
name: rule-error-handling
description: Use for work involving operation outcomes or error behavior, including requested assessment.
---

# Error Handling

## Preserve the Promised Outcome

Classify success, ordinary refusal or absence, contracted failure, and programming violations by
the operation's promise, independently of their representation, frequency, or retryability.

Keep failed outcomes and partial effects visible. Catching an error, supplying a default, or
restoring future usability does not establish success: the current operation must fulfill its
promise or an accepted degraded or partial outcome.

Keep infallible operations direct. Use the language's native mechanisms and the project's actual
contracts, introducing stable distinctions where callers need different decisions. Translate at
the boundary that owns the contract. Cover a closed business vocabulary exhaustively; for an open
protocol, preserve an explicit unknown-failure path and useful causes rather than converting
incidental failures into ordinary refusal.

Keep programming violations distinct from ordinary negatives. Production-required validation,
control flow, side effects, and invariants must remain enforced when optional checks are disabled.

Validate data where its syntax and meaning are understood, distinguishing invalid content from
failed I/O. Explain important caller obligations where code, types, and referenced contracts leave
them unclear.

## Keep Public Failure Contracts Deliberate

Prefer a semantically accurate existing failure contract. A new public distinction can clarify
handling or diagnosis, but it also adds caller knowledge, handling choices, and a compatibility
commitment. Require a concrete benefit that justifies those costs, including when the distinction
only provides optional detail.

Before adding a publicly consumable failure distinction, ask the user and obtain explicit agreement
to the concrete addition unless it qualifies as a faithful refinement below. This applies across
native error mechanisms: exception types, error identities or codes, result cases, and newly
inspectable underlying failures can all add a public failure contract. Existing explicit agreement
covering the addition remains valid; general authorization to implement a feature is insufficient.

A faithful refinement preserves a semantically accurate, concrete language or standard-library
failure category and its promised recognition, information, and handling behavior. Existing
category-level handling must remain valid without caller adaptation; callers may opt into the
specific detail. Establish this through the language's native matching or classification mechanism;
inheritance is not required. Merely inheriting a generic exception base or implementing a generic
error interface does not qualify. This exception removes only the additional user-agreement
requirement, not the cost judgment or responsibility to preserve supported contracts.

## Assign Ownership Through Completion

Handle failures for owned recovery, cleanup, compensation, required contract translation, or final
handling; otherwise propagate faithfully through the accepted contract. A library may fulfill its
responsibility by transferring the failed outcome to its caller.

Give each independently initiated operation a final owner. Required asynchronous work belongs to
the operation's completion promise; detached work needs its own completion, failure, and lifecycle
ownership. Guarantee owned cleanup through success, failure, cancellation, and interruption.

Consuming a failure or delegating reporting retains responsibility for remaining state, cleanup,
retry, and feedback. Carry unresolved outcomes and consequential effects to their final owner.

## Handle Failures Within an Established Scope

When evidence supports normal conditions usually holding and failure being exceptional, prefer
direct execution with local handling of the failures this boundary owns over repetitive
prechecks. When normal validity is uncertain, prefer a reliable, low-cost explicit check.

Preserve the language's safety preconditions; catching a failure cannot make undefined or otherwise
unsafe execution safe. Prechecks of mutable state establish only check-time conditions. Handle or
propagate actual operation failures even after a successful check.

Use native matching or classification to handle only the failures for which this boundary has an
established disposition. Keep handling local to the relevant operation, preserving required
propagation or reporting of programming defects and unrelated failures. Respect the language and
library's semantics for failure mechanisms: ordinary returned errors and panic or equivalent
interruption may have different handling constraints. A name such as `Error` or the technical
ability to intercept a failure does not alone decide its disposition; the actual contract and
safe handling do.

A common recovery, fallback, or conversion is safe only when it applies to every failure it covers.
At each broad interception site in authored code, leave a meaningful nearby maintainer comment
explaining why interception must be broad and why the disposition is safe for every intercepted
failure. This includes broad exception capture and panic-like interception. Routine inspection of
an operation's returned error followed by faithful propagation is not broad interception and does
not require this comment.

## Preserve Evidence and Feedback

Distinguish primary failures from failures of recovery, cleanup, or compensation. Preserve available
originating errors, cause chains, stacks, and useful context through translation and final handling.
Filter sensitive data, including credentials and needless private information. Human explanations
supplement this evidence rather than replacing it.

Decide diagnostic retention separately from public error recognition. Making an underlying error
inspectable through native matching or unwrapping can expose it as a caller dependency. Preserve
already promised recognition, and apply the public failure-contract policy above before adding
such a promise. Retaining useful evidence does not by itself justify a new public wrapper or
inspection contract, nor does it require every native error representation to carry a stack.

Give each reportable incident one final report owner. Complementary diagnostics and audience
feedback may coexist; propagation should not create duplicate incident reports.

Use project-owned severity and alerting according to impact, operational expectations, and needed
response, rather than channel or recovery alone. Successful recovery may still warrant investigation.

Final feedback must convey useful context, impact, and disposition through the owning boundary,
including material loss or unavailability even when its audience cannot repair it.

At final handling, rely on human remediation only when the actual actor has the capability,
authority, and available tools to perform it with reasonable effort. Exposing a failure does not
establish that the human receiving it can resolve it.

## Load the Relevant Branch

Ordinary propagation, clear translation or capture, routine review, I/O failure transfer, and
asynchronous ownership use the policy above. Read the following resources before choosing, changing,
or reviewing the corresponding behavior:

- [Recovery and effects](references/recovery-and-effects.md) when a recovery, retry, compensation,
  or accepted partial-completion strategy needs constraints on effects, replay, or resulting state.
- [Persisted data](references/persisted-data.md) when repairing, reconstructing, discarding, or
  degrading use of persistent or serialized data requires decisions about authority, loss, later
  reads, or interpretation. Propagating an ordinary I/O failure alone does not trigger this branch.
- [Remediation](references/remediation.md) when a final disposition relies on human action, or
  cross-role resolution and feedback responsibilities need to be established. A diagnostic or
  feedback change that leaves an established disposition and its responsibilities intact does not
  by itself trigger this branch.

## Resolve and Verify Within the Task

Scale investigation to affected outcomes, following implementation, caller, and contract evidence
from origin through translation to final ownership and production enforcement. Distinguish observed
behavior from proposed corrections, identifying the smallest coherent correction and its effects
for each mismatch. Make authorized changes at the owning boundary, preserving unrelated outcomes
and supported contracts. Assessment-only work remains read-only; this policy adds no remote or
destructive permission.

Investigate derivable facts before asking for missing disposition, loss, ownership, or audience
burden decisions. Unknown root causes permit an established safe disposition; use the applicable
diagnostic workflow for needed root-cause investigation. If a required resource, material contract
or decision, evidence, tool, access, or permission is unavailable, report the gap and pause dependent
work. Independent authorized work may continue where its owner permits.

Verify changed outcomes through the responsible public operation or boundary using discovered
owner checks and available tools. Cover meaningful success, absence or refusal, propagation, final
feedback, and remaining state in scope, including secondary failure, cancellation, and interruption
where they affect those outcomes. A failed check requires correction or an inconclusive result;
failed or unavailable required validation leaves work incomplete.

Use the current task's validation and handoff without a separate routine audit or report. For
investigated work, account for every identified path with a disposition or evidence gap, reporting
scope, supported findings or corrected mismatches, actual verification, unresolved decisions, and
untested surfaces. A gap is neither a verified path nor a completed correction.
