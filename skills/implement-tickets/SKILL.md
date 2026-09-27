---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of tracker tickets in one isolated worktree.
disable-model-invocation: true
---

# Implement Tickets

Complete one frozen, dependency-ordered batch in one prepared worktree. Accept a fixed commit for
each ticket, then accept the combined result and hand it to the selected finalizer. Tracker
completion follows proven authoritative delivery, not merely implementation or a successful handoff.
A proven empty new selection returns `nothing-to-do` without mutation.

The active Agent is the **Controller**, responsible for selection, progression and acceptance.
Fresh scoped **Workers** implement tickets and repairs. Keep the frozen requirements, membership,
order and accepted commit boundaries intact. A blocked ticket pauses the batch; skipping it does
not resolve the blocker. Each ticket and the combined batch receive one independent Standards/Spec
round, followed by scoped correction and Controller verification until acceptance. A Worker return
is a point to verify progress, not a reason to stop repairing or manufacture an edit.

## Use each owner's contract

Load public `create-worktree`, `code-review` and `finish-worktree` before using them. They own
workspace/environment readiness, generic independent review and finalization respectively. Resolve
tracker and triage policy through the target project's `docs/agents/issue-tracker.md` and its owner
pointers. Applicable project rules and documented verification interfaces supply required checks;
independently supplied SmartKit core governance supplies authority, precedence and no-progress
judgment.

This workflow protects the canonical checkout and unrelated work. Current worktree readiness permits
local scope-only candidate commits and bounded amendments through normal hooks. It does not grant
tracker, remote, installation, finalization or cleanup effects. Establish those authorities with
their owners. Missing configuration or a required unavailable, failed or ambiguous capability stops
its dependent work with attributable state retained; a present failed dependency is not an absent
one.

Before new selection, look for an existing or possible attempt in repository/worktree state, branch
history, tracker observations, retained handoffs and live Worker/finalizer identities. On that
branch, interrupted control, missing evidence or a material blocker, read [Pause and Resume](references/resume.md)
before proceeding. Recover the original attempt first. Its finalization and tracker closure take
precedence over what the current queue would select.

## Freeze an eligible dependency-ordered batch

For a proven new attempt, establish the caller's bounded scope, authoritative target, committed
immutable `batch_base`, selected finalizer outcome, history policy and exact effect authorities.
Observe the complete candidate set and the dependency edges needed to determine its closure. Retain
canonical identities, complete requirements and source revisions, statuses, owners/claims, ordering
evidence and either positive eligibility proof or an exclusion reason. Uncertain identity,
membership, eligibility or dependencies prevent selection.

Recursively include an open same-scope blocker only when it has affirmative eligibility proof.
Completed, rejected, human-owned, information-blocked, externally claimed and other authoritative
negative results are exclusions. An external blocker needs authoritative completion proof; otherwise
exclude its dependents. Propagate unsatisfied dependencies, reject cycles and order the closed
selection by dependency. The tracker's stable public order breaks ties only among equally ready
tickets.

Resolve the claim route for each selected ticket before writes:

| Route | Required timing |
| --- | --- |
| Initial claim | The tracker permits the claim now; complete required initial claims before creation or other batch writes. |
| Just-in-time claim | The owner expressly supports claiming at that ticket's later dependency-ready frontier. |
| No claim | The tracker requires none; establish current eligibility at the frontier. |

Account for session and timing constraints. The existence of a claim operation does not authorize
claiming before dependencies are ready. An incompatible or uncertain route stops before writes.
Freeze membership, graph/order, requirements and source revisions, external completion proofs,
exclusions and the claim plan. Report the selection and exclusions. When this proves a new selection
empty, return `nothing-to-do`; do not create a batch or mutate state.

### Preserve tracker facts and effect provenance

At claim, ticket-acceptance and finalization boundaries, re-observe relevant tickets and blockers
against the frozen selection. At ticket acceptance, check the complete accepted sources; before
finalization, check all selected sources and the complete graph. Use authoritative revisions,
digests or change signals, rereading content when a signal is missing or changed. An accepted
`completed-in-batch` commit and its proof satisfy that selected dependency for later tickets.

Only exact claim/owner deltas proved by this batch's consumed operations are exempt from drift
handling. Other material requirement, status, owner, claim or edge changes pause progression for
owner reconciliation. Preserve frozen membership and requirements. Refresh affected checks and
determine whether the original review coverage plus focused closure can support the reconciled
state. Insufficient coverage or a material decision/authority gap remains a blocker.

For each claim, completion or release, establish the documented operation, its success meaning and
exact authority. Observe before-state, request the effect once, keep the raw result and prove the
authoritative after-state before dependent work. Existing state is consumable only with sufficient
meaning and provenance for this batch; otherwise it is drift. A success response alone is not proof,
and a returned failure remains a failed attempt. Recover an ambiguous or missing response as the
original operation rather than repeating it to obtain a receipt.

Hold acquired claims through authoritative delivery. Release separately only when the tracker
requires it as part of closure; other dispositions need the tracker's separate exact authority.

## Prepare one clean-base environment

If selected work depends on uncommitted source-checkout changes, preserve them and pause for their
owner to supply a separately authorized committed baseline. Reconcile the accepted base before
continuing. This workflow cannot absorb, recreate, commit or discard that source work.

Before an initial or just-in-time claim, qualify dispatch read-only when release, reassignment or
expiry semantics could make a later dispatch failure strand the claim. Establish runtime
availability, supported observation/control, scope authority and absence of a possibly live
competing attempt. Attribute an existing worktree exclusively; before creation, keep readiness as
a prerequisite to actual dispatch. Reuse current shared facts and assess ticket-specific constraints.
Qualification neither dispatches a Worker nor reserves capacity or creates state. Unresolved
material dispatch risk stops the claim with its fact and next owner.

Perform all required initial claims in stable dependency order, proving each after-state before the
next. Complete them before creation or any other batch write. Leave just-in-time claims for their
respective ticket frontiers.

Invoke public `create-worktree` for explicit **clean** creation at `batch_base`, supplying accepted
scope, ownership, placement and setup-effect authority. That owner preserves the source and prepares
the environment, including its `worktree-environment-setup` dependency. Consume an attributable
`ready` result and bind its exact worktree to the batch.

Before the first Worker or deferred claim, compare physical path, Git common identity, registration,
branch, base, HEAD/tree, index and expected local state with that result. Recheck the current binding
on use and investigate material drift. All Workers and Reviewers use this prepared environment;
project checks still rerun when their inputs change. A control gap or invalidated readiness follows
[Pause and Resume](references/resume.md).

## Produce one ticket candidate

Take the next dependency-ready ticket in the frozen order. Revalidate its complete accepted sources,
blockers, status and claim. Consume its proven initial claim, perform the supported just-in-time
claim, or establish no-claim eligibility. Freeze `ticket_base` and its tree at the preceding accepted
HEAD; the first ticket uses `batch_base`.

### Dispatch and observe a bounded Worker

Use a fresh Worker per ticket and keep its implementation and repairs together. A later batch repair
uses a fresh Worker under this same protocol. Before dispatch, require supported identity,
observation, interruption and quiescence interfaces as well as dispatch capability.

Prove the exact worktree, unit base, HEAD/tree, complete local-state ownership and scope authority,
with earlier writers quiescent. At most one Worker writes. Independent read-only roles may run in
parallel while writers are paused. Supply the Worker with:

- Canonical ticket identity or batch-repair scope, complete requirements and source revisions,
  project rules, accepted dependency results and relevant research pointers.
- Exact worktree, batch/unit bases, earlier accepted commits, required targeted checks and scoped
  write/normal-hook commit authority.
- For repairs, original review evidence, consolidated findings, check failures and focused
  verification evidence.

The Worker owns only the current candidate. Accepted commits, tracker effects, finalization and
authorizing its own completion marker remain outside that scope. Require an attributable return:
Agent identity and raw status, candidate and final HEAD/tree, complete owned local state, checks and
their inputs, returned/interrupted phase, unresolved work and next action. Repair returns also give
finding dispositions and the exact delta.

Preserve failed attempts as failures even when files appear complete. Prove paused writes before
review and quiescence before acceptance. Neither elapsed time nor a missing response proves those
conditions; an uncertain Worker follows the original-attempt recovery route.

### Establish the complete intended result

The Worker implements the ticket and supplies the checks needed for acceptance and safe subsequent
work. Disclose genuinely noncritical coverage deferred to the combined barrier. Implementation,
testing and debugging continue before the review freeze.

For nonempty changes, create one normal-hook candidate whose sole parent is `ticket_base`. Its
message carries the configured tracker's discoverable ticket reference, with no `SmartKit-Ticket`
trailer. If existing behavior already fulfills the ticket, keep the base state for affirmative
requirement-based review. Omitting intended changes cannot make a no-change result.

Pause writes and independently verify the entire intended result, passing ticket checks and a clean
index/worktree under the project's predicate. Material untracked or ignored state needs known
ownership. Return omissions or failed checks to the same Worker before freezing review.

## Review once, then close findings on the resulting state

This contract governs both each ticket and the combined barrier. Freeze the comparison base
(`ticket_base` or `batch_base`), HEAD/tree, complete intended diff and all accepted requirements with
source identities/revisions. Establish paused writers and that no intended task change is omitted.

For a nonempty diff, invoke public `code-review` on these exact inputs with **all** accepted sources,
even if commit discovery finds only one. Standards and Spec must be independent of the Worker and
one another, and both axes are required. Supply applicable standards, the public advisory
smell-baseline treatment, check evidence and a deep-review brief covering:

- Every accepted requirement's implementation and verification, including missing, partial,
  incorrect or unsupported fulfillment and unintended scope.
- Relevant callers, callees and affected contracts beyond changed lines; edge, error and recovery
  paths, compatibility and regressions. Combined review also covers shared constraints, conflicting
  requirements and interactions across the complete batch.
- All useful evidence-backed findings with source locations, requirement or standard, behavior and
  supporting evidence, distinguishing severity, advisory smells, coverage gaps and uncertainty.

Preserve separate axes and findings. Retain full supporting reports where public summaries cannot
hold them.

### Review an empty result affirmatively

Public `code-review` rejects empty diffs. For an empty ticket or batch, use the same sole round with
two independent read-only Standards and Spec roles, supplying the frozen implementation/base, full
sources, standards, checks and deep-review brief above. Require fulfillment evidence for every
requirement and Standards coverage of the relevant implementation.

An empty ticket must already be fulfilled at `ticket_base`. A net-empty batch must fulfill every
selected requirement even if ticket changes cancel each other; preserve its ticket commits. Neither
emptiness nor a Worker assertion establishes fulfillment. Missing required roles or inputs stops
this route.

### Collect the original reports before repair

Obtain both complete reports, each identifying its role, immutable inputs, coverage, findings and
uncertainty. Retain originals or recovery locations and each axis's attributable `never-started`,
`in-flight`, `complete` or unresolved state. Recover incomplete or missing reports before repair;
missing coverage is not a clean verdict.

### Close findings until the Controller can accept

Judge every finding against accepted requirements and standards. Give a reasoned disposition to
each, including advisory and declined findings, and pass the consolidated repair set and check
failures to the Worker. Keep original reports and reviewed identities unchanged.

After each return, pause writes and repeat required checks on the resulting state. Record the exact
delta from review, verify every accepted finding's resolution and inspect repair impact on directly
affected behavior/contracts, including regressions, hooks and commit-sensitive checks. Explain how
original coverage and this focused verification support the exact final HEAD/tree and scope. This
is Controller acceptance of repairs, not a new passing reviewer verdict on unreviewed code.

Return incomplete fixes, related check failures, repair regressions and omissions found during
focused verification to the Worker. Continue correction and verification until acceptance. When no
repair is needed, use the unchanged reports and proceed. Amend only the current unpublished,
unaccepted candidate through normal hooks. Ticket repair that introduces changes from the base
creates its one candidate; repair that empties the candidate keeps it for that ticket's empty commit.

Acceptance requires complete original coverage, justified dispositions for every finding, no
unresolved blocker or required-check failure, attributable authorized repair deltas where present,
and Controller verification of the exact final state. A metadata-only equivalent needs an explicit
binding and refreshed dependent checks. A changed diff shape, Worker, commit, source fact, route,
resumption or finalizer return grants neither a new formal round nor broader scope.

Stop for a material decision/authority gap, unavailable prerequisite, unsafe or ambiguous state,
inadequate original coverage requiring new formal review, or no progress under applicable rules.
Preserve the original work and next owner through recovery. Later in-scope content changes use this
same focused closure; accepted commits remain fixed.

## Fix the accepted ticket boundary

After closure, the Controller authorizes one bounded normal-hook marking operation on the exact
candidate, retaining its canonical discoverable ticket reference and adding one completion trailer:

```text
SmartKit-Ticket: <canonical-id>
```

Amend the existing candidate's message. For a no-change ticket with no candidate, create one empty
commit with `ticket_base` as sole parent. If repair emptied an existing candidate, amend it into
that same ticket's empty commit; do not append a second ticket commit.

Inspect the resulting commit, tree and diff. Bind metadata-only equivalence to the original reports
and refresh commit-identity and hook-sensitive checks. A no-change ticket must equal the base tree
and retain affirmative fulfillment evidence. Hook-created content makes the ticket incomplete:
return the candidate to the Worker to remove the premature marker and close that delta under the
original review, then reauthorize marking. Neither a trailer nor a successful hook proves acceptance.

With writes paused, prove exactly one commit in the first-parent range from `ticket_base`, that sole
parent and exactly one canonical-ID trailer. Also prove full ticket scope, unchanged earlier accepted
commits, final tree/diff bound to original review and repair closure, passing required checks, clean
local state and Worker quiescence. Recheck worktree/target binding and frozen sources, blockers,
status and claim.

Return this fixed commit as `completed-in-batch`. It satisfies an in-batch dependency; the tracker
ticket stays open and its claim held. Continue automatically to the next dependency-ready ticket,
or to combined acceptance when all selected tickets are accepted. Corrections to accepted tickets
belong to the combined result.

## Accept the combined batch

With every ticket accepted and Workers quiescent, freeze HEAD/tree and run required whole-batch
checks. Apply the review-and-closure contract above to immutable `batch_base`, the complete combined
diff and all accepted requirements. Both independent reports are required even for one ticket or a
net-empty batch. Ticket evidence provides context; it cannot replace the combined barrier.

Collect findings and check failures before choosing repair. Ordinary check failures need not prevent
review of a meaningfully reviewable frozen state; missing prerequisites or incomplete evidence pause
the barrier. For repair, freeze `repair_base` at the accepted HEAD, keep the failed state, original
reports and all accepted ticket commits, and dispatch a fresh batch-repair Worker under the bounded
protocol with consolidated findings, checks and scope authority.

Content changes create at most one separate normal-hook repair candidate, with `repair_base` as its
sole parent and no ticket trailer. Continue focused closure by amending only that unpublished,
unaccepted candidate. If content needs no change, retain HEAD with evidence resolving the failure.

Accept only when closure and required whole-batch checks support the exact final HEAD/tree within
`batch_base`. Prove scope, unchanged accepted ticket history, clean local state, Worker quiescence,
source freshness and complete acceptance evidence. A repair candidate is the sole commit from
`repair_base`, with that sole parent and no ticket trailer; without one, prove HEAD unchanged.
Continue scoped repair for unresolved work and retain it on a stop.

Acceptance fixes the repair commit. A later in-scope correction may establish the sole batch-repair
candidate if none exists. Changing an accepted repair commit or adding another requires its history
owner and separate authority.

## Hand the accepted result to finalization

Revalidate every frozen ticket, source and dependency edge. Compare the worktree's current identity,
base, HEAD/tree and complete local state with final acceptance. Recheck the authoritative target and
account for material untracked/ignored residuals. Material content, source or target drift requires
owner reconciliation and affected focused closure before proceeding.

Read public `finish-worktree`'s selected route and required history, effect-recovery and results
contracts. Supply one handoff containing:

- Accepted scope and complete ticket/spec sources; exact source/target identities, immutable base,
  accepted HEAD/tree/diff and ticket/batch-repair commit boundaries.
- Original review inputs and full reports, every finding disposition, authorized repair deltas,
  check provenance and Controller closure bound to the accepted state.
- Selected outcome and history policy, exact effect and cleanup authority, publication/local
  residuals, preservation and lifecycle owners.

Preserve ticket history by default. Separately authorized consolidation retains original source
boundaries for recovery and tracker closure. Use the finalizer's implementation-owner acceptance
evidence route: original reports plus Controller closure, without another formal review. Its
operation-sensitive checks still apply. Returned content or source/target changes need owner
reconciliation and the same focused closure, with accepted history and original effect provenance
preserved. Other history operations require their owner's contract and authority.

For **Already Delivered**, including a net-empty batch, bind existing requirement-based acceptance
evidence to the exact authoritative target by proven equivalence with the covered state and refresh
target-dependent checks. The finalizer independently proves all accepted effects on that target.
Source emptiness alone is insufficient. Unproved equivalence or fulfillment pauses for externally
resolved evidence or the already selected supported outcome; it authorizes neither another formal
round nor manufactured changes, delivery or an empty PR.

Invoke the finalizer once for the accepted result. Retain its attributable invocation, raw response
and effects, recovering any prior or interrupted attempt before a replacement effect.

### Consume the result

Consume the public result unchanged: raw status, causal boundary, phase results, effects and strongest
proven classification. Only attributable `authoritative delivery`, including the finalizer's own
Already Delivered proof, permits tracker closure. That proof survives a stopped/failed status or
incomplete cleanup.

On authoritative delivery, re-observe tickets in dependency order, perform each documented completion
and any separately required claim release, and prove each after-state under the tracker-effect
contract. Consume an already-proven completed prefix and continue only its unresolved suffix. The
first failed or ambiguous effect stops closure and leaves later tickets untouched. Preserve delivery
and accepted source/recovery boundaries. Give closure proof to the finalizer's named lifecycle owner
for authorized retention, release or cleanup without repeating delivery.

Every other classification keeps tickets open and claims held while its named continuation proceeds,
unless separate tracker authority resolves their disposition. Retain attributable PR, retained
worktree, transfer, authorized-discard and partial-result evidence. Cancellation needing a claim
disposition belongs to the tracker owner under separate exact authority. An unavailable or ambiguous
classification returns to the finalizer owner; it proves neither delivery nor permission to retry.

Record consumption in the retained handoff and resume only the named unfinished action. Keep proven
effects, source history and recovery items until their owners establish their dispositions. Report
accepted tickets, exclusions, raw finalizer outcome, tracker and lifecycle state, retained locations
and the next owner/action for anything unfinished.
