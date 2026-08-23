# 工作区政策

强度：`Mandatory`

适用范围：工作区选择、本地 Git 状态、commit 权限和远程操作授权。

## 所有 Checkout

- 本节适用于当前 checkout 和每个 linked worktree。
- 在实施和 review 已接受任务时，保留所有既有 staged、unstaged 和 untracked 工作。
- 某项任务操作会覆盖、stash、reset、clean 或丢弃这些状态时，改用无损方案；没有无损方案时请求用户
  决定。
- 同一文件同时包含既有改动和任务改动时，能够区分两者并验证结果完整保留既有改动才继续；否则停止
  并请求用户决定。
- 除非用户另行授权 commit，或 worktree 已取得下文规定的特定 commit 权限，否则保留未提交的任务
  改动。

## Worktree 选择与 Commit 权限

- 当用户、Harness 和适用 Skill 都不要求隔离，并行工作不需要独立状态，且 checkout 既有状态可以
  原地保留时，使用当前 checkout。
- 当用户、Harness 或适用 Skill 要求隔离、并行工作需要独立状态，或必须通过隔离保护 checkout 既有
  状态时，应用 `create-worktree`。由其负责 linked-worktree 的选择、创建、验证、就绪和机械性 handoff。
- `create-worktree` 返回 ready 结果且调用方复核后，所属 workflow 可以无需单独授权，在该 worktree
  中通过仓库正常 commit hooks 创建仅含该 scope 改动的 Checkpoint Commits。后续 Agent 只有在已
  接受的 workflow 标识出准确的 worktree 和 base，且当前 Git evidence 证明此后每个 commit 和本地
  改动都属于同一 scope 时，才能延续该权限；存在歧义时停止创建新 commit。
- implementation workflow 准备收束或交付时，应用 `finish-worktree`。implementation workflow
  负责正式 review；`finish-worktree` 负责 finalization，并且只有在证明同一 head 和 tree 已通过验证
  与正式 review，且不存在 blocking finding 后，才能交付。
- synchronization 改变 reviewed content 时，将其交回 implementation workflow，在交付前重新验证
  并进行正式 review。

## 远程操作

- 只有用户明确要求相应结果时，才执行每项远程操作。
