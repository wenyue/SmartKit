# WenYue SmartKit

[English](README.md) | 简体中文

WenYue SmartKit 是适用于 Codex、Cursor、GitHub Copilot 和 Qoder 的插件，提供可复用的 AI 编程工作流和
统一的项目规范，帮助团队配置和维护编程助手。支持 Windows 和 Linux。

## Skill 一览

包含 SmartKit 工作流、Matt Pocock 技能集和 ponytail 系列。各组按日常开发中的预计使用频率
由高到低排列，方便优先找到常用功能；顺序不是实际使用统计。

### 必须由用户手动调用

需要明确说出 Skill 名称，助手不会自行选用。

| Skill | 出处 | 用途与使用时机 |
| --- | --- | --- |
| `implement` | [Matt Pocock](https://github.com/mattpocock/skills) | 根据规格或工单实现一项工作。 |
| `implement-spec` | [Matt Pocock](https://github.com/mattpocock/skills) | 通过并行 Agent 实现规格的依赖工单，汇入统一集成分支。 |
| `grill-me` | [Matt Pocock](https://github.com/mattpocock/skills) | 通过深入追问梳理计划或设计，找出尚未明确的决定。 |
| `to-spec` | [Matt Pocock](https://github.com/mattpocock/skills) | 将已讨论的内容整理成规格，发布到项目任务跟踪器。 |
| `to-tickets` | [Matt Pocock](https://github.com/mattpocock/skills) | 将计划或规格拆成可逐步交付的工单，并声明依赖关系。 |
| `review-for-humans` | [SmartKit](https://github.com/wenyue/SmartKit) | 按文件用简单例子和有依据的评价解释用户提供的修改，分组展示，便于人类 reviewer 阅读并继续审核。 |
| `collect-todos` | [SmartKit](https://github.com/wenyue/SmartKit) | 将暂缓任务保存到项目配置的任务跟踪器，并报告收集了哪些待办；需要记录旁支任务并继续当前主任务时使用。 |
| `handoff` | [Matt Pocock](https://github.com/mattpocock/skills) | 将当前对话整理成交接文档，供另一个 Agent 或后续会话继续工作。 |
| `retro` | [Matt Pocock](https://github.com/mattpocock/skills) | 复盘编码会话，提出 Agent 工作环境改进建议。 |
| `ask-matt` | [Matt Pocock](https://github.com/mattpocock/skills) | 根据当前情况推荐适合的 Skill 或工作流；不知道该选哪个时使用。 |
| `wait-what` | [Matt Pocock](https://github.com/mattpocock/skills) | 让助手重新解释上一条回答；说明难以理解时使用。 |
| `teach` | [Matt Pocock](https://github.com/mattpocock/skills) | 结合当前工作区学习一个技能或概念。 |
| `triage` | [Matt Pocock](https://github.com/mattpocock/skills) | 对 Issue 和外部 PR 分类、核实并整理成 Agent 可执行的任务说明。 |
| `grill-with-docs` | [Matt Pocock](https://github.com/mattpocock/skills) | 通过追问梳理设计，同时记录架构决策和领域术语。 |
| `improve-codebase-architecture` | [Matt Pocock](https://github.com/mattpocock/skills) | 扫描代码库中的结构改进机会，展示可视化报告，并深入讨论选中的目标。 |
| `to-questionnaire` | [Matt Pocock](https://github.com/mattpocock/skills) | 将尚不能回答的决策整理成问卷，供其他人补充信息。 |
| `wayfinder` | [Matt Pocock](https://github.com/mattpocock/skills) | 将跨多个会话的大型工作整理成决策工单地图，逐项明确实施路径。 |
| `setup-project-agents` | [SmartKit](https://github.com/wenyue/SmartKit) | 配置或更新仓库中的编程助手；接入 SmartKit 或更新项目 Agent 配置时使用。 |
| `setup-matt-pocock-skills` | [Matt Pocock](https://github.com/mattpocock/skills) | 配置任务跟踪器、分诊标签和领域文档布局；首次使用 Matt Pocock 工程技能前运行。 |

### 可以自动调用

任务匹配时，助手可以自行选用；用户也可以明确指定。

| Skill | 出处 | 用途与使用时机 |
| --- | --- | --- |
| `ponytail` | [ponytail](https://github.com/DietrichGebert/ponytail) | 编码时优先选择满足需求的最简单方案，减少不必要的抽象、依赖和代码。 |
| `diagnosing-bugs` | [Matt Pocock](https://github.com/mattpocock/skills) | 逐步诊断故障或性能回退，找到原因并验证修复。 |
| `code-review` | [Matt Pocock](https://github.com/mattpocock/skills) | 审查相对指定提交、分支或标签的修改，同时核对项目规范与需求规格。 |
| `pr` | [Matt Pocock](https://github.com/mattpocock/skills) | 撰写 PR 正文，说明变更、验证证据和合并风险。 |
| `tdd` | [Matt Pocock](https://github.com/mattpocock/skills) | 按“先写失败测试，再实现，再重构”的方式开发功能或修复问题。 |
| `ponytail-review` | [ponytail](https://github.com/DietrichGebert/ponytail) | 审查当前修改中的过度设计，指出可删除、简化或替换的实现。 |
| `refactor-code` | [SmartKit](https://github.com/wenyue/SmartKit) | 在保持行为不变的前提下改善一个具体代码目标的结构；该目标存在明确结构问题时使用。 |
| `rename-code` | [SmartKit](https://github.com/wenyue/SmartKit) | 重命名一个符号或受 Git 跟踪的路径，并更新其实际引用；需要精确完成仓库内的重命名时使用。 |
| `what-changes` | [SmartKit](https://github.com/wenyue/SmartKit) | 用户要求执行累积较多或跨度较大的修改时，先核对范围，再询问是否开始实施；也可以明确指定调用。 |
| `research` | [Matt Pocock](https://github.com/mattpocock/skills) | 对照可信的一手资料调查问题，将结论保存为仓库中的 Markdown 文档。 |
| `prototype` | [Matt Pocock](https://github.com/mattpocock/skills) | 构建可丢弃的原型，验证设计、状态模型或界面是否可行。 |
| `grilling` | [Matt Pocock](https://github.com/mattpocock/skills) | 深入追问并检验计划、决定或想法，找出薄弱环节。 |
| `create-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | 准备隔离的 Git worktree；并行工作或需要保护当前检出目录中的改动时使用。 |
| `finish-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | 通过交接、拉取请求、本地合并、保留或明确丢弃来结束隔离 worktree 的工作；需要确定该 worktree 的后续去向时使用。 |
| `codebase-design` | [Matt Pocock](https://github.com/mattpocock/skills) | 梳理模块接口与职责，改善封装、可测试性和代码导航。 |
| `domain-modeling` | [Matt Pocock](https://github.com/mattpocock/skills) | 明确领域术语、维护术语表并记录架构决策。 |
| `ponytail-audit` | [ponytail](https://github.com/DietrichGebert/ponytail) | 扫描整个代码库的过度设计，按优先级报告可删除或简化的内容；不直接修改代码。 |
| `ponytail-debt` | [ponytail](https://github.com/DietrichGebert/ponytail) | 将代码中的 `ponytail:` 注释汇总成技术债清单；获得授权后才保存文件。 |
| `diagnose-agent-session` | [SmartKit](https://github.com/wenyue/SmartKit) | 调查单个 Agent 会话的 token 开销、工具活动、等待或未完成的调用；会话行为异常时使用。 |
| `write-rules-and-skills` | [SmartKit](https://github.com/wenyue/SmartKit) | 编写或修订一条 Agent Rule 或一个 Skill；创建或修改可复用的 Agent 指令时使用。 |
| `writing-for-agents` | [Matt Pocock](https://github.com/mattpocock/skills) | 编写或修改面向 Agent 的文档，使指令、边界和行动条件清晰可执行。 |
| `wizard` | [Matt Pocock](https://github.com/mattpocock/skills) | 为只能由人完成的配置步骤生成交互式 Bash 向导，例如凭证、CI 密钥或迁移切换。 |

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
