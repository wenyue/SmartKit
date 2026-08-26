---
name: setup-project-agents
description: 当需要跨 Codex、Cursor 和 Copilot 初始化或对齐仓库的 Rules、Skills、智能体或 MCP 时使用。
---

# 设置项目 Agents

本混合型技能对齐一个仓库的 Rules、Skills、智能体和 MCP。智能体决定已接受的能力意图；公开
工作流负责确定性的发现、渲染、验证、事务和清理。

## 判断框架

将四类能力视为平级。在 `start` 前检查其规范的输入，并且只有用户要求变更时才修改。

| 能力 | Canonical project 输入 | Setup 职责 |
| --- | --- | --- |
| Rules | `.agents/rules/` 下的项目自有源，以及请求生成的 Rule 目标 | 保留项目 Rules，并向各智能体宿主交付 setup 受管的 Rules。 |
| Skills | `.agents/skills/` 下的项目自有目录、请求生成的 Skill 目标，以及 `.agents/config.json` 的 `skills` 声明 | 保留项目 Skills，并安装请求生成或外部来源的 Skills。 |
| 智能体 | `.agents/agents/` 下的项目自有源，以及 `.agents/config.json` 的 `agents` 声明 | 保留智能体源，生成声明的宿主适配器，并安装 catalog 声明的 Codex Plugin 智能体默认项。 |
| MCP | `.agents/config.json` 的 `mcp` 声明 | 生成声明的智能体宿主原生 MCP 条目，不存储 secret 值。 |

使用随插件发布的 `.agents/config.json` schema。配置的智能体源是与 ID 匹配的
`.agents/agents/<id>.md`；每个 MCP 条目只声明 `url` 或 `command` 之一。按顺序执行的 `when`/`set`
override 可选择智能体宿主和操作系统平台；可选的 MCP 就绪可限定或替换推断出的静态检查。

项目自有规范的输入始终是可编辑的项目内容。Setup 生成的文件和结构化字段由 setup 拥有。
Plugin Rules、Skills、MCP，以及原生 Cursor 和 Copilot Plugin 智能体不属于此项目工作流。Setup
只把 catalog 声明的 Codex Plugin 智能体默认项安装为受管理资产；它们绝不会成为 Project 智能体声明。

Matt 仓库上下文是独立的项目自有前置条件。本工作流既不生成也不拥有
`docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md`，或指向
这些文件的 `## Agent skills` 区块。

## 事务工作流

1. 从目标仓库根目录验证 Matt 仓库 setup 已完成：三个 `docs/agents/` 上下文文件均存在，且
   `AGENTS.md` 或 `CLAUDE.md` 包含匹配的 `## Agent skills` 区块。任何部分缺失时，在 `start` 前停止，
   并告诉用户在该仓库中显式调用 `setup-matt-pocock-skills`。不要代替该 Skill 重复提问或选择 issue
   跟踪器。只有 Matt setup 报告完成后，才再次调用 `setup-project-agents` 继续。

2. 确定 Rules、Skills、智能体和 MCP 各自表达已接受的项目意图。

3. 将已加载 Skill 的目录识别为 `SETUP_PROJECT_AGENTS_ROOT`，然后启动公开工作流：

   ```sh
   sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" start \
     --target "$PWD"
   ```

   在 Windows 上使用相同参数调用 `setup_project_agents.ps1`。返回非零时停止。将返回的 `session`
   记录为 `SESSION`，将 `generated` 记录为 `GENERATED`，并记录 `request` 与 `source_root` 路径。
   只有一个私有会话存在且目标保持不变时才继续。

4. 读取请求，确认它已捕获接受的 Rules、Skills、智能体和 MCP 意图。任何选择不正确时，取消
   会话，修正规范的 project 输入，再重新 start。Start 后保持请求不变。

5. 在 `GENERATED/<target>` 下完成每个 `generation_requests` 条目，并保留完整目标路径。从
   `source_root` 解析每项项目设置编写契约，然后在目标仓库上下文中为契约的 Rule 或
   Skill 目标调用 `$write-rules-and-skills`。为每次调用显式选择公共 Default Fresh Role Adapter；
   setup 本身不提供 Adapter 或隔离机制。把每份已解析契约视为不可变 setup 输入；setup 不会创建或
   修改它。

   Matt 上下文永远不会成为 generation 请求。

   使用当前仓库证据；除非用户要求重新配置，否则保留完整的项目自有内容。只有 `GENERATED` 恰好
   包含由 `generation_requests` 声明的全部完整目标路径且没有未声明路径时才继续。

6. 审查 Gate 通过后，恰好完成同一个会话一次：

   ```sh
   sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" finish \
     --session "$SESSION"
   ```

   在 Windows 上调用 `setup_project_agents.ps1`。完成条件是退出码为零，且 JSON 包含
   `phase: finish` 和 `check: clean`。

7. 如果工作必须在 `start` 后、`finish` 前停止，取消会话：

   ```sh
   sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" cancel \
     --session "$SESSION"
   ```

   `finish` 后不要调用 cancel；无论成功或失败，清理由 finish 负责。

## Review Gate

- [ ] Rules、Skills、智能体和 MCP 都符合已接受的项目意图。
- [ ] Matt 仓库 setup 在 `start` 前已完成，并保持为项目自有内容。
- [ ] 每个已配置的智能体都指向完整且匹配的项目自有源。
- [ ] 每个生成的 Rule 和 Skill 都遵循其编写契约和当前仓库证据。
- [ ] Request 未被修改，每个请求目标都存在于生成的 root 下。
- [ ] 生成的项目内容不包含 credential 或 secret。

## 停止与恢复

`start`、`finish` 或 `cancel` 失败时停止并原样报告错误。`finish` 失败后丢弃该会话，解决原因后
重新开始。能力声明、所有权冲突或生成输出仍未解决时，在 `finish` 前停止。
只使用 `start`、`finish` 和 `cancel`；其实现负责 selection、rendering、deletion、验证、
transaction、checking 和会话清理。

## 结果

报告 finish 结果：固定的源提交、启用的智能体宿主、changed 路径、外部 Skills、保留的项目
自有路径和 clean check 状态。要求维护者审查并提交报告的项目快照；其他开发者通过 clone 或拉取
获取该快照。
