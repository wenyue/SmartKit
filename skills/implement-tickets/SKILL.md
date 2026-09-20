---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of eligible tracker tickets in one isolated worktree, or prove that the bounded scope has no eligible work; independently accept each ticket, then review and finalize the batch.
---

# Implement Tickets

Complete one frozen batch in dependency order in one prepared worktree. Independently accept one
commit per ticket, accept the combined result, then finalize it under the selected outcome. Only
proven authoritative delivery permits tracker completion. A proven empty new selection returns
`nothing-to-do` without mutation.

The active Agent is the **Controller**: it owns selection, progression and acceptance. Scoped
**Workers** implement tickets and repairs. Choose methods suited to the work within these boundaries:

- Preserve frozen membership, requirements, order and accepted commit boundaries. A blocked ticket
  pauses the batch; resolve the blocker before advancing.
- Each ticket and the whole batch receive one independent Standards/Spec round, followed by scoped
  correction and Controller verification until acceptance. Worker returns are verification points;
  clean results need no fabricated edits.
- Preserve the canonical checkout and unrelated work. Current worktree readiness permits local
  scope-only candidate commits and bounded amendments through normal hooks. That authority grants
  no tracker, remote, installation, finalization or cleanup effects.

Load public `create-worktree`, `code-review` and `finish-worktree` before using their contracts.
They own workspace/environment readiness, generic independent review and finalization. Resolve
tracker and triage contracts through the target project's `docs/agents/issue-tracker.md` and its
owner pointers; resolve required checks through applicable project rules and documented verification
interfaces. Use installed SmartKit core governance for ordinary authority, precedence and no-progress
judgment. Missing configuration or a required unavailable, failed or ambiguous capability stops at
its owner with attributable state retained; a present failed dependency is not an absent dependency.

On a possible prior attempt, interrupted control, missing evidence or material blocker, read
[Pause and resume](references/resume.md) before continuing. That branch preserves the original work
and effects; the ordinary path follows below.

## 1. Establish the batch

Before selecting work, observe repository and registered-worktree state, branch history, tracker
state, retained handoffs and live Worker/finalizer identities. Recover any existing or possible
attempt first. Original finalization and closure take precedence over current ticket eligibility.

For a proven new attempt, establish the caller's bounded scope, authoritative target, committed
immutable `batch_base`, selected finalizer outcome, history policy and exact effect authorities.
Observe the complete candidate set and every dependency edge needed for closure. Retain identities,
complete requirements and source revisions, statuses, owners/claims, ordering evidence, and positive
eligibility proofs or exclusion reasons. Uncertain membership, eligibility, identity or edges prevent
selection.

Recursively include same-scope open blockers only with affirmative eligibility proof. Record
completed, rejected, human-owned, information-blocked, externally claimed and other authoritative
negative results as exclusions. External blockers require authoritative completion proof; otherwise
exclude their dependents. Propagate unsatisfied dependencies, reject cycles, and order the closed
selection by dependency, using the tracker's stable public order only between equally ready tickets.

Resolve each ticket's owner-supported claim route and session/timing constraints: initial claim
before other batch writes, expressly compatible just-in-time claim at its later frontier, or no
claim when none is required. A claim operation's existence does not authorize claiming a ticket
before its dependencies are ready. Incompatible or uncertain timing stops before writes.

Freeze membership, dependency graph/order, requirements and source revisions, external completion
proofs, exclusions and claim routes. Report the selection and exclusions. If eligibility is proven
empty, return `nothing-to-do` with that evidence and make no mutation or batch.

### Keep tracker facts and effects attributable

At each claim, ticket acceptance and finalization boundary, re-observe relevant tickets and blockers
and compare them with the frozen selection. Check full accepted sources at ticket acceptance, and
all selected sources and the complete graph before finalization. Use authoritative revisions,
digests or change signals; reread content when a signal is unavailable or changed. An accepted
`completed-in-batch` commit and its proof satisfy that selected dependency for later tickets.

Exempt only exact claim/owner deltas proved by this batch's consumed operations. Other material
requirement, status, owner, claim or edge changes pause the batch for owner reconciliation. Preserve
the frozen requirements and membership; refresh affected checks and determine whether original
review coverage plus focused closure can support the reconciled result. Insufficient coverage or a
material decision/authority gap remains a blocker.

For every claim, completion or release, require the owner's documented operation, success meaning
and exact effect authority. Observe the before-state, request the effect once, retain the raw result,
and prove the authoritative after-state before dependent work. An already-existing state is
consumable only with sufficient meaning and provenance for this batch; otherwise treat it as drift.
A success response alone is insufficient, and a returned failure remains a failed attempt. An
ambiguous or missing response enters recovery of that original operation, not a repeat to obtain a
receipt. Hold acquired claims through authoritative delivery; release separately only where the
tracker defines it as part of closure.

## 2. Prepare one environment

If selected work depends on uncommitted source-checkout changes, preserve them and pause for their
owner to supply a separately authorized committed baseline. Reconcile the accepted base before
continuing; this workflow does not absorb, recreate, commit or discard that source work.

Before an initial or just-in-time claim, qualify dispatch read-only when release, reassignment or
expiry semantics make a later dispatch failure capable of stranding the claim. Establish runtime
availability, supported observation/control, scope authority and absence of a possibly live competing
attempt. Attribute any existing worktree exclusively; before creation, retain the readiness gate
before dispatch. Reuse current shared facts and assess ticket-specific constraints. This check
neither dispatches a Worker nor reserves capacity or creates state. Unresolved material dispatch
risk stops the claim with its fact and next owner.

Perform required initial claims in stable dependency order, proving each after-state before the
next and completing them all before creation or any other batch write. Defer just-in-time claims
to their ticket frontier.

Ask public `create-worktree` for explicit **clean** creation at `batch_base`, supplying accepted scope,
ownership, placement and setup-effect authority. That owner preserves the source and prepares the
environment, including its `worktree-environment-setup` dependency. Consume its attributable `ready`
result and bind that exact worktree to the batch.

Before the first Worker or deferred claim, compare the current physical path, Git common identity,
registration, branch, base, HEAD/tree, index and expected local state with the ready result. Recheck
the current binding on use and investigate material drift. Reuse the prepared environment for all
Workers and Reviewers; project checks still run when their inputs change. Recovery after a control
gap or invalidated readiness follows `resume.md`.

## 3. Complete each ticket

Take the next dependency-ready ticket in the frozen order. Revalidate its complete accepted sources,
blockers, status and claim. Consume its proven initial claim, perform its supported just-in-time
claim, or establish current no-claim eligibility. Freeze `ticket_base` and its tree at the preceding
accepted HEAD, using `batch_base` for the first ticket.

### Give the Worker one bounded unit

Use a fresh Worker for each ticket; keep that Worker's implementation and repair together. The batch
repair later uses a fresh Worker under this same protocol. Require supported runtime dispatch,
identity, observation, interruption and quiescence interfaces before dispatch.

Prove the exact worktree, unit base, HEAD/tree, complete local-state ownership and scoped authority,
with prior writers quiescent. At most one Worker may write; independent read-only roles may run in
parallel while writers are paused. Give the Worker:

- canonical ticket identity or batch-repair scope, complete requirements and source revisions,
  project rules, accepted dependency results and relevant research pointers;
- exact worktree, batch/unit bases, previous accepted commits, required targeted checks and scoped
  write/normal-hook commit authority; and
- for repair, original review evidence, consolidated findings, check failures and focused
  verification evidence.

The Worker owns only the current candidate. Accepted commits, tracker operations, finalization and
authorization of its own completion marker remain outside its authority. Require an attributable
return with Agent identity and raw status, candidate and final HEAD/tree, complete owned local state,
checks and their inputs, returned/interrupted phase, unresolved work and next action. Repair returns
also identify finding dispositions and exact delta. Preserve failed attempts as failures even when
files appear complete. Prove paused writes before review and quiescence before acceptance; elapsed
time or a missing response proves neither.

### Establish the complete candidate

Have the Worker produce the intended ticket result and the checks needed for acceptance and safe
subsequent work. Disclose any genuinely noncritical coverage deferred to the whole-batch barrier.
Implementation, testing and debugging continue before the review freeze.

For nonempty changes, create one normal-hook candidate with `ticket_base` as its sole parent and the
configured tracker's discoverable ticket reference in its message, without a `SmartKit-Ticket`
trailer. If existing behavior already fulfills the ticket, retain the base state for affirmative
requirement-based review. Omitting intended changes cannot establish a no-change result.

Pause writes. Independently verify that the candidate contains the entire intended result, ticket
checks pass, the index/worktree is clean under the project predicate, and material untracked or
ignored state has known ownership. Return omissions and failed checks to the same Worker before
freezing review.

### Obtain one independent review round

Use this review and closure contract for both a ticket and the whole-batch barrier. Freeze the
comparison base (`ticket_base` for a ticket, `batch_base` for the whole batch), HEAD/tree, complete
intended diff, and accepted requirements with source identities and revisions. Establish that
writers are paused and no intended task change is omitted.

For a nonempty diff, invoke public `code-review` with these exact inputs and **all** accepted sources,
even when commit discovery finds only one. Standards and Spec must be independent of the Worker and
one another. Both axes are required. Supply the applicable standards, public advisory smell-baseline
treatment, check evidence and this deep-review brief:

- Trace every accepted requirement to implementation and verification. Identify missing, partial,
  incorrect or unsupported fulfillment and unintended scope.
- Inspect relevant callers, callees and affected contracts beyond changed lines; challenge edge,
  error and recovery paths, compatibility and regressions. Whole-batch review covers all requirements
  and shared constraints, conflicting requirements and interactions.
- Report all useful evidence-backed findings with concrete source locations, the requirement or
  standard, behavior and evidence. Distinguish severity, advisory smells, coverage gaps and
  uncertainty. Preserve separate axes and findings; retain full supporting reports when the public
  summaries cannot hold them.

Public `code-review` rejects empty diffs. For an empty ticket or batch, use the same sole round for
two independent read-only Standards and Spec roles with the frozen implementation/base, full sources,
standards, checks and brief above. Require affirmative fulfillment evidence for every requirement
and Standards coverage of the relevant implementation. A ticket must already be fulfilled at
`ticket_base`; a net-empty batch must fulfill every selected requirement even when ticket changes
cancel one another. Preserve ticket commits. Emptiness or Worker assertions alone prove nothing.
Missing roles or inputs stop this route.

Collect both complete reports before repair. Each identifies its role, immutable inputs, coverage,
findings and uncertainty. Retain the original reports or recovery locations, and attributable
`never-started`, `in-flight`, `complete` or unresolved state for each axis. Recover incomplete or
missing reports before repair; missing coverage is not a clean verdict.

### Close findings until the Controller can accept

Judge every finding against accepted requirements and standards, with a reasoned disposition for
each, including advisory and declined findings. Give the Worker the consolidated repair set and
check failures. Preserve original reports and reviewed identities unchanged.

After each return, pause writes, repeat required checks on the resulting state, and record the exact
delta from review. Verify each accepted finding's resolution and repair impact on directly affected
behavior/contracts, including regressions, hooks and commit-sensitive checks. Explain how original
coverage plus this focused closure supports the exact final HEAD/tree and scope. This is Controller
acceptance of repairs, not a new passing reviewer verdict for unreviewed code.

Return incomplete fixes, related check failures, repair regressions and omissions found by focused
verification to the Worker. Continue correction and verification until acceptance; a return does
not exhaust repair authority. With no repair needed, use the unchanged reports and proceed. Amend
only the current unpublished, unaccepted candidate through normal hooks. If ticket repair introduces
changes from the base state, create its one candidate; if it empties that candidate, retain it for
the same ticket's empty commit.

Acceptance requires complete original coverage, justified dispositions for every finding, no
unresolved blocker or required-check failure, attributable authorized repair deltas when present,
and Controller verification on the exact final state. Metadata-only equivalents require explicit
binding and refreshed dependent checks. Changed diff shape, Worker, commit, source facts, route,
resumption or finalizer return never starts another formal round or expands scope.

Stop for a material decision/authority gap, unavailable prerequisite, unsafe or ambiguous state,
inadequate original coverage that would require new formal review, or no progress under applicable
rules. Preserve the original work and next owner through recovery. Later in-scope content changes
require this same focused closure; accepted commits remain fixed.

### Mark and accept the ticket commit

After closure, the Controller authorizes one bounded normal-hook operation on the exact candidate
with its canonical discoverable ticket reference and one completion trailer:

```text
SmartKit-Ticket: <canonical-id>
```

Amend the existing candidate's message. If no candidate exists for a no-change ticket, create one
empty commit with `ticket_base` as sole parent. A repair-emptied candidate becomes that same empty
commit by amendment, without appending another ticket commit.

Inspect the resulting commit, tree and diff. Bind metadata-only equivalence to original reports and
refresh commit-identity and hook-sensitive checks. A no-change ticket must equal the base tree and
retain affirmative fulfillment evidence. Hook-created content leaves the ticket incomplete: return
the candidate to the Worker to remove the premature marker and close the delta under the original
review, then reauthorize marking. A trailer or successful hook alone cannot prove acceptance.

With writes paused, the Controller proves exactly one commit in the first-parent range from
`ticket_base`, that sole parent, and exactly one trailer with the canonical ID. Prove full ticket
scope, unchanged earlier accepted commits, final tree/diff bound to original review and any repair
closure, passing required checks, clean local state and Worker quiescence. Recheck worktree/target
binding and frozen sources, blockers, status and claim.

Return this fixed commit as `completed-in-batch`. It satisfies an in-batch dependency, while the
tracker ticket remains open and its claim held. Continue automatically to the next ready ticket,
or to the combined barrier once all selected tickets are accepted. Later corrections to accepted
tickets belong to the combined result.

## 4. Accept the combined result

With every ticket accepted and Workers quiescent, freeze HEAD/tree and run required whole-batch
checks. Obtain both complete independent reports under the review contract above against immutable
`batch_base`, the entire combined diff and all accepted requirements. Ticket evidence is context,
not a substitute. This barrier also applies to a single-ticket or net-empty batch.

Collect check failures and findings before choosing repair. Ordinary check failures need not prevent
review of a meaningfully reviewable frozen state; missing prerequisites or incomplete evidence pause
the barrier. If repair is needed, freeze `repair_base` at accepted HEAD and retain the failed state,
original reports and every accepted ticket commit. Dispatch a fresh batch-repair Worker under the
bounded-unit protocol with the consolidated findings, checks and scope authority.

If content changes, create at most one separate normal-hook repair candidate with `repair_base` as
sole parent and no ticket trailer. Amend only that unpublished, unaccepted candidate while continuing
focused closure. If content need not change, retain HEAD and evidence resolving the failure.

Accept only after closure and required whole-batch checks support exact final HEAD/tree within
`batch_base`. Prove scope, unchanged accepted ticket history, clean local state, Worker quiescence,
source freshness and complete acceptance evidence. A repair candidate must be the sole commit from
`repair_base`, with that sole parent and no ticket trailer; otherwise prove unchanged HEAD.
Continue scoped repair for unresolved work and preserve it on a stop. Acceptance fixes the repair
commit. A later in-scope correction may establish the sole batch-repair candidate if none exists;
changing an accepted repair commit or adding another requires its history owner and separate authority.

## 5. Finalize and close according to delivery

Revalidate every frozen ticket, source and dependency edge. Compare the bound worktree's current
identity, base, HEAD/tree and complete local state with final acceptance; recheck the authoritative
target and account for material untracked/ignored residuals. Material content, source or target drift
requires owner reconciliation and affected focused closure before progression.

Read public `finish-worktree`'s selected route and required history, effect-recovery and results
contracts. Supply one accepted handoff with:

- scope and complete ticket/spec sources; exact source/target identities, immutable base and accepted
  HEAD/tree/diff; ticket and any batch-repair commit boundaries;
- original review inputs and full reports, every disposition, authorized repair deltas, check
  provenance and Controller closure bound to the accepted state; and
- selected outcome/history policy, exact effect and cleanup authority, publication/local residuals,
  preservation and lifecycle owners.

Preserve per-ticket history by default. Separately authorized consolidation retains original source
boundaries for recovery and tracker closure. Use the finalizer's implementation-owner acceptance
evidence route: it consumes original reports and Controller closure without another formal review
and retains its operation-sensitive checks. A returned content or source/target change requires
owner reconciliation and the same focused closure, preserving accepted history and original effect
provenance. Different history operations require their owner's contract and authority.

For **Already Delivered**, including net-empty batches, bind existing requirement-based acceptance
evidence to the exact authoritative target through proven equivalence with the covered state and
refresh target-dependent checks. The finalizer independently proves every accepted effect on that
target. Source emptiness alone is insufficient. Unproved equivalence or fulfillment pauses for
externally resolved evidence or the already selected supported outcome; it permits neither another
formal round nor manufactured changes, delivery or an empty PR.

Invoke the finalizer once for this accepted result, retaining its attributable invocation, raw
response and effects. Recover a prior or interrupted attempt before any replacement effect.

### Consume the result

Consume the public result unchanged: raw status, causal boundary, phase results, effects and strongest
proven classification. Only attributable `authoritative delivery`, including the finalizer's own
Already Delivered proof, permits tracker closure. Delivery remains proven despite a coincident
stopped/failed status or incomplete cleanup.

For authoritative delivery, re-observe tickets in dependency order, perform each documented completion
and any separately required claim release, and prove each after-state through the tracker effect
contract above. Consume an already-proven completed prefix and continue only its unresolved suffix.
The first failed or ambiguous effect stops closure and leaves later tickets untouched. Preserve
delivery and accepted source/recovery boundaries. Give completed closure proof to the finalizer's
named lifecycle owner for authorized retention, release or cleanup without repeating delivery.

Every other classification keeps tickets open and claims held while following its named continuation,
unless separate tracker authority resolves their disposition. Preserve attributable PR, retained
worktree, transfer, authorized-discard and partial-result evidence. Cancellation requiring claim
disposition stays with the tracker owner under separate exact authority. An unavailable or ambiguous
classification returns to the finalizer owner; it proves neither delivery nor retry authority.

Record consumption in the retained handoff and resume only the named unfinished action. Keep proven
effects, source history and recovery items until their owners establish their dispositions. Report
accepted tickets, exclusions, raw finalizer outcome, tracker and lifecycle state, retained locations,
and the next owner/action for anything unfinished.
