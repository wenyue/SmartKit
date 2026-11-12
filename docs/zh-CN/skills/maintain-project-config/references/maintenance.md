# 项目配置维护

本参考为管理项目配置的调用方提供共享维护约定与命令接口。从已加载的 Skill 安装解析 `<plugin-root>`，将业务项目解析为 `<target-root>`，以 `<plugin-root>/skills/maintain-project-config/scripts/maintain.py` 作为 `<maintain>`。资源必须来自同一套受支持的插件发行；命令或必需资源不可用时，依赖它们的工作保持未完成。阅读本参考并使用受支持命令，不会调用仅限用户调用的维护 Skill。

```text
python "<maintain>" --help
```

命令帮助负责参数和输出细节。`<plugin-root>/setup-assets/catalog/project-config.schema.json` 中的项目 schema 负责受支持的项目声明。调用方确定其请求的操作和前置条件。维护负责绑定、快照、应用、有意执行的本地同步和配置仓库发布。恢复快照不能证明新 checkout 已成功初始化。

## 选择维护模式

目标的 `.agents/config.json` 记录模式；仓库模式还记录仓库、分支和项目条目。以用户语言一起提供以下三种选择：

| 用户可见模式 | 存储模式 | 配置和 Git 处理 |
| --- | --- | --- |
| 项目共享 | `local` | 规范输入保留在业务项目中，通过其 Git 仓库共享。SmartKit 不添加个人配置排除。 |
| 仅本机 | `local-only` | 规范输入保留在业务项目中，并在本地从业务 Git 排除配置路径。不需要访问配置仓库。 |
| 独立配置仓库 | `repository` | 个人私有 GitHub 仓库存储选中的完整配置备份；目标配置路径在本地从业务 Git 排除。 |

已有 `local` 绑定仍表示项目共享。缺少选择是可读取的旧状态，绑定前需要用户选择。两种本地模式均保留现有编写和生成行为；选择项目共享不会暂存、提交或推送业务项目文件。绑定不包含本机特定的 checkout 路径。

```text
python "<maintain>" inspect --target "<target-root>"
```

检查读取可用的绑定、来源、目标和同步状态，不拉取、不修复排除规则，也不写配置。报告不可用证据，不假定备份完整。仓库模式使用用户持有的持久 checkout，项目条目为 `projects/<entry>/`；它可能保存未发布工作的唯一副本，不能当作可丢弃缓存。各条目的范围相互独立。

## 完整备份文件和目录

条目包含 `manifest.json` 和 `files/`。清单在 `files` 中声明精确的目标相对文件，在 `directories` 中声明递归目录根：

```json
{
  "files": [".agents/config.json", ".cursor/mcp.json", ".codex/config.toml"],
  "directories": [".agents/rules", ".agents/skills"]
}
```

清单仅支持 `files` 和 `directories` 字段。带版本的清单不受支持；报告格式错误并保留来源，不对其进行转换。

`files/` 下的快照按字节保留选定文件，递归保留选定目录。通过 `ruleEntry` 选择 `AGENTS.local.md` 本身不会将该本地文件加入已有清单；需要恢复时，通过既有的备份范围接受流程明确选中它。原生 MCP 和设置文件、项目说明及选中的生成文件均可完整备份。备份不拆分字段，也不使用 `smartkit.lock.json` 决定复制哪些内容。lock 和现有初始化机制各自保留原有行为；恢复整文件快照不需要重新生成 MCP。显式范围可以将 lock 作为普通完整文件纳入；默认范围省略它和运行时状态。

### 接受选中内容的完整范围

选择恢复用户配置所需的路径。接受范围前审阅完整内容：选中文件可能包含凭据和机器路径，而备份不筛除秘密值。凭据值仍应保留在原有凭据设施中，目标本地同步状态不纳入备份。

选中 `.agents/config.json` 时，完整复制其中的绑定和 `setupVersion` 等内容。复制来的初始化标记不能证明当前 checkout 已完成初始化。其仓库绑定必须与选定来源匹配；有差异时解决差异，不静默改写快照字节。

快照支持普通文件和目录。符号链接和命令校验拒绝的路径需要先解决再继续。来源内容不可用时应报告，不当作空备份。

绑定和采纳中重复的 `--file` 参数接受文件或目录。创建条目时没有显式选择，命令会选择已有的默认项目配置路径和目录；发布前检查实际范围和全部选中内容。命令帮助和检查报告提供当前选择。默认范围包括项目入口文件、`.agents/config.json`、原生 MCP／设置文件，以及项目 Rule、Skill 和 Agent 目录；默认列表只是起始范围，不能证明覆盖了每个项目特有的配置。

## 绑定或有意更换来源

仓库绑定或更新前，需要 Git 和 GitHub CLI（`gh`），并以仓库所属的个人账户在对应 github.com 或 GitHub Enterprise 主机上完成认证。该账户必须能访问私有仓库。这些操作会验证仓库并使用经过认证的 Git 访问；工具或权限缺失时，停止依赖仓库的工作并保留已有状态。凭据保留在用户的凭据设施中，不进入绑定。

```text
python "<maintain>" bind --help
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<repository>" --branch "<branch>" --entry "<entry>"
```

本地模式不接受仓库参数或导入选择。仓库模式需要确定用户的个人私有仓库、分支和项目条目；远端默认分支是可选项，不能自行假定。创建仓库需要用户指定身份和名称，并显式传入 `--create-repository`。github.com 使用 `owner/repository`，GitHub Enterprise 使用不含凭据的 HTTPS URL，例如 `https://github.example/owner/repository.git`。主机名决定认证，并区分不同主机上同名仓库的持久 checkout。

对于新条目，绑定前检查现有目标内容并接受备份范围。绑定成功后，目标记录选定维护方式，初始的 `.agents/config.json` 整文件备份包含绑定后的文档。如果保存来源内容后绑定失败，保留这些来源工作，并与目标结果分开报告。例如，使用 `--file ".cursor/mcp.json" --file ".agents/rules"` 选择完整 MCP 配置和项目 Rule。导入选择仅用于新条目；更新和检查后，使用采纳来刷新已有条目。

仅为有意切换模式或来源使用 `--replace-binding`。检查旧来源、目标和拟用来源，保留未发布工作，并在重试被拒绝的切换前确定预期内容。常规升级保留绑定。切换既不删除旧来源，也不授权丢弃待处理工作；绑定命令负责移除过时的本地同步状态。

如果内嵌项目拥有 Git 根目录的 Wiki，有意切换时先验证 Wiki 与旧备份一致，再移除与旧绑定匹配的同步记录。保留 Wiki 文件和两个来源条目。切换到项目共享模式时，清除该项目管理的根目录 Wiki 排除规则。后续 Wiki 维护使用新绑定。

## 显式恢复或启动时同步

显式恢复时，仅当匹配的本地记录表明此 checkout 已成功恢复，才复用已有仓库绑定。否则，在绑定选定来源前，询问用户配置仓库的 Git 地址、分支和已有项目条目。复制了绑定但没有本地成功记录时，同样需要这项选择。不从业务远端、已知仓库或其他本地 checkout 推断来源。检查具体目标差异，并在每次有差异的应用前通过下文路径取得用户选择。

仅恢复的操作通过绑定、更新、检查和应用，恢复选定备份的精确字节，再检查本地前置条件和 Git 处理。它们不编写来源、不生成配置、不调用完整初始化，也不发布来源变更。分别报告恢复内容和缺失的本地工具、凭据或服务；这些条件缺失不授权重写快照。

启动自动同步是显式的本地偏好，默认为关闭。会话启动 hook 只为已绑定仓库、具有匹配的成功记录且已启用自动同步的 checkout 提供同步指导。更新备份，运行不带 `--adopt-local` 的 `reconcile`，再按[差异判定结果](#adopt-accepted-target-changes)处理。启动同步可直接恢复已确认仅配置仓库发生的更新，无需再次询问。保存本地改动需要用户接受本次上传；自动同步本身不授予上传权限。未绑定或已禁用的 checkout 保持静默。报告已启用状态中无效的绑定或记录。关闭自动同步时仍可显式手动恢复。其他就绪发现仍遵循各自的同意和初始化要求。

## 编写或恢复前更新

```text
python "<maintain>" update --target "<target-root>"
```

仓库支持验证个人私有仓库及持久 checkout 身份，再拉取并对受支持状态安全快进。更新前保留已暂存、未暂存、未跟踪和未发布工作。脏工作区、分叉或未完成状态可能被拒绝；处理报告的问题，不使用 reset、自动 stash、强推或改写历史。认证、拉取或更新失败时，保留已有状态并在应用前停止；不能用过时 checkout 代替成功更新。

更新成功后，编辑或采纳已接受的来源范围。初始导入、编写或有意进行的本地生成可能在同次操作中留下已接受来源变更；在验证、应用和发布期间保留其归属，无需在这些步骤之间再次要求干净 checkout 更新。

## 应用权威备份

```text
python "<maintain>" apply --help
python "<maintain>" inspect --target "<target-root>"
python "<maintain>" apply --target "<target-root>"
```

仓库模式下，验证已接受的来源并检查对目标的影响。存在差异时，应用前需要用户对整次同步作出选择；已启用的启动同步能够确认仅配置仓库发生更新时除外。询问用户前，展示变更路径和内容差异，涵盖新增、删除和二进制文件差异。已授权的 Setup 或维护任务要求保留更新的本地配置时，在应用前[确认并采纳](#adopt-accepted-target-changes)已接受的本地更新。等待用户选择期间，保留整个目标。

### 应用用户对整次同步的选择 <a id="apply-the-users-whole-synchronization-choice"></a>

**将本地保存到配置仓库** 表示接受已审查的本地内容和备份范围，包括对来源文件的覆盖或删除。遵循下文的采纳流程，验证已接受的结果，执行应用以记录一致状态，再仅发布本次操作精确且已验证的范围。接受保存即包含该范围的提交和正常推送；除非用户要求只保留本地结果或禁止发布，否则无需再次确认发布。

**暂时保留本地** 会跳过本次同步，保留目标内容和原有同步记录。报告同步已跳过及仍存在的差异。独立工作可以继续；需要来源与目标收敛的工作保持待处理。这项选择既不采纳本地内容，也不将其发布到配置库。后续同步仍会检查这些差异。

**使用配置库** 会应用完整的已审查恢复结果，通过 `--accept-existing <inspect-fingerprint>` 传入精确检查过的状态。检查后任一侧发生变化，都应重新检查、展示新差异并取得新的选择；过期令牌会被拒绝。不依赖逐文件历史或三方冲突处理。来源与目标已经一致时，应用不需要差异接受令牌。

### 记录已验证的一致状态和启动偏好 <a id="record-verified-agreement-and-the-startup-preference"></a>

仓库模式将成功达成的一致状态记录在目标本地的 `.agents/project-config-sync.json` 中，包含 `binding`、`source`、`sourceFingerprint`、`sourceManifest`、`appliedPaths` 和 `automatic`，不含格式版本。来源指纹覆盖所选条目的范围及实际快照内容，包括已接受但未发布的编辑，而非整个仓库提交。`sourceManifest` 记录该范围，使差异判定能在配置仓库变化后核验完整的本地基线。缺少此字段的旧记录仍可读取，但无法证明只有配置仓库发生变化；下一次成功应用时会记录范围。其他项目的变更不会使本记录失效。带版本的记录不受支持；报告格式错误并保留状态，不进行迁移。

只有保存的来源指纹匹配且选中的本地内容也一致，命令才能跳过内容写入。`appliedPaths` 用于提出删除备份已移除、此前应用过的文件。应用成功后记录新指纹、范围和已应用路径。拒绝或失败时保留旧记录。

通过受支持的应用路径显式设置当前 checkout 后续启动偏好，需要时按上述要求取得差异接受：

```text
python "<maintain>" apply --target "<target-root>" --auto-sync on
python "<maintain>" apply --target "<target-root>" --auto-sync off
```

恢复复制选定快照并验证一致，不生成原生输出，也不能证明完整初始化成功。单独显示仍需进行的初始化或迁移，并等待用户显式调用其所属 Skill。操作失败时，保留已保存进度，分别报告来源、目标和同步记录的结果。

## 采纳已接受的目标改动 <a id="adopt-accepted-target-changes"></a>

更新后用 `reconcile` 对照上次成功的本地同步记录判断差异类型。只有完整本地内容与记录的基线范围一致，且来源新选中的路径不会覆盖有差异的本地内容时，才能确认仅配置仓库发生更新。配置仓库指纹发生变化，本身不能证明本地配置落后。仅本地变化，是指配置仓库快照仍与同步记录一致；本地新增、编辑和删除都算变化。双方都变，或基线无法确定同步方向时，即使配置仓库看起来包含本地改动，也要取得用户选择。

启动时发现仅本地变化，应展示差异，询问是将这些改动保存到配置仓库，还是暂时保留本地。用户接受保存后，或既有的配置写入任务已经涵盖这次保存时，传入 `--adopt-local` 生成计划。按备份范围约定审查计划范围和所选文件的完整内容。将已接受的 `planned` JSON 保存在私有任务状态中，再通过 `--accept-plan` 传入其 `plan_fingerprint` 执行。

```text
python "<maintain>" reconcile --target "<target-root>"
python "<maintain>" reconcile --target "<target-root>" --adopt-local
python "<maintain>" reconcile --target "<target-root>" --adopt-local --accept-plan "<plan-fingerprint>"
```

| 结果 | 下一步 |
| --- | --- |
| `in-sync` | 本次操作需要记录一致状态时，应用已一致的快照。 |
| `source-updated` | 在已启用的启动同步中，使用精确的检查指纹应用，无需再次询问。显式手动恢复仍需要用户对差异作出选择。 |
| `adopted` | 执行应用以记录一致状态。保留 `source_changes`，供已授权的发布使用。 |
| `planned` | 审查确切的保存计划，并在执行前保留其 JSON。 |
| `needs-choice` | `local_updates_only` 为真时，询问是保存本地改动，还是暂时保留本地。否则展示差异，提供整次同步的选择：保存本地、使用配置仓库，或暂时保留本地。 |

已启用的启动同步能够确认仅配置仓库发生更新时，记录的偏好已接受该同步方向；将应用绑定到精确检查过的内容：

```text
python "<maintain>" apply --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

如果计划改变，或其仅本地变化的证据不再成立，检查新的状态并重新确认处理方式。`source_changes` 的键是确切的仓库相对路径。值是预期的内容摘要，删除时为 `null`。

双方都变或方向不明时，用户显式选择保存本地内容，才允许对该选择涵盖的确切差异文件使用带保护的 `adopt`。取得选择前，审查对来源的覆盖和删除。如果指纹变化导致命令拒绝，重新检查并确认处理方式。执行应用以记录一致状态，然后将 `source_changes` 纳入发布范围。

```text
python "<maintain>" adopt --target "<target-root>" --accept-existing "<inspect-fingerprint>" --file ".agents/rules/project.md"
```

进行其他有意采纳时，检查当前来源和目标，确定预期结果，再保存已接受的范围：

```text
python "<maintain>" adopt --help
python "<maintain>" adopt --target "<target-root>" --file ".cursor/mcp.json" --file ".agents/rules"
python "<maintain>" adopt --target "<target-root>" --all
```

用可重复的 `--file` 指定确切的路径，或用 `--all` 刷新清单中已声明的文件和目录。使用 `--all` 时，从备份和清单中移除缺失的已声明文件，并保留目录声明。保留未选中的内容和无关的来源工作。发布前验证、应用并检查已接受的结果。

## 仅在需要时生成本地配置

既有本地同步仍可用于有意修改规范输入。它与整文件备份恢复分开处理，保留原有所有权及冲突保护：

```text
python "<maintain>" sync-project --help
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

此路径生成已有发现入口及原生 Agent、MCP 和设置映射，不拉取、不编写蓝图，也不执行完整迁移。检查模式不写入：退出 0 表示一致，退出 1 表示差异，退出 2 表示失败。生成若有意改变了选中的已备份文件，将这些接受的结果采纳回来源，并在发布前重新确认来源与目标一致。两种本地模式在编辑项目规范输入后直接使用此路径。

schema 的 `ruleEntry` 选择 `AGENTS.md`（默认）或 `AGENTS.local.md` 作为生成 `Project rules` 章节的入口。两种本地同步路径管理所选文件中的该章节，保留其余字节和未选择的入口。修改选择不会移动或删除现有章节，也不会删除原入口。

仅需更新该生成章节时，使用不要求完整初始化所有权的更窄路径：

```text
python "<maintain>" sync-project-rules --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

遵守前提和所有权失败。维护不自动调用完整初始化，也不通过其他工作流或回调间接调用。保留已保存的来源和目标工作，报告未满足前提；用户完成所属初始化工作流后，重新检查当前状态。

## 将个人配置排除在业务 Git 之外

仅本机和仓库模式为配置范围、本地同步状态和已知生成输出维护目标本地的 Git 排除。仅本机模式还将所选 Rule 入口纳入这些排除。维护命令在绑定、应用和有意执行本地同步后管理排除。排除规则放在目标 worktree 的 Git `info/exclude` 中，由 Git 解析，并在业务仓库内正确锚定，包括 monorepo 内嵌项目。保留共享 `.gitignore` 和无关排除规则。

排除仅影响未跟踪路径。保留并报告业务 Git 已跟踪的配置；选择个人模式不授权自动取消跟踪或改写历史。没有 Git worktree 时报告不适用。切换到项目共享仅移除经过验证、由 SmartKit 管理的当前目标规则块；保留并报告其他匹配排除。即使配置已保存，排除更新失败仍意味着模式落实未完成。

检查有关目标相对路径，不根据空的已跟踪路径报告推断排除情况：

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

第一条命令报告已跟踪路径；第二条指出未跟踪路径所匹配的忽略规则，退出 1 表示无匹配。检查和 `--check` 不修复 Git 状态。

## 使用项目绑定维护 OpenWiki

OpenWiki 继承所选项目的现有绑定。通过 `--target` 传入该项目，命令会找到 Wiki 文件所在的 Git 根目录。拥有独立绑定的 Git 根目录负责自己的 Wiki。有所有权冲突时，按该绑定处理。在仓库模式下，内嵌项目的 Wiki 备份存放在 `projects/<entry>/wiki/`，同步记录存放在 Git 根目录的 `.agents/openwiki-config-sync.json`。如果项目就在 Git 根目录，准备阶段使用普通项目快照。

新运行开始前，确认 Git 根目录的写入已获授权。仓库模式下，使用该绑定仍有效的刷新证据，或执行普通的 `update` 命令，然后准备 Wiki。`ready` 表示继承的 Git 处理方式已落实，并报告已应用的备份改动和已跟踪路径。结果为 `needs-choice` 时，按[整次同步选择](#apply-the-users-whole-synchronization-choice)处理。如果用户接受恢复，传入精确指纹。准备或保存 Wiki 备份前，先在所属工作树中续跑仍在进行的 Wiki 任务。

```text
python "<maintain>" wiki prepare --target "<target-root>"
python "<maintain>" wiki prepare --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

各模式下均由 Wiki 所有者验证完成结果。仓库模式下，`wiki save` 会为整个 `openwiki/` 目录和存在的 `.openwikiignore` 制定备份计划。如果 Git 根目录的 `AGENTS.md` 或现有 `CLAUDE.md` 发生改动且已接受整文件备份，对每个选中的文件添加一次 `--file`。审查确切选择及其内容，保留计划 JSON，再使用 `--accept-plan` 执行同一选择。保存命令会验证一致性并写入同步记录。

```text
python "<maintain>" wiki save --target "<target-root>" > "<wiki-save-plan.json>"
python "<maintain>" wiki save --target "<target-root>" --accept-plan "<plan-fingerprint>"
```

如果备份已写入但保存流程中断，按保留的计划核验已保存的来源。需要记录一致状态时，使用 `wiki prepare`，然后按原先接受的范围恢复发布。即使新计划为空，此前已确认归属本次操作的来源改动或保留提交仍待处理。对已确定的范围遵循[发布约定](#publish-an-exact-verified-scope)。

```text
python "<maintain>" wiki publish --target "<target-root>" --plan "<wiki-save-plan.json>" --message "Back up OpenWiki"
```

## 发布经过验证的精确范围 <a id="publish-an-exact-verified-scope"></a>

仓库模式下，已授权的配置写入操作在所需本地工作成功后包含一次精确范围提交和普通推送。除非用户要求本地结果或禁止发布，否则无需再单独确认发布。此默认不授权检查、普通业务项目编辑、其他条目或任何仅恢复操作的发布，无论恢复是手动还是自动；也不授权发版、强推或改写历史。两种本地模式均不向配置仓库发布。

发布前确定本次操作已接受的来源变更和待推送提交，包括已接受的初始导入，以及归属经过验证、由本次操作保留的工作。尚无提交的分支也可能有新来源文件待发布。收集精确仓库相对文件，包括清单变化和删除；整个目录、无关暂存项和未经接受的已有内容不属于提交范围。操作既不拥有待处理来源变更，也没有保留的已验证提交时，无需创建空提交或发布更早的工作。

已接受的采纳结果涵盖完整发布范围时，通过 `--plan` 传入其 JSON。命令会验证每个路径及其内容摘要。如果发布范围由调用方另行汇总，对每个已接受的文件使用一次 `--path`。`publish` 和 `wiki publish` 都支持这两种方式。

在来源验证、已接受的应用、必要且有意执行的本地生成及全部适用检查成功后发布。确认来源与目标一致。调用方在使用此发布路径前，确认其他前置条件均已完成。整文件恢复没有自动生成器前提。显式要求本地结果时保留已接受来源工作，并说明发布被有意延后。

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --plan "<adoption-result.json>" --message "Update project configuration"
```

提交 hook 正常执行。重新验证 hook 改变的内容，将其恢复到目标，并在发布前重复相关检查。发布被拒绝时保留提交和诊断。在本次已接受的范围内处理路径不明确、待推送范围未验证或存在额外待推送提交的情况。

### 恢复失败或结果不确定的发布

推送失败或结果不确定时，可能仍有有效本地提交和已应用目标。重试保留的已验证提交前，先检查实际本地和远端结果：

```text
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

确认来源和已应用证据仍然一致。根据操作使用 `publish` 或 `wiki publish`，已有接受的计划证据时复用 `--plan`。远端推进或分叉时保留本地提交，解决分支状态后再受保护地重试。验证预期提交可从选定远端分支到达。

### 报告已确认的结果

分别报告来源编辑和验证、目标应用、任何有意执行的生成、排除与已跟踪配置、未满足前提和远端发布。仓库模式完成要求本地工作成功，并验证预期范围已发布；显式要求本地结果，或没有本次操作拥有的来源变化／提交需要发布时例外。推送失败保留已保存来源、保留提交、已应用目标和已完成的本地工作。报告本地成功及远端同步未完成。更广泛的完成结果由调用方负责。
