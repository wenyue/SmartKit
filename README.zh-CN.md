# WenYue SmartKit

[English](README.md) | 简体中文

WenYue SmartKit 是适用于 Codex、Cursor、GitHub Copilot 和 Qoder 的插件，提供可复用的 AI 编程工作流和
统一的项目规范，帮助团队配置和维护编程助手。支持 Windows 和 Linux。

## Skill 一览

包含 SmartKit 工作流、Matt Pocock 技能集和 ponytail 系列。各组按用途组织，方便按当前任务查找所需 Skill。

### 必须由用户手动调用

需要明确说出 Skill 名称，助手不会自行选用。

| Skill | 出处 | 用途与使用时机 |
| --- | --- | --- |
| `implement` | [Matt Pocock](https://github.com/mattpocock/skills) | 根据规格或工单实现一项工作。 |
| `implement-spec` | [Matt Pocock](https://github.com/mattpocock/skills) | 通过并行 Agent 实现规格的依赖工单，汇入统一集成分支。 |
| `grill-me` | [Matt Pocock](https://github.com/mattpocock/skills) | 通过深入追问梳理计划或设计，找出尚未明确的决定。 |
| `what-if` | [SmartKit](https://github.com/wenyue/SmartKit) | 判断你不确定的想法是否优于当前做法和替代方案，给出带优缺点的独立结论，且不做任何修改。 |
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

### 用户可主动调用的任务 Skill

针对一项具体任务使用。用户可以明确指定 Skill 名称，助手也可以在任务匹配时自行选用。此类按核对范围、调查与验证、开发与改进、审计与交付、配置与会话诊断的用途顺序排列。

| Skill | 出处 | 用途与使用时机 |
| --- | --- | --- |
| `what-changes` | [SmartKit](https://github.com/wenyue/SmartKit) | 用户要求执行累积较多或跨度较大的修改时，先核对范围，再询问是否开始实施；也可以明确指定调用。 |
| `research` | [Matt Pocock](https://github.com/mattpocock/skills) | 对照可信的一手资料调查问题，将结论保存为仓库中的 Markdown 文档。 |
| `prototype` | [Matt Pocock](https://github.com/mattpocock/skills) | 构建可丢弃的原型，验证设计、状态模型或界面是否可行。 |
| `diagnosing-bugs` | [Matt Pocock](https://github.com/mattpocock/skills) | 逐步诊断故障或性能回退，找到原因并验证修复。 |
| `tdd` | [Matt Pocock](https://github.com/mattpocock/skills) | 按“先写失败测试，再实现，再重构”的方式开发功能或修复问题。 |
| `refactor-code` | [SmartKit](https://github.com/wenyue/SmartKit) | 在保持行为不变的前提下改善一个具体代码目标的结构；该目标存在明确结构问题时使用。 |
| `ponytail-audit` | [ponytail](https://github.com/DietrichGebert/ponytail) | 审计代码库的缺陷、安全与负载风险、测试缺口、性能和复杂度；按重要性报告发现，不直接修改代码。 |
| `ponytail-debt` | [ponytail](https://github.com/DietrichGebert/ponytail) | 将 `shortcut:` 和旧 `ponytail:` 注释汇总成包含限制、重审触发条件与升级路径的技术债清单；获得授权后才保存文件。 |
| `pr` | [Matt Pocock](https://github.com/mattpocock/skills) | 撰写 PR 正文，说明变更、验证证据和合并风险。 |
| `write-rules-and-skills` | [SmartKit](https://github.com/wenyue/SmartKit) | 编写或修订一条 Agent Rule 或一个 Skill；创建或修改可复用的 Agent 指令时使用。 |
| `wizard` | [Matt Pocock](https://github.com/mattpocock/skills) | 为只能由人完成的配置步骤生成交互式 Bash 向导，例如凭证、CI 密钥或迁移切换。 |
| `diagnose-agent-session` | [SmartKit](https://github.com/wenyue/SmartKit) | 调查单个 Agent 会话的 token 开销、工具活动、等待或未完成的调用；会话行为异常时使用。 |

### 一般由 Agent 自动调用

Agent 通常会在工作过程中自行选用这些辅助 Skill。用户也可以明确指定；此类只在一览中列出，不设置独立用法章节。

| Skill | 出处 | 用途与使用时机 |
| --- | --- | --- |
| `ponytail` | [ponytail](https://github.com/DietrichGebert/ponytail) | 编码时优先选择满足需求的最简单方案，减少不必要的抽象、依赖和代码。 |
| `ponytail-review` | [ponytail](https://github.com/DietrichGebert/ponytail) | 审查改动的正确性、安全、负载、测试、性能与复杂度；项目标准和 Spec 符合性检查使用 `code-review`。 |
| `code-review` | [Matt Pocock](https://github.com/mattpocock/skills) | 审查相对指定提交、分支或标签的修改，同时核对项目规范与需求规格。 |
| `grilling` | [Matt Pocock](https://github.com/mattpocock/skills) | 深入追问并检验计划、决定或想法，找出薄弱环节。 |
| `rename-code` | [SmartKit](https://github.com/wenyue/SmartKit) | 重命名一个符号或受 Git 跟踪的路径，并更新其实际引用；需要精确完成仓库内的重命名时使用。 |
| `create-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | 准备隔离的 Git worktree；并行工作或需要保护当前检出目录中的改动时使用。 |
| `finish-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | 通过交接、拉取请求、本地合并、保留或明确丢弃来结束隔离 worktree 的工作；需要确定该 worktree 的后续去向时使用。 |
| `codebase-design` | [Matt Pocock](https://github.com/mattpocock/skills) | 梳理模块接口与职责，改善封装、可测试性和代码导航。 |
| `domain-modeling` | [Matt Pocock](https://github.com/mattpocock/skills) | 明确领域术语、维护术语表并记录架构决策。 |
| `writing-for-agents` | [Matt Pocock](https://github.com/mattpocock/skills) | 编写或修改面向 Agent 的文档，使指令、边界和行动条件清晰可执行。 |

## SmartKit Skill 用法

以下只展开前两类中来源为 SmartKit 的 Skill，并按一览中的出现顺序排列。在消息中明确写出 Skill 名称即可调用，下面的例子可供参考。必须手动调用的 Skill 需要用户明确指定；用户可主动调用的任务 Skill 也可以由助手自动选用。

### `what-if`

在行动前需要独立判断一个想法时，手动调用。它会比较提议、当前做法和有价值的替代方案，说明利弊，全程只读。实施需要后续单独下达指令。

例子：“用 `what-if` 判断这两个配置文件是否应该合并。”

### `review-for-humans`

需要按文件理解改动，并分别判断改动是否合理、实现是否优雅时，手动调用。可以指定 PR、分支或文件；未指定范围时，审查当前 worktree 中未提交改动的净效果。它跳过测试文件，分组展示完整文件；可以要求继续展示下一组，也可以按编号选择修复问题或优化建议。

例子：“用 `review-for-humans` 解释我未提交的改动。”随后：“修复第 2 项，然后继续。”

### `collect-todos`

需要将选定的暂缓任务保存到项目声明的任务跟踪器，再回到主任务时，手动调用。它会检查已有记录，报告经验证的链接。先配置项目的任务跟踪器；缺少配置时，Skill 不会自行改用其他存储位置。

例子：“用 `collect-todos` 记录刚才讨论的缓存清理，留待以后处理，然后继续修复登录问题。”

### `setup-project-agents`

接入 SmartKit 或更新项目 Agent 配置时，手动调用。完整配置会检查项目 Rule、Skill、自定义 Agent 和 MCP 映射，并保留仍然有效的项目决定。缺少必需的任务跟踪器和领域上下文时，先运行 `setup-matt-pocock-skills`。只需要本地同步或更新 Rule 索引时，明确限定范围。

例子：“用 `setup-project-agents` 更新这个仓库的 Agent 配置。”

### `what-changes`

实施前需要核对累积的修改时使用。用户可以明确指定调用；要求执行累积较多的修改时，Agent 也可以自行选用。它会只读整理当前目标、排除项、未决选择和计划修改的文件。未决选择明确后，再询问是否开始实施。

例子：“用 `what-changes` 核对这次对话中累积的修改，暂不实施。”

### `refactor-code`

一个具体代码目标存在已知结构问题时使用。说明目标和要解决的问题；它会改善内部结构，同时保留已支持的行为和外部契约。开放式寻找架构改进机会属于另一类任务。

例子：“用 `refactor-code` 消除 `parse_record` 中重复的转义处理，保留输入顺序和错误行为。”

### `write-rules-and-skills`

需要编写或修订一条可复用的 Agent Rule 或一个 Skill 时使用。用户可以明确指定调用，Agent 也可以在任务匹配时自行选用。说明预期任务、读者和约束。它会产出一份完整工件，经过必需检查以及质量、变更和正确性审查；发布和安装是另外的操作。

例子：“用 `write-rules-and-skills` 编写一条项目 Rule，要求在替换已有导出文件前核对导出记录。”

### `diagnose-agent-session`

需要调查单个 Agent 会话的异常 token 用量、工具活动、等待或未完成调用时使用。诊断其他会话时，提供客户端和会话标识；两者都未提供时，可以推定为当前 Codex 会话。Codex 支持轮次和整场会话证据，Cursor 与 Copilot CLI 支持整场会话的用量证据。报告会区分观察结果与缺失证据，并将费用标为估算值；获取整场会话证据需要授权提供方扫描记录、访问网络和读写缓存。

例子：“用 `diagnose-agent-session` 调查当前 Codex 轮次中的工具活动和等待。”

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
