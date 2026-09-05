# Worktree Lifecycle

Worktree Lifecycle defines how SmartKit isolates implementation work, preserves recoverable
history, processes ticket batches, and proves delivery and completion.

## Language

**Ticket Batch（工单批次）**:
A dependency-ordered set of implementation tickets processed sequentially, reviewed, and finalized
as one implementation scope.
_Avoid_: Ticket queue, combined task

**Batch Worktree（批次工作树）**:
A named isolated linked worktree in which every ticket of one Ticket Batch is implemented
sequentially while the delivery target remains unchanged.
_Avoid_: Ticket Worktree, base checkout, shared worktree

**Checkpoint Commit（检查点提交）**:
A provisional commit that preserves a recoverable implementation state within an isolated
worktree and is not necessarily part of the promised final history.
_Avoid_: Final commit, Delivery Commit

**Delivery Commit（交付提交）**:
A single delivery-history commit that consolidates the complete reviewed result of one isolated
implementation scope.
_Avoid_: Checkpoint Commit, Ticket Commit

**Ticket Review（工单审查）**:
A review of one ticket's fulfillment of its accepted requirements and applicable project standards.
_Avoid_: Implementation self-check, Batch Review

**Batch Review（批次审查）**:
A review of the combined ticket results, including their interactions, shared constraints, and
fulfillment of the overall accepted requirements.
_Avoid_: Repeated Ticket Review, Batch Delivery

**Ticket Commit（工单提交）**:
The commit that marks one completed ticket's boundary in a Batch Worktree with exactly one
`SmartKit-Ticket` trailer. It may follow that ticket's Checkpoint Commits and may be consolidated
during finalization.
_Avoid_: Delivery Commit, completion record, tracker transition

**Batch Commit（批次提交）**:
A Delivery Commit whose implementation scope is one complete Ticket Batch.
_Avoid_: Ticket Commit, Checkpoint Commit

**Batch Delivery（批次交付）**:
The verified advancement of the unchanged target branch to a reviewed Ticket Batch result, either
through its preserved commits or one Batch Commit.
_Avoid_: Working-tree review handoff, tracker completion, ticket boundary

**Ticket Completion（工单完成）**:
The tracker transition performed by the Ticket Batch controller after Batch Delivery is proven.
_Avoid_: Ticket staging, Task Commit creation, Git cleanup

**Finalization Contract（收尾契约）**:
The closed interface by which a caller supplies Git identities, evidence, history policy, target,
recovery, cleanup, and one authorized outcome to `finish-worktree`.
_Avoid_: Tracker contract, generic parameter bag, Ticket Batch orchestration

**Already Delivered（已交付）**:
A terminal state in which the selected target is proven to contain the complete accepted scope
result, so no Delivery Commit or delivery mutation is needed.
_Avoid_: Empty Delivery Commit, no diff
