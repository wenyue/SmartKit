# Worktree Lifecycle

Worktree Lifecycle defines how SmartKit isolates implementation work, preserves task history,
accumulates ticket batches, and proves delivery and completion.

## Language

**Ticket Batch（工单批次）**:
A frozen dependency-ordered set of implementation tickets whose per-ticket Task Commits are
accumulated, reviewed, and delivered as one scope.
_Avoid_: Ticket queue, combined task, batch commit

**Batch Worktree（批次工作树）**:
A named isolated linked worktree whose branch accumulates the ordered Task Commits for one Ticket
Batch while the delivery target remains unchanged.
_Avoid_: Ticket worktree, base checkout, shared worktree

**Task Worktree（任务工作树）**:
A named, isolated linked worktree whose branch and local state belong exclusively to one accepted
implementation task.
_Avoid_: Worktree, base checkout, shared worktree

**Checkpoint Commit（检查点提交）**:
A provisional commit that preserves a recoverable implementation state within a Task Worktree and
is not part of the promised final history.
_Avoid_: Final commit, Task Commit

**Task Commit（任务提交）**:
A single delivery-history commit that consolidates one accepted task's Checkpoint Commits. In a
Ticket Batch it remains staged until the whole batch passes review and verification.
_Avoid_: Checkpoint Commit, squash commit

**Batch Review Commit（批次审查提交）**:
The optional final Task Commit that consolidates fixes produced by the whole-batch review without
rewriting the preceding per-ticket Task Commits.
_Avoid_: Ticket Task Commit, amended ticket commit, review checkpoint

**Staged Ticket（已编入批次的工单）**:
A Ticket whose Task Commit has been appended to its Batch Worktree but whose batch has not yet been
delivered to the final target. It remains claimed and is not completed.
_Avoid_: Delivered Ticket, completed Ticket, merged Ticket

**Batch Delivery（批次交付）**:
The verified fast-forward of a reviewed Ticket Batch's ordered Task Commit range and optional Batch
Review Commit to its unchanged final target.
_Avoid_: Ticket staging, tracker completion, batch merge

**Ticket Completion（工单完成）**:
The tracker transition performed by the Ticket Batch controller after Batch Delivery is proven.
_Avoid_: Ticket staging, Task Commit creation, Git cleanup

**Finalization Contract（收尾契约）**:
The closed, mode-discriminated interface by which a caller supplies Git identities, evidence,
history, target, recovery, cleanup, and authorization policy to `finish-worktree`.
_Avoid_: Tracker contract, generic parameter bag, Ticket Batch orchestration

**Already Delivered（已交付）**:
A terminal state in which the selected target is proven to contain the complete accepted task
result, so no Task Commit or delivery mutation is needed.
_Avoid_: Empty Task Commit, no diff
