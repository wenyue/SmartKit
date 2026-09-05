---
name: finish-worktree
description: Finish an isolated linked Git worktree by keeping it for later, publishing a pull request, merging locally, transferring its changes back to a checkout, or explicitly discarding it.
---

# Finish Worktree

Achieve the selected outcome for one isolated worktree and leave a reliable account of what remains.
The implementation workflow owns changes to the accepted result, verification, and formal review;
this Skill owns the selected handoff or delivery, optional history preparation, and its recovery and
cleanup. Tracker closure stays with its existing owner.

## Principles

- **Outcome first.** Require the evidence and authority that the selected effect needs. Keeping
  unfinished work and transferring changes are useful outcomes in their own right.
- **Preserve ownership.** Distinguish task changes from the user's state. Carry only accepted task
  changes across a boundary and retain anything whose ownership is uncertain.
- **Reuse valid evidence.** Bind evidence to the state and effect it proves. Refresh it when those
  dependencies change, rather than replaying unrelated proofs.
- **Keep proven results.** A later failure cannot erase a proven history result, publication, handoff,
  or delivery. Recover the original incomplete effect from observation.

## Establish the job

Identify the source's physical path, linked-worktree registration, common repository, branch and
current `HEAD`; resolve any substitution or ambiguous identity before proceeding. Establish the
accepted scope, ownership of local state, selected outcome, and unresolved effects from prior
attempts. A prior `create-worktree` result can locate the job; current Git evidence establishes it.

Derive authority from the accepted request and applicable project policy. A request to create a pull
request authorizes its necessary publication; a request to transfer changes authorizes the bounded
transfer and its protective preparation. Reuse authority already granted. Ask only for a missing
material choice or effect, such as an unidentified destination or losses outside an explicit discard
request. Retention is the safe disposition for unowned state. Independently applicable project or
caller policies can require stronger verification or review than a route here.

Select one outcome and read its complete reference. Resolve an ambiguous outcome before mutation;
never silently replace integration with transfer or cleanup with discard.

| Outcome | Contract |
| --- | --- |
| `keep-for-later` | [Retain the work as it stands](references/keep-for-later.md), including unfinished and dirty work. |
| `create-pull-request` | [Publish an exact reviewed commit and establish its PR](references/create-pull-request.md). |
| `merge-locally` | [Fast-forward the authorized local target](references/merge-local.md). |
| `return-for-review` | [Transfer task changes back to a checkout](references/return-for-review.md), preserving its HEAD and complete index. |
| explicit discard | [Remove only authorized observed losses](references/discard.md). |

Preserve commits by default. Read [history preparation](references/history.md) for publication or
integration, or when consolidation is expressly requested by the user or required by project
policy. Keeping and transferring normally have `history_result: inapplicable`; they need no history
rewrite or blanket formal-review gate. Explicit consolidation uses the history contract even when
paired with retention or transfer.

## Execute and close

The selected route owns its readiness and success proof. Native Git and the repository's host
interface establish deterministic facts and perform bounded operations; the Agent judges intent,
ownership, semantic compatibility, and authority. Before the first effect, read only
[Operation receipt](references/recovery.md#operation-receipt) and
[Resume the incomplete effect](references/recovery.md#resume-the-incomplete-effect), then create the
small external receipt. Load that reference's mechanism sections only when the selected route needs
them.
For a read-only retention outcome, the returned record is sufficient. Resume any unresolved prior
attempt through that reference before starting another effect on the same state.

Capture the selected write set and dependencies once. Use shared proofs at batch boundaries and
related path guards within a bounded batch. Immediately before an effect, refresh mutable facts it
depends on: identities, relevant refs, index, affected files, host state, and authority over
newly observed losses. Afterward observe what that effect could change. Immutable commit/tree and
review evidence remains usable while its dependencies match; a content change returns verification
and review to the implementation owner. Observed drift stops the dependent effect and preserves
completed phases.

Cleanup follows proven outcome-specific dispositions. Retain dirty sources; finalization cleanup
never authorizes their loss. Remove only exact owned items whose route-specific retention conditions
are satisfied, whose lifecycle and retention owners have released them, and whose removal is already
authorized. Inventory ignored content before a removal
that could reach it. The host removes host-created worktrees. Delete branches only when absent from
all worktrees, and delete owned branch/recovery refs through expected-old-OID updates. Treat each
removal as its own recoverable effect. Retention or delegation with an owner and release condition
is completed cleanup, not an error.

Return the selected route, concise evidence, retained locations and next action using the unchanged
[public results contract](references/results.md). Read that reference before returning, including on
a stop or failure. Report required checks that did not pass without claiming their outcome proven.
