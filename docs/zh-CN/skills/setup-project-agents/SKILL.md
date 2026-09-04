---
name: setup-project-agents
description: 用于在 Codex、Cursor 和 Copilot 之间初始化或协调一个仓库的 Rules、Skills、Agents 或 MCP。
---

# 设置项目 Agent

根据可信 SmartKit 快照和仓库自己的 Agent 输入，协调一个仓库。

## 原则

- **一个仓库，一项事务。**探索完整的设置相关状态，将其冻结在一个私有会话中，然后完成该会话一次或取消它。
- **明确所有权。** SmartKit 拥有目录、渲染目标、主机适配器、所有权记录、验证和事务。仓库保留其本地 Rules、Skills、Agent 来源、配置、无关内容和秘密。
- **项目意图仍是权威。**只有获得已接受权限时，才更改项目所有的输入。渲染文件是这些输入的结果，绝不是新的事实来源。
- **效果各需授权。**网络访问、临时存储、生成内容编写和目标变更是不同效果。允许一种效果并不代表允许另一种。
- **证据会被冻结。**会话会绑定源、外部快照、生成请求，以及设置实际使用的目标状态。该表面发生漂移时必须新建会话。
- **完成必须收敛或恢复。**在一个回滚边界内应用完整计划，保留无关状态，并且只有后置条件干净时才宣告完成。

## 输入与所有权

随附目录始终启用 Codex、Cursor 和 Copilot。它会安装声明的共享 Rules 和 Skills、Codex Plugin Agent 默认值，以及目录声明的所有项目蓝图。可选项目配置可以添加外部 Skills、项目 Agents 和 MCP 服务器。

若 `.agents/config.json` 存在，或已接受意图要求任何非默认输入，则从当前已加载 Skill 目录解析[随附 schema](../../setup-assets/catalog/project-config.schema.json)，并在 `start` 前使用它协调或创建该目标所有文件。没有此文件表示使用随附默认值。在 schema 中，`skills` 标识 GitHub 来源和包含的 Skill 目录；`agents` 将项目所有的 `.agents/agents/<id>.md` 来源映射到主机适配器；`mcp` 声明 `url` 或 `command` 中恰好一项，还可包含有序的主机或操作系统覆盖以及就绪元数据。

设置会发现并保留 `.agents/rules/` 和 `.agents/skills/` 下额外的项目所有 Rules 与 Skills。项目 Agent 来源也仍归项目所有。目录声明的 Codex Plugin Agent 默认值只是回退项，不是项目 Agent 声明。原生 Cursor 和 Copilot Plugin Agents，以及原生插件 Rules、Skills 和 MCP，均不属于本工作流。

SmartKit 只拥有 `.agents/smartkit.lock.json` 中记录的文件和结构化字段，以及一个由所有权标记包围并包含 `## Project rules` 的已认证 `AGENTS.md` 单元。若不存在该节，它会追加此单元；只有当一个无标记旧节的全部内容与当前生成内容完全相同时，才可接管它。节内容冲突、标记格式错误或重复、所有权模糊，或任何其他所有权或摘要冲突，都会在替换前停止设置。保留标记单元之外的每个字节，以及每个未声明文件、字段、目录和秘密值。

MCP 环境字段命名环境变量；URL、命令、参数和覆盖字面量仍属于项目输入。不要推断任意字符串是敏感信息。若合格的仓库证据识别出真实的敏感字面量，在渲染前停止，并要求项目所有者将其替换为受支持的间接引用。

MCP 就绪状态属于另一个每日自动项目检查。设置会验证、冻结并保留就绪声明，但不执行它们。该检查选择当前 Harness 和操作系统，在 `checks` 不存在时推断检查，遵守显式检查和 `checks: []`，并负责自己的发现。它不会安装任何内容，也不会启动服务器、联系端点或进行身份验证。因此，设置成功和 `check: clean` 证明的是配置收敛，而不是 MCP 已就绪。

## 预检

只解析会影响随附默认值、项目所有输入或获准效果的重要选择。优先使用合格的仓库证据，只询问真正尚未解决的选择。

首先要求存在 `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md` 和 `docs/agents/domain.md`，并且 `AGENTS.md` 或 `CLAUDE.md` 中有一个真实的 `## Agent skills` 节引用全部三者。这些 Matt 上下文归项目所有：设置既不创建也不拥有这些文件或入口块。若不完整，结束本次调用并要求用户在目标中调用 `setup-matt-pocock-skills`。只有该工作流完成后，才能开始新的 `setup-project-agents` 调用。

在 `start` 前，取得已接受的项目意图，并分别取得以下权限：私有系统临时会话、对规范 SmartKit `master` 的一次只读 Git 获取，以及配置的外部 Skills 声明的每次获取。下游生成内容编写效果和 `finish` 应用的确切目标变更仍是独立授权；各自在操作开始前取得。

这些获取只能联系其声明的仓库，并可创建后再删除私有临时检出。它们以非交互方式运行，不使用环境中的 Git 配置、凭据辅助程序、代理、SSH 或 askpass 状态。它们均不授权依赖安装、发布、Git 历史变更或任何其他目标写入。遇到未授权效果时，在其发生前停止。若规范获取不可用，`start` 可以使用经过验证的已安装插件根目录，并报告 `source_commit: null`；配置的外部来源仍需各自的网络权限。

对于每个配置的外部来源，`source` 必须用 GitHub `owner/repository` 标识来源；`ref` 可以是既有安全分支、标签或完整提交，省略时选择远程默认分支。仓库根目录必须包含一份明确、完整且可识别的 MIT、Apache-2.0、BSD-2-Clause、BSD-3-Clause、MPL-2.0 或 ISC 许可证。每个包含路径都必须是安全的常规目录树，其中 UTF-8 `SKILL.md` 有一段由确切标记包围的 frontmatter，且 `name` 等于目标目录 basename。链接、格式错误或重复的 frontmatter、矛盾的许可证文本、非常规条目、目标冲突和共享 Skill 名称冲突都会被拒绝。先前记录的标签不得解析到另一提交。任何拒绝都会在目标变更前停止 `start`，并删除其私有检出。修正声明或来源后，开始新的调用。

## 启动冻结会话

从目标仓库根目录，将当前已加载 Skill 目录标识为 `SETUP_PROJECT_AGENTS_ROOT`，然后启动一个私有会话：

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" start --target "$PWD"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" start `
  --target (Get-Location).Path
```

两个启动器都只先检查 `python3`，再检查 `python`，要求 Python 3.10 或更高版本，并使用第一个兼容命令执行。若两个命令都不合格，启动器会说明要求和检查顺序，然后以 2 退出。不要搜索其他解释器或绕过启动器。

遇到非零结果时停止。将 `session` 记录为 `SESSION`，将 `generated` 记录为 `GENERATED`，并记录返回的 `request`、`source_root`、`source_commit` 和 `source_fingerprint`。请求会冻结设置输入、外部快照、生成请求，以及源和设置相关目标指纹。目标指纹只覆盖设置使用的证据：项目设置配置、所有权与托管资产、生成目标、项目 Rule 元数据、项目 Agent 来源，以及涉及的原生主机配置。Git 历史和索引状态、缓存、日志及其他项目所有工作均不在其中。
编写前确认它符合已接受意图。规范运行固定到其提交和指纹；已安装回退由其根目录、空提交和指纹标识。

在一次 `finish` 或 `cancel` 前，只保留这一个私有会话。将请求和来源视为不可变。`finish` 和 `cancel` 都会原子声明会话；若声明已存在，说明另一项终止操作已经开始，此时保留会话并停止。`start` 后，冻结的设置相关表面发生任何目标变更——包括下游编写工作流在该表面产生的 Acceptance 效果——都会终止此会话：取消它，并从变更后的已接受目标状态重新开始。该表面之外的变更不会重启生成；将其作为无关状态保留。这样，编写效果仍受自己的授权约束，而不会被悄然纳入设置。

## 完成生成请求

对于每个请求，从 `source_root` 解析其不可变 Setup Authoring Contract，然后加载并调用 `source_root/skills/write-rules-and-skills/SKILL.md` 中的公共工作流，包括它要求的同源 references 和 `writing-for-agents` 依赖。在目标仓库上下文中运行该工作流，将 Setup Authoring Contract 作为已接受任务或规格输入，将 `GENERATED` 作为请求根目录。环境中或目标检出内的编写器不是本会话的权威。编写工作流独立拥有自己的 Candidate、相称证据与证明、Acceptance 效果和结果；设置不提供任何目标效果权限。只有从其 ready 交接才能继续，并且交接中的确切 Candidate 路径必须已经位于 `GENERATED` 下。除非已接受的重新配置另有说明，否则保留完整的项目所有内容。

所有冻结请求均就绪后，使用以下确切结构创建 `GENERATED/.setup-generation.json`：

```json
{
  "version": 1,
  "requests": [
    {"id": "<generation request id>", "outputs": ["<exact target-relative path>"]}
  ]
}
```

每个请求和返回的 Candidate 路径都恰好包含一次。每个请求的主 `target` 都是必需项。Rule 请求只声明其主目标。Skill 请求还可以声明其 Authoring Contract 返回的、位于该 Skill 目录下的确切支持路径；目录、glob、推断路径或来自非 ready 交接的资源都不构成声明。此清单是私有会话控制数据，不会安装。

## 完成一次

恰好运行一次 `finish`：

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" finish --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" finish --session "$SESSION"
```

变更前，Finish 会重新验证请求、设置相关目标指纹、来源与外部快照、确切生成清单、所有权、渲染状态和计划。它在一个回滚边界内应用计划及其干净后置条件。在返回前，给予 `finish` 对每个计划目标路径的独占访问。每次变更前，它会重新检查观察到的完成前内容、模式和身份，但受支持主机文件系统无法通过先前身份提供可移植的原子比较交换替换或删除。因此，不协作的写入者在检查与文件系统变更之间的狭窄时间窗内所作的写入可能被覆盖。成功要求零退出，并返回包含 `phase: finish` 和 `check: clean` 的 JSON；只有此时，会话才会作为已完成事务被移除。

## 停止与恢复

若工作必须在 `start` 后、任何 `finish` 尝试前停止，取消该会话：

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" cancel --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" cancel --session "$SESSION"
```

完成前，未解决的声明、所有权或摘要冲突、设置相关目标漂移，或生成路径不匹配，都要求取消会话，并在修正后新建会话。取消失败是终止结果，应原样报告。

固定来源的 finish 或事务失败后，保留其确切错误。事务会尝试还原完成前的设置状态；若检查发现并发第三方变更，则拒绝执行回滚变更。报告的回滚失败会指出残留目标状态，供人工检查。同一文件系统限制也适用于回滚检查与其变更之间，因此在失败处理期间保持独占访问。随后，Finish 会尝试删除私有会话；若清理失败，必须报告确切会话路径。

清理失败可能发生在目标已达到干净预期状态之后，也可能发生在事务失败后，因此不能推断零退出成功或已经回滚。绝不复用、完成或取消该残留会话。将任何剩余声明或部分会话内容视为终止操作证据。检查报告的目标和会话，只移除经过验证的工作流所有残留；存在原始原因时先解决它；若仍需设置，再启动新会话。

## 交接

报告来源模式、来源根目录、来源指纹，以及存在时的提交；启用的主机；变更路径；所有权结果中的外部 Skill 来源和提交；保留的项目所有路径；适用时的回滚或残留状态证据；以及干净检查状态。要求维护者审查并提交项目快照。本 Skill 不授予提交、推送、发布、依赖安装、目标外安装或发行权限。
