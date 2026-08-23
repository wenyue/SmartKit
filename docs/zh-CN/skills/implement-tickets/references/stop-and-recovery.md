# 停止和恢复

主 Skill 路由任何非 complete 结果时进入。

1. 保留并报告 Batch Worktree、target、claims、ticket boundaries、未标记 commit tail、本地改动、
   branches 和 recovery state，以及准确 failed operation 和 next owner。
2. Batch Delivery 前，只使用已配置 tracker 记录的 compare-and-set release，并按 reverse dependency
   order 执行。缺少 safe operation 或 compare-and-set 失败时，保留剩余 claims 并停止 release。
3. Batch Delivery 后，保留 unresolved claims，并 handoff 已配置 completion operation。保留 delivered
   commits，以及重建经 consolidation 收束的 ticket boundaries 所需的任何 recovery ref。
4. 没有单独授权时，不执行 force operation、rebase、rollback、discard 或未配置 tracker action。

此路径以 `stopped` 或 `failed` 退出；retained state 和 handoff 仍为 recovery boundary。
