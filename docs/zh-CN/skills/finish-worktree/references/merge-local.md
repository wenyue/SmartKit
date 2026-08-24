# 本地 Merge

把记录的本地目标分支推进到已验证的交付提交头。范围为**已交付**时，复核
local 目标仍指向已证明提交，只执行此结果授权的清理，报告证明和保留的状态，
然后停止。

1. 确认目标检出目录位于记录的目标分支。任何范围路径与已暂存、未暂存或未跟踪
   目标本地改动重叠且合并可能覆盖它们时，保持两个检出目录不变，改为提供
   return-for-review。
2. 要求记录的目标 `HEAD` 等于收尾契约的 `expected_head`，并且是交付提交头
   要求的历史边界。目标已经移动时，返回**完成已审查历史**。
3. 从目标检出目录运行 `git merge --ff-only <source-branch>`。
4. 从目标检出目录重新运行 relevant 验证。证明目标现在指向交付提交头，且每个
   无关的目标本地改动仍与其快照匹配。
5. 验证通过后，请记录的 lifecycle 归属移除 host-created 工作树。对于 Git-created
   工作树，从目标检出目录移除该准确 clean 工作树，并使用 Git safe 分支 deletion 删除已
   合并的源分支。

fast-forward integration 或 post-merge 验证失败时，保留源分支、工作树和恢复
引用，并报告 resulting 目标状态。不得自动 rewrite 或 rollback 目标。
