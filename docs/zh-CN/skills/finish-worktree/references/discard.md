# 丢弃

只丢弃显式用户请求中准确指明的本地隔离工作树和分支。

1. 展示已解析的工作树路径、源分支、自有的提交范围、发布状态，以及每个无法从
   基点到达的提交。除非已确认的请求已经指明这些准确目标并明确授权其丢失，否则取得
   confirmation。
2. 要求源工作树 clean，并证明该分支未由另一个工作树检出目录。任何 dirty 或
   未跟踪 content、目标标识或 lifecycle 归属有歧义时停止。
3. 把 host-created 工作树的移除委托给该智能体宿主。对于 Git-created 工作树，只移除准确记录的
   工作树；其历史已 integrated 时使用 safe 分支 deletion，只有 confirmed discard 必然放弃
   unmerged 提交时，才强制 delete 本地分支。
4. 验证基点检出目录和其全部本地状态保持不变，并且准确本地工作树和分支已不存在。
5. 只通过 expected-old-value checks 删除工作流-owned 恢复引用。保留并报告 expected value 或
   归属不匹配的任何引用。
