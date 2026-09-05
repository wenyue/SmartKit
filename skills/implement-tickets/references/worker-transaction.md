# Worker Boundary

The Controller owns a ticket or batch-repair scope and its acceptance. The host runtime owns Agent
identity, dispatch, interruption, observation and quiescence. Establish that its current supported
interfaces can provide those facts; an unavailable or ambiguous runtime stops before dispatch.

Use a fresh implementation Worker for each new ticket and a fresh Worker for a new batch repair.
Keep ordinary repair of the same incomplete candidate with its Worker. Immediately before dispatch,
prove the exact worktree and unit base, current HEAD/tree and local-state ownership, scoped effect
authority, and quiescence of every prior writer. At most one Worker may write. Independent review
roles may run in parallel, read-only, while implementation is paused; they are independent from the
Worker and from one another. Reuse the established environment, not a prior ticket's Worker scope.

The ticket or repair procedure supplies the Worker's inputs. Bound writes and normal-hook candidate
commits/amendments to that current unit. It cannot amend an
accepted commit, act on the tracker, finalize the batch, or authorize its own completion marker.
Require its return to identify the Agent and raw status, current candidate, final HEAD/tree,
complete owned local state, checks and their inputs, unresolved findings, and next action.

Preserve raw results. A failure remains a failed attempt even if current files look complete;
observe the effects, resolve the cause, and obtain a supported continuation or recovered result
before acceptance. Prove writes paused before review and quiescence before accepting its result.
After a missing response or interruption, read [Pause and resume](resume.md): elapsed time and
plausible Git contents do not prove the original Worker stopped.

## Qualify dispatch before a claim when needed

Use this read-only gate only when the tracker's release, reassignment or expiry semantics mean a
later dispatch failure could strand the proposed claim. Establish runtime availability, observation
and control routes, scoped authority, and the absence of a possibly live competing attempt. If the
worktree exists, verify its exclusive attribution; before creation, retain the requirement for
readiness before dispatch. Reuse shared facts while current and add only ticket-specific constraints
that affect feasibility.

Qualification dispatches no Worker, reserves no capacity and creates no persistent state. An
unresolved material dispatch risk stops the claim with that fact and its next owner.
