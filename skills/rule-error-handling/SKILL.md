---
name: rule-error-handling
description: Use for work involving operation outcomes or error behavior, including requested assessment.
---

# Error Handling

Choose the simplest handling that fulfills the operation's promise, respects accepted loss and permission, and leaves valid state. Recovery that restores future usability does not by itself complete the failed operation.

## Load the guidance for affected decisions

Apply the common principles below to substantive work and assessment. Before choosing, changing, or reviewing a decision in this table, read every matching reference. A cancelled remote write may need several. If required guidance is unavailable, report the gap and pause the dependent decision.

| Affected decision | Required reading |
| --- | --- |
| Stored or serialized data: interpretation, recovery, discard, migrations, or persistence guarantees. | [Persistence](references/persistence.md) |
| Filesystem, network, subprocess, or other external operations: dispatch, uncertain outcomes, replay, reconciliation, or compensation. | [External operations](references/external-operations.md) |
| Concurrent or deferred work: completion, cancellation, timeouts, stale results, streams, or lifecycle cleanup. | [Async work and streaming](references/async-and-streaming.md) |
| Authentication, authorization, integrity checks, security fallback, or diagnostics containing credentials or private payloads. | [Identity and security](references/identity-and-security.md) |
| User-facing recovery: retained input, remedial actions, human repair, or handoff to another actor. | [User recovery](references/user-recovery.md) |

## Start with the promised outcome

Distinguish success, ordinary refusal or absence, contracted failure, and programming violations by the operation's promise, rather than their representation, frequency, or retryability.

Report success only when the operation fulfills its promise or an accepted degraded or partial outcome. Catching an error or supplying a default is insufficient; preserve failures and remaining effects that matter to callers.

Keep infallible operations direct. Use native language mechanisms and existing project contracts; translate failures at the boundary that owns the contract.

Cover a closed business vocabulary exhaustively. An open protocol needs an explicit unknown-failure path with useful causes; incidental failures must not become ordinary refusal.

Keep required validation, control flow, side effects, and invariants effective in production when optional checks are disabled.

Validate data where its syntax and meaning are understood, distinguishing invalid content from failed I/O. Explain consequential caller obligations left unclear by code, types, and referenced contracts.

## Choose public failure contracts deliberately

Prefer a semantically accurate existing failure contract. Add a public distinction only for a concrete handling or diagnostic benefit that justifies its caller knowledge and compatibility costs, including when the detail is optional.

Before adding a publicly consumable failure distinction, obtain the user's explicit agreement to that addition unless it qualifies as a faithful refinement below. Exception types, error identities or codes, result cases, and newly inspectable underlying failures can all add such a contract. Existing explicit agreement remains valid; general authorization to implement a feature is insufficient.

### When a refinement needs no additional agreement

A faithful refinement preserves a semantically accurate, concrete language or standard-library failure category and its promised recognition, information, and handling. Existing category-level handling must work without caller adaptation; callers may opt into the specific detail.

Establish preservation through native matching or classification; inheritance is not required, and a generic exception base or error interface alone does not qualify. This exception removes only the additional agreement requirement; the benefit must still justify its costs and preserve supported contracts.

## Keep an owner through completion

Intercept failures for owned recovery, cleanup, compensation, required contract translation, or final handling; otherwise propagate faithfully. A library may fulfill its responsibility by returning the failed outcome through its accepted caller contract.

Give each independently initiated operation an owner for completion, failure, remaining state, and final feedback. Complete owned cleanup through success, failure, cancellation, and interruption.

Consuming a failure or delegating reporting retains responsibility for remaining state and recovery. Transfer unresolved outcomes, consequential effects, and needed evidence to an identified owner; delegation alone does not complete the operation.

## Choose the simplest acceptable recovery

Reuse the simplest established recovery that preserves required state and work. A short wait or safe manual retry can suffice when those affected have a practical way to proceed. Add wrappers, fallback state, or automatic repair only to protect a required outcome or materially reduce failure's impact.

Keep recovery feasible, bounded, and within the owner's authority. Establish accepted loss, remaining effects, and the outcome if recovery fails. Disclose material effects of accepted partial completion.

A retry needs a reason the cause can be overcome and a stopping bound.

## Handle only failures with an established disposition

Prefer direct execution with local handling when evidence supports normal conditions usually holding. When validity is uncertain, prefer a reliable, low-cost explicit check.

Preserve language safety preconditions; catching a failure cannot make unsafe execution safe. A precheck of mutable state establishes only check-time conditions, so handle or propagate actual operation failures after a successful check too.

Use native matching or classification to handle only failures with an established disposition at this boundary. Keep handling local and preserve propagation or reporting of programming defects and unrelated failures. Respect language and library constraints on returned errors, exceptions, and panic-like interruption; a name such as `Error` or the ability to intercept it does not establish safe handling.

A common recovery, fallback, or conversion must be safe for every failure it covers.

At each broad interception site in authored code, including broad exception capture and panic-like interception, leave a nearby maintainer comment explaining why interception must be broad and why its disposition is safe for every intercepted failure. Routine returned-error inspection with faithful propagation needs no such comment.

## Preserve evidence without widening the public contract

Preserve originating errors, cause chains, available stacks, and useful audience-safe context through translation and final handling. Distinguish the original failure from failed recovery, cleanup, or compensation. If a secondary failure determines the caller's disposition, retain the original as complementary evidence; otherwise preserve the original outcome and handle the secondary failure at its owner. Human explanations supplement this evidence.

Decide diagnostic retention separately from public error recognition: native matching or unwrapping can expose an underlying error as a caller dependency. Preserve promised recognition and apply the public-contract policy before adding it. Useful evidence alone justifies neither a new public wrapper nor an inspection contract, and does not require every native error representation to carry a stack.

## Make final feedback useful to its audience

Give each reportable incident one final report owner. Complementary diagnostics and audience feedback may coexist; propagation must not duplicate incident reports.

Use project-owned severity and alerting according to impact, operational expectations, and needed response. Neither the reporting channel nor successful recovery alone determines severity.

Final feedback must convey useful context, impact, resulting state, and any supported next action, including material loss or unavailability even when the audience cannot repair it.

## Resolve and verify within the current task

Trace affected outcomes through implementation, callers, translation, and final ownership before judging a correction. Change the owning boundary within the current task's authority, preserving unrelated outcomes and supported contracts. Assessment remains read-only; this policy adds no remote or destructive permission.

Investigate derivable facts before asking for disposition, loss, ownership, or audience-burden decisions. A safe established disposition need not wait for a root cause. If material evidence, a contract or decision, a required resource or capability, or authority is missing, report the gap and pause dependent work; independent authorized work may continue.

Verify changed outcomes, final feedback, and remaining state through the responsible public operation or boundary and its owner checks. Cover materially different success, absence or refusal, and failure paths, including recovery or stopping bounds and secondary failure, cancellation, or interruption when they can change the promise. Failed or unavailable required validation leaves work incomplete.

Use the current task's validation and handoff rather than a separate routine audit. Account for every identified path with a disposition or evidence gap, reporting scope, supported findings or corrections, actual checks, unresolved decisions, and untested surfaces. A gap is not a verified path or completed correction.
