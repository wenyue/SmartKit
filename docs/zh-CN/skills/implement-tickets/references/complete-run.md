# 完成运行

Delivery 前，只有每个 selected ticket 在 Batch Worktree first-parent history 中都有一个已证明 Ticket
Commit 后才能进入。Delivery 后恢复只有在主 Skill 已重建相同有序 boundaries 并证明 Batch Delivery
后，才从第 5 步进入。

1. 使用 immutable batch base 作为 fixed point，以完整 Spec 和 selected tickets 作为 acceptance
   sources，运行 full verification 并调用 `code-review`。
2. 在同一 Batch Worktree 中以 Checkpoint Commits 处理 blocking findings。每次 correction 后，重新
   运行 full verification 和相同 whole-batch review。只有两个 gates 对同一最终 `HEAD` 和 tree 都通过
   时才继续；unresolved finding 或 failed gate 进入 **停止和恢复**。
3. 在 controller Agent context 中调用 `finish-worktree` 一次，并提供从当前 evidence 推导出的完整
   generic Finalization Contract。不提供 mode。把选定的 `preserve-commits` 或
   `consolidate-checkpoints` policy 绑定到从 immutable base 到 reviewed `HEAD` 的完整 batch-owned
   range，并选择本地已授权 outcome，不添加 tracker data。对于 consolidation，保留指向 reviewed
   Batch Worktree head 的 workflow-owned recovery ref，直到每个 Ticket Completion 和 claim removal
   都得到证明。
4. 独立证明准确 selected outcome 和 target verification。对于 `consolidate-checkpoints`，要求一个
   Batch Commit，其唯一 parent 是 immutable base，且 tree 等于 reviewed Batch Worktree。对于
   `preserve-commits`，要求 delivery head 和完整 owned range 保持不变。任何 mismatch 都进入
   **停止和恢复**。
5. 只有 Batch Delivery 得到证明后，才按 dependency order 完成 tracker tickets。一个 transition
   失败时，保留后续 claims 并进入 **停止和恢复**，不 rollback delivery，也不改变后续 ticket。
6. 每个 Ticket Completion 和 claim removal 成功后，通过 expected-old-value check 删除保留的
   workflow-owned recovery ref，并执行剩余已授权 Git cleanup。mismatch 会保留 ref 并使 cleanup 失败。

只有 Batch Delivery、每个 Ticket Completion、claim removal 和已授权 Git cleanup 都得到证明后才
complete。成功的 `return-for-review`、`keep-for-later` 或 `create-pull-request` outcome 返回该准确
handoff，不执行 Ticket Completion。报告 selected order、immutable base、target 和 batch branches、
workers、Ticket Commits、whole-batch review 和 verification、final history policy、保留及删除的
recovery refs、tracker transitions、cleanup 和 exclusions。
