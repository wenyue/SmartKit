---
name: setup-project-agents
description: 初始化或升级项目 Agent 配置，选择其维护来源，并准备受支持的开发工具。
disable-model-invocation: true
---

# 设置项目 Agents

初始化或升级项目的 Agent 配置，同时保留仍然有用的决定。完整 setup 会评估每份已声明蓝图和每个项目自定义 Agent，即使指纹一致，并为本地目标准备 CodeGraph。有效工件可以逐字节保留。本 Skill 必须由用户明确调用。

## 1. 选择请求的操作

将本目录解析为 `<skill-root>`，将相邻的维护入口 `<skill-root>/../maintain-project-config/scripts/maintain.py` 解析为 `<maintain>`，将仓库解析为 `<target-root>`。在获取来源或改变项目输入前，选择执行路径：

| 意图 | 路径 |
| --- | --- |
| 首次 setup | 在第 2 步确定项目情况并选择维护来源，然后完成第 3 至第 8 步。 |
| 升级、对现有项目未限定范围的 setup/更新，或必要的项目迁移 | 在第 2 步保留现有基线和维护选择，然后完成第 3 至第 8 步。 |
| 明确仅同步本地 Rule/Skill 发现及已声明的 Agent/MCP 映射 | 下文的本地同步。 |
| 明确仅处理 `AGENTS.md` 的 Rule 索引 | 本地同步中的 Rule 索引分支。 |

执行任一路径前，阅读 [所有权](references/ownership.md)，了解权威输入、发现、加载含义和替换边界。目录和 schema 负责支持的输入形式；脚本负责验证与应用；Setup 负责项目决策、编写协调及整个集合的一致性。在依赖范围选择的效果发生前，解决重大范围选择。

## 2. 确定项目状态及其配置来源

阅读 [完整会话协议](references/session-protocol.md)，了解效果权限、Matt 上下文、来源选择和恢复；阅读 [项目迁移](references/migrations.md)，了解基线和发布版本特定的义务。阅读 [项目配置维护](../maintain-project-config/references/maintenance.md)，了解来源绑定、私有仓库访问、应用和发布边界。Setup 使用该 Skill 支持的参考文档、命令接口和配置引擎，不调用这个仅限用户调用的维护 Skill。先运行两项只读检查；其帮助说明报告的检查和退出码：

```text
python "<skill-root>/scripts/workflow.py" inspect --help
python "<skill-root>/scripts/workflow.py" inspect --target "<target-root>"
python "<maintain>" inspect --target "<target-root>"
```

结合检查结果，以及通过项目文档约定取得的完整项目配置、所有权、既有生成内容和决策记录进行判断。在受影响步骤前解决前置条件错误；setup 检查退出码为 0 时，返回的 `pending_assessment` 仍由 Setup 处理。缺少 Matt 上下文时，遵循协议的重新调用路径。

### 首次 setup

选择 setup 管理的内容前，识别现有项目指令、个人配置和独立所有者。仅缺少维护声明不能说明这是新项目。询问一次用户希望在项目本地维护，还是使用个人私有 GitHub 配置仓库；按共享参考的说明，通过维护命令的 `bind` 路径记录已接受的选择。

采用仓库维护时，确定个人仓库身份、分支和项目条目。连接现有私有仓库；仅在用户指定所有者和名称后，才能创建仓库。不同项目可以使用同一仓库中的不同条目。只导入已识别且已接受的现有个人文件；保留业务项目中已跟踪的内容和独立所有者的配置。在另一台机器上连接现有条目时，首次应用前必须比较其来源和当前目标。

维护选择已记录、选定来源可用，且初始导入或冲突已有接受的解决方案后，继续执行。只有共用的完整 setup 结束流程成功，首次 setup 才算完成；仅建立绑定还不够。

### 升级现有项目

确定上次成功的 setup 版本，收集每项适用迁移，不猜测缺失历史。已初始化但没有成功版本的项目保留其所有权记录和内容，由完整 setup 建立基线。如果检查报告 `selection_required`，询问一次维护选择并保存；否则保留已记录的模式、仓库、分支和条目。只有用户请求变更时，才切换模式或条目，且必须先比较并保留旧来源和目标中的工作。

在仓库模式下，编辑持久源检出前先更新它。如果绑定或先前维护已经刷新该检出，并产生了已接受的待处理改动，就核验并保留这些证据，基于这些改动继续，不再运行要求干净检出的更新。结合业务项目及其源条目读取相关迁移决策，先在该条目中修正可移植配置。冻结会话前，通过维护命令刷新已应用的目标。只有全部选定迁移和共用的完整 setup 结束流程成功，升级才算完成；来源发布有独立结果。

### 为完整运行准备已接受的输入

按照“所有权”指明的 schema 协调配置，保留无关工作。在本地模式下，编辑项目的权威输入。在仓库模式下，使用检查报告的源路径，以业务项目证据为依据，并在 `start` 前应用已接受的源改动。绑定和本地状态仍由目标中的相应所有者负责。共享参考说明了初始冲突接受与采纳后续目标编辑的区别。

预检迁移来自已加载插件来源；第 4 步会确认会话选定的 SmartKit 来源。项目状态、来源选择、输入决策、迁移要求和前置条件缺口均已明确后，继续执行。

## 3. 发现并协调每个项目自定义 Agent

使用预检清单；项目输入改变后刷新：

```text
python "<skill-root>/scripts/adopt_project_agents.py" inspect --target "<target-root>"
```

自动发现覆盖四个受支持的原生 Agent 目录，以及项目 `.codex/config.toml` 中角色的 `config_file` 引用，后者相对于声明它的配置文件解析。清单对匹配的发现去重，报告身份冲突、不安全路径和不可用文件；绝不读取目标之外的内容。未使用独立配置文件的 Codex 角色列在 `role_declarations` 中：评估其声明和继承设置，无需将其转换为使用独立配置文件的形式。显式无效引用仍算问题。手动检查其他已启用的宿主发现机制；用户配置和不受支持的布局不在自动覆盖范围内。不受支持的布局需要由宿主所有者修正，或进行保留源内容的位置调整。原生角色语义见 [Codex 配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)。

读取每个自定义 Agent 的完整提示词和配置，包括未声明的 Agents；按照“所有权”区分已记录的插件默认 Agents。根据职责和引用匹配身份，保留工具、权限、沙箱边界、宿主元数据和特意继承的设置。

每次完整运行都依据当前官方提供方、宿主资料及可取得的模型证据，评估模型和思考设置。选择当前可用、适合同一职责且成本与延迟定位相近的后继模型，并采用兼容的思考设置。跨模型档位、显著增加成本或改变项目明确选择前，先询问用户。无法验证可用性时保留现有值，报告评估未完成，并继续独立工作。证据表明模型不可用时，暂停该 Agent，直到确定受支持的选择；仅有新版本发布不要求迁移。

需要保留完整原生文档时，使用“所有权”中的 `native_source` 路径。清单中标有 `requires_relocation` 的条目需要先进行明确的、保留源内容的位置调整，再纳管：处理实际生效的宿主引用，并确保提示词和配置的相对引用在安装位置仍然有效。仅复制文件不会让宿主改用新位置。

首次纳管时，根据清单捕获的摘要准备完整最终原生内容和清单文件。说明模型变更及其他行为如何保留，然后在任一维护模式下使用受保护的导入：

```text
python "<skill-root>/scripts/adopt_project_agents.py" apply --help
python "<skill-root>/scripts/adopt_project_agents.py" apply --target "<target-root>" --manifest "<adoption-plan.json>"
```

在仓库模式下，受保护的导入先将已接受的权威原生源和可移植 Agent 声明保存到选定源条目，再应用既有的受保护目标事务，并记录已应用来源。清单、摘要和所有权保护仍然必需。如果该事务失败，保留已保存的源工作，单独报告目标恢复情况。

对于已管理的适配文件，编辑其选定的权威源；完整 setup 在现有摘要保护下渲染。转换结构化声明前，解决源文件和设置的所有权。该工具不选择模型，也不证明语义保留。

发生冲突时，列出路径、字段和值、各个选项的影响及需要作出的决定。保留冲突输入，继续独立检查。只有每个自定义 Agent 都有映射并得到交代、报告的问题均已解决，且模型变更、保留和未完成验证已清楚区分，才能进入冻结。遗漏 Agent 或存在未解决冲突都不算完成。

## 4. 准备 CodeGraph 并启动一个冻结会话

目标、当前宿主和输入决策确定后，按照协议确定 CodeGraph 效果权限，并在冻结前准备运行时：

```text
python "<skill-root>/scripts/workflow.py" setup-codegraph --target "<target-root>" --harness "<active-harness>" --approved
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

只有准备操作返回退出码 0、`phase: setup-codegraph` 和 `ready: true` 后，才运行 `start`。保留 `start` 返回的会话、请求及来源、版本和迁移信息。从该来源读取选定的迁移指南；对照已接受的项目与 Agent 决策，验证完整蓝图请求。新发现的输入修正需求遵循协议的取消并重启规则。

只有运行时就绪经过验证、完整请求有效且源特定前置条件均已解决，才能继续。

## 5. 规划完整生成集合

阅读 [生成编写](references/generated-authoring.md)。从冻结来源读取每份请求的蓝图及其更新重点，同时读取完整既有内容和合格项目证据。在生成及保留的 Rules、相关 Skills 和适用全局策略之间，规划职责、覆盖和加载。

对每个请求，指出哪些仍有效、哪些必须改变，以及原因。保留项目义务和影响结果的例外；修正过时事实和实际重复。指纹变化和追求新措辞都不能作为重写理由。每个请求都有有依据的方向、证据及在整个集合计划中的位置后，继续执行。

## 6. 取得并协调完整编写结果

将已确定的共同计划保存到私有会话中、`GENERATED` 之外，包含合格证据引用和所有者依赖状态。使用当前有效会话准备输入：

```text
python "<skill-root>/scripts/workflow.py" writer-inputs --help
python "<skill-root>/scripts/workflow.py" writer-inputs --session "<SESSION>" --plan "<SESSION>/common-plan.md"
```

按照“生成编写”为每个请求调用固定来源的公共 writer，每次处理一个 Candidate，并协调组合结果。输入包提供证据，不是语义交接结果。只有每个请求，包括未变化工件及其支持输出，都取得最终独立的 `COMPLETE`，且整个集合符合计划，才能继续。修正、编写受阻和依赖遵循该引用文档中的登记与取消边界。

## 7. 登记并完成

每份协调后的交接结果只登记一次，列出完整输出。命令帮助提供路径语法：

```text
python "<skill-root>/scripts/workflow.py" register --help
python "<skill-root>/scripts/workflow.py" register --session "<SESSION>" --request-id "<ID>" --output "<PATH>"
python "<skill-root>/scripts/workflow.py" finish --session "<SESSION>"
```

首次尝试 `finish` 前，确认 CodeGraph 就绪；若守护进程因空闲退出，遵循协议的运行时刷新分支。在仓库模式下，finish 先将已接受的生成项目源保存到条目，再应用常规目标计划；任一部分失败时，都要保留来源和目标两侧的证据。只接受协议规定的成功本地 finish 结果，包括清理和最终 setup 版本记录。失败时遵循协议中原始尝试的恢复路径。

## 8. 交付经过验证的结果

评估全部直接项目 Rules 始终加载带来的上下文开销。只有大量策略依赖可识别的条件时，才建议采用原生 `rule-<domain>` Skills；不能仅凭大小就移动无条件策略。

报告配置维护模式和源条目、SmartKit 来源信息、之前和最终的 setup 版本、迁移、启用宿主、改动及保留路径、自定义 Agent/模型决策和外部来源。包含实际配置检查、CodeGraph 安装/索引/运行时结果、上下文评估、未完成验证和恢复证据。

分别报告本地 setup 和远端发布。单独执行 Setup 会保留源改动，供审查和以后发布；它不授权提交或推送。提供已保存的确切源改动和本地结束证据，供另行授权的维护重新评估当前状态并从已有进展继续。后续推送失败不会使成功的本地 `setupVersion` 失效，但远端同步仍未完成。

## 本地同步

使用已加载插件中的 `<maintain>`，同步前阅读其 [项目配置维护](../maintain-project-config/references/maintenance.md) 参考。这些命令使用维护拥有的引擎；setup 工作流中的 `project-config`、`sync-project` 和 `sync-project-rules` 阶段仍是转发至同一所有者的入口。此路径不执行获取、生成、模型评估、蓝图/共享/外部更新或 CodeGraph 准备。“所有权”定义前置条件及保留边界；`clean` 只证明配置收敛。

1. 检查请求的范围：

   ```text
   python "<maintain>" sync-project --target "<target-root>" --check
   ```

   广泛同步需要已有的项目映射所有权，且外部 Skill 声明没有变化。报告完整 setup 依赖，不扩大请求。仅处理 Rule 索引时，使用 `sync-project-rules --check`；完整 setup 之前也可使用。

2. 省略 `--check`，应用获准范围。Rule 索引路径为：

   ```text
   python "<maintain>" sync-project-rules --target "<target-root>" --check
   python "<maintain>" sync-project-rules --target "<target-root>"
   ```

   应用和回滚期间保持独占访问。退出码 0 且 `check: clean` 表示收敛；退出码 1 且 `check: drift` 列出计划改动；退出码 2 表示拒绝或失败。重试前解决报告的原因。

3. 报告操作、结果、改动及保留路径，以及任何拒绝或恢复证据。两条本地路径都不推进 `setupVersion`。
