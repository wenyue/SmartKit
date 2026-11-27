---
name: rule-error-handling
description: Use for work involving operation outcomes or error behavior, including requested assessment.
---

# Error Handling

Start with what the caller needs the operation to accomplish. A failed operation can have a perfectly adequate outcome for its caller: the save failed, the edits are still available, and the user can free space and try again. Add protection when the benefit justifies the cost of building and maintaining it. Keep state valid, respect authority and accepted loss, and leave infallible operations direct.

## Establish the outcome and its owner

Use the operation's promise to distinguish success, ordinary absence or refusal, contracted failure, and a programming violation. A failure's frequency, representation, or retryability does not determine which it is. Report success only when the promise is fulfilled, including a degraded or partial result the contract accepts. A catch or default alone establishes no such result. Preserve failures and remaining effects that matter to callers, and disclose the material effects of partial completion.

Give each independently initiated operation an owner for completion, failure, remaining state, and final feedback. A library can discharge its part by returning the failure through the accepted caller contract. Complete owned cleanup through success, failure, cancellation, and interruption. If work passes to another owner, transfer unresolved outcomes, consequential effects, and the evidence needed to act. Consuming an error or delegating a report leaves remaining state and recovery to account for.

Before choosing, changing, or reviewing how to handle an affected operation, read every reference whose decision applies. A cancelled remote write can involve several. If a required reference is unavailable, report the gap and pause the decision that needs it.

| Decision | Required reading |
| --- | --- |
| Interpret, migrate, discard, or recover stored or serialized data, or establish persistence guarantees. | [Persistence](references/persistence.md) |
| Choose how to dispatch a filesystem, network, subprocess, or other external operation, determine its effects, or decide whether to replay, reconcile, or compensate. | [External operations](references/external-operations.md) |
| Determine completion, cancellation, timeout, stale results, stream behavior, or cleanup for concurrent or deferred work. | [Async work and streaming](references/async-and-streaming.md) |
| Handle authentication, authorization, integrity checks, security fallback, or diagnostics containing credentials or private payloads. | [Identity and security](references/identity-and-security.md) |
| Preserve user input, offer a remedial action, assess the feasibility of human repair or handoff, or rely on either for recovery. | [User recovery](references/user-recovery.md) |

## Choose what to do with a failure

Let the failure reach the boundary that can act on it. Intercept it for owned recovery, cleanup, compensation, required contract translation, or final handling. Otherwise propagate it faithfully using the language's native mechanisms and the existing project contract. A safe, established disposition can proceed before the root cause is known.

When recovery is needed, prefer the simplest existing approach that meets the caller's needs. Keep recovery feasible, within the owner's authority, and within the limits of accepted loss. Bound the work and establish what effects remain, including what happens if recovery itself fails. Retry only when there is a reason a later attempt can succeed and a bound on when to stop.

When the evidence supports normal conditions usually holding, prefer executing the operation directly and handling a relevant failure locally. When validity is uncertain, prefer a reliable, inexpensive explicit check. Observe language safety preconditions before execution. A check of mutable state establishes only what was true at check time, so still handle or propagate failures of the operation itself.

Validate data where both syntax and meaning are understood, distinguishing invalid content from failed I/O. Keep required validation, control flow, side effects, and invariants effective in production with optional checks disabled. Handle every case in a closed business vocabulary. For an open protocol, provide an explicit path for unknown failures with useful causes so incidental failures cannot silently become ordinary refusals. Explain consequential caller obligations the code, types, and referenced contracts leave unclear.

Match failures by native classification and handle only those with an established disposition at this boundary. Keep handling local and let unrelated failures and programming defects propagate or reach their report owner. Respect the language and library semantics of returned errors, exceptions, and panic-like interruptions. The ability to catch a failure, or a name such as `Error`, says little about whether recovery is safe.

Any common recovery, fallback, or conversion must be safe for every failure it covers. At each broad interception site in authored code, including broad catches and panic-like interception, leave a nearby maintainer comment explaining why interception must be broad and why the disposition is safe across that range. Routine inspection of a returned error followed by faithful propagation needs no such comment.

## Preserve evidence and choose what callers can recognize

Carry originating errors, cause chains, available stacks, and useful audience-safe context through translation and final handling. Keep a failed recovery, cleanup, or compensation distinguishable from the initial failure. If the secondary failure determines the outcome or remaining state the caller must receive, or how the caller should respond, retain the original as complementary evidence. Otherwise preserve the original outcome and handle the secondary failure at its owner. A human explanation supplements the underlying evidence. Use available stacks without requiring every native error representation to carry one.

Decide separately what callers can depend on. A native matcher or unwrap operation can expose an underlying failure as part of the public contract. Preserve promised recognition, translate at the boundary that owns it, and prefer a semantically accurate existing contract. Diagnostic value alone does not call for a public wrapper or inspection contract.

Add a publicly consumable distinction only for a concrete handling or diagnostic benefit that justifies the caller knowledge and compatibility cost, even when using the detail is optional. New exception types, error identities or codes, result cases, and newly inspectable causes all count. Obtain the user's explicit agreement to the addition unless it is a faithful refinement. Prior explicit agreement suffices. General permission to implement the feature does not authorize this contract change.

A faithful refinement keeps a concrete, semantically accurate language or standard-library failure category and preserves its promised recognition, information, and handling. Establish that existing category-level callers continue to work without adaptation through native matching or classification. More specific detail is opt-in. Inheritance is optional, and sharing only a generic exception base or error interface is insufficient. This exception concerns agreement alone. The addition still needs a justified benefit and must preserve supported contracts.

## Deliver the outcome and verify it

Give each reportable incident one final report owner. Provide complementary diagnostics and audience feedback where needed without repeating incident reports as an error propagates. Set project-owned severity and alerting by impact, operational expectations, and the response needed. Neither the channel nor successful recovery alone determines severity. Tell the audience what happened, its impact, what state remains, and any supported next action. Material loss or unavailability matters even to someone who cannot repair it.

Trace the affected outcomes through the implementation, callers, translations, and final owner before judging a correction. Change the owning boundary only within the current task's authority, preserving unrelated outcomes and supported contracts. An assessment is read-only. This rule grants no additional remote or destructive permission.

Investigate derivable facts before asking who should act, what loss or audience burden is acceptable, or how to dispose of the failure. If material evidence, a contract or decision, a required resource or capability, or authority is missing, identify the gap and pause dependent work. Continue independent authorized work.

Verify changed outcomes, final feedback, and remaining state through the responsible public operation or boundary and its owner checks. Cover materially different success, absence or refusal, and failure paths. Include recovery and stopping bounds, secondary failure, cancellation, or interruption where they can change the promise. A failed or unavailable required check leaves the work incomplete.

Use the current task's validation and handoff. Account for every identified path with its disposition or evidence gap. Report scope, supported findings or corrections, actual checks, unresolved decisions, and untested surfaces. Claim a verified path or completed correction only where the evidence supports it.
