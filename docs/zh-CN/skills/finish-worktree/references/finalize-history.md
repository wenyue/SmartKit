# Finalize History

进入时应有已证明 Finalization Contract 和一个 reviewed source tree。

1. refresh target。只通过 current ancestry 或 equivalent-change evidence 加 required verification
   检测 **Already Delivered**。
2. 只有 accepted evidence 能确定 conflict behavior 时，才可以把 moved target merge 到 source branch。
   调用 `resolving-merge-conflicts` 前，检查 accepted behavior 和双方。evidence 允许多个结果时，恢复
   pre-merge source state 并请求 decision。synchronization 会使 review 失效，并把 changed source
   交回其 implementation workflow 重新验证和 formal review。
3. 要求 accepted scope 在准确 fixed point、source head 和 tree 上通过 formal review，且没有 blocking
   finding。
4. 对 `preserve-commits`，要求 target 是完整 owned range 的 parent boundary；证明每个 preserved
   commit 都属于 accepted scope、source clean，且其 head 和 tree 等于 reviewed evidence。source
   `HEAD` 成为 delivery head。
5. 对 `consolidate-checkpoints`，根据 accepted scope 和 repository convention 推导一个 commit
   message。创建唯一 recovery ref，并针对准确 target 运行
   `scripts/consolidate_worktree_history.py`。证明得到的 Delivery Commit 以 target 为唯一 parent、
   tree 与 reviewed source 逐字节相同、hooks 成功且 source worktree clean。该 commit 成为 delivery
   head。

completion 要求一个已证明 delivery head 或 **Already Delivered**。返回 history policy、owned source
range、delivery head 或 Delivery Commit、tree、recovery data 和 current target proof。
