# Review, Finalize, and Close the Batch

This reference owns the one whole-Batch barrier, its repair cycle, the single finalizer invocation,
and post-delivery tracker and lifecycle closure.

## Principles

- **Immutable evidence.** Required verification and both `code-review` axes pass on one Batch base,
  `HEAD`, tree, and diff. A repair creates a new immutable state and replays that entire barrier.
- **Single active transition.** Keep at most one current Repair Unit and invoke the finalizer once.
  Completed repair predecessors remain audit history; an inferred or missing response authorizes no
  repeat.
- **Owner-bound closure.** Preserve `finish-worktree`'s raw status and strongest classification.
  Only authoritative delivery opens tracker closure; claims and source history remain until tracker
  and lifecycle owners prove their dispositions.

## Choose one entry

Use exactly one entry:

- **Normal:** every selected ticket has one proven Ticket Commit; every applicable claim is
  retained; no current blocking barrier result and no current dispatchable Repair Unit is
  retained; the Batch Worktree is clean under the repository predicate with no unowned local tail;
  observed ignored or untracked state material to Batch ownership, pending writes, recovery,
  finalizer correctness, or cleanup safety is attributable or retained as an owned residual; other
  observed noncritical state is recorded as a bounded residual or untested surface under its owner;
  the immutable target/base remains current; no worker attempt is unresolved; and no finalizer
  attempt exists. Immutable predecessor Repair-Unit audit history does not violate this entry. Enter
  **Verify and review one immutable state**.
- **Repair-recovery:** the current blocking barrier results, failed immutable barrier state whether
  verification-only or reviewed, `repair_base`, repair-owned commits and complete local state,
  applicable claims, and worker status are attributable to exactly one current dispatchable Repair
  Unit that has not yet produced an admitted complete repair, and no finalizer attempt exists. Enter
  **Repair and replay**.
- **Repaired-state replay:** the current blocking barrier results and current Repair Unit remain
  active; the repair worker has returned and is quiescent; its complete repair-owned range and local
  state are attributable; Ticket Commit boundaries are unchanged; checks necessary for safe replay
  pass; the worktree is clean; the target/base remains current; and no finalizer attempt exists.
  Enter **Verify and review one immutable state** without applying Normal's no-current-blocker or
  no-current-Repair-Unit predicate.
- **Returned-finalizer-result:** one complete attributable raw `finish-worktree` response exists,
  including an authoritative-delivery result whose tracker closure is incomplete. Enter
  **Consume the finalizer result**.

The entries are mutually exclusive. A local tail without an exact ticket or Repair Unit owner, a
stale target/base, or an unresolved worker or finalizer enters [`stop.md`](stop.md) without
running an earlier phase.

## Verify and review one immutable state

Freeze the current Batch Worktree `HEAD` and tree and prove that its immutable whole-Batch diff
from the Batch base is nonempty. An empty diff cannot enter the current public `code-review`
contract: preserve every Ticket Commit boundary, claim, worktree, and recovery fact, then enter
[`stop.md`](stop.md) with that dependency boundary and owner. Do not manufacture a change or
claim review, finalization, or delivery.

For a nonempty diff, run the repository's required verification, selecting additional checks only
when the changed surface or observed risk warrants them. Build one transient originating-spec input
containing the accepted Batch scope, each selected ticket's materially relevant acceptance sources,
and governing Specs they reference, preserving each component's identity and provenance. Record
noncritical checks or surfaces that remain untested rather than broadening the pass gate without a
risk owner.

When required verification reaches review, invoke public `code-review` once from the immutable
Batch base with that complete input. Require both its Standards and Spec axes to cover the same
immutable diff, base, `HEAD`, and tree. Standards covers the applicable repository standards and
smell-baseline inputs owned by that dependency; Spec covers every materially relevant obligation in
the provenance-preserving originating ticket/spec input. **Blocking barrier results** are failed
required-verification results, blocking review findings, missing or incomplete axes, and
unclassifiable owner results. A baseline smell is advisory unless accepted project authority
independently makes it blocking.

Use one barrier-failure transition for Normal and Repaired-state replay. Retain any current Repair
Unit throughout required verification and both review axes. When the complete barrier passes, clear
only its current blocking and dispatchable designations and retain it with any predecessors as
immutable audit history; a passing Normal state has no current Unit to clear. The result is then
finalization-ready.

When the barrier does not pass, preserve the failed immutable state, every current blocking barrier
result, claims, worktree, target/base freshness, and the complete verification and review evidence
that exists. For a Repaired-state replay, first make the completed current Repair Unit and its
attempt immutable, non-redispatchable predecessor history, preserving its status, commits and local
state, attribution, worker quiescence, and Ticket Commit boundaries. If correction is supported,
atomically freeze the failed immutable state and all current blocking barrier results as exactly one
initial or successor current Repair Unit with no started or admitted repair; a successor links its
completed predecessor only as history. Enter **Repair-recovery**. When no supported correction may
proceed, enter [`stop.md`](stop.md) with the preserved evidence and next owner/action. Never invoke
the finalizer from a failed barrier.

**Complete when:** required verification and both review axes pass without a blocking barrier result
on one immutable diff, base, `HEAD`, and tree, each axis establishes its owned coverage, and any
expressly noncritical untested surface is disclosed without widening the result.

## Repair and replay

Enter with exactly one current Repair Unit containing the blocking barrier results and failed
immutable state, which may be verification-only or reviewed. Its repair either has not started or
remains incomplete; completed predecessor Units are retained only as immutable history. Read
[`worker-transaction.md`](worker-transaction.md) and dispatch or resume one exclusive repair worker
only for the current Unit. Repair commits contain no ticket trailer. Independently establish the
complete attributable repair-owned range and local state, worker quiescence and status, unchanged
Ticket Commit boundaries, checks necessary for safe replay, a clean final worktree, and the
unchanged target/base. Accept attributable worker evidence unless it is contradicted, materially
incomplete, or stale; resolution of blocking barrier results belongs to the replayed verification
and review barrier.

A noncomplete worker result or unsupported repair enters [`stop.md`](stop.md). After a complete
repair, establish every **Repaired-state replay** predicate and enter **Verify and review one
immutable state** while retaining the findings and Repair Unit. Rerun the required verification and
both review axes against the new immutable state; only evidence whose validity depends on the prior
diff is invalidated.

**Complete when:** the repaired state passes the entire verification/review barrier.

## Invoke the finalizer once

Enter only from a finalization-ready immutable state whose required verification and both review
axes passed and which retains no current blocking barrier result or dispatchable current Repair Unit.
Immutable predecessor Repair-Unit audit history is allowed and remains non-dispatchable.

Build the public `finish-worktree` input from current proof: the complete accepted Batch scope and
ticket/spec sources; exact source worktree and target; immutable base; reviewed `HEAD` and tree;
complete Batch-owned range and boundary history; verification and both review reports; accepted
outcome and history policy; immutable Repair-Unit audit history; preservation boundary; current
publication facts; and exact effect and cleanup authorities. Tracker operations and alternative
delivery judgments remain with their respective owners.

Immediately before the finalizer effect, re-observe the source worktree's registration, path,
branch, `HEAD`, tree, index, and local state and the target ref. Require the source identity to
match the reviewed state, then require [`tracker.md`](tracker.md)'s whole-selection revalidation
against the frozen Selection Result and the exact claim effects already consumed by this Batch.
Drift in either check invalidates the verification/review barrier and enters
[`stop.md`](stop.md) without invoking the finalizer.

Invoke `finish-worktree` once and preserve its raw response and observable effects. If the response
is missing, interrupted, or not attributable, enter
[`recover-finalizer.md`](recover-finalizer.md) with the original invocation; do not start another
finalizer attempt.

## Consume the finalizer result

Consume `status`, `classification`, phase results, effects, residuals, and handoff exactly as the
dependency returned them. Select the route from its strongest retained classification:

- An authoritative-delivery classification, including **Already Delivered** only when classified
  by `finish-worktree`, enters [`tracker.md`](tracker.md)'s post-delivery closure. Re-observe any
  authoritatively completed tracker prefix and continue only its unresolved suffix; never repeat a
  proven tracker effect. Preserve any raw stopped or failed status alongside that independently
  proven classification.
- A non-integrating handoff returns unchanged. Tickets remain open; supported claims, worktree,
  source-boundary history, publication evidence, and recovery state remain with its named owner.
- `history finalized` or `no positive result` returns that exact classification and handoff
  through `stop.md`; neither authorizes tracker completion.
- An unavailable or ambiguous classification returns one consumed unresolved-classification
  handoff through `stop.md`. It preserves the complete raw result, the unknown classification,
  and the dependency owner/action without inference, finalizer retry, tracker effect, or later
  reconsumption.

A raw `stopped` or `failed` status accompanies whichever classification branch applies. It
cannot turn authoritative delivery into a non-delivery result or independently authorize tracker
completion.

After post-delivery tracker closure, give its proof to the lifecycle owner named by the finalizer
handoff. That owner decides authorized cleanup or retention without repeating history or outcome
effects. Retain the source boundary history until both tracker closure and its lifecycle disposition
are proven.

**Complete when:** the one finalizer invocation has an attributable result whose exact route is
consumed, or its original in-flight owner and next action are preserved.
