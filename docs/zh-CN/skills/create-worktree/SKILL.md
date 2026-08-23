---
name: create-worktree
description: 当会改变仓库状态的工作因并行执行、workflow 隔离或保护当前 checkout 而需要隔离的 linked Git worktree 时使用。
---

# 创建 Worktree

此 Procedure-led Skill 创建或复用一个具名 linked Git worktree，并在保留 base branch、index 和
既有本地状态的同时，为所属 implementation scope 做好准备。它负责 worktree 的选择、创建、验证、
就绪和机械性所有权 handoff。它不把 scope 分类为 task、ticket 或 batch。业务实施、已完成改动的
集成、tracker 状态和清理仍由各自 owner 负责。

## 建立准备契约

1. 记录已接受的 implementation scope、调用方提供的 `scope_owner`、预期路径或小写连字符 slug、
   具名 branch、准确 base commit、后续的 `integration_owner` 和 `cleanup_owner`、host 是否已经
   创建预期 worktree；如果已经创建，还要记录调用方提供的 `creation_owner`。
2. 根据调用方提供的准确 base commit，解析一个 base checkout 和具名 base branch。检查当前 branch
   和 `HEAD`、Git common directory 以及 `git worktree list --porcelain`；预期 base 处于 detached
   状态或存在歧义，或者解析结果与所提供 commit 不同时停止。不得用当前 branch tip 替代它。
3. mutation 前，snapshot base checkout 的 branch、`HEAD`、commit tree、index tree、staged、
   unstaged 和 untracked 状态，以及所有已注册 worktrees 和本地 branches。此 snapshot 是保留边界
   和已接受的 readiness base。

## 选择并验证 Worktree

1. 只有所属 workflow 为准确的 implementation scope 选择了当前 linked worktree 时，才复用它。
   要求其具名 branch、`HEAD`、commit tree 和本地状态 ownership 与准备契约匹配；否则停止且不提供
   ready 结果。
2. 对新 worktree，选择 `<base-root>/.worktrees/<slug>`，并遵循已验证的仓库 branch 约定；没有约定时
   回退为 `worktree/<slug>`。验证 branch 名，并要求该路径和 branch 在文件系统、已注册 worktrees
   和本地 branches 中都不存在。
3. 对 `<base-root>/.worktrees/` 下每个选定路径，无论复用还是新建，都要求根 `.gitignore` 包含有效的
   仓库相对 `.worktrees/` 条目。条目缺失或无效时，只有 `.gitignore` 归项目所有，并且该编辑能够
   保留、区分全部既有内容和本地状态，才追加 `.worktrees/` 作为最小有效修复；把它记录为有意的
   project-owned 改动。文件为 generated、read-only、ownership 不明确，或编辑会与无法区分的本地
   工作重叠时停止。
4. 使用 `git check-ignore -v` 证明每个选定的仓库相对 `.worktrees/` 路径都被根 `.gitignore` 忽略；
   global exclude 或 `.git/info/exclude` 不充分。对新 worktree，取得准确选定目录和 worktree 所需的
   权限。该权限不授权任何无关 Git 或文件系统改动。

## 创建并验证

1. 创建前立即根据已记录契约复核 base branch、`HEAD`、commit tree、路径和 branch。任何值已移动或
   出现时，在创建前停止，并报告记录值、当前值和保留的 snapshot。
2. host 的原生 worktree 创建能力可用时，使用它并把其具体 lifecycle owner 记录为
   `creation_owner`。只有该能力不可用时，才使用 Git fallback，并把执行
   `git -C <base-root> worktree add -b <branch> <worktree-path> <base-commit>` 的具体 Agent 记录为
   `creation_owner`。
3. 使用 `git worktree list --porcelain` 验证路径、branch 和 `HEAD` 等于选定值。复核 base checkout
   的 `HEAD`、commit tree、index tree 和既有本地状态与 snapshot 匹配；只允许已记录的
   `.worktrees/` `.gitignore` 添加。
4. 创建失败时，检查 Git worktree metadata 和选定路径。只移除已证明由本次尝试创建且不含用户工作
   的不完整 artifact。无法证明时，保留 evidence，并以准确 recovery owner 和 action 停止。安全
   移除后，重复创建前检查并重试一次。第二次失败时保留全部剩余 evidence 并停止。

## 准备并建立就绪状态

1. 在选定 worktree 中继续。目标仓库提供 `worktree-environment-setup` 时，在 baseline 验证前应用。
2. environment 准备后，运行仓库声明的 baseline 验证。失败的 baseline 是既有 evidence：除非用户
   明确接受它用于此 worktree，否则在实施前停止。未声明 baseline 时，除非所属 workflow 或用户明确
   接受 baseline 不可用，否则停止且不提供 readiness。不得用已完成改动的验证代替，也不得臆造命令。
3. 只有 worktree 有一个具名 branch、其 `HEAD` 和 commit tree 等于已接受 base、baseline 通过或已
   明确接受，并且每个本地路径都只属于已接受 implementation scope 时，才报告 worktree ready。
4. 保留每个失败 worktree 供诊断，不自动丢弃 evidence。

## 结果

返回一个 preparation handoff，其中包含 `status`；已接受 implementation scope；选定 `worktree`、
`branch`、准确 `head` 和准确 `tree`；base checkout、branch、准确 commit 和 tree 以及保留的本地状态；
`scope_owner`、`creation_owner`、`integration_owner` 和 `cleanup_owner`；预期路径或 slug、
`.gitignore` 结果和允许的本地状态 scope；environment setup 和 baseline 命令、结果及已接受失败；
readiness 结果和原因；不 ready 时还包含 retained state、failed phase 和 next owner。调用方在实施或
finalization 前复核 handoff。handoff 不授予其记录值以外的任何权限。
