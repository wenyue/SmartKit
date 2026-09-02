---
name: setup-project-agents
description: 当需要跨 Codex、Cursor 和 Copilot 初始化或对齐仓库的 Rules、Skills、智能体或 MCP 时使用。
---

# 设置项目智能体

对齐一个目标仓库的 Rules、Skills、智能体和 MCP。应存在什么由已接受的项目意图决定；随软件交付的
setup 工作流负责确定性的发现、渲染、验证、事务和清理。将四类能力视为平级，并且仅当用户请求变更
时才修改规范输入。

## 权威与所有权

| 能力 | 规范项目输入 | Setup 职责 |
| --- | --- | --- |
| Rules | `.agents/rules/` 下的项目自有源以及请求生成的 Rule 目标 | 保留项目 Rules，并向各宿主交付 setup 受管的 Rules。 |
| Skills | `.agents/skills/` 下的项目自有目录、请求生成的 Skill 目标以及 `.agents/config.json` 的 `skills` 声明 | 保留项目 Skills，并安装请求生成或外部来源的 Skills。 |
| 智能体 | `.agents/agents/` 下的项目自有源以及 `.agents/config.json` 的 `agents` 声明 | 保留智能体源，渲染声明的宿主适配器，并安装 catalog 声明的 Codex Plugin 智能体默认项。 |
| MCP | `.agents/config.json` 的 `mcp` 声明 | 渲染声明的宿主原生 MCP 条目，但不存储密钥值。 |

使用随软件交付的 `.agents/config.json` schema。每个已配置的智能体都有与之匹配的
`.agents/agents/<id>.md` 源文件。每个 MCP 条目只能声明 `url` 或 `command` 两者之一；按顺序应用的
`when`/`set` 覆盖项可以选择智能体宿主和操作系统平台，可选的就绪配置则可以限定或取代推断得到的 MCP
检查。

项目自有的规范输入仍是可编辑的项目内容。setup 生成的文件和结构化字段归 setup 所有，并由其所有权
清单和摘要保护。遇到所有权冲突时应停止，不得覆盖。Plugin Rules、Skills、MCP 以及原生 Cursor 和
Copilot Plugin 智能体不属于此工作流。Setup 仅管理 catalog 声明的 Codex Plugin 智能体默认项；这些
默认项绝不会成为 Project Agent 声明。

Matt 仓库上下文是一项独立的项目自有前置条件。本工作流既不生成也不拥有
`docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、
`docs/agents/domain.md`，也不生成或拥有指向这些文件的 `## Agent skills` 区块。

## 前置条件

在 `start` 前，确定全部四类能力的已接受意图，并验证 Matt 仓库 setup 已完成：上述三个上下文文件
均存在，而且 `AGENTS.md` 或 `CLAUDE.md` 包含与它们匹配的 `## Agent skills` 区块。如果该前置条件
不完整或无法确认，则在 `start` 前终止本次 `setup-project-agents` 调用，并告诉用户在目标仓库中
显式调用 `setup-matt-pocock-skills`。不要复述该 Skill 的问题，也不要替它选择问题跟踪器。Matt setup
报告完成后，只能通过一次全新的 `setup-project-agents` 调用进入本 Skill；不得恢复或继续已终止的
运行。

## 单会话事务

从目标仓库根目录开始，将已加载的 Skill 目录识别为 `SETUP_PROJECT_AGENTS_ROOT`，然后启动一个私有
会话：

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" start --target "$PWD"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" start `
  --target (Get-Location).Path
```

返回非零时停止。将返回的 `session` 记录为 `SESSION`，将 `generated` 记录为 `GENERATED`，并记录
`request` 和 `source_root` 路径。只有在恰好存在该私有会话且目标保持不变时才继续。捕获的请求不可
变更：验证它表达了已接受的 Rules、Skills、智能体和 MCP 意图；如果没有，则取消会话、修正规范输入
并重新启动。

在每个 `generation_requests` 条目对应的准确 `GENERATED/<target>` 路径下完成该条目。从
`source_root` 解析其 Setup Authoring Contract，保持该契约不变，并在目标仓库上下文中为请求的 Rule
或 Skill 调用 `$write-rules-and-skills`。使用当前仓库证据；除非已接受重新配置，否则保留完整的项目
自有内容。Matt 上下文绝不会成为生成请求。

在 finish 前，`GENERATED` 必须恰好包含声明的全部完整目标路径；未请求生成任何内容时，也必须满足
这一空集合要求。同时确认：

- 全部四类能力均符合已接受的意图；
- Matt 上下文仍归项目所有，且前置条件仍然完整；
- 每个已配置的智能体都有完整且匹配的项目自有源；
- 每个生成的 Rule 和 Skill 均符合其已解析的契约和当前仓库证据；
- 请求和目标均未发生漂移，每个请求路径都存在，且不存在任何未声明路径；并且
- 生成的项目内容不包含凭据或密钥。

上述条件通过后，恰好完成同一会话一次：

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" finish --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" finish --session "$SESSION"
```

成功要求退出码为零，并且 JSON 包含 `phase: finish` 和 `check: clean`。

## 停止与恢复

如果必须在 `start` 之后、任何 `finish` 尝试之前停止工作，则取消会话：

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" cancel --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" cancel --session "$SESSION"
```

只能使用 `start`、`finish` 和 `cancel`；它们的实现负责选择、渲染、删除、验证、事务检查和清理。
任何操作失败时，报告其准确错误。未解决的声明、所有权或摘要冲突、请求或目标漂移以及生成路径不匹配
都会阻止 finish；取消会话并修正后，必须启动全新会话。

一旦尝试过 `finish`，绝不能取消会话或重试 finish：无论成功还是失败，均由 finish 负责清理。finish
失败后，丢弃该会话；只有解决原因后才能重新开始。取消失败是本次运行的终止状态，必须原样呈现。

## 结果

报告 finish 结果：固定的源提交、启用的宿主、变更路径、外部 Skills、保留的项目自有路径以及 clean
检查状态。请维护者审查并提交报告的项目快照；其他开发者通过 clone 或 pull 获取该快照。
