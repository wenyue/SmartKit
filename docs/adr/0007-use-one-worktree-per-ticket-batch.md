---
status: accepted
---

# Use one worktree per sequential ticket batch

SmartKit implements a dependency-ordered Ticket Batch sequentially in one Batch Worktree. Ticket
boundaries are machine-readable commits in that branch, so Git history and current tracker state
provide the recovery evidence without a second Task Worktree per ticket or a separate Batch
journal. The batch receives one whole-scope review and uses the same generic `finish-worktree`
contract as any other isolated worktree; finalization may preserve its commits, consolidate them
into one Batch Commit, or return the reviewed result to the target working tree.

This replaces the Task-Worktree-per-ticket design in ADR-0005 and the Task-only checkpoint authority
in ADR-0003. It accepts that one interrupted ticket leaves recoverable state in the Batch Worktree;
strict sequential execution prevents that state from contaminating another ticket.
