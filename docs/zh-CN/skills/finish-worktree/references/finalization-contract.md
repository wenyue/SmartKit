# 收尾契约

只接受一个闭合 contract。它提供：

- `source` worktree、branch、准确 base、`head` 和 `tree`、`creation_owner` 及 `scope_owner`；
- `target` checkout、branch、`expected_head` 和 `target_policy`；
- `evidence` fixed point、acceptance sources、review kind 和 result、reviewed head 和 tree、
  verification commands 和 results 以及 findings；
- 等于 `consolidate-checkpoints` 或 `preserve-commits` 的 `history_policy`，以及其完整 owned range；
- recovery refs、当前和后续 owners；
- authorized cleanup 和 retained state；
- 一个等于 `merge-locally`、`create-pull-request`、`keep-for-later` 或 `return-for-review` 的
  `authorized_outcome`。

拒绝 unknown policies 或 outcomes、missing values、tracker data 和 implicit remote authority。

## 证明当前状态

重新推导每个具名 Git identity、clean owned state、ancestry、range、publication、evidence、recovery
fact 和 owner。snapshot 每个受影响 checkout 的 branch、`HEAD`、index tree、staged、unstaged 和
untracked 状态。每次 mutation 前立即复核其依赖 facts。存在 stale、ambiguous、published 或 unrelated
state 时停止。

只有准确 source 和 target、完整 owned history、current evidence、authorized recovery 和 cleanup，
以及 preserved unrelated state 都得到证明时，contract 才通过。
