# 准备 PR 审查

## 核实选定的工作区

在这个虚构的 PR 审查中，`/work/app` 位于干净的 `main` 分支。`contributor` 远端指向已核实的源 fork。本地 `feature/export` 分支跟踪 `contributor/feature/export`，目前可签出，也可从 `b1ce402` 快进到该远端跟踪引用上的固定 head `38bf06d`。现有任务工作树均不符合条件。

- A． **创建** （推荐）：在 `38bf06d` 上使用 `codex/export-review` 分支创建 `/work/app/.worktrees/export-review`，配置新分支跟踪 `contributor/feature/export`，并检查工作区是否就绪。`/work/app` 保持在 `main` 分支。
- B． **切换** ：将 `/work/app` 切换到 `feature/export`，并快进至 `38bf06d`，保留干净状态及 `main` 的分支顶端。
- C． **快照** ：审查已经核实的固定 PR 比较，保留本地工作。

用户选择创建。创建返回 `ready` 后，核实固定提交和原有检出。按已选方案设置跟踪，再确认新分支的上游远端及合并引用分别指向已核实的源 fork 和 `feature/export`。开始实时审查前，刷新 PR 比较和 Viewed 证据。

## Viewed 筛选不可用时

固定比较已经可用，但已获授权的采集方式无法取得完整的 Viewed 状态，也无需用户再提供事实。询问是否审查所有符合其他条件的非测试文件。如果用户坚持保留筛选，保留固定比较，等完整的 Viewed 证据可用后再继续筛选后的审查。
