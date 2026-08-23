# 留待以后处理

保留 completed delivery head，不进行 integration、publication 或 cleanup。scope 为
**Already Delivered** 时，复核已证明 target，完全按记录保留 source branch 和 worktree，报告 proof
和 preserved state，然后停止。

1. 不进行 branch、checkout、index、worktree、filesystem 或 remote mutation。
2. 再次确认 source branch 指向记录的 delivery head，且 worktree clean。
3. 报告 target branch 和 commit、source branch 和 delivery head、history policy、worktree path、
   creation owner、verification result、publication state，以及剩余 integration 或 cleanup owner。
