# Matt 主分支票据工作流对照研究

研究日期：2026-09-05。本文是供设计讨论使用的事实笔记，不是 Rule、Skill、ADR 或已接受的设计；“可借鉴”仅表示值得讨论。

## 版本与范围

GitHub 的 `branches/master` 返回永久迁移，目标是 `branches/main`。本次读取的当前主分支提交是 `3cca18b368ae95cdbdebbff572ccafa662551015`，提交时间为 2026-09-04 08:43:27 UTC，根 tree 为 `6e84c093fda2026396cea9fad6a924a6da0e1452`。后续源码均固定到该提交，不用浮动分支解释历史事实。[分支迁移 API](https://api.github.com/repos/mattpocock/skills/branches/master)、[主分支 API](https://api.github.com/repos/mattpocock/skills/branches/main)、[固定提交](https://github.com/mattpocock/skills/commit/3cca18b368ae95cdbdebbff572ccafa662551015)。

本地对照基线 HEAD 为 `7b20483326e1c92ffa0f633a39825abcbfff4ac1`；读取的是当前工作区文件。`create-worktree`、`finish-worktree` 等已有用户改动，因此 HEAD 不足以代表这些文件的实际内容。调查未修改它们。

已检查上游根递归 tree，并展开 engineering、in-progress、deprecated、misc 分类确认实际路径；主要读取 implement-spec、implement、wayfinder、to-tickets、code-review 及 in-progress README。implement-spec 与 implement 的目录没有额外流程引用文件，仅 SKILL.md 与 agents 元数据目录。没有执行真实 Agent 工作流或进行成功率、费用测量。[固定 tree](https://api.github.com/repos/mattpocock/skills/git/trees/6e84c093fda2026396cea9fad6a924a6da0e1452?recursive=1)。

## 上游事实

1. **最接近完整批次执行的是 `skills/in-progress/implement-spec/SKILL.md`。** 输入是已有 spec 及其 tickets，目标是一条分支上的单一 PR。票据表示有阻塞关系的任务图，可立即执行的集合称为 frontier；主代理与子代理尽量通过 spec、票据、研究笔记、之前提交的 context pointers 通信，避免复制已经可查的信息。[输入、图与通信，L7–L15][spec-core]
2. **执行结构以最大并发为目标。** 可先让 exploration subagent 把研究笔记放在仓库外、后续代理都能访问的位置；先建分支和 draft PR，并标注关闭 spec 与 tickets；每个 implementer 使用独立 worktree 和分支，完成后由 merger subagent 合入 PR 分支，frontier 扩大后继续派发。[步骤 1–6，L19–L29][spec-run]
3. **批次末尾统一审查。** 所有票据完成后，在 PR 分支运行 code-review；由一个 implementer 修复全部问题，然后 PR 转为 ready 并清理 implementer worktrees。该文件没有展开 worker 失败、合并失败、响应丢失、重复远程效果、tracker claim、需求漂移或修复后重新审查的具体协议；这里只能说文本未规定，不能推断真实运行一定缺少这些行为。[步骤 7–9，L31–L35][spec-end]
4. **implement-spec 是 Beta。** in-progress 的说明明确该分类不进入插件和顶层 README、没有文档页，允许改变或消失；因此不宜把它当作与本地同等成熟的恢复契约。[分类说明，L1–L5][beta]
5. **稳定分类的 `engineering/implement` 很薄。** 它接受 spec 或 tickets，建议在事先约定的测试接缝使用 TDD；经常运行类型检查和单个测试文件，结束时运行完整测试套件；完成后 code-review，并提交到当前分支。它没有 implement-spec 的图调度或 worktree 隔离编排。[全文，L7–L15][implement]
6. **`engineering/wayfinder` 默认规划决策。** 它用 tracker 上的 map issue 和 decision tickets 找清到目的地的路径，默认产生决策而非直接执行交付。map 是索引，细节归具体票据；加载低分辨率索引后按需深入。它的 frontier 是开放、无阻塞、未认领的子票据；HITL 票据要求真实人类参与，不能由 Agent 代答。[定位与 map，L7–L27][wayfinder] 这适合作为规划与信息组织参考，不能把 decision tickets 直接等同于实施票据。
7. **`engineering/to-tickets` 强调可独立验证的纵向切片与真实阻塞边。** 一票据尽量覆盖完整但狭窄的端到端行为，适配一个 fresh context window；宽泛机械重构允许 expand–contract 及共享 integration branch 的例外；发布前要求用户批准拆分。它属于票据形成阶段，不是已明确实施票据的执行循环。[切分规则与审批，L25–L59][tickets]
8. **上游 code-review 仍以非空 diff 为入口。** 固定点不存在或 diff 为空时提前失败；Standards 和 Spec 两轴由并行子代理完成。这并未提供“既有行为已满足全部验收要求”的无改动审查替代路径。[入口，L16–L24][review]

## 与本地当前契约的差异

| 方面 | 上游 implement-spec | 本地 implement-tickets |
| --- | --- | --- |
| 输入与选择 | 已提供 spec 和关联票据；读懂任务图 | 对用户限定候选范围进行正向 eligibility 证明、依赖闭包与稳定排序；空选择可成功无效果返回 |
| 调度 | ready frontier 上最大并发，每票各自分支/worktree | 冻结一次依赖有序批次，同一 Batch Worktree 内最多一个 ticket 或 repair worker |
| 数据传递 | context pointers，探索笔记一次生成供多代理使用 | 明确 worker 边界及来源、状态、权限、验证证据；允许证据在新鲜度成立时复用 |
| 提交归属 | merger 把独立工作合入 PR 分支 | 每票恰有一个 first-parent Ticket Commit，唯一 `SmartKit-Ticket` trailer；repair 不带 ticket trailer |
| 远程终点 | 开始 draft PR，末尾 ready PR | 按已接受 outcome 和精确 authority 调用 finish-worktree；PR 属于非合入交接 |
| 完成语义 | 文本以全票完成、整批审查、ready PR 收尾 | 只有 finalizer 证明权威交付后才进入 tracker closure，保留已完成前缀与原失败状态 |
| 恢复 | 核心文件未展开 | Git、tracker、依赖回执与原 worker/finalizer 身份恢复；不维护 Batch journal，不因响应缺失重试效果 |

本地来源：[SKILL.md](../../skills/implement-tickets/SKILL.md) L8–L40、[tracker.md](../../skills/implement-tickets/references/tracker.md) L18–L57 与 L148–L161、[worker-transaction.md](../../skills/implement-tickets/references/worker-transaction.md)、[complete-run.md](../../skills/implement-tickets/references/complete-run.md) L49–L92 与 L115–L168。本地已经有依赖图、frontier 和一次整批审查，不能把它们描述为上游首次带来的新能力。

[ADR-0007](../adr/0007-use-one-worktree-per-ticket-batch.md) 已接受单批单 worktree、串行、票据提交边界和不单独建 Batch journal；它替代 ADR-0005 与 ADR-0003 的相关旧设计。直接采用上游并行每票 worktree 会改变这项决策，而非普通文字精简。

当前工作区 [finish-worktree](../../skills/finish-worktree/SKILL.md) 已按所选 outcome 判断前置条件，支持保留未完成工作与转移变更，复用仍有效的证据，并引入外部操作回执。[implement-tickets 的统一 finalizer 入口](../../skills/implement-tickets/references/complete-run.md) L115–L138 仍要求整批验证和双轴审查通过，存在值得单独讨论的接口差异。

本地“空选择”和“选中票据全部无需修改”不同：前者已经是成功无效果结果；后者可以产生空 Ticket Commit，但整批 diff 为空仍不能进入现有 code-review，进入保留状态的 stop。这不是查询不到工作的问题。[主技能](../../skills/implement-tickets/SKILL.md) L8–L9、[单票证明](../../skills/implement-tickets/references/process-one-ticket.md) L40–L60、[最终审查入口](../../skills/implement-tickets/references/complete-run.md) L49–L55。

## 可借鉴的方向：分析而非已接受设计

- **指针式上下文与一次探索、多次消费。** 可减少重复读取、重复转述；若用于本地自动化，指针仍需能够定位准确版本和适用范围，否则旧笔记会误导后续 Worker。上游提出信息组织方式，本地已有的新鲜度与归属约束可提供判断边界。[spec-core][spec-run]
- **把任务图与执行资源策略分开讨论。** 图和 frontier 描述依赖；它们本身不推出必须并行。保留本地串行也能借用 frontier 解释“为什么现在可以处理这一票”。若改为并行，需要另行处理集成结果、语义冲突、失败分支与恢复权属，而非仅增加线程数。[spec-core][spec-run]、[ADR-0007](../adr/0007-use-one-worktree-per-ticket-batch.md)
- **把探索、票据形成与明确任务执行分清。** wayfinder 的问题发现、to-tickets 的人工批准拆分、implement-spec 的已有图执行分别承担不同结果。用户当前希望执行更自动化，不意味着执行器应自行作出新产品决定。[wayfinder][tickets][spec-core]
- **复用整批审查，保留本地更强的修复闭环。** 两边都在批次末尾审查；本地明确修复后以新 HEAD/tree 重跑整个验证及两轴，是上游简短步骤没有展开的部分。[spec-end]、[本地修复](../../skills/implement-tickets/references/complete-run.md) L94–L113。

不能直接照搬的行为包括：无条件最大并发、默认每票新 worktree、默认提前创建并关联关闭所有票据的 PR、把 ready PR 视为任务权威交付、无条件清理所有 worker worktrees、把 wayfinder 每会话只解决一个决策的 HITL 节奏带入自动执行。这些行为各自对应不同的隔离、授权、完成或交互选择；本文未替用户作出选择。

## 后续讨论需要决定的事项

- 是否保留 ADR-0007 的串行单 worktree；若变化，要解决什么已观察到的瓶颈。
- 用户后续已明确票据集合固定；尚需明确给定集合与 spec 的对应关系以及依赖闭合方式。
- 用户后续已同意单票受阻时继续安全独立票据；尚需明确部分成果的验收、交付与恢复。
- 预先授权的终点是 PR、合入、转移还是保留；每个终点如何影响 tracker 状态。
- 无改动验收、证据失效和进程中断恢复由哪个现有契约负责，是否真的需要新持久化状态。

这些问题仅列出设计分歧，不形成默认行为。无需为了借鉴上游而同步复制其工具、目录或命名。

[spec-core]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/implement-spec/SKILL.md#L7-L15
[spec-run]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/implement-spec/SKILL.md#L19-L29
[spec-end]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/implement-spec/SKILL.md#L31-L35
[beta]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/README.md#L1-L5
[implement]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/implement/SKILL.md#L7-L15
[wayfinder]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/wayfinder/SKILL.md#L7-L27
[tickets]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-tickets/SKILL.md#L25-L59
[review]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/code-review/SKILL.md#L16-L24

## 审查分工补充核实（2026-09-05）

再次读取上游 main，HEAD 仍为 `3cca18b368ae95cdbdebbff572ccafa662551015`。以下是两份 Skill 的明确文本和未规定事项，不是新增实施规则。

- **调用点及修复者：** implement-spec L31 在所有票据完成后于 PR 分支调用 code-review，并指定一个 implementer subagent 修复全部 findings；L33 再将 PR 标为 ready。[批次审查与修复](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/implement-spec/SKILL.md#L31-L35)
- **审查子代理：** code-review L8–L11 明确 Standards 与 Spec 两轴并行运行，以免相互污染上下文；L58–L72 明确分别派发两个子代理。Standards 收到完整 diff 命令、commit 列表、规范文件列表及完整 smell baseline，报告规范违反和启发式异味，区分硬约束与判断，不重复工具已检查的项。Spec 收到 diff 命令、commit 列表、spec 路径或正文，报告遗漏、部分实现、范围外行为及错误实现，并引用需求依据。两份报告各少于 400 words；spec 缺失时允许跳过 Spec 并报告。[身份与目的](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/code-review/SKILL.md#L8-L11)、[启动上下文与职责](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/code-review/SKILL.md#L58-L72)
- **汇总者：** 调用 code-review 的代理整理两个结果，保持各轴分别报告，不能合并或跨轴重新排序 findings。[汇总规则](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/code-review/SKILL.md#L74-L87)
- **未明确规定：** 这两份 Skill 没有身份级条款禁止已参与实现或修复的代理后来担任 Reviewer；没有指定不继承实现讨论、只接收干净上下文的启动机制；没有要求再额外启动一个“总 Reviewer”代理。可以合理理解为角色分开，但不能将“实现者永不兼任 Reviewer”称为上游已写明的保证。
- **审查粒度与复审：** implement-spec 明确的是全部票据完成后的 PR 分支整体审查，没有逐票正式 review 的步骤，也没有明确禁止其他检查。其修复之后下一步是标记 PR ready；两份 Skill 均未给出强制修复后复审或循环直到无阻塞结果的协议。不能由缺少条款推断其实际运行绝不复审，也不能称其已规定闭环。

行号校验说明：GitHub connector 返回原始文件，implement-spec 为 2043 bytes、blob SHA `d5097f847fc003935599a7f7bf8f0f7186427910`；code-review 为 6589 bytes、blob SHA `e28d7acbf7b3bb4d7817b7eb5d9c105af03f6ec4`。已按 Git blob 算法重新计算并匹配。网页浏览工具解析 raw 文本时会省略部分空行，因此其显示行号不能直接用作 GitHub 源码锚点。
