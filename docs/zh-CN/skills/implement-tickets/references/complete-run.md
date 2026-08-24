# 完成运行

Delivery 前，只有每个选定的工单在批次工作树第一父提交历史中都有一个已证明 Ticket
Commit 后才能进入。Delivery 后恢复只有在主 Skill 已重建相同有序边界并证明批次交付
后，才从第 5 步进入。

1. 使用不可变的批次基点作为 fixed 节点，以完整 Spec 和选定的工单作为验收
   源，运行完整验证并调用 `code-review`。
2. 在同一批次工作树中以 Checkpoint 提交处理 blocking 问题。每次 correction 后，重新
   运行完整验证和相同 whole-batch 审查。只有两个 gates 对同一最终 `HEAD` 和树都通过
   时才继续；未解决的问题或失败 gate 进入**停止和恢复**。
3. 在控制器智能体上下文中调用 `finish-worktree` 一次，并提供从当前证据推导出的完整
   generic 收尾契约。不提供模式。把选定的 `preserve-commits` 或
   `consolidate-checkpoints` 政策绑定到从不可变的基点到已审查的 `HEAD` 的完整 batch-owned
   范围，并选择本地已授权结果，不添加跟踪器 data。对于合并，保留指向已审查的
   批次工作树提交头的工作流-owned 恢复引用，直到每个工单完成和归属声明 removal
   都得到证明。
4. 独立证明准确选定的结果和目标验证。对于 `consolidate-checkpoints`，要求一个
   批次提交，其唯一 parent 是不可变的基点，且树等于已审查的批次工作树。对于
   `preserve-commits`，要求交付提交头和完整自有的范围保持不变。任何不匹配都进入
   **停止和恢复**。
5. 只有批次交付得到证明后，才按 dependency 顺序完成跟踪器工单。一个 transition
   失败时，保留后续归属声明并进入**停止和恢复**，不 rollback 交付，也不改变后续工单。
6. 每个工单完成和归属声明 removal 成功后，通过 expected-old-value check 删除保留的
   工作流-owned 恢复引用，并执行剩余已授权 Git 清理。不匹配会保留引用并使清理失败。

只有批次交付、每个工单完成、归属声明 removal 和已授权 Git 清理都得到证明后才
完成。成功的 `return-for-review`、`keep-for-later` 或 `create-pull-request` 结果返回该准确
交接，不执行工单完成。报告选定的顺序、不可变的基点、目标和批次分支、
执行智能体、Ticket 提交、whole-batch 审查和验证、final 历史政策、保留及删除的
恢复引用、跟踪器 transitions、清理和 exclusions。
