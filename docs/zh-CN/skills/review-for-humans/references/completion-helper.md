# 完成助手

这里定义 CLI 能力、输入、证据绑定和恢复机制。[完成操作](completion.md)负责就绪、授权、覆盖及对应分支的完成选择，[技能入口](../SKILL.md)负责普通沟通和审查。使用工具前阅读相关归属。

## 能力与前提

助手支持已选本地分支上、已验证的 github.com PR：仅记录 Viewed，或新建提交并正常推送后记录 Viewed。可以复用已提交的待发布内容。amend、带租约或强制发布、镜像推送远端、detached 工作区、未解决 Git 操作、特殊暂存区标记，以及变化的子模块或目录条目，使用完成操作的手动流程。

需要 Python 3.8+、Git、已认证 GitHub CLI（`gh`）、PR 及源访问、已准备源码对象和回读。查看者必须匹配审查身份。使用针对 github.com 的 `gh api`，不会安装工具、fetch、同步或选择工作区。

从实际加载的技能解析 `<skill-root>`，不依赖目标工作目录。先阅读接口：

```text
python "<skill-root>/scripts/complete_review.py" --help
```

## 冻结准备好的操作

提供完整提交 ID、确切本地分支、完整符合条件的 `viewed_paths`，以及工作树外稳定的绝对证据文件，证明就绪、覆盖、已披露范围和授权。助手散列证据字节，不判断其含义。`plan_id` 标识效果，不授予权限。

```json
{
  "repository": "/absolute/selected-worktree",
  "branch": "review-branch",
  "pull_request": "owner/repository",
  "number": 123,
  "base": "1111111111111111111111111111111111111111",
  "head": "2222222222222222222222222222222222222222",
  "viewer": "reviewer-login",
  "viewed_paths": ["src/feature.py"],
  "mode": "commit-push",
  "remote": "origin",
  "message": "Fix reviewed behavior",
  "requires_amend": false,
  "evidence": ["/absolute/private/review-and-checks.json"]
}
```

`pull_request` 指 PR 所属仓库，源仓库和引用从 GitHub 获取，包括 fork。`viewed-only` 省略 `remote` 和 `message`，本地 HEAD 必须匹配被审查 PR head，差异会被冻结保留。按记录如实设置 `requires_amend`；准备会拒绝它，让手动 amend 与租约流程继续负责。

通过所属产物生命周期选择工作树外的新私有状态目录。保持这份唯一恢复证据可用且不发布。创建使用仅所有者可访问的 POSIX 权限；Windows 使用具有合适继承访问控制的账户私有目录。

```text
python "<skill-root>/scripts/complete_review.py" prepare --input "/private/request.json" --state "/private/completion-state"
```

准备保留计划、原始暂存区字节、已跟踪二进制差异、文件字节及符号链接目标、预期完整文件树、待发布祖先链与差异、完整 PR 分页和证据摘要。发布准备用隔离暂存区和原生 clean filter，可能添加 Git 对象，同时验证真实暂存区、分支、HEAD 和内容不变。范围披露需要查看清单和日志，简短计数不足以代替。

## 执行或恢复

取得确切效果授权后，复用返回的 `plan_id`：

```text
python "<skill-root>/scripts/complete_review.py" run --state "/private/completion-state" --confirm "<plan_id>"
```

命令加锁并重新验证状态，需要时暂存预期内容，运行正常钩子，验证文件树、父提交、待发布祖先链和源目标。只在必要时执行正常的指定范围推送，不自动发布标签或子模块；验证源引用、PR 版本、已发布提交和文件树，再标记剩余路径，回读整个选定集合及未变的 PR 版本。复用前验证既有效果，不创建空提交。

stdout 是包含状态、版本计数、计划进度路径和私有日志位置的简短 JSON。每个 Git/gh 子进程保留参数、身份、stdout/stderr、退出状态和耗时。退出 `0` 表示所需回读完成，`1` 未完成，`2` 用法错误，`130` 中断。检查失败与残余效果；助手不回滚，也不推进审查进度。

中断或丢失响应后，使用相同状态和计划 ID 运行同一命令。它会检查实际效果并恢复缺失工作，包括部分 Viewed。原生锁随进程退出释放；子进程启动后失败时，父进程等待自己拥有的 Git/gh 子进程停止，再释放锁。

内容、分支、证据、查看者、源、base/head、发布范围或检测到的钩子改动发生变化时，停止依赖效果。保留状态，通过完成操作和技能入口解决清点、检查、复审及同意，只为已确定的新效果准备新计划。准备失败时保留私有诊断。缺失回读或未知子进程状态仍为未完成：不要删除锁、reset、推测性重复写入或改用继续。
