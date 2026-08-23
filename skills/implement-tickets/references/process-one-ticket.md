# Process One Ticket

Enter with the selected dependency-ready ticket, the exact current Batch Worktree, and the
controller's current ticket graph. This path has one `completed-in-batch` exit; every other result
enters **Stop and Recovery** in the main Skill.

## Claim and Hand Off

1. Re-read the ticket and its blockers immediately before claiming. Stop on a material status,
   requirement, or edge change.
2. Use the configured tracker's documented compare-and-set Ticket Batch claim with Ticket Commit
   proof. Record the prior state and claim; stop when no safe claim operation is documented.
3. Record the Batch Worktree path, branch, exact `HEAD`, tree, immutable base, clean or owned recovery
   state, and the selected ticket as its only current scope. Stop if another worker still owns the
   worktree or an earlier ticket has unresolved state.

## Dispatch One Worker

Start one fresh write-capable worker Agent and give it one complete handoff:

- `ticket`: canonical identifier, complete contract, acceptance sources, and blocker proof;
- `batch`: worktree, branch, exact `head` and `tree`, immutable base, and controller identity;
- `history`: existing ticket boundaries, current ticket base, the exact
  `SmartKit-Ticket: <canonical-id>` completion trailer, and worker commit authority;
- `verification`: focused and repository-required commands;
- `tracker_boundary`: no worker claim, release, completion, or other tracker transition.

The worker performs this complete lifecycle in its existing Agent context:

1. Recheck the supplied Batch Worktree, ticket base, prior ticket boundaries, ownership, and local
   state. Work only in that Batch Worktree and only on this ticket.
2. Establish the current mechanism and seams, implement only the ticket, use `tdd` when behavior has
   a testable seam, and create any useful recoverable Checkpoint Commits through the normal commit
   workflow.
3. Run focused verification during implementation and every repository-required check at the end.
4. Self-review the complete ticket diff against its acceptance criteria and correct every observed
   mismatch. The worker does not invoke formal `code-review`.
5. End with a clean worktree and one final hook-validated Ticket Commit containing exactly the
   supplied completion trailer. The ticket may have preceding Checkpoint Commits. When no content
   remains to commit, create a hook-validated empty Ticket Commit rather than rewriting another
   ticket's history.
6. Return the exact Ticket Commit, ticket and worker identities, current Batch Worktree head and
   tree, verification, and self-review evidence.

At any phase before the Ticket Commit is proven, a non-complete result or missing decision returns one
structured Worker Recovery Handoff containing:

- `status` (`stopped` or `failed`), ticket and worker identities, `completed_phase`, and
  `failed_phase`;
- Batch Worktree path, branch, immutable base, ticket base, `HEAD`, tree, and owned local-state facts;
- the exact current-ticket Checkpoint Commit range, trees, publication facts, and uncommitted state;
- each verification command, result, and associated `HEAD` and tree, plus self-review evidence and
  unresolved findings;
- every retained branch, commit, recovery ref, and other useful recovery state;
- the exact blocker, mismatch, error, or missing decision; and
- `next_owner` and the exact next action.

Preserve all reported Git and recovery state. The controller neither replaces the worker nor
touches another ticket before entering **Stop and Recovery**.

## Verify the Ticket Boundary

1. Require a complete worker result and independently verify the worker and ticket mapping, exact
   trailer, commit ancestry, evidence, clean Batch Worktree, and that every commit after the supplied
   ticket base belongs to this ticket. Any mismatch enters **Stop and Recovery**.
2. Keep the ticket claimed. The proven Ticket Commit may unlock dependants inside this run but is
   neither Batch Delivery nor Ticket Completion.
3. Re-read the selected contracts. A material contract change enters **Stop and Recovery**;
   otherwise return the `completed-in-batch` exit to the main Skill.
