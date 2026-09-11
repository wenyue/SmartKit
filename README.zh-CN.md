# WenYue SmartKit

[English](README.md) | 简体中文

`WenYue SmartKit` 是同时适配 Codex、Cursor、GitHub Copilot 和 Qoder 的跨 Harness 插件。它将 Rules、Skills、
Agents 和 MCP 作为平级能力提供，并在会话开始时检查推荐工具和已配置 MCP 的前置条件是否可用。

## 安装插件

请在实际使用的每个宿主中分别安装一次 `smartkit`。

Codex：

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

也可以在 Codex 中使用 `/plugins` 完成安装。

> **必须完成的 Codex Hook 审查：** 安装或启用 SmartKit 不会自动信任其内置 Hook。安装后，
> 请打开 Codex CLI 会话，运行 `/hooks`，审查并信任 SmartKit 的 Hooks，然后开启
> 新的 Codex 会话或运行 `/clear`。完成信任前，Codex 会跳过 SmartKit 的推荐工具检查和 Rule 分发。只有更新
> 改变了 Hook 定义且 Codex 将其重新标记为待审查时，才需要再次审查。

Cursor：通过 Plugin Marketplace 或 `/add-plugin` 安装；私有版本请通过团队市场或本地插件方式
导入。

GitHub Copilot CLI：

```sh
copilot plugin marketplace add wenyue/SmartKit
copilot plugin install smartkit@wenyue
```

需要更新 Copilot 插件时，先运行 `copilot plugin marketplace update wenyue`，再运行
`copilot plugin update smartkit`。

Copilot CLI 和 VS Code 通过 `.claude-plugin/plugin.json` 发现 SmartKit，入口布局对齐
Superpowers。Codex 和 Cursor 保留原生清单，Qoder 保留现有原生集成；这不代表新增了对
Claude Code 宿主的支持。Copilot hooks 使用 `CLAUDE_PLUGIN_ROOT`，PowerShell 中写作
`$env:CLAUDE_PLUGIN_ROOT`。入口迁移不会消除 Copilot CLI 与 VS Code 的 hook 事件及响应协议差异。

Qoder：

```sh
qoder plugin marketplace add wenyue/SmartKit
qoder plugin install smartkit@wenyue
```

## 插件 Rules、Skills、Agents 与 MCP

| 能力 | SmartKit 提供的内容 |
| --- | --- |
| Rules | 核心指令，以及由 Agent 根据内容描述和当前任务自主读取的 Rules。优先比较强度（`Mandatory` > `Default` > `Advisory`），再比较项目归属和更窄的适用范围。描述不改变优先级。 |
| Skills | SmartKit 工作流，以及经过审查、许可证校验和版本固定的第三方工作流。 |
| Agents | 四个宿主上的 `change-set-verifier`。它使用项目的 change-set-verification Skill；setup 未安装该 Skill 时报告 `inconclusive`，并继承宿主选择的模型。Cursor、Copilot 和 Qoder 从插件获取它；Codex 通过 setup-managed 默认交付获取它。 |
| MCP | 四个宿主上隔离、无界面模式的 Playwright，并继续遵守宿主正常的审批行为。 |

四个宿主都通过 Hook 接收核心 Rules 和 Rule 索引。规则正文直接放在 `rules/` 下；
`rules/registry.json` 的每条 Rule 只包含 `id`、`source`、`strength` 和 `description`。
ID 以 `smartkit/core-` 开头的规则立即交付正文。每份交付的正文都包含在标明源路径的文件 wrapper
中，并要求 Agent 将其视为独立的 Rule 文件；Strength、Scope 等声明保留文件内语义，相对引用从该
路径解析。其他规则的内容描述和解析后的源文件路径出现在索引中。Agent 根据描述和当前任务决定读取
哪些规则，也可以先读取确认相关性，或在有需要时重新读取。描述不是由程序判断的加载条件。加载需要
对插件 Rule 目录具有读取权限。路径用于定位正文，不用于触发加载。

Codex 和 Qoder 通过会话生命周期恢复这些上下文。Copilot CLI 和 Cursor 跟踪上下文压缩，
在下一个受支持的继续执行节点前恢复核心 Rules 和索引。因此，压缩后可能需要重试一次工具调用
或重新检查答案；普通文件操作不会激活 Rules，也不会引发重试。索引中的规则正文由 Agent 按需重新读取。

预期 Rule 未生效时，请检查宿主 Hook 诊断，并验证 Agent 实际可见的上下文。Cursor 使用文档规定的
`sessionStart.additional_context` 接口，其交付是异步的；脚本成功本身不能证明宿主完成了注入。
Cursor cloud agent 和 Copilot cloud agent 不在此插件 Rule 契约范围内。

Codex 插件包不会加载自定义 Agents。请在每个受维护的项目快照中运行 `setup-project-agents`，将
SmartKit 的 Codex Agent adapter 安装到 `.codex/agents/`。该 adapter 仍归插件所有，不需要在
`.agents/config.json` 中添加 Project Agent 声明。

## Harness 与平台支持

四个宿主都支持 Windows 和 Linux。

| 宿主 | Rules | Skills | Agents | MCP |
| --- | --- | --- | --- | --- |
| Codex | 会话 Hook | 插件 Skill catalog | Setup-managed `change-set-verifier` | Playwright |
| Cursor | 会话 Hook 与压缩后恢复 | 插件 Skill catalog | `change-set-verifier` | Playwright |
| GitHub Copilot CLI | 会话 Hook 与压缩后恢复 | 插件 Skill catalog | `change-set-verifier` | Playwright |
| Qoder | 会话 Hook | 插件 Skill catalog | `change-set-verifier` | Playwright |

## 为每个项目执行设置

进入目标仓库，请 Agent 使用 `setup-project-agents` 配置 Codex、Cursor、Copilot 和 Qoder。
如果提示需要先运行 `setup-matt-pocock-skills`，完成后再继续设置。

由一名维护者运行设置、审查并提交改动，团队其他成员通过 Git 获取配置。每次未限定范围的设置或更新都是全量设置：依据当前项目证据和插件中不可变的编写契约，重新编写当前全部生成的项目 Rules 和 Skills，包括配套资源。生成的源文件可以直接编辑；即使上游契约未变，这些编辑也会成为下次全量设置的输入。

明确请求项目同步，可以更新本地 Rule/Skill 发现及项目 Agent/MCP 映射，无需获取外部内容、生成内容或升级共享及外部资产。这需要全量设置建立的所有权记录；外部 Skill 声明变化时，必须执行全量设置。变化仅限于 `AGENTS.md` Rule 索引时，请求 Rule 索引同步即可，这在尚未执行全量设置时也可使用。两个本地操作都支持只读检查。

| 能力 | 配置位置 |
| --- | --- |
| Rules | `.agents/rules/` |
| Skills | `.agents/skills/`；外部 Skills 在 `.agents/config.json` 中声明 |
| Agents | `.agents/agents/`；在 `.agents/config.json` 中声明 |
| MCP | `.agents/config.json` |

项目 `AGENTS.md` 的索引分为必读表和按需表，空表省略。必读表只列路径和强度；Agent 在开始任务前
读取其中全部规则，并在上下文压缩后重新读取正文已不在上下文中的规则。按需表包含内容描述，
由 Agent 根据当前任务决定读取和重读哪些规则。加载策略与规则强度相互独立。

catalog 的 Rule 元数据通过 `loading` 声明 `always` 或 `on-demand`，只有 `on-demand` 要求
提供 `description`。对于额外的项目 Rule，将它放入两列的必读表即可声明为必读。完整 setup 和项目同步
都会保留这一选择，同时更新规则强度并移除已删除的条目。其他被发现的项目规则使用 `Scope` 作为按需描述。
单独同步索引时会保留 catalog 管理的条目，并应用其当前加载策略。

支持的字段见[配置 schema](setup-assets/catalog/project-config.schema.json)。

### MCP overrides

每条 override 都包含 `when` selector 和 `set` 对象。省略 `when.harnesses` 时匹配该 server 启用的
全部宿主，省略 `when.operatingSystems` 时匹配全部受支持的操作系统（`windows` 和 `linux`）。两者
同时提供时必须都匹配。匹配的规则按数组顺序应用，后面的规则只覆盖其声明的字段：

```json
{
  "id": "inspector",
  "command": "python",
  "overrides": [
    {
      "when": {"operatingSystems": ["windows"]},
      "set": {"command": "py"}
    },
    {
      "when": {"harnesses": ["cursor", "copilot"]},
      "set": {"cwd": "tools/inspector"}
    }
  ]
}
```

### Project MCP readiness

Project MCP 的前置条件检查默认自动执行。当检查只适用于特定宿主或操作系统时，使用
`readiness.harnesses` 或 `readiness.operatingSystems` 限定范围：

```json
{
  "id": "inspector",
  "command": "cache/inspector.exe",
  "readiness": {
    "operatingSystems": ["windows"]
  }
}
```

添加 `readiness.checks` 可替换自动检查，设为 `[]` 则禁用检查。支持的检查种类包括
`command-exists`、`runtime-version`、`workspace-path` 和 `environment-variable`。

SmartKit 只管理自己生成的内容，并尽量保留项目原有文件和用户配置。应提交 `AGENTS.md`、
`.agents/`、受管宿主 wrapper 和配置以及 `docs/agents/`；不要将它们加入 `.gitignore`。Session
数据、缓存、日志和凭据留在仓库外，生成的项目文件不得包含 secret。

## Hook、多智能体、MCP readiness 与工具维护

插件会按 canonical project、当前宿主和本地日期，每天自动运行一次 readiness pipeline。第一步
就是 daily gate；policy 变化不会绕过它，显式 `--force` 可以重跑。当前检查包括：

- 推荐工具的安装状态和版本，包括 CodeGraph 与 Tokscale；
- 必要的实际配置值，包括 Codex 多智能体支持；
- 适用于当前 Harness 和操作系统的 MCP 前置条件。

这些检查不会安装工具、修改 MCP 配置、启动 MCP server、探测网络或应用端口、触发 OAuth，也不
要求 debug session 在线。因此，Project HTTP MCP 不会执行连接检查。

发现缺失或过期工具时，SmartKit 会先列出需要处理的项目并询问用户，只执行用户明确同意的维护
操作。如果用户明确拒绝列出的操作，SmartKit 会直接跳过，不再重复询问，Agent 随后继续原任务。
不能自动处理的项目会给出手动操作建议。Cursor 在交互会话中会阻止受影响的提示；在 headless
`--print` 会话中，则通过会话上下文要求 Agent 先询问并结束本轮。

## 典型使用流程

```text
安装或更新 SmartKit → 开启新的宿主会话 → 完成宿主 Hook 审查（Codex：/hooks）→ 由维护者运行
setup-project-agents → 审阅并提交生成快照 → 其他开发者 pull → 开始使用
```

如果检查提示需要安装或升级工具，请先确认工具名称和操作，再决定是否授权。
