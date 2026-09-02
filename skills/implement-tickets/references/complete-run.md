# Complete the Run

This reference has three mutually exclusive entries:

- **Normal:** all Ticket Commit boundaries are proven, Batch claims are retained, the Batch
  Worktree is clean, the immutable target/base remains valid, and no finalizer effect attempt
  exists. Start at verification below.
- **Repair-recovery:** the same Batch binds the frozen whole-review findings, `repair_base`, every
  Ticket Commit boundary, retained claims, fully accounted repair-owned commits and local state,
  and the durable Worker Handoff; no finalizer effect attempt exists. Enter only **Repair and
  replay**.
- **Returned-response:** the exact durable `finish-worktree` response and its attempt are bound to
  a post-finalizer marker and Batch Handoff that agree on `result-awaiting-consumption`. Enter only
  **Consume the returned result**; do not rerun verification, review, repair, or finalization.

For each immutable review pass, assemble one transient **Originating Spec Input**: the union/package
of the complete accepted Batch scope; every selected ticket and its complete acceptance sources;
and every governing Spec referenced by those sources. Preserve every component's identity,
provenance, and full content. The package neither collapses its components into a new normative
Spec nor persists a Review Adapter.

## Verify and review one immutable state

Freeze one candidate `HEAD` and tree. Run the repository's complete required verification, then
invoke public `code-review` once from the immutable Batch base with the complete transient
Originating Spec Input as its single originating issue/spec input. Retain its separate Standards
and Spec reports. Prove that both axes and every packaged source were covered against the same
base, `HEAD`, and tree.

A Spec requirement mismatch and a documented-standard violation are blocking. A baseline smell is
nonblocking unless an accepted project standard or source independently makes it blocking. Missing
axes, incomplete source consumption, unclassifiable findings, failed verification, or failed review
evidence does not pass the barrier.

For blocking findings, freeze the whole set, reviewed state, `repair_base`, allowed paths, Ticket
Commit boundaries, retained claims, and any owned repair state as one **Repair Unit**, then enter
the repair route below.

**Complete when:** full verification and both review axes pass without blocking findings on one
immutable base/`HEAD`/tree, with every Ticket Commit boundary preserved.

## Repair and replay

At the first worker-related need, read
[`worker-transaction.md`](worker-transaction.md). Give it the frozen Repair Unit and durable Worker
Handoff and consume only its complete, incomplete, or ambiguous result and replacement
eligibility. A permitted replacement stays within that transaction and uses a fresh attempt;
otherwise a noncomplete or ambiguous handoff reads [`stop.md`](stop.md) and returns without
adapting worker state.

As Repair Unit owner, independently prove a complete handoff: worker quiescence; the entire
first-parent range from `repair_base`; ownership and allowed paths; resolution of every frozen
finding; absence of ticket trailers; unchanged Ticket Commit boundaries; required validation and
self-review; a clean final `HEAD` and tree; retained claims; and the unchanged target/base. Any
missing proof enters `stop.md`.

After that proof, freeze the repaired `HEAD` and tree and return to **Verify and review one
immutable state**. Rerun the complete required verification and both public review axes against the
same immutable base and a freshly assembled complete transient Originating Spec Input. No proof
survives a repair; findings outside the Batch or exhausted authorized repair capacity enter
`stop.md`.

**Complete when:** the repaired state is independently proven and the complete verification and
two-axis review barrier passes on it.

## Invoke the finalizer once

Build the `finish-worktree` input from the proven current evidence: exact worktree and target,
immutable base, reviewed `HEAD` and tree, complete Batch-owned range, retained boundary history,
verification and both review reports, chosen outcome and history policy, lifecycle owners,
preservation boundary, and every required effect/publication/cleanup grant. Supply no tracker
operation or alternative delivery rule.

Before invocation, transition one finalizer attempt record through the Persistence Contract. Bind
its unique identity, expected prior state, authorization, exact frozen dependency contract and
input, and reviewed base/`HEAD`/tree. Invoke `finish-worktree` once. An absent, interrupted, or not
causally attributable dependency response keeps that finalizer effect attempt in flight; read
[`recover-finalizer.md`](recover-finalizer.md) and do not invoke another finalizer effect attempt.

For a causally attributable raw response, transition the complete response,
`result-awaiting-consumption` marker, and current Batch Handoff through the Persistence Contract
against that attempt. If the persistence capability, authority, or proof route is unavailable, or
that transition's invocation or after-state is ambiguous, enter [`stop.md`](stop.md)'s
**Persistence is unavailable or unresolved** entry with the same persistence boundary. Do not
route that condition to finalizer recovery or initiate another response transition. Enter the
result route below only after the frozen persistence recovery owner reconciles that same transition
and its exact awaiting-consumption after-state is re-proven.

## Consume the returned result

Consume the response's `status`, `classification`, `causal_boundary`, `history_result`,
`outcome_result`, `cleanup_result`, effects, residuals, and handoff exactly as returned. This is
the sole public result route. It never derives a classification from target state or upgrades,
downgrades, or replaces the dependency's status. Before a selected branch performs an effect,
returns, or hands off, transition its marker and current Batch Handoff together through the
Persistence Contract and prove the exact agreeing after-states described below. An unavailable or
ambiguous transition keeps `result-awaiting-consumption` in flight and blocks that branch:

- `authoritative delivery`, including **Already Delivered** only when supplied by
  `finish-worktree`, transitions to `delivery-consumed(first-tracker-cursor)` with the exact raw
  result and delivery phase, then enters the delivery-closure section of
  [`tracker.md`](tracker.md). Preserve a raw `stopped` or `failed` status alongside the
  authoritative classification.
- `non-integrating handoff` transitions to `non-delivery-consumed` with the exact dependency
  handoff, owner/action, and lifecycle/retention disposition, then returns it. Tickets and claims
  remain open; retain the worktree, source-boundary history, publication and recovery evidence
  required by it.
- `history finalized` or `no positive result` enters [`stop.md`](stop.md) with
  `non-delivery-consumed` as the required marker state for the Batch Handoff transition it owns,
  then returns the raw stopped/failed/other noncomplete handoff. Tracker closure is not authorized.
- An unavailable or ambiguous dependency classification transitions to `non-delivery-consumed`
  with the exact raw response and finalizer owner's unresolved handoff, then returns that owner and
  action without inference or retry.

After authoritative delivery and tracker closure, give its proof to the existing
`finish-worktree`/lifecycle cleanup owner for the same attempt. Retain the reviewed source history
until tracker closure and that owner proves the disposition of every worktree, ref, boundary and
recovery item. This cleanup continuation does not rerun history or outcome effects.

**Complete when:** the single attempt has an authoritative raw result and its marker and Batch
Handoff prove its unique result route consumed before return, or its in-flight recovery owner and
next action are preserved.
