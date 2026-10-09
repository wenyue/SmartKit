# Worktree Lifecycle

Worktree Lifecycle defines how SmartKit isolates implementation work, preserves recoverable
history, and proves delivery and completion.

## Language

**Checkpoint Commit（检查点提交）** :
A provisional commit that preserves a recoverable implementation state within an isolated
worktree and is not necessarily part of the promised final history.
_Avoid_: Final commit, Delivery Commit

**Delivery Commit（交付提交）** :
The accepted commit at the tip of the history selected for publication or integration.
It can retain the task’s existing history or be the result of authorized consolidation.
_Avoid_: Checkpoint Commit

**Already Delivered（已交付）** :
A state in which the selected target is proven to contain the complete accepted scope result,
so no further delivery operation is needed.
_Avoid_: Empty Delivery Commit, no diff
