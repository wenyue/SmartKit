---
name: implement-tickets
description: Implement or resume a dependency-ordered batch of eligible tracker tickets in one isolated worktree, or prove that the bounded scope has no eligible work; independently accept each ticket, then review and finalize the batch.
---

# Implement Tickets

Complete one frozen ticket selection in dependency order, with one accepted commit per ticket and
one final whole-batch review and finalization. A proven empty selection returns `nothing-to-do`
without creating a worktree or making another effect.

The active Agent is the **Controller**. It owns selection, serial implementation, independent
acceptance, and the final evidence handoff. The configured project tracker owns eligibility,
dependencies, claims, and tracker completion. Public `create-worktree` owns workspace readiness and
its environment dependency; public `code-review` owns Standards and Spec review; public
`finish-worktree` owns history preparation, the selected outcome, recovery of its effects, and
cleanup. Read their current public contracts before using them. Resolve the tracker through the
target project's `docs/agents/issue-tracker.md` and its configured triage owner; resolve required
verification through applicable project rules and documented verification interfaces. Missing,
unavailable, failed, or ambiguous required capabilities stop at their owner, with attributable
state retained. A present dependency that failed is never treated as absent.

Use only authority supplied by the accepted request, applicable policy, and these owner contracts.
After consuming and rechecking worktree readiness, scope-only local candidate commits and bounded
amendments use the workflow's commit authority and normal repository hooks. They grant no tracker,
remote, installation, finalizer, or cleanup effect. Preserve the canonical checkout and unrelated
work. Preserve accepted commits by default; consolidation requires a separate explicit selection.

## 1. Establish the batch

Identify the bounded input scope and target. Before fresh selection, observe relevant repository
and registered-worktree state, branch history, retained selection and dependency handoffs, and live
Worker or finalizer identities. Read [Tracker boundary](references/tracker.md) before any tracker
observation. If these observations identify an existing or possible batch attempt, use
[Pause and resume](references/resume.md) to recover its original phase and frozen scope. A prior
finalizer or closure handoff takes precedence over current ticket eligibility.

Only evidence supporting a new batch permits fresh selection. Establish its accepted committed
`batch_base`, requested finalizer outcome, history policy and exact effect authorities. Use
`tracker.md` to resolve same-scope dependencies and freeze membership, order, complete accepted
requirements and their source revisions, exclusions, and the owner-supported claim plan. Report
selected tickets and exclusions; selection does not promise completion of the user's broader input.
A proven empty new selection ends here without effects.

## 2. Establish one environment

If a selected ticket depends on uncommitted source-checkout work, pause before batch implementation
and resolve a separately authorized committed baseline through that work's owner. Preserve the
source checkout; do not automatically commit, discard, reimplement or absorb its work as ticket
changes. Reconcile the accepted base before continuing.

Satisfy every required initial claim before other batch writes. Request **clean** creation at the
frozen `batch_base` through public `create-worktree`, with the accepted scope, ownership, placement,
and setup-effect authority. This explicit clean choice preserves a dirty source without importing
its changes. Placement decisions, source preservation, and environment preparation remain with
that owner, including its target `worktree-environment-setup` dependency.

Consume only its attributable current `ready` result. Recheck the physical path, Git common
identity, linked-worktree registration, branch, base, HEAD/tree, index, and expected local state
before the first worker or deferred claim effect. Bind that exact worktree to this batch. Reuse its
environment for all Workers and Reviewers; refresh readiness on material drift or interrupted
control as described in `resume.md`. Required project checks still run when their inputs change.

## 3. Implement and accept each ticket

For each dependency-ready ticket, follow [Process one ticket](references/process-one-ticket.md).
That procedure owns dispatch, the nonempty candidate/review loop or independent no-change branch,
and Controller acceptance. Give it the frozen ticket and preceding accepted HEAD; require
`completed-in-batch` with exactly one independently accepted first-parent commit before advancing.
Earlier accepted commits stay fixed. Tickets remain open and claims stay held.

## 4. Verify and review the batch

After all selected tickets are accepted and Workers are quiescent, freeze the final HEAD/tree and
run required whole-batch verification. Choose the review route from the final diff against immutable
`batch_base` before invoking review:

- For a nonempty diff, invoke public `code-review` with every accepted ticket/spec source and its
  provenance. Both axes examine the complete combined result, emphasizing interactions, shared
  constraints, regressions and overall fulfillment. Individual reports provide context; they do not
  replace examination of the final state or narrow its coverage to interactions alone.
- For an empty diff, including changed tickets whose effects cancel, use
  [independent empty-diff acceptance](references/review.md#independently-accept-an-empty-difference)
  over the final implementation and all accepted requirements.

Whole-batch findings requiring repair enter [batch repair](references/review.md#repair-the-whole-batch).
Preserve ticket boundaries through both routes. Accept the batch only when required checks and both
independent judgments pass on its exact final state with complete accepted scope coverage.

## 5. Finalize and report

Read [Finalize the accepted batch](references/complete-run.md). Revalidate frozen source facts and
current worktree/target evidence, then give public `finish-worktree` the accepted scope, exact
base/HEAD/tree, ticket boundaries, complete verification/review evidence, chosen outcome and
history policy, and exact effect authority. It consumes that evidence without a duplicate formal
review and performs its own operation-sensitive verification.

Consume its strongest proven classification with its raw status. Only its `authoritative delivery`
classification permits tracker closure. PRs, retained worktrees, review transfers, and empty diffs
do not establish delivery. Report accepted tickets, exclusions, finalizer outcome, tracker and
lifecycle dispositions, retained locations, and the next owner/action for any unfinished boundary.

At a material blocker, use `resume.md` to pause the whole batch and preserve partial work. Supported
ordinary repairs continue while they make progress; an unavailable capability or no-progress
failure stops with its exact owner. Never skip a ticket, change the queue, revert work, or repeat a
possibly completed external effect to get past a blocker.
