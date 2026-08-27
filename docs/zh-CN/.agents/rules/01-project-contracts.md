# 项目契约

强度：`Mandatory`

适用范围：能力所有权、目标安装、文档、评估、契约演进、分发，以及硬依赖或暴露边界的变更有效性。

只有在每项受影响能力都有唯一规范所有者，并且每个派生、交付或安装表面都保持在下列契约内时，
项目变更才有效。`AGENTS.md` 负责激活本 Rule，Plugin Rule Configuration 负责优先级。如果当前
证据无法选定必需的所有者、路径或结果，应在修改或交付受影响表面前停止。

## 规范所有权与交付

- 将每个插件能力注册表及其声明的源视为规范来源。生成的宿主 adapter 和交付表面仍是其声明的
  synchronizer 或 renderer 的输出；它们既不获得政策所有权，也不成为独立编辑点。
- 将 MCP adapter 视为宿主配置，绝不视为随附的服务器实现。
- 将锁文件声明的外部 Skill 快照视为由更新器拥有、固定版本、只读的插件能力。其来源、选定内容、
  许可证和完整性记录继续保存在外部源锁文件及其所属更新器中。
- setup catalog 负责目标选择、生成和交付路由，以及受管配置。其 blueprint 和 template 是生成输入，
  不是目标运行时内容，也不是其他工作流输出的代理。
- setup 控制平面负责 setup 机制；规范目标输入或生成的目标内容负责目标特定政策。
- 只通过能力所声明的直接宿主或 setup 管理路径进行交付；生成的 adapter 不授予交付权限，仅限 setup
  的 adapter 只能通过 catalog 管理的 setup 到达目标。

## 目标安装所有权

- 在公开 setup prompt、template、manifest、script 和文档中，始终保留 `.agents/` 作为目标安装
  根目录。
- 将目标拥有的 Rule、Skill、Agent 源文件和类型化能力配置视为规范项目输入。Setup 只能管理
  catalog 选定的公共资产、已声明的生成输出、wrapper、已配置的外部 Skill 安装和已渲染的结构化
  字段；它必须保留规范输入、无关的结构化字段、同级条目和 secret 值。
- 将 `.agents/smartkit.lock.json` 作为 setup 管理的文件、目录树、结构化字段和外部源元数据的唯一
  权威。`AGENTS.md` 中受管的 `## Project rules` 区段是唯一的组合例外：替换该区段直至下一个一级
  或二级标题，同时保留所有周边内容，并使该文件不受整文件所有权约束。
- 首次采用时，只认领缺失的目标或确定性摘要与期望内容一致的目标。后续运行只能在验证每项已记录资产
  的摘要后开始规划；根据已配置选择和已验证快照校验外部源元数据。出现无主冲突或已拥有目标被修改
  时，应在写入任何目标前停止运行。
- 只有先前拥有的文件、目录树或字段，或先前拥有目录树的后代，在当前期望状态中不存在时，Setup 才能
  删除它；历史名称不属于 catalog。

## 独占所有者与私有所有者

- `setup-matt-pocock-skills` 独占 Matt 仓库上下文，包括其项目文档和入口文件指针区块。项目 Agent
  setup 工作流可以验证该上下文存在，也可以在保留 `AGENTS.md` 周边内容的前提下读取并原样复现
  指针区块；其 catalog、生成请求、renderer 和所有权 manifest 不得解释、编写、认领或另行交付
  Matt 输出。
- 将推荐工具 Hook 可执行文件私有地保存在 `runtime/recommended-tools/` 下且不提供可发现的
  `SKILL.md`；将其权威声明保存在 `policies/recommended-tools/` 下。MCP 就绪性应与其 Plugin 或
  Project MCP 声明放在一起，并且仅在项目、宿主和本地日期门槛通过后，才通过同一私有运行时进行
  解释。Setup 不得把这些私有运行时或政策资产复制到目标中。
- 将共享生成输入保存在 `setup-assets/` 下，将 setup 控制平面保存在
  `skills/setup-project-agents/` 下。在生产环境中，只有推荐工具 Hook 和维护流水线使用其私有运行时
  和政策；setup 控制平面使用 setup 资产。
- 将 `write-setup-authoring-contracts`、`write-shared-rules-and-skills` 和
  `translate-agent-artifacts` 作为项目私有 Skill 保存在 `.agents/skills/` 下。
  `write-setup-authoring-contracts` 独占 setup blueprint 契约的编写。对于本仓库治理的任何 Rule
  或 Skill，包括共享 SmartKit 候选项，都应直接调用本仓库拥有的
  `skills/write-rules-and-skills/`。不得通过项目私有的
  `.agents/skills/write-shared-rules-and-skills/` 调用或路由编写工作。
  `translate-agent-artifacts` 独占根据最终英文源文件更新必需的简体中文文档镜像。这三个项目私有
  Skill 都不得进入插件 Skill 注册表、根插件 manifest、setup catalog 或目标安装。

## 文档契约

- `README.md` 和 `README.zh-CN.md` 仅限公开安装、配置、使用和故障排除。贡献者工作流、发布与
  生成机制、维护、架构、验证内部细节和实现细节应留给相应的项目或代码所有者。
- 将英文第一方 Rule 和 Skill 视为唯一规范语义来源。项目文档所有者选择哪些文件需要镜像。每个
  位于 `<path>` 的选定源文件映射到 `docs/zh-CN/<path>`。`write-rules-and-skills` 完成所有受影响
  源文件后，宿主 Agent 调用一次 `translate-agent-artifacts`，更新完整的受影响镜像集。
- 将 `docs/zh-CN/` 仅视为文档，绝不能将其作为运行时源、插件入口点、setup 输入或目标安装资产。
- 翻译应保留英文源文件的内容块和 Markdown 结构、字面量、完整含义及强调，同时使用平实自然的
  简体中文。翻译内容和可读性检查仍是普通文档验证；它们不进入英文编写工作流或可执行 Acceptance。
- 将 `.agents/rules/` 视为本仓库的开发政策源。将本仓库 `.agents/` 的内容限制为本地插件配置、
  Rule 和三个已声明的项目私有 Skill；它不是生成的目标项目快照。
- 将 `CONTEXT.md` 和 `CONTEXT-MAP.md` 视为不稳定、非规范的对话词汇表。它们可帮助解释或说明
  直接用户沟通中的语言。唯一的工件例外是 `translate-agent-artifacts`：它可以查阅 `CONTEXT.md`
  作为非规范措辞辅助，但必须将最终英文视为唯一语义来源。Rule、Skill、Setup Authoring Contract、
  代码、测试、schema 和配置不得将上下文文档用作证据、术语权威、验证或 Acceptance 输入或运行时
  依赖。翻译不得利用它们添加、更改、消除歧义或解析英文含义。每个持久术语都需要独立的已接受来源。

## 证据与验收

- 使用机器检查验证结构化配置、schema、标识符、注册与资源关系、生成输出、文件系统影响、状态转换
  和进程退出。自然语言含义和措辞质量需要对整个工件进行 Quality Review 和 Correctness Review，
  并进行任何必需的可执行 Acceptance。散文快照、关键字检查、物理换行、完整标题清单或与外部范例
  相似，都不是语义证据。
- 向 Correctness Reviewer 提供完整的已接受用户决定上下文和每项要保留的义务，包括候选项变更
  编写或审查标准的情况。在这种情况下使用相同的证据基础，且不要让候选项重新定义、缩小或在语义上
  削弱用于判断它的要求。ADR 仍是决策记录，而不是运行时政策。
- 实质要求或候选项变更会使每个可能依赖它的更早 Quality、机器、Correctness 或 Acceptance 结果
  失效。返回最早失效的已通过阶段；只有变更不可能影响证据所证明的内容时才保留证据。

## 当前契约

- 只实现、记录、测试和验证当前由 SmartKit 拥有的契约。删除路径、标识符、schema、命令、配置字段
  或行为时，应在同一变更中删除其实现、文档、测试和处理逻辑。
- 已废止的 SmartKit 所有契约不提供别名、弃用分支、迁移、shim、fallback、双读或双写行为，也不
  提供版本转换。旧输入不受支持，可以无法通过当前验证；测试和文档不得将它们保留为可执行或规范
  表面。不要为了执行此政策而改写更新器拥有的外部快照；其上游所有者仍具有权威性。
- 将所有权检查、数据完整性检查、事务回滚和安全离线行为视为当前正确性要求，而不是兼容性机制。

## 分发与依赖方向

- Rule 可以命名或调用 Skill。Skill 或 Setup Authoring Contract 可以要求适用的项目或仓库政策来
  处理受治理事项，但必须按关注点发现该政策，不得命名、链接或假定特定 Rule ID、标题、路径或编号。
  `setup-project-agents` 及其拥有的实现是唯一例外，仅限发现、生成、保留和验证已声明的 Rule 目标。
- 分发是单向的：目标变更没有反向路径进入插件运行时资产、规范源或文档。
- 将推荐工具运行时的生产依赖限制为其权威政策声明、Plugin MCP 注册表、可选的目标能力配置和 Python
  标准库。Setup 资产、私有运行时或政策区域以及 Plugin Hook 均不得依赖插件发现或随附的 Skill。
- catalog 管理的外部 Skill 只能通过 setup 进入目标。
- 插件 manifest 只暴露已声明的公共表面。
