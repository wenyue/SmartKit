# 本地 Merge

把记录的本地 target branch 推进到 verified delivery head。scope 为 **Already Delivered** 时，复核
local target 仍指向已证明 commit，只执行此 outcome 授权的 cleanup，报告 proof 和 preserved state，
然后停止。

1. 确认 target checkout 位于记录的 target branch。任何 scope path 与 staged、unstaged 或 untracked
   target-local work 重叠且 merge 可能覆盖它们时，保持两个 checkouts 不变，改为提供
   return-for-review。
2. 要求记录的 target `HEAD` 等于 Finalization Contract 的 `expected_head`，并且是 delivery head
   要求的 history boundary。moved target 返回 **Finalize Reviewed History**。
3. 从 target checkout 运行 `git merge --ff-only <source-branch>`。
4. 从 target checkout 重新运行 relevant verification。证明 target 现在指向 delivery head，且每个
   unrelated target-local change 仍与其 snapshot 匹配。
5. verification 通过后，请记录的 lifecycle owner 移除 host-created worktree。对于 Git-created
   worktree，从 target checkout 移除该准确 clean worktree，并使用 Git safe branch deletion 删除已
   merge 的 source branch。

fast-forward integration 或 post-merge verification 失败时，保留 source branch、worktree 和 recovery
refs，并报告 resulting target state。不得自动 rewrite 或 rollback target。
