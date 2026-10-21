---
name: setup-project-agents
description: 初始化或升级项目 Agent 配置，或从配置仓库恢复配置。
disable-model-invocation: true
---

# 设置项目 Agents

选择完整 setup，或恢复已有配置备份。完整 setup 会评估每份已声明蓝图和每个项目自定义 Agent，即使指纹一致，并为本地目标准备 CodeGraph。恢复会复制已接受的备份并检查本机前置条件，不重新生成配置。本 Skill 必须由用户明确调用。

## 1. 选择请求的操作

将本目录解析为 `<skill-root>`，将相邻的维护入口 `<skill-root>/../maintain-project-config/scripts/maintain.py` 解析为 `<maintain>`，将仓库解析为 `<target-root>`。遵循明确的操作请求；否则，在获取来源或改变项目输入前，使用用户的语言呈现以下两种选择：

| 选择 | 结果与路径 |
| --- | --- |
| A. 初始化或升级配置 | 在第 2 步确定或保留维护模式，然后完成第 3 至第 8 步，包括全部必要迁移和整个集合的评估。 |
| B. 从配置仓库恢复 | 执行下文“从配置仓库恢复”，然后结束本次操作。 |

明确仅同步本地 Rule/Skill 发现及已声明 Agent/MCP 映射的请求，执行下文“本地同步”；仅处理 `AGENTS.md` Rule 索引的请求，使用其中更窄的分支。这些既有的限定范围无需选择完整 setup 或恢复。明确要求初始化、升级或迁移时选择 A；未指定操作的调用仍需选择。

执行选定操作前，阅读 [所有权](references/ownership.md)，了解权威输入和替换边界。目录和 schema 负责支持的输入形式；脚本负责验证与应用；Setup 负责操作选择、项目决策、编写协调及整个集合的一致性。新 checkout 需手动调用此 Skill：会话 hook 不发现缺失配置，也不询问是否恢复。配置相关启动处理仅限对有效既有 checkout 绑定明确启用的同步；其他就绪检查保留各自的所有者。

## 从配置仓库恢复

阅读 [项目配置维护](../maintain-project-config/references/maintenance.md)，了解绑定、备份范围、恢复、Git 排除和失败恢复。直接使用其受支持命令，不调用仅限用户调用的维护 Skill。此分支不需要完整会话预检、Matt 上下文、迁移、自定义 Agent 重新评估或生成内容编写。

1. 检查选定 checkout，确定已有备份来源：

   ```text
   python "<maintain>" inspect --target "<target-root>"
   python "<maintain>" bind --help
   ```

   既有 checkout 绑定具有匹配的本地成功同步记录时，复用其仓库地址、分支和条目。没有该记录的复制绑定只是一项待确认的来源提议，不能证明本 checkout 已恢复，也不授予自动同步权限。仅询问缺失信息、来源确认或用户有意请求的来源变更。没有绑定时，由用户提供这些值；不从业务 Git 远端推断，也不扫描已知仓库。绑定前核验选定条目存在，且确实是预期备份；缺少条目时恢复保持未完成，不创建新备份。仅在需要绑定时，使用维护参考中的仓库 `bind` 路径，保留已有目标和来源工作。

2. 更新已绑定来源，再检查实际恢复效果：

   ```text
   python "<maintain>" update --target "<target-root>"
   python "<maintain>" inspect --target "<target-root>"
   ```

   认证、拉取或更新失败时停止应用；保留已有状态并报告原因。比较选定完整文件、目录与目标，包括拟进行的覆盖和删除。替换前取得用户对有差异的已有内容的接受。首次应用时，按照共享约定，通过 `--accept-existing` 传入精确检查指纹；发生任何差异后重新检查。只有另行接受后，才通过维护所有者的采纳路径保留有意进行的目标编辑。

3. 将启动自动同步作为独立的本地偏好：A. 开启；B. 关闭，没有偏好时默认关闭。除非用户要求改变，否则保留已记录选择。说明开启同步会以权威备份覆盖范围内后续本地差异。按已接受偏好应用，需要时添加 `--accept-existing "<inspect-fingerprint>"`：

   ```text
   python "<maintain>" apply --help
   python "<maintain>" apply --target "<target-root>" --auto-sync off
   python "<maintain>" inspect --target "<target-root>"
   ```

   `--auto-sync` 使用已记录或新接受的偏好。按照共享参考的只读 Git 检查，核验来源与目标一致、目标本地同步记录和适用的 Git 排除。依照共享备份约定恢复快照字节；复制的 `setupVersion` 或所有权记录不能证明当前 checkout 已成功完成完整 setup 或运行时已就绪。

4. 使用各自所有者支持的只读检查，核验恢复配置要求的本地工具、凭据和服务。报告缺失或无法核验的前置条件；恢复期间不安装工具、启动服务或重写快照。结束时报告来源、恢复和保留的路径、同步偏好、排除规则、实际前置条件结果，以及任何失败或恢复证据。分别报告配置恢复和本机就绪状态，明确说明未执行完整 setup。此分支不生成配置、不记录新的成功 setup 版本、不提交或发布来源变更；用户请求的初始化或升级属于单独的 A 操作。

## 2. 确定项目状态及其维护模式

阅读 [完整会话协议](references/session-protocol.md)，了解效果权限、Matt 上下文、来源选择和恢复；阅读 [项目迁移](references/migrations.md)，了解基线和发布版本特定的义务。阅读 [项目配置维护](../maintain-project-config/references/maintenance.md)，了解来源绑定、私有仓库访问、应用和发布边界。Setup 使用该 Skill 支持的参考文档、命令接口和配置引擎，不调用这个仅限用户调用的维护 Skill。先运行两项只读检查；其帮助说明报告的检查和退出码：

```text
python "<skill-root>/scripts/workflow.py" inspect --help
python "<skill-root>/scripts/workflow.py" inspect --target "<target-root>"
python "<maintain>" inspect --target "<target-root>"
```

结合检查结果，以及通过项目文档约定取得的完整项目配置、所有权、既有生成内容和决策记录进行判断。在受影响步骤前解决前置条件错误；setup 检查退出码为 0 时，返回的 `pending_assessment` 仍由 Setup 处理。缺少 Matt 上下文时，遵循协议的重新调用路径。

### 首次 setup

选择 setup 管理的内容前，识别现有项目指令、个人配置和独立所有者。仅缺少维护声明不能说明这是新项目。保留已有的记录选择。检查报告 `selection_required` 时，使用用户的语言，一次性呈现以下三种完整选择，询问一次：

| 选择 | 记录的模式 | 用户得到的结果 |
| --- | --- | --- |
| A. 项目共享 | `local` | 配置保留在业务项目中，随其仓库进行版本管理。 |
| B. 仅本机 | `local-only` | 配置保留在业务项目中，并通过本地规则排除在业务 Git 之外；不需要 GitHub 来源。 |
| C. 独立配置仓库 | `repository` | 在个人私有 GitHub 仓库中维护配置，并通过本地规则将目标配置排除在业务 Git 之外。 |

通过维护命令的 `bind` 路径记录已接受的选择。仓库模式下，应说明 setup 默认按共享发布契约，在本地成功完成后提交确切范围的源文件并正常推送，除非用户要求仅保留本地结果。Git 排除行为和已跟踪文件遵循该参考；选择模式本身不改变现有跟踪状态。

采用仓库维护时，确定个人仓库身份、分支和项目条目。连接现有私有仓库；仅在用户指定所有者和名称后，才能创建仓库。不同项目可以使用同一仓库中的不同条目。只导入已识别且已接受的现有个人文件；保留业务项目中已跟踪的内容和独立所有者的配置。在另一台机器上连接现有条目时，首次应用前必须比较其来源和当前目标。

维护选择已记录、选定来源可用，且初始导入或冲突已有接受的解决方案后，继续执行。只有本地结束流程成功，并达到第 8 步要求的发布结果后，首次 setup 才算完成；仅建立绑定还不够。

### 升级现有项目

确定上次成功的 setup 版本，收集每项适用迁移，不猜测缺失历史。已初始化但没有成功版本的项目保留其所有权记录和内容，由完整 setup 建立基线。如果检查报告 `selection_required`，呈现上面相同的三种完整选择，并记录一次回答；否则保留已记录的模式、仓库、分支和条目。已有 `local` 表示项目共享，不是尚未解决的选择。只有用户请求变更时，才切换模式或条目，且必须先比较并保留旧来源和目标中的工作。

在仓库模式下，说明同样的默认发布行为，并在编辑持久源检出前先更新它。如果绑定或先前维护已经刷新该检出，并产生了已接受的待处理改动，就核验并保留这些证据，基于这些改动继续，不再运行要求干净检出的更新。结合业务项目及其源条目读取相关迁移决策，先在该条目中修正配置。冻结会话前，通过维护命令刷新已应用的目标。只有全部选定迁移、本地结束流程成功，并达到第 8 步要求的发布结果后，升级才算完成。

### 为完整运行准备已接受的输入

按照“所有权”指明的 schema 协调配置，保留无关工作。在任一种本地模式下，编辑项目的权威输入。在仓库模式下，使用检查报告的源路径，以业务项目证据为依据，并在 `start` 前应用已接受的源改动。将已接受的初始导入和准备阶段的源改动及其来源证据带入最终发布；尚无首次提交的分支应包含已接受的完整导入，而不只是后续生成的差异。遵循共享参考中整文件备份与目标本地状态的边界。共享参考说明了初始冲突接受与采纳后续目标编辑的区别。

仓库绑定尚未记录启动同步偏好时，提供 A. 开启；B. 关闭，默认关闭。在刷新来源、检查并解决初始冲突后，通过维护命令的 `apply --auto-sync on|off` 路径记录已接受选择。常规 setup 和升级保留已有偏好；仅为建立或有意改变选择使用显式标志。两种本地维护模式都没有仓库同步偏好。

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

首次纳管时，根据清单捕获的摘要准备完整最终原生内容和清单文件。说明模型变更及其他行为如何保留，然后在任何维护模式下使用受保护的导入：

```text
python "<skill-root>/scripts/adopt_project_agents.py" apply --help
python "<skill-root>/scripts/adopt_project_agents.py" apply --target "<target-root>" --manifest "<adoption-plan.json>"
```

在仓库模式下，受保护的导入先将已接受的来源和配置变更保存到选定源条目，再应用既有的受保护目标事务，并记录已应用来源。清单、摘要和所有权保护仍然必需。如果该事务失败，保留已保存的源工作，单独报告目标恢复情况。

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

首次尝试 `finish` 前，确认 CodeGraph 就绪；若守护进程因空闲退出，遵循协议的运行时刷新分支。在仓库模式下，finish 先将已接受的生成项目源保存到条目，再应用常规目标计划；任一部分失败时，都要保留来源和目标两侧的证据。只有取得协议规定的成功本地 finish 结果，包括清理和最终 setup 版本记录，才能继续发布。finish 失败会阻止本次操作的发布，并须遵循原始尝试的恢复路径。

## 8. 发布并交付经过验证的结果

本地结束流程成功后，按照 [发布经过验证的确切范围](../maintain-project-config/references/maintenance.md#publish-an-exact-verified-scope) 完成仓库模式的发布。该契约负责规定已接受范围、必需检查、发布例外、常规推送验证和保留提交的恢复。两种本地维护模式都没有配置仓库推送。直接使用受支持命令，不调用仅限用户调用的维护 Skill：

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/manifest.json" --path "projects/<entry>/files/.agents/rules/example.md" --message "Set up project configuration"
```

将示例路径替换为本次 setup 全程保留的、已接受的完整确切源文件范围；每个文件使用一个 `--path`。对于已验证的保留提交，改用命令的 `--commit` 路径和共享恢复契约。报告仓库模式完成前，先确认远端结果。发布失败时，保留成功的本地 `setupVersion`，并报告本地 setup 成功、远端同步未完成。

评估全部直接项目 Rules 始终加载带来的上下文开销。只有大量策略依赖可识别的条件时，才建议采用原生 `rule-<domain>` Skills；不能仅凭大小就移动无条件策略。

报告配置维护模式和适用时的仓库源条目、SmartKit 来源信息、之前和最终的 setup 版本、迁移、启用宿主、改动及保留路径、自定义 Agent/模型决策和外部来源。包含实际配置检查、Git 排除结果与已跟踪路径、CodeGraph 安装/索引/运行时结果、上下文评估、未完成验证和恢复证据。

分别报告本地 setup 和远端发布，包括已保存的确切源范围、本地结束证据，以及已验证的远端结果或共享契约中适用的发布例外。区分必需发布失败、用户有意要求仅保留本地结果而暂缓发布，以及 setup 既没有归属于它的源改动，也没有待发布的已验证保留提交这几种情况；保留已保存来源和保留提交，供恢复使用。

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
