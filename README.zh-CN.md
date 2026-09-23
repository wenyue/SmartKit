# WenYue SmartKit

[English](README.md) | 简体中文

WenYue SmartKit 是适用于 Codex、Cursor、GitHub Copilot 和 Qoder 的插件，提供可复用的 AI 编程工作流和
统一的项目规范，帮助团队配置和维护编程助手。支持 Windows 和 Linux。

## Matt Pocock 技能集之外的 Skill

### 必须由用户手动调用

需要明确说出 Skill 名称，助手不会自行选用。

| Skill | 用途与使用时机 |
| --- | --- |
| `setup-project-agents` | 配置或更新仓库中的编程助手；接入 SmartKit 或更新项目 Agent 配置时使用。 |
| `implement-tickets` | 按依赖顺序实现并审查一批符合条件的工单；多个已就绪工单适合成批处理时使用。 |

### 可以自动调用

任务匹配时，助手可以自行选用；用户也可以明确指定。

| Skill | 用途与使用时机 |
| --- | --- |
| `what-changes` | 用户要求执行累积较多或跨度较大的修改时，先核对范围，再询问是否开始实施；也可以明确指定调用。 |
| `refactor-code` | 在保持行为不变的前提下改善一个具体代码目标的结构；该目标存在明确结构问题时使用。 |
| `rename-code` | 重命名一个符号或受 Git 跟踪的路径，并更新其实际引用；需要精确完成仓库内的重命名时使用。 |
| `create-worktree` | 准备隔离的 Git worktree；并行工作或需要保护当前检出目录中的改动时使用。 |
| `finish-worktree` | 通过交接、拉取请求、本地合并、保留或明确丢弃来结束隔离 worktree 的工作；需要确定该 worktree 的后续去向时使用。 |
| `diagnose-agent-session` | 调查单个 Agent 会话的 token 开销、工具活动、等待或未完成的调用；会话行为异常时使用。 |
| `write-rules-and-skills` | 编写或修订一条 Agent Rule 或一个 Skill；创建或修改可复用的 Agent 指令时使用。 |

## 安装插件

先安装你使用的编程助手，再按对应步骤安装插件。

### Codex

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

安装后，打开 Codex CLI 会话，运行 `/hooks`，审查并信任 SmartKit 的 Hooks，然后开启新会话或运行
`/clear`。也可以通过 `/plugins` 从已添加的市场中安装。参见 [Codex 插件指南](https://learn.chatgpt.com/docs/plugins)。

### Cursor

将插件克隆到 Cursor 的本地插件目录：

```sh
git clone https://github.com/wenyue/SmartKit.git "$HOME/.cursor/plugins/local/smartkit"
```

重启 Cursor 或运行 `Developer: Reload Window`，然后打开 Customize，确认插件已加载。
所在组织需允许导入本地插件。通过团队市场安装的方法，参见 [Cursor 插件指南](https://cursor.com/docs/plugins)。

### GitHub Copilot CLI

```sh
copilot plugin marketplace add wenyue/SmartKit
copilot plugin install smartkit@wenyue
```

参见 [Copilot 插件安装指南](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)。

### Qoder

```sh
qoder plugin marketplace add wenyue/SmartKit
qoder plugin install smartkit@wenyue
```

这些命令需要 Qoder 已启用插件市场功能。参见 [Qoder 插件指南](https://docs.qoder.com/cli/plugins)。
