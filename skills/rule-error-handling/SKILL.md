---
name: rule-error-handling
description: Use for work involving operation outcomes or error behavior, including contracts, propagation, translation, recovery, feedback, and requested assessment or design.
---

# Error Handling

Strength: `Default`

Scope: Operation outcomes, failure contracts, propagation, handling, recovery, and final feedback
in development and review across languages, and requested assessment, diagnosis, or design of that
behavior.

## Preserve the promised outcome

Classify success, ordinary refusal or absence, contracted failure, and programming violations by
the operation's promise, independently of their representation, frequency, or retryability. Keep
failed outcomes and partial effects visible. Catching an error, supplying a default, or restoring
future usability does not establish success: the current operation must fulfill its promise or an
accepted degraded or partial outcome.

Keep infallible operations direct. Use the language's native mechanisms and the project's actual
contracts, introducing stable distinctions where callers need different decisions. Translate at
the boundary that owns the contract. Cover a closed business vocabulary exhaustively; for an open
protocol, preserve an explicit unknown-failure path and useful causes rather than converting
incidental failures into ordinary refusal. Keep programming violations distinct from ordinary
negatives. Production-required validation, control flow, side effects, and invariants must remain
enforced when optional checks are disabled. Validate data where its syntax and meaning are
understood, distinguishing invalid content from failed I/O. Explain important caller obligations
where code, types, and referenced contracts leave them unclear.

## Place handling with its owner

Handle failures for owned recovery, cleanup, compensation, required contract translation, or final
handling; otherwise propagate faithfully through the accepted contract. A library may fulfill its
responsibility by transferring the failed outcome to its caller. Give each independently initiated
operation a final owner. Required asynchronous work belongs to the operation's completion promise;
detached work needs its own completion, failure, and lifecycle ownership. Guarantee owned cleanup
through success, failure, cancellation, and interruption.

Capture the narrowest failure type that permits the established disposition. Broad capture is safe
only when every failure it can capture can receive that disposition. At each broad capture site in
authored code, leave a meaningful nearby maintainer comment explaining why the capture must be broad
and why the disposition is safe for every captured failure.

Consuming a failure or delegating reporting retains responsibility for remaining state, cleanup,
retry, and feedback. Carry unresolved outcomes and consequential effects to their final owner.
Distinguish primary failures from failures of recovery, cleanup, or compensation; preserve available
originating errors, cause chains, stacks, and useful context through translation and final handling.
Filter sensitive data, including credentials and needless private information. Human explanations
supplement this evidence rather than replacing it.

Give each reportable incident one final report owner. Complementary diagnostics and audience
feedback may coexist; propagation should not create duplicate incident reports. Use project-owned
severity and alerting according to impact, operational expectations, and needed response, rather
than channel or recovery alone. Successful recovery may still warrant investigation. Final feedback
must convey useful context, impact, and disposition through the owning boundary, including material
loss or unavailability even when its audience cannot repair it.

## Load constraints for the decision

Ordinary propagation, clear translation or capture, routine review, I/O failure transfer, and
asynchronous ownership use the policy above. Read the following resources before choosing, changing,
or reviewing the corresponding behavior:

- [Recovery and effects](references/recovery-and-effects.md) when a recovery, retry, compensation,
  or accepted partial-completion strategy needs constraints on effects, replay, or resulting state.
- [Persisted data](references/persisted-data.md) when repairing, reconstructing, discarding, or
  degrading use of persistent or serialized data requires decisions about authority, loss, later
  reads, or interpretation. Propagating an ordinary I/O failure alone does not trigger this branch.
- [Remediation](references/remediation.md) when human remedial actions or cross-role resolution and
  feedback responsibilities require decisions about capability, authority, or reasonable effort.
  An ordinary diagnostic or feedback change alone does not trigger this branch.

## Resolve and verify within the task

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
