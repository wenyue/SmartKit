---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of eligible tracker tickets in one isolated worktree, or prove that the bounded scope has no eligible work; review and finalize a nonempty batch once.
---

# Implement Tickets

Resolve one bounded ticket scope. A proven empty selection is a successful no-effect result. A
nonempty selection becomes one **Ticket Batch** in one isolated **Batch Worktree**.

## Principles

- **Controller-owned orchestration.** The active Agent is the Controller and owns Batch
  orchestration. The configured tracker owns ticket, blocker, claim, and completion meaning;
  `create-worktree` owns worktree choice and readiness; `code-review` owns its Standards and Spec
  judgments; and `finish-worktree` owns history, delivery, **Already Delivered**, non-integrating
  handoffs, recovery, and cleanup judgments.
- **Stable Batch.** Freeze one positively eligible, dependency-ordered selection. Run at most one
  ticket or repair worker at a time, and never silently widen or reorder the Batch.
- **Commit boundary.** Each selected ticket ends in exactly one first-parent **Ticket Commit** whose
  sole ticket trailer is `SmartKit-Ticket: <canonical-id>`. Checkpoint and repair commits carry no
  ticket trailer. Preserve these source-history boundaries even if finalization consolidates them.
- **One final barrier.** Verify and review the whole Batch once, then finalize it once. Any repair
  replays the complete verification and both review axes on the new immutable state.
- **Explicit effects.** Use only accepted authority for the exact tracker, worktree, worker,
  repository, finalizer, and cleanup effects. Preserve the canonical checkout and unrelated or
  user-owned state. Force, rebase, reset, clean, discard, and implicit remote or tracker effects are
  outside the grant.
- **Recover from evidence.** Recover from Git history, current tracker state, retained dependency
  handoffs, and observable live-worker or finalizer state. Keep no Batch journal, and never retry an
  effect merely because current state resembles its intended result.

The caller supplies the accepted scope, target, outcome, history policy, and exact effect
authorities. Project rules, ticket and spec sources, repository validation, and the current public
dependency contracts supply the remaining meaning.

Use proportionate evidence for ordinary judgments, but exhaustively close ticket selection and
dependencies, mutation attribution, repository-required verification, and effect recovery. Reuse
attributable evidence only while its freshness condition holds. Missing noncritical evidence
narrows the claim and is reported; uncertainty about safety, permission, ownership, an external
effect, or recovery stops before that effect.

## Establish the route

Read [`references/tracker.md`](references/tracker.md) before the first tracker observation. Observe
the bounded scope and target, repository and registered worktrees, relevant branch history and
local state, retained public-Skill handoffs, and any live worker or finalizer identity. Select
exactly one route:

- **New.** No evidence identifies an unfinished Batch. Let `tracker.md` select the Batch. Its
  `nothing-to-do` result ends with no Batch and no effect. For a nonempty selection, complete its
  initial claim gate before asking `create-worktree` to establish the Batch Worktree from the exact
  target base. Consume only an attributable current `ready` result; otherwise retain the dependency
  result and enter the Pre-ready handoff.
- **Pre-ready selection.** A frozen nonempty Selection Result and claim plan exist, but no current
  `ready` result has been consumed. Resume through [`references/stop.md`](references/stop.md), which
  owns the independent claim and Create partitions. Consume readiness only while its recorded
  snapshot still matches current state.
- **Before finalization.** The Batch has consumed its initial readiness and has no possible
  finalizer attempt, response, or consumed-result handoff. Reconstruct the immutable base,
  dependency-valid Ticket Commit prefix, and at most one current ticket or repair tail, accounting
  for every commit and local-state item. With continuous attributable control, recheck current Git,
  tracker, worktree, and worker evidence before continuing. After any gap in control or evidence,
  first use
  [`references/worker-transaction.md`](references/worker-transaction.md) to prove quiescence and
  attribution. At a ticket or retained-repair frontier after a gap, ask `create-worktree` to
  re-evaluate the existing candidate before another mutation. Consume its fresh `ready` result only
  for the same candidate; preserve any `non-ready` or unresolved result with its owner. Continue a
  ticket through
  [`references/process-one-ticket.md`](references/process-one-ticket.md), a retained repair through
  [`references/complete-run.md`](references/complete-run.md), or, after every Ticket Commit is
  proven, freeze the registered path, branch, `HEAD`, tree, index, local state, base, and target
  before entering `complete-run.md`.
- **Retained finalizer result.** No consumed terminal handoff exists. Give the complete attributable
  raw response to `complete-run.md`'s sole result route, including authoritative delivery with
  incomplete tracker closure.
- **Finalizer response missing or possibly live.** Enter
  [`references/recover-finalizer.md`](references/recover-finalizer.md) with the original attempt.
- **Consumed terminal handoff.** Preserve a consumed `non-integrating handoff`, `history finalized`,
  or `no positive result` result, or an unresolved classification already returned to the dependency
  owner. Resume only the named owner and action; do not consume the result or repeat an effect.

An unconsumed `ready` result remains Pre-ready until its snapshot and the common binding below pass.
Once a finalizer attempt exists or cannot be excluded, Before finalization is ineligible.

Ambiguous Batch identity, scope, base, route, ownership, or effect state reads
[`references/stop.md`](references/stop.md) and stops at that boundary.

**Route complete:** one authoritative route and next owner are established, or `nothing-to-do` is
proven.

## Execute a nonempty Batch

When either New or Pre-ready selection yields an attributable current `ready` result, bind the
frozen tracker selection, immutable target base, accepted outcome and history policy, explicit
authorities, lifecycle owners, and recorded worktree identity. Immediately recheck its physical
path, registration, branch, `HEAD`, tree, index, and local state before a pending just-in-time claim
and before the first post-readiness implementation, worktree, or worker effect. Consume the initial
claims and readiness result without repeating them.

Process each dependency-ready ticket through `process-one-ticket.md`. Return its independently
proven Ticket Commit to the frozen selection before choosing the next frontier. Tickets remain open
and supported claims remain held until authoritative delivery.

After every Ticket Commit is proven, enter `complete-run.md`. Only `finish-worktree`'s authoritative
delivery classification, including its own **Already Delivered** result, permits tracker closure.
Preserve its strongest classification and raw status: a coincident `stopped` or `failed` status
does not erase delivery, while every non-delivery, unavailable, ambiguous, or in-flight result
retains the handoff, tickets, claims, worktree, and source history required by its owner.

At the first noncomplete boundary, read `stop.md`, preserve the raw owner result and observed
effects, and block later tickets and phases.

**Invocation complete:** either the empty selection is proven with no effects; delivery, tracker
closure, and lifecycle disposition are proven; or one exact noncomplete handoff names the only safe
next owner and action.
