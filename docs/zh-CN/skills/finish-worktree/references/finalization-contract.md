# 收尾契约

只接受一个闭合契约。它提供：

- `source` 工作树、分支、准确基点、`head` 和 `tree`、`creation_owner` 及 `scope_owner`；
- `target` 检出目录、分支、`expected_head` 和 `target_policy`；
- `evidence` fixed 节点、验收源、审查 kind 和结果、已审查的提交头和树、
  验证命令和结果以及问题；
- 等于 `consolidate-checkpoints` 或 `preserve-commits` 的 `history_policy`，以及其完整自有的范围；
- 恢复引用、当前和后续归属；
- 已授权的清理和保留的状态；
- 一个等于 `merge-locally`、`create-pull-request`、`keep-for-later` 或 `return-for-review` 的
  `authorized_outcome`。

拒绝 unknown 政策或结果、missing values、跟踪器 data 和 implicit 远程 authority。

## 证明当前状态

重新推导每个具名 Git 标识、clean 自有的状态、ancestry、范围、发布状态、证据、恢复
fact 和归属。快照每个受影响检出目录的分支、`HEAD`、索引树、已暂存、未暂存和
未跟踪状态。每次修改前立即复核其依赖 facts。存在 stale、ambiguous、已发布或 unrelated
状态时停止。

只有准确源和目标、完整自有的历史、当前证据、已授权的恢复和清理，
以及保留的 unrelated 状态都得到证明时，契约才通过。
