# 项目配置维护

本 Skill 拥有供 setup 和明确维护共用的配置维护契约及命令接口。从已加载 Skill 的安装位置解析 `<plugin-root>`，并使用 `<plugin-root>/skills/maintain-project-config/scripts/maintain.py` 作为 `<maintain>`。将业务项目解析为 `<target-root>`。这些资源必须来自同一受支持的插件分发包；命令、schema 或资源不可用时，依赖它的操作仍未完成。使用这些资源不等于调用这个仅限用户调用的维护 Skill。

```text
python "<maintain>" --help
```

命令帮助负责参数和输出详情。`<plugin-root>/setup-assets/catalog/project-config.schema.json` 处的项目 schema 负责受支持的声明。维护命令在现有所有权检查下负责来源访问、绑定、应用和本地同步；完整 setup 继续负责初始化、交付、迁移和成功的本地 setup 版本更新。消费这些资源的工作流确定意图、已接受改动、权限和完成条件。

## 确定编写来源

目标的 `.agents/config.json` 记录明确的本地维护选择，或一个仓库、分支和项目条目。缺少选择属于可读取的旧状态：检查会报告需要选择。消费资源的工作流必须在绑定或依赖来源的变更前明确用户选择。绑定不包含机器特定的检出路径。

```text
python "<maintain>" inspect --target "<target-root>"
```

检查是只读操作。利用其源路径、目标差异和保留状态，在选择产生何种效果前确定可用内容。本地模式将权威输入保留在业务项目中。仓库模式使用由维护的仓库支持模块解析的、用户自有的持久检出，以及 `projects/<entry>/` 条目。该检出可能包含未发布工作的唯一副本；失败时保留它，绝不能把它当作一次性会话或工件缓存。

每个条目包含 `manifest.json`、`config.json` 和 `files/`。清单明确选择单个源文件；可移植配置包含 `skills`、`agents`、`mcp` 和 `settings`。条目之间不相互继承。以业务项目证据为依据编写，并在选定条目内解析链接的支持文件；同处一个私有仓库不意味着有权修改另一个项目。

绑定、成功的本地 setup 版本、所有权记录、凭据和运行时状态仍由现有所有者负责。选择源指令、Rules、Skills 及必要支持内容，还有自定义 Agent 源。排除由 setup 管理的已交付插件文件、外部快照、原生适配文件和生成索引。源 `AGENTS.md` 包含生成的 `Project rules` 章节之外的项目指令；本地同步命令渲染该章节。宿主设置仅使用 schema 支持的结构化字段，目前位于 `.codex/config.toml` 和 `.cursor/cli.json`，而非整个宿主配置文件。

## 建立或有意变更绑定

绑定前明确用户的维护选择及已接受的初始导入。命令记录该选择；仅有现成的远端或邻近源文件不能证明用户意图。

绑定仓库或更新之前，必须具备 Git 和 GitHub CLI（`gh`），并且 `gh` 已在选定的 github.com 或 GitHub Enterprise 主机名上认证为仓库所属的个人账户。现有私有仓库必须能被该账户访问；创建仓库遵循下文的显式路径。这些操作使用 `gh` 验证仓库并进行经过认证的 Git 访问。如果工具或所需访问不可用，报告该前置条件，停止依赖仓库的工作，同时保留现有状态。凭据留在用户的凭据设施中，不进入绑定或可移植源。阅读命令帮助：

```text
python "<maintain>" bind --help
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<owner/repository>" --branch "<branch>" --entry "<entry>"
```

仓库模式下，确定用户的个人私有 GitHub 仓库、选定分支和项目条目。远端默认分支是可选项，不能直接假定使用它。其他项目可复用同一仓库，但使用不同条目。创建新仓库需要用户指定身份和名称，并显式使用 `--create-repository` 标志。

github.com 使用 `owner/repository`；GitHub Enterprise 使用完整、不含凭据的 HTTPS 仓库 URL，例如 `https://github.example/owner/repository.git`。URL 中的主机名决定认证目标，并将持久检出与其他主机上的同名仓库分开。现有 `owner/repository` 绑定继续使用 github.com，其身份和检出位置保持不变。

对于新条目，检查现有目标内容，通过向 `bind` 重复传入 `--file` 参数选择已接受的个人源文件。初始导入保留来源信息和独立所有权，不会取得所有邻近文件的所有权。对于现有条目，应用前比较其来源和目标。保留业务项目中已经跟踪的文件：本地 Git 排除无法取消其已跟踪状态。对于新应用的个人配置，使用受支持的本地排除行为；接管已跟踪文件之前，说明其所有权决策。

只有有意切换来源时才使用 `--replace-binding`。先比较旧来源、当前目标和拟用来源，保留未发布和未采纳的工作，并确定移动哪些已接受内容。常规升级保留绑定。

## 编辑前更新

```text
python "<maintain>" update --target "<target-root>"
```

仓库支持模块验证个人私有仓库和选定检出的身份，使用经过认证的访问，并在受支持的状态下安全获取和快进。这个持久检出不同于隔离的公开 SmartKit 和外部 Skill 快照。工具缺失、认证不可用或仓库无法验证时，停止依赖仓库的工作。

更新前检查并保留已有的已暂存、未暂存、未跟踪和未发布工作。存在未完成操作、检出不干净或历史分叉时，命令可能拒绝，而不是自动协调。解决报告的问题，不丢弃工作，也不把它暗中纳入本次请求。拒绝不授予重置、强制推送、自动 stash 或改写历史的权限。更新后，在已接受范围内编辑选定源文件和可移植声明；Rules 和 Skills 使用适用的公共编写工作流。初始导入、编写、受保护的 Agent 纳管和 setup 生成输出，都可能在同一操作中留下已接受的待处理源改动。将其证据直接带入验证、应用和发布；这些步骤之间无需再次运行要求干净检出的更新。

## 应用已接受的来源并保护目标编辑

```text
python "<maintain>" apply --help
python "<maintain>" apply --target "<target-root>"
```

应用前审查源改动和检查报告的目标差异。通过所属检查验证可移植声明和完整源文件。应用操作写入权威输入，同时保留绑定和本地状态，并尊重独立所有者的表面。`apply` 本身不渲染原生适配文件；随后执行下文的本地同步路径。来源应用和本地同步不能证明完整 setup 成功。

首次应用可能遇到既有目标内容，而没有上次已应用来源的记录。只有接受了检查所得的确切差异后，此次应用才可使用 `--accept-existing <inspect-fingerprint>`。指纹将接受范围限定在已检查状态，不授权后续漂移。后续目标修改需要明确采纳或由所有者批准的其他解决方案，不能复用初始冲突接受。

目标的 `.agents/project-config-state.json` 记录应用了哪些来源，供以后比较。解释差异时，比较上次应用的内容、当前来源和当前目标。保留冲突双方。这份应用记录提供证据，不增加对所有权记录、生成章节或已交付资产的权限。

## 同步已建立的本地配置

权威输入改变后，使用维护命令渲染本地发现结果以及原生 Agent、MCP 和 settings 映射：

```text
python "<maintain>" sync-project --help
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

此路径不获取来源、不编写蓝图，也不执行完整迁移。它使用已建立的所有权记录，拒绝需要完整 setup 的变更。检查模式报告漂移而不写入：退出码 0 表示干净，1 表示漂移，2 表示检查失败。本地模式在编辑项目权威输入后也使用同一路径。

只有 `AGENTS.md` 中生成的 `Project rules` 章节需要更新时，使用范围更窄的路径；它不要求完整 setup 所有权：

```text
python "<maintain>" sync-project-rules --help
python "<maintain>" sync-project-rules --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

遵守报告的前置条件或所有权冲突。如果需要完整 setup 或迁移，保留已保存的源和目标进度，报告仍未完成的部分，并等待用户明确调用所属 Skill。维护既不自动调用完整 setup，也不通过其他工作流或回调调用它。前置条件满足后，恢复依赖它的工作之前，重新检查源和目标状态。

## 采纳选定的目标改动

```text
python "<maintain>" adopt --help
python "<maintain>" adopt --target "<target-root>" --file ".agents/rules/example.md" --field settings
```

采纳操作要求用户明确选择要带回来源的目标编辑。检查上次应用的内容、当前来源和当前目标，说明重叠部分，并通过重复的 `--file` 或 `--field` 参数仅选择已接受文件或可移植字段。示例选择一份 Rule 和可移植 settings 字段；将这些选择替换为实际接受的范围。保留所有未选中的目标内容及其他源工作。采纳后，在发布前通过常规路径完成验证、应用和核验。

## 发布经过验证的确切范围

只有明确的维护并同步或采纳请求，才包含限定范围的提交和常规推送。单独执行 Setup 或普通项目编辑会使发布保持待处理。收集本次请求改动的确切源文件，使用仓库相对路径，适用时包括改动的清单或可移植配置；整个目录和无关条目的改动都不是提交范围。

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.agents/rules/example.md" --message "Update project configuration"
```

使用重复的 `--path` 参数提供完整已接受范围。发布前验证来源和已应用目标一致，且本地同步检查干净。提交 hook 照常运行：hook 改动的源内容必须重新验证，并按需重新应用和同步后才能发布。保留原有已暂存和未选中的工作；选定路径存在歧义，或待推送提交的范围未经验证时，必须解决，不能扩大提交范围。

发布失败可能留下有效的本地提交和已应用目标。先检查实际结果。确认来源和已应用证据仍然一致后，使用命令的 `--commit` 路径重试保留的已验证提交：

```text
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

远端前进或分叉时，必须保留本地提交，解决分支状态后再进行受保护重试。常规发布必须确认预期提交可从选定远端分支到达；仅有看似成功的推送消息还不够。

分别报告来源编辑和验证、目标应用和本地同步、未满足的前置条件，以及远端发布。仓库模式维护只有在所需目标检查和远端确认成功后才算完成；本地模式没有源仓库发布步骤。`setupVersion` 仅在本地完整 setup 成功后改变；维护和发布保留该值。
