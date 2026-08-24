# 停止和恢复

主 Skill 路由任何非完成结果时进入。

1. 保留并报告批次工作树、目标、归属声明、工单边界、未标记提交 tail、本地改动、
   分支和恢复状态，以及准确失败操作和下一个归属。
2. 批次交付前，只使用已配置跟踪器记录的 compare-and-set release，并按 reverse dependency
   顺序执行。缺少 safe 操作或 compare-and-set 失败时，保留剩余归属声明并停止 release。
3. 批次交付后，保留未解决的归属声明，并交接已配置完成操作。保留 delivered
   提交，以及重建经合并收束的工单边界所需的任何恢复引用。
4. 没有单独授权时，不执行强制操作、rebase、rollback、discard 或未配置跟踪器操作。

此路径以 `stopped` 或 `failed` 退出；保留的状态和交接仍为恢复边界。
