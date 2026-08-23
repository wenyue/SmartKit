---
name: implement-tickets
description: Implement the remaining agent-ready tickets sequentially in one isolated worktree, mark recoverable ticket boundaries in Git history, then review and finalize the batch once.
---

# Implement Tickets

This Procedure-led Skill runs one Ticket Batch as a dependency-ordered pipeline in one Batch
Worktree. The controller owns ticket selection, claims, worker handoffs, batch evidence, finalization,
and tracker completion. Each fresh worker owns one ticket's changes in that shared sequential
history; only one worker may use the Batch Worktree at a time.

## Establish the Run

1. Read the configured issue-tracker instructions, referenced Spec or parent source, and every
   ticket in the requested effort. Infer an omitted effort only when context identifies exactly one
   ticket set; otherwise ask for it.
2. Record all identifiers, published order, statuses, claims, blocking edges, and acceptance
   criteria in the controller context. Identify the named local target checkout and branch. Require
   accepted local-delivery authority;
   ask once before tracker or Git mutation if the target or outcome remains ambiguous.

Select exactly one entry path:

- **New Batch**: Include only agent-ready work; exclude completed, rejected, human-owned,
  information-blocked, and claimed tickets. Require every blocker to resolve to a selected ticket
  or completed external dependency, require an acyclic graph, and use published order to break
  readiness ties. Invoke `create-worktree` from the exact target `HEAD` to create one Batch Worktree
  for the complete selected scope; record that commit and tree as the immutable batch base.
- **Interrupted Before Delivery**: Identify the current or explicitly supplied Batch Worktree and
  derive its immutable base as the unique merge base with the target; require the target still to
  equal that commit. Include tickets whose current tracker claims prove ownership by this exact
  Batch plus otherwise eligible tickets from the requested effort; exclude claims owned elsewhere.
  Rebuild and validate the graph, then replay it at each completed boundary in the worktree's
  first-parent history. Require exactly one `SmartKit-Ticket: <canonical-id>` trailer naming the
  earliest published dependency-ready ticket; otherwise stop. Treat the unmarked commit tail and
  local changes as the current ticket's recovery state.
- **Interrupted After Delivery**: Require current tracker evidence of this Batch's unresolved claims
  or partial Ticket Completion and prove the target contains the delivered result. For preserved
  history, reconstruct ticket boundaries from the delivered first-parent range. For consolidated
  history, require the unique retained workflow recovery ref whose reviewed tree equals the Batch
  Commit tree, and reconstruct the boundaries from that ref's first-parent range. Rebuild and replay
  the graph against those boundaries, then enter `complete-run.md` at Ticket Completion without
  creating a worktree, dispatching a worker, repeating review, or invoking `finish-worktree`.

Every entry path stops when the worktree or delivery evidence, immutable base, selected scope,
claim ownership, graph, history, or local-state ownership is ambiguous.

Before delivery, the run is ready only when the selected graph, unchanged target, Batch Worktree,
authorized local outcome, and first dependency-ready ticket are established. If unfinished tickets
remain but none is ready, report their unresolved edges and enter **Stop and Recovery** without a
new claim.

## Execute the Batch

A selected blocker is satisfied only when its Ticket Commit is present in the Batch Worktree's
first-parent history or the tracker proves it was completed before this run.

1. While a selected ticket remains unfinished, read and execute
   [`references/process-one-ticket.md`](references/process-one-ticket.md) completely. After its
   `completed-in-batch` exit, select the earliest published ticket whose blockers are satisfied and
   repeat.
2. After every selected ticket has a proven Ticket Commit, read and execute
   [`references/complete-run.md`](references/complete-run.md) completely.
3. On any non-complete result, missing decision, or failed invariant, read and execute
   [`references/stop-and-recovery.md`](references/stop-and-recovery.md) completely. This exit takes
   precedence over the next ticket and completion.

Complete only through the completion criterion in `complete-run.md`.
