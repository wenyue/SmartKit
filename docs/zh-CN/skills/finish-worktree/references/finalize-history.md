# Finalize History

进入时应有已证明收尾契约和一个已审查的源树。

1. refresh 目标。只通过当前 ancestry 或 equivalent-change 证据加 required 验证
   检测**已交付**。
2. 只有已确认的证据能确定 conflict 行为时，才可以把 moved 目标合并到源分支。
   调用 `resolving-merge-conflicts` 前，检查已确认的行为和双方。证据允许多个结果时，恢复
   pre-merge 源状态并请求决定。synchronization 会使审查失效，并把 changed 源
   交回其实施工作流重新验证和 formal 审查。
3. 要求已确认的范围在准确 fixed 节点、源提交头和树上通过 formal 审查，且没有 blocking
   问题。
4. 对 `preserve-commits`，要求目标是完整自有的范围的 parent 边界；证明每个保留的
   提交都属于已确认的范围、源 clean，且其提交头和树等于已审查的证据。源
   `HEAD` 成为交付提交头。
5. 对 `consolidate-checkpoints`，根据已确认的范围和仓库 convention 推导一个提交
   message。创建唯一恢复引用，并针对准确目标运行
   `scripts/consolidate_worktree_history.py`。证明得到的交付提交以目标为唯一 parent、
   树与已审查的源逐字节相同、hooks 成功且源工作树 clean。该提交成为交付
   提交头。

完成要求一个已证明交付提交头或**已交付**。返回历史政策、自有的源
范围、交付提交头或交付提交、树、恢复 data 和当前目标证明。
