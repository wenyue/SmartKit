---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of eligible tracker tickets in one isolated worktree, or prove that the bounded scope has no eligible work; independently accept each ticket, then review and finalize the batch.
---

# Implement Tickets

Complete one frozen selection in dependency order, independently accepting one commit per ticket,
then accepting and finalizing the combined result. A proven empty new selection returns
`nothing-to-do` without effects.

The active Agent is the **Controller**. It owns batch progression and acceptance; Workers implement
bounded units. Choose investigation, implementation and verification methods suited to the work.
These boundaries govern the result:

- **Frozen scope.** Preserve selected membership, requirements, dependency order and accepted commit
  boundaries. A blocker pauses the batch; skipping a ticket or changing the queue cannot resolve it.
- **Independent acceptance.** Each ticket and the whole batch receive the deep review and bounded
  closure defined in [Review and repair](references/review.md).
- **Scoped authority.** Preserve the canonical checkout and unrelated work. After current worktree
  readiness is established, local candidate commits and bounded amendments use normal hooks and
  the workflow's scope-only commit authority. They grant no tracker, remote, installation,
  finalization or cleanup effects.

Read public `create-worktree`, `code-review` and `finish-worktree` before using their contracts.
They own workspace/environment readiness, generic independent review, and finalization respectively.
Resolve tracker policy through [Tracker boundary](references/tracker.md), and required checks through
applicable project rules and documented verification interfaces. Missing, unavailable, failed or
ambiguous required capabilities stop at their owner with attributable state retained. A present
failed dependency is never treated as absent.

## 1. Establish the batch

Before fresh selection, observe repository and registered-worktree state, branch history, retained
handoffs, and live Worker or finalizer identities. Read `tracker.md` before tracker observation. Any
existing or possible attempt enters [Pause and resume](references/resume.md); prior finalization or
closure takes precedence over current eligibility.

Only evidence of a new batch permits selection. Establish the bounded input scope, target,
committed immutable `batch_base`, selected finalizer outcome, history policy and exact effect
authorities. Use `tracker.md` to close dependencies and freeze membership, order, complete accepted
requirements with source revisions, exclusions and claim routes. Report the selection and exclusions
so it is clear which part of the user's input will be handled. A proven empty selection ends here.

## 2. Establish one environment

If a selected ticket depends on uncommitted source-checkout work, pause for its owner to supply a
separately authorized committed baseline. Preserve that work; automatically committing, discarding,
reimplementing or absorbing it as ticket changes is outside this workflow. Reconcile the accepted
base before continuing.

Complete all required initial claims before other batch writes. Request explicit **clean** creation
at the frozen `batch_base` through `create-worktree`, supplying scope, ownership, placement and
setup-effect authority. That owner preserves the source and prepares the environment, including its
`worktree-environment-setup` dependency.

Consume an attributable `ready` result and bind its exact worktree to this batch. Before the first
Worker or deferred claim, check its current physical path, Git common identity, registration,
branch, base, HEAD/tree, index and expected local state against that result. Reuse the environment
for Workers and Reviewers; `resume.md` governs refresh after drift or interrupted control. Required
project checks still run when their inputs change.

## 3. Accept each ticket

For each dependency-ready ticket, follow [Process one ticket](references/process-one-ticket.md) with
its frozen requirements and preceding accepted HEAD. Advance only on the Controller's
`completed-in-batch` result: exactly one independently accepted first-parent ticket commit. Earlier
accepted commits remain fixed; tickets stay open and claims held.

## 4. Accept the combined result

With every selected ticket accepted and Workers quiescent, enter the whole-batch procedure in
[Review and repair](references/review.md#accept-the-whole-batch). Advance only when that contract
accepts the exact final HEAD/tree, preserving all ticket boundaries. This barrier applies even to a
one-ticket batch and a net-empty result.

## 5. Finalize the accepted batch

Revalidate all frozen tickets, sources and dependency edges through `tracker.md`. Check the bound
worktree's current identity, base, HEAD/tree and complete local state against final acceptance, and
recheck the authoritative target. Account for material untracked and ignored residuals. Material
content, source or target drift pauses for reconciliation by its owner; refresh affected evidence
within `review.md`'s existing allowance.

Read `finish-worktree`'s selected route and required history, recovery and public results contracts.
Supply one accepted handoff: scope and complete ticket/spec sources; exact source/target identities,
immutable base and accepted HEAD/tree/diff; ticket and any batch-repair commit boundaries; and the
acceptance evidence defined in `review.md`. Include the selected outcome and history policy, exact
effect and cleanup authority, publication/local residuals, and preservation/lifecycle owners.
Preserve per-ticket history unless consolidation was separately explicitly selected; retain original
source boundaries for recovery and tracker closure even then.

Use the finalizer's implementation-owner acceptance-evidence route. It consumes original reports
and Controller repair closure without another formal review, while retaining its operation-sensitive
checks. A returned content or source/target change re-enters authorized reconciliation here. Only an
unused batch repair with adequate original coverage can change the accepted result; a different
history operation needs its owner's contract and authority.

For **Already Delivered**, including a net-empty batch, provide existing requirement-based acceptance
evidence bound to the exact authoritative target through proven equivalence with the covered state.
Refresh target-dependent checks. The finalizer independently proves every accepted effect on that
target; source emptiness alone is insufficient. If equivalence or fulfillment is unproved, pause
for externally resolved evidence or the already selected supported outcome. This creates no target
review allowance and cannot justify manufactured content, delivery or an empty PR.

Invoke the finalizer once for this accepted result and retain its raw response and effects. A prior
or interrupted attempt follows `resume.md` before any replacement effect.

### Consume the result

Consume the finalizer's public result unchanged, preserving its raw status, causal boundary, phase
results, effects and strongest proven classification. Only attributable `authoritative delivery`,
including its own Already Delivered proof, enters [tracker closure](references/tracker.md#close-after-authoritative-delivery).
Delivery remains valid despite a coincident stopped/failed status or incomplete cleanup. Give
closure proof to the named lifecycle owner for remaining retention or cleanup without repeating
delivery.

Every other classification follows its named continuation with tickets open and claims held,
unless separate tracker authority resolves their disposition. Retain the PR, worktree, transfer,
authorized-discard or partial-result evidence that the public contract supplies. An unavailable or
ambiguous classification returns to the finalizer owner; it establishes neither delivery nor retry
authority.

Record consumption in the retained handoff and resume only the named unfinished action. Preserve
proven effects and accepted source/recovery boundaries until tracker and lifecycle owners resolve
their dispositions. Report accepted tickets, exclusions, raw finalizer outcome, tracker/lifecycle
state, retained locations and the next owner/action for anything unfinished.

At any material blocker, use `resume.md` to preserve partial work and pause the whole batch. An
unavailable capability, exhausted allowance or unresolved failure remains with its exact owner;
never repeat a possibly completed external effect to get past it.
