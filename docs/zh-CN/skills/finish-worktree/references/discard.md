# 丢弃

只丢弃显式用户请求中准确指明的本地隔离 worktree 和 branch。

1. 展示 resolved worktree path、source branch、owned commit range、publication state，以及每个无法从
   base 到达的 commit。除非 accepted request 已经指明这些准确 targets 并明确授权其丢失，否则取得
   confirmation。
2. 要求 source worktree clean，并证明该 branch 未由另一个 worktree checkout。任何 dirty 或
   untracked content、target identity 或 lifecycle ownership 有歧义时停止。
3. 把 host-created worktree 的移除委托给该 host。对于 Git-created worktree，只移除准确记录的
   worktree；其 history 已 integrated 时使用 safe branch deletion，只有 confirmed discard 必然放弃
   unmerged commits 时，才 force delete 本地 branch。
4. 验证 base checkout 和其全部本地状态保持不变，并且准确本地 worktree 和 branch 已不存在。
5. 只通过 expected-old-value checks 删除 workflow-owned recovery refs。保留并报告 expected value 或
   ownership 不匹配的任何 ref。
