---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of eligible tracker tickets in one isolated worktree, or prove that the bounded scope has no eligible work; review and finalize a nonempty batch once.
---

# Implement Tickets

Resolve one bounded ticket scope. A nonempty eligible selection forms one **Ticket Batch** in one
isolated **Batch Worktree**; an empty eligible selection establishes no Batch. The controller owns
batch orchestration. The configured tracker owns ticket, blocker, claim, and completion meanings;
`create-worktree` owns worktree readiness; `code-review` owns its two review axes; and
`finish-worktree` owns history finalization, delivery, **Already Delivered**, non-integrating
handoffs, recovery, and cleanup judgments.

Execute tickets in stable dependency order with at most one ticket or repair worker using the
Batch Worktree at a time. Every selected ticket ends in exactly one first-parent **Ticket Commit**
whose sole ticket trailer is:

```text
SmartKit-Ticket: <canonical-id>
```

Checkpoint and repair commits carry no ticket trailer. Preserve these boundaries in the source
history even when finalization consolidates the delivered history. The whole Batch receives one
verification/review barrier and one finalization; a repair replays that complete barrier.

Use the caller's accepted scope, target, outcome, history policy, and explicit effect authorities.
Project rules, ticket/spec sources, repository validation, and the current public dependency
contracts supply the rest. No visible command or capability grants an effect. Preserve the
canonical checkout and all unrelated or user-owned state; do not force, rebase, reset, clean,
discard, or perform an implicit remote or tracker effect.

Git history, current tracker state, retained dependency handoffs, and observable live-worker or
finalizer state are the recovery evidence. Do not create or require a separate Batch journal. When
that evidence cannot distinguish an in-flight effect from an effect that never started, retain the
original attempt and route it to its owner rather than retrying by inference.

## Establish the route

Read [`references/tracker.md`](references/tracker.md) before the first tracker observation. Observe
the bounded scope, target and repository, registered worktrees, relevant branch history and local
state, retained public-Skill handoffs, and live worker or finalizer identities. Choose exactly one
route:

- **New:** no evidence identifies an unfinished Batch. Execute `tracker.md`'s Batch selection
  using authoritative meanings, operations, and evidence obtained through the configured tracker
  owner and route. A proven empty eligible selection returns its `nothing-to-do` result without a
  claim, worktree, worker, or finalizer effect. For a nonempty selection, consume `tracker.md`'s
  complete claim-plan gate, including the required read-only worker qualifications and any
  tracker-authorized initial claims, before invoking `create-worktree` from the exact target base.
  Consume only its attributable `ready` handoff. A `non-ready`, missing, or ambiguous result stays
  with that dependency's original recovery owner.
- **Pre-ready selection:** one frozen nonempty Selection Result and claim plan are attributable,
  but no current `ready` worktree handoff has been consumed. Reconstruct the independent claim
  partition—zero or more proven initial claims, an optional current failed or in-flight attempt,
  the untouched initial suffix, and every JIT/no-claim disposition—and the Create partition:
  `never-started`, original `non-ready-or-in-flight`, or attributable `ready`. With no unresolved
  claim and every required initial claim proven, `never-started` may invoke Create once.
  `non-ready-or-in-flight` stays with the original dependency owner/action. Consume attributable
  `ready` without another Create and enter the common Batch binding below. A ready handoff whose
  snapshot has drifted requires public `create-worktree` Reuse evaluation; it never becomes
  `never-started`. This route ends when the initial `ready` handoff is consumed.
- **Before finalization:** one active Batch Worktree has consumed its originating public `ready`
  handoff and completed the common Batch binding. No finalizer attempt, response, or
  consumed-result handoff exists or remains unexcluded. Reconstruct the immutable base,
  dependency-valid Ticket Commit prefix, and at most one current ticket or repair tail, including
  every commit and local-state item. With uninterrupted causally attributable control, recheck the
  current Git, tracker, worktree, and worker evidence before continuing. After any gap in execution,
  identity, control, or evidence, first route every retained or possibly dispatched worker through
  [`references/worker-transaction.md`](references/worker-transaction.md) and prove quiescence and
  complete attribution of its state. An unresolved worker returns its exact in-flight handoff.
  Otherwise freeze the observed `HEAD`, tree, index, and local state and invoke public
  `create-worktree` once in Reuse mode. Consume only its attributable `ready` handoff after the
  immediate current readiness recheck; a non-ready or unresolved result remains with that
  dependency owner. A ticket frontier enters
  [`references/process-one-ticket.md`](references/process-one-ticket.md); a retained repair or
  completed-ticket frontier enters [`references/complete-run.md`](references/complete-run.md).
- **Retained finalizer result:** when no consumed terminal handoff exists, pass the complete
  attributable raw `finish-worktree` response to `complete-run.md`'s sole result/closure route,
  including when authoritative delivery is proven and tracker closure is incomplete. That route
  re-observes proven tracker effects and continues only the unresolved suffix.
- **Finalizer response missing or possibly live:** read
  [`references/recover-finalizer.md`](references/recover-finalizer.md).
- **Consumed terminal handoff:** when the exact result-route handoff proves that either a
  `non-integrating handoff`, `history finalized`, or `no positive result` classification was
  consumed, or that an unavailable or ambiguous classification was returned unresolved to the
  dependency owner, preserve the complete raw response and classification state. Resume only its
  returned owner/action when authorized; never reconsume the response or repeat a finalizer or
  tracker effect.

An unconsumed or newly recovered `ready` handoff remains Pre-ready until the common binding and
readiness recheck pass. Once any finalizer attempt is observed or cannot be excluded,
Before-finalization is ineligible; only its matching retained-result, missing-response recovery, or
consumed-result route may proceed.

Ambiguous Batch identity, scope, base, route, ownership, or effect state reads
[`references/stop.md`](references/stop.md) and stops at that boundary.

**Complete when:** one authoritative route and next owner are established, or a no-effect
`nothing-to-do` result is proven.

## Execute a nonempty Batch

When either New or Pre-ready selection yields an attributable `ready` handoff, bind the
tracker-owned selection, immutable target base, accepted outcome and history policy, explicit
authorities, lifecycle owners, and that handoff. Immediately recheck its physical path,
registration, branch, `HEAD`, tree, index, and local state before any pending just-in-time claim
and before the first post-readiness implementation, worktree, or worker effect. Consume initial
claims and the ready handoff without reinvocation.

Consume the selected dependency order. For each ready ticket, execute `process-one-ticket.md`
through `completed-in-batch`; return its proven Ticket Commit to the tracker selection before
choosing the next frontier. Never reorder or widen the frozen Batch. Tracker tickets remain open
through implementation, and every supported claim remains held until authoritative delivery.

After all Ticket Commits are proven, execute `complete-run.md`. Only a `finish-worktree`
classification of authoritative delivery, including its own **Already Delivered** result, permits
tracker completion. Route by that dependency's strongest classification while preserving its raw
status: `stopped` or `failed` does not override retained authoritative delivery. Every
non-delivery classification, unavailable classification, ambiguous result, or in-flight finalizer
retains the exact public handoff, tickets, supported claims, worktree, and source history required
by its owner.

At the first noncomplete boundary, read `stop.md`, preserve the raw owner result and observed
effects, and block later tickets and phases.

**Complete when:** either an empty eligible selection is proven with no effects; authoritative
delivery, tracker closure, and the lifecycle disposition are proven; or the exact noncomplete
handoff names the only safe next owner/action.
