---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of eligible tracker tickets in one isolated worktree, then review and finalize the batch once.
---

# Implement Tickets

Run one nonempty **Ticket Batch** sequentially in one isolated **Batch Worktree**. Worker attempts
are serial and exclusive; every authorized attempt uses a fresh identity that is never reused
across attempts or units. A ticket may have **Checkpoint** commits, but ends in exactly one
**Ticket Commit** with exactly this trailer:

```text
SmartKit-Ticket: <canonical-id>
```

No Checkpoint or repair commit has a ticket trailer. The controller retains recoverable first-
parent boundaries, but workers own only their assigned unit. The selected Batch receives one
whole-batch review and one finalization; complete verification and review reruns after repair are
part of that same Batch.

Use the project-owned tracker, ticket/spec sources, repository rules, and validation. Invoke the
public `create-worktree`, `code-review`, and `finish-worktree` Skills through their current
contracts. Those dependencies retain their own judgments: in particular, `create-worktree` alone
decides readiness and `finish-worktree` alone decides delivery, **Already Delivered**, and
non-integrating classification. This Skill grants no tracker, Git, worker, network, publication,
retention, or cleanup effect beyond authority supplied by the caller and those owners.

Before any Batch effect, the caller or environment must freeze one **Persistence Contract**. It
names one durable route and store outside repository Candidate or cache state; the store owner and
permitted actors; the existing record identities for Batch and Worker handoffs, `create-worktree`
Create/Reuse invocation attempts and raw responses, finalizer attempts and raw responses,
post-finalizer progress markers, and operation cursors; each actor's exact read, write, retention,
and deletion capabilities and authorities; the before/after proofs; recovery owners; and every
consumer, lifecycle, retention, and deletion disposition. Use those records and that supplied
mechanism only—create no repository file, cache, standalone adapter, or global lock.

Every record transition is one uniquely identified authorized persistence attempt. Observe its
exact before-state, write once, then re-read and prove the exact after-state. An unavailable
capability or authority stops before the attempt; an unavailable verifiable after-state stops
before the guarded effect. An ambiguous transition remains in flight and is not repeated, and its
guarded effect cannot run, until the frozen recovery owner reconciles that same attempt. Retain
recovery records until their frozen consumer and lifecycle owners prove disposition. Deletion uses
the same transition rule and requires exact deletion authority and proof of the after-state. Every
later instruction to record, transition, advance, or retain durable state means this contract.

Every public `create-worktree` Create or Reuse invocation follows one **Worktree Invocation
Boundary** using those existing attempt and response records. Before invocation, transition one
unique attempt binding the mode, exact input and pre-state, authority, and original actor/effect-
recovery owner; prove its after-state, then invoke once. On an attributable return, transition the
complete raw response and prove its after-state before consuming it. A missing or ambiguous
response keeps that invocation in flight and hands its unchanged identity, input, evidence, and
uncertainty to the original owner fixed by the frozen dependency contract. No new Create or Reuse
invocation is eligible until that owner returns an attributable response or exactly reconciles the
original effects, residuals, and current state to a disposition that the frozen dependency
contract proves permits the next invocation. This boundary assumes no recovery interface and never
infers `ready` or `non-ready`. Consume `ready` only after both record proofs and an immediate recheck
of the public mode-specific readiness snapshot.

Through that contract, freeze a durable **Batch Handoff** before the first non-persistence Batch
effect. It binds the canonical scope and sources, selection and dependency order, immutable
target/base commit and tree, outcome and history policy, Batch Worktree identity and lifecycle
owners, tracker operations and claims, worker runtime/retention authority, verification and review
sources, Ticket Commit boundaries, finalizer attempt, every relevant grant and effect, and the
exact current phase and next owner. Keep it current at every recoverable boundary. Drift in an
immutable field stops this Batch.

For post-finalizer recovery, the existing progress marker has exactly three states:

- `result-awaiting-consumption` binds the exact raw response before its public result route runs;
- `delivery-consumed` binds that response and the current tracker/lifecycle cursor after its route
  consumes an authoritative-delivery classification; or
- `non-delivery-consumed` binds that response, the selected public result branch, retained handoff,
  next owner/action, and lifecycle/retention disposition after any other result route runs.

Every progress-marker transition includes the current Batch Handoff and proves their exact
agreeing after-states. A consuming route does so before any branch effect, return, or handoff. An
unavailable or ambiguous transition keeps `result-awaiting-consumption` in flight and blocks the
branch. These proven states make first consumption, delivery closure, and non-delivery disposition
mutually exclusive.

At the first noncomplete boundary—whether an owner returns it or the Controller finds route
ambiguity, conflict, an invalid causal chain, or another unproved boundary—read
[`references/stop.md`](references/stop.md) before classifying or returning. Select its entry from
the raw boundary. Its pre-Batch and unresolved-persistence entries return evidence without another
durable transition; its established entry updates the existing Batch or Worker Handoff. Enter that
owner with the raw evidence; do not reproduce its status mapping here or infer continuation.

## Route the entry

Initially observe only non-tracker durable Batch, Git, retained-worker, and finalizer evidence
without mutation. Before observing any ticket, blocker, status, claim, selection, or tracker
residue, read [`references/tracker.md`](references/tracker.md) and delegate that observation to its
owner. When route selection needs such evidence, load it before selecting the route; a
finalizer-only route that needs none does not load it. Select one route:

- **New:** non-tracker evidence admits a New candidate. After the tracker first-use gate, admit
  establishment only when the Controller combines a nonempty frozen Selection Result with the
  tracker's own ticket, claim, residue, and operation-cursor observations and proves no overlap
  with an attributable unfinished Batch or in-flight tracker operation. If the combined tracker
  and non-tracker evidence uniquely binds an existing Batch or operation, route it to that existing
  owner. Ambiguous or conflicting attribution enters `stop.md`.
- **Before finalization:** reconstruct the exact Batch, first-parent boundaries, at most one
  current unit range, and all local state. Every item needs one Batch unit owner. Load
  [`references/process-one-ticket.md`](references/process-one-ticket.md) for a ticket frontier, or
  [`references/complete-run.md`](references/complete-run.md) for a repair or review frontier. When
  a worker may have been dispatched, its route must first load
  [`references/worker-transaction.md`](references/worker-transaction.md) and prove the worker
  boundary. After any required quiescence proof, freeze the observed current `HEAD` and tree and
  apply the Worktree Invocation Boundary once in Reuse mode against that caller-frozen snapshot.
  Continue only from its attributable raw `ready` handoff and immediate readiness-snapshot recheck.
- **Returned finalizer result awaiting consumption:** the durable raw response exists and the
  post-finalizer marker and Batch Handoff agree on `result-awaiting-consumption` and prove that its
  result route has not run. Read `complete-run.md` and enter only its result-only entry with that
  unmodified response.
- **Consumed non-delivery result:** the marker and Batch Handoff agree on
  `non-delivery-consumed`, the finalizer attempt and exact raw response, selected public result
  branch, phase, retained handoff, next owner/action, and lifecycle/retention disposition. Return
  or resume only that bound owner/action; never re-enter result consumption, tracker closure, or a
  finalizer effect.
- **Lost or in-flight finalizer response:** the attempt exists but no attributable durable response
  or consumed-result marker does. Read
  [`references/recover-finalizer.md`](references/recover-finalizer.md) and return its route.
- **Consumed delivery with incomplete closure:** the marker binds the exact `finish-worktree`
  authoritative-delivery classification and current tracker or lifecycle cursor. Read `tracker.md`
  for a tracker cursor, or resume the frozen `finish-worktree`/lifecycle cleanup owner at its bound
  cursor.

Target state, ticket state, absent local changes, or missing cleanup never substitutes for the
durable causal evidence. Ambiguous identity, ownership, phase, or multiple possible routes enters
`stop.md` through the first-use gate above.

**Complete when:** exactly one authoritative route and next owner are established.

## Select and establish a New Batch

Resolve one bounded scope and ask `tracker.md` for its frozen **Selection Result**. Consume its
selected tickets, complete sources, dependency graph and order, exclusions, external completion
proofs, and drift boundary without reinterpreting them.

Freeze the Batch Handoff and the exact worker/runtime capabilities required by every reachable
ticket and repair before mutation. Apply the Worktree Invocation Boundary once in Create mode from
the immutable target base. If its response is lost or establishment is ambiguous, never repeat
Create. Only after its original owner proves the call and creator quiescent and reconciles every
observed candidate item to that exact invocation may one Reuse invocation under the same boundary
validate that exact worktree against a caller-frozen current `HEAD`/tree and the immutable-base
lineage. Otherwise stop with the attempt and residue retained.

Accept only the public Skill's attributable raw `ready` handoff after the boundary's attempt and
response proofs. Immediately before the first claim or worktree mutation, recheck its mode-specific
readiness snapshot. Preserve the canonical checkout and unrelated state.

**Complete when:** the closed selection, immutable Batch, empty tracker-operation prefix, and one
ready Batch Worktree at the immutable base are proven.

## Execute the dependency frontier

Consume the frozen Selection Result's dependency order and readiness evidence. For each indicated
ticket, read `process-one-ticket.md` at first use and follow it through `completed-in-batch`; give
the proven boundary back to the Selection Result before requesting the next ticket. A result that
cannot identify one next ticket while tickets remain stops rather than authorizing reordering or a
wider Batch. Worker replacement and attempt eligibility remain solely in `worker-transaction.md`.

Do not complete tracker tickets or release claims during implementation. Retain the source history
that proves every Ticket Commit boundary, including when finalization later consolidates it.

**Complete when:** every selected ticket has exactly one independently proven Ticket Commit in
dependency-valid first-parent order.

## Review, finalize, and close

Read [`references/complete-run.md`](references/complete-run.md) before normal review and follow its
verification, public review, repair, finalizer, and result route. Only authoritative delivery as
classified by `finish-worktree` enters the post-delivery route in `tracker.md`. Non-integrating
results retain open tickets, claims, worktree, history, and the dependency's exact handoff.

After tracker closure, supply its proof to the frozen finalizer/lifecycle cleanup owner. Completion
requires proof that every retained worktree, ref, boundary-history item, and recovery object has the
authorized removed, released, or retained disposition. After-delivery recovery never recreates a
worktree, dispatches a worker, reruns verification or review, or starts another finalizer effect
attempt.

Return the Batch selection/order, boundaries, worker handoffs, verification and separate review
axes, raw finalizer status/classification/phase results, tracker-operation cursor, delivery and
cleanup proof, effects and retained state, and exact next owner/action.

**Complete when:** authoritative delivery, dependency-ordered tracker closure, and lifecycle
cleanup are all proven; or the exact authoritative non-integrating, in-flight, stopped, or failed
handoff is returned without reinterpretation.
