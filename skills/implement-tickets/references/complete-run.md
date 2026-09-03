# Review, Finalize, and Close the Batch

Use exactly one entry:

- **Normal:** every selected ticket has one proven Ticket Commit; every applicable claim is
  retained; no blocking review, finding set, or Repair Unit is retained; the Batch Worktree is
  clean under the repository predicate with no unowned local tail; every ignored item is accounted
  for; the immutable target/base remains current; no worker attempt is unresolved; and no
  finalizer attempt exists. Enter
  **Verify and review one immutable state**.
- **Repair-recovery:** the retained blocking findings, reviewed state, `repair_base`, repair-owned
  commits and complete local state, applicable claims, and worker status are attributable to one
  Repair Unit, and no finalizer attempt exists. Enter **Repair and replay**.
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

For a nonempty diff, run the repository's complete required verification. Build one transient
originating-spec input containing the complete accepted Batch scope, every selected ticket and
acceptance source, and every governing Spec they reference, preserving each component's identity
and provenance.

Invoke public `code-review` once from the immutable Batch base with that complete input. Require
both its Standards and Spec axes to cover the same immutable diff, base, `HEAD`, and tree.
Standards must cover the repository standards and smell-baseline inputs owned by that dependency;
Spec must cover every component of the provenance-preserving originating ticket/spec input. A
failed verification, documented-standard violation, Spec mismatch, missing axis, incomplete
owner-defined coverage, or unclassifiable finding blocks finalization. A baseline smell is
advisory unless accepted project authority independently makes it blocking.

**Complete when:** full verification and both review axes pass without blocking findings on one
immutable diff, base, `HEAD`, and tree, with Standards and Spec each proving its own source
coverage above.

## Repair and replay

Freeze all blocking findings and the reviewed state as one Repair Unit. Read
[`worker-transaction.md`](worker-transaction.md) and dispatch or resume one exclusive repair worker
whose scope is those findings. Repair commits contain no ticket trailer. Independently prove its
complete range and local state, resolution of every finding, unchanged Ticket Commit boundaries,
required validation and self-review, a clean final worktree, and the unchanged target/base.

A noncomplete worker result or unsupported repair enters [`stop.md`](stop.md). After a complete
repair, re-establish every **Normal** entry predicate before returning to **Verify and review one
immutable state** and rerunning the full verification and both review axes. No earlier proof
survives the repair.

**Complete when:** the repaired state passes the entire verification/review barrier.

## Invoke the finalizer once

Build the public `finish-worktree` input from current proof: exact source worktree and target; the
originating `create-worktree` ready handoff as lifecycle provenance; either the uninterrupted
attributable implementation handoff or the fresh Reuse `ready` handoff required by the public
contract after a gap; immutable base; reviewed `HEAD` and tree; complete Batch-owned range and
boundary history; verification and both review reports; accepted outcome and history policy;
lifecycle owners; preservation boundary; publication facts; and exact effect and cleanup
authorities. Supply no tracker operation or alternative delivery judgment.

Immediately before the finalizer effect, require [`tracker.md`](tracker.md)'s whole-selection
revalidation against the frozen Selection Result and the exact claim effects already consumed by
this Batch. Drift invalidates the verification/review barrier and enters
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
