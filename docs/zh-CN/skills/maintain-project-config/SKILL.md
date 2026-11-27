---
name: maintain-project-config
description: 维护项目 Agent 配置。适用于检查或更改维护绑定、编辑和验证本地配置、保存或恢复备份、运行已启用的启动同步，以及处理 Setup 或 OpenWiki 请求的配置操作。
---

# 维护项目配置

按用户或调用流程授予的范围维护业务项目的 Agent 配置。检查完成后报告发现。编辑验证后，可以留在业务项目中，也可以继续已获授权的备份。恢复以已接受的文件就位为止。完整 Setup 决定配置操作及其顺序，包括自己的源端编写流程。

将 `<maintain>` 解析为已加载插件中的 `skills/maintain-project-config/scripts/maintain.py`，将 `<target-root>` 指向业务项目。通过 `python "<maintain>" --help` 查询命令选项，通过同一插件的 `setup-assets/catalog/project-config.schema.json` 查询项目声明。写入期间须保持对源和目标的独占访问。资源缺失时报告缺口，依赖它的事项仍未完成。编辑、恢复和发布都需要相应的授权。

从用户请求的操作开始。

- [检查或选择绑定](#inspect-or-choose-a-binding)，或[编辑、渲染或检查本地配置](#edit-and-verify-in-the-project)。
- [保存已验证的配置](#save-verified-configuration)，或[发布已接受的范围或重试已验证的提交](#publish-or-retry-the-verified-scope)。
- [恢复明确选定的备份](#restore-an-explicitly-chosen-backup)，或[执行已启用的启动同步](#synchronize-on-enabled-startup)。
- [准备或保存 Git 根目录的 OpenWiki](#prepare-and-save-the-git-root-openwiki)。

## 检查或选择绑定 <a id="inspect-or-choose-a-binding"></a>

用本地只读证据检查项目。检查阶段只使用本地可用内容。复用有效绑定。项目尚未绑定且需要选择模式时，用用户的语言一并呈现三种模式。在已有配置上初始化之前，请用户决定是否替换。

```text
python "<maintain>" inspect --target "<target-root>"
```

| 模式 | 存储值 | 配置保存在何处 |
| --- | --- | --- |
| 项目共享 | `local` | 保存在项目中，通过业务 Git 共享。 |
| 仅本机 | `local-only` | 保存在项目中，使用本地 Git 排除。 |
| 独立配置仓库 | `repository` | 保存在项目中并使用本地排除，另备份到私人 GitHub 仓库。 |

绑定选定模式。仓库绑定指定一个个人私有仓库、分支和项目条目，三项都需确认。使用已在对应 GitHub 或 GitHub Enterprise 主机上以个人所有者身份认证的 Git 和 `gh`。github.com 使用 `owner/repository`，其他选定主机使用不含凭据的 HTTPS URL。用 `--create-repository` 创建指定仓库前需要明确授权。`bind` 和 `publish` 会核验所有权和私有性。`update` 成功会核实检出和获取结果，所有权或私有性仍有疑问时另行核实。

```text
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<repository>" --branch "<branch>" --entry "<entry>"
```

运行 `bind` *之前*，先区分连接已有条目和导入新条目。连接时，在刷新后命令实际会使用的状态中核实 `projects/<entry>/manifest.json`。首次克隆时检查选定的远端分支。已有持久源检出时，在该检出中验证条目，包括已经接受的未发布工作。如果条目缺失或未核实，暂停连接，因为同一命令可能导入本地文件。需要新导入时，按下文[首次导入](#initial-import)处理。解决待处理的差异后，仅在切换已获同意时使用 `--replace-binding`。差异也包括嵌套项目所拥有的 Git 根目录 Wiki。保留已有工作和条目。

### 完整内容和 Git 处理 <a id="complete-contents-and-git-treatment"></a>

每个条目的 `manifest.json` 选择相对于目标的 `files` 和递归 `directories`，备份内容存放在 `files/` 下。审阅所选文件和目录的全部内容，留意凭据和机器路径。机密保存在凭据设施中，同步回执留在备份之外。选中的原生设置、MCP 文件和 `.agents/config.json` 按整份文件复制。备份范围由清单选择，锁文件和 `ruleEntry` 各有各的用途。复制的 Setup 标记只反映备份内容，本机就绪和 Setup 结果要另行核实。保留并报告不可读或不受支持的状态，包括带版本字段的清单和回执。

个人模式通过项目限定范围的 Git `info/exclude` 保护配置。切换为项目共享时，只移除受管理的排除块。保留共享忽略文件和已跟踪的配置。即使暂缓同步，也要检查相关路径，报告已跟踪的文件或缺失的排除项。绑定、应用和渲染会管理排除项。只读检查和 `--check` 仅读取现有状态。

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

## 在项目中编辑和验证 <a id="edit-and-verify-in-the-project"></a>

如果初始化会替换现有配置，编辑前须取得[用户的替换决定](#inspect-or-choose-a-binding)。以项目的实际文件和证据为准。编辑 Rule 或 Skill 时，把这些文件作为[编写规则与技能](../write-rules-and-skills/SKILL.md)的候选。运行适用检查，并在需要时渲染。备份发生冲突或不可用时，仍可继续独立且已获授权的本地工作。

用 `sync-project` 渲染已有本地配置，只处理生成的 Project rules 部分时用 `sync-project-rules`。`ruleEntry` 决定使用 `AGENTS.md` 还是 `AGENTS.local.md`。两条命令都使用现有输入并检查归属。渲染已获授权时，运行下方相应命令。

```text
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>"
```

只读检查这两个范围时，使用 `--check`。

```text
python "<maintain>" sync-project --target "<target-root>" --check
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

仓库模式下，两条命令都需要可读且匹配的备份，包括使用 `--check` 时。如果编辑导致必要的生成或验证无法进行，在受支持的本地检查足以验证时，可以使用该检查。否则保留编辑并暂缓备份。保存前验证选定的渲染结果。另行报告仍未满足的 Setup 或迁移前提。

任务包含保存时，按[保存已验证的配置](#save-verified-configuration)完成相应操作并报告结果。只编辑或检查时，报告改动的文件、实际执行的检查和未满足的前提。

## 保存已验证的配置 <a id="save-verified-configuration"></a>

保存前须完成适用验证。报告改动的本地文件、实际执行的检查和未满足的前提，以及适用的备份、回执和发布结果。检查、访问、刷新或采纳失败，或保存暂缓时，保留本地工作并报告在哪一步停下，包括未执行或结果仍不确定的阶段。

单独请求保存和编辑后保存都复用项目的有效绑定。项目尚未绑定时，[建立已选绑定](#inspect-or-choose-a-binding)。未指定模式时，请用户选择。两种本地模式都在项目内完成，核对[适用的 Git 处理方式](#complete-contents-and-git-treatment)。

使用仓库备份时，从刷新、保存、记录一致到发布，沿用同一个持久源检出、绑定和相关证据。已授权的仓库保存包含限定范围的提交和正常推送，用户要求本地结果时除外。保留本次操作已产生并获接受的源端工作的来源记录。

### 首次导入 <a id="initial-import"></a>

日常维护首次绑定并导入前，审阅和验证所选文件的完整内容。重复使用 `--file` 选择相对于目标的文件或目录，也可以审阅实际默认范围。选中 `.agents/config.json` 时，备份中包含绑定后的配置。核实绑定结果。保留精确的导入路径及清单，以便使用 `--path` 发布。文件一致后记录一致状态。绑定失败时源检出可能已保存部分工作，应与业务项目的状态分别报告。

### 已有条目 <a id="existing-entry"></a>

刷新或采纳前，为当前绑定确认[仓库访问条件](#inspect-or-choose-a-binding)，复用仍然有效的证据，并在所有权或私有性存疑时核实。复用当前绑定有效的刷新和核对证据，或运行下列命令。刷新失败时停止备份。只读的 `reconcile` 将两侧与上次一致状态做比较。把条目的 `source_fingerprint` 和 `scope` 与任何可靠的早期观察比较。`local_updates_only` 为真且已有证据与之无冲突时，保存任务已授权且已验证的文件。条目在上游发生变化或方向仍不明确时，保存前[审阅当前差异并取得选择](#choose-between-differing-copies)。

```text
python "<maintain>" update --target "<target-root>"
python "<maintain>" reconcile --target "<target-root>"
```

用当前检查的 `fingerprint` 保护精确选定且存在差异的文件。核实完整内容仍与审阅过的版本一致。检查影响备份路径和清单的已暂存、未暂存、未跟踪及待推送改动。可能覆盖任务范围外的待处理工作时暂缓保存。实际范围变化需要获得接受，包括会删除清单声明的删除操作。采纳可能重写清单而保持其选择。路径超出检查范围时，须先接受扩展，并核实本地文件已审阅且保持稳定，以及源端目标位置，之后才能在未使用指纹保护的情况下按精确路径采纳。

用 `adopt` 保存选中的文件，并保留结果供发布。如果所需文件和范围已经备份，可以跳过采纳。

```text
python "<maintain>" adopt --target "<target-root>" --accept-existing "<inspect-fingerprint>" --file ".agents/rules/project.md" > "<adoption-result.json>"
```

有权采纳 **全部** 已证实仅本地变更时，也可以先审阅完整选择，再按带指纹的计划执行。显式执行 `adopt --all` 会刷新整个声明范围并移除缺失文件的声明。仅在整个刷新范围都已获授权时使用。

```text
python "<maintain>" reconcile --target "<target-root>" --adopt-local
python "<maintain>" reconcile --target "<target-root>" --adopt-local --accept-plan "<plan-fingerprint>"
```

### 记录一致状态

文件一致后，用不带差异令牌的 `apply` 在本地 `.agents/project-config-sync.json` 回执中记录一致状态。这个命令只记录已有的一致。仍有差异时，保留双方内容，解决后再发布。备份已写入、回执已一致、提交已发布是三个独立结果。

```text
python "<maintain>" apply --target "<target-root>"
```

### 发布或重试已验证的范围 <a id="publish-or-retry-the-verified-scope"></a>

完成必要检查、确认一致并建立仓库访问条件后，用 `--plan` 传入已接受的采纳 JSON，或用 `--path` 逐个指定已接受的仓库相对路径。包括本次操作负责的导入内容、清单改动和删除。请求只包含相关 Git 工作。保存时可能没有新内容需要发布。命令会检查计划摘要、确切范围、两侧一致和远端结果。

```text
python "<maintain>" publish --target "<target-root>" --plan "<adoption-result.json>" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

发布失败后检查所报告的状态，并保留已留下的提交。重新验证被钩子改写的内容。源、目标和远端证据都支持时，重试已验证的提交。有已接受的计划证据时，将 `--plan` 与 `--commit` 一起保留。Wiki 范围使用 `wiki publish`。分别报告本地工作、检查、备份、回执和推送的实际结果，包括未完成或未知的影响。

## 恢复明确选定的备份 <a id="restore-an-explicitly-chosen-backup"></a>

显式恢复仅在有匹配且成功的本地回执时复用绑定。否则，取得用户选定的仓库、分支和已有条目，在绑定前核实。建立仓库访问条件后，运行 `update` 并检查确切的新增、覆盖和删除。用户接受有差异的恢复时，使用检查指纹执行 `apply`。核对恢复后的文件、Git 处理及本机前提。仅恢复以已接受的文件字节就位为止。渲染、完整 Setup 和保存本地改动各有自己的操作范围。

### 在有差异的副本间选择 <a id="choose-between-differing-copies"></a>

展示确切差异，包括二进制差异。恢复在任务范围内时，提供应用已审阅备份的选项。只有保存已获授权且当前流程支持时，才提供保存已审阅本地改动的选项。始终允许把两份副本和回执留在原处。影响发生变化时，展示新的差异并重新取得选择。等待选择时，暂缓受影响的同步，继续独立且已获授权的工作。

项目保存获接受后，按上文带保护的保存及发布流程完成。项目恢复获接受后，使用已审阅的检查指纹应用备份。Wiki 相关选择走[Git 根目录维护流程](#prepare-and-save-the-git-root-openwiki)。

```text
python "<maintain>" apply --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

应用后，在本地回执中记录一致状态。Git 排除设置失败时，分别核对实际文件、回执和排除项。明确设置当前检出的启动偏好时，对 `apply` 使用 `--auto-sync on` 或 `--auto-sync off`。应用已接受的差异时同时提供差异令牌。

## 执行已启用的启动同步 <a id="synchronize-on-enabled-startup"></a>

启动同步默认关闭。已启用且绑定有效、回执匹配的检出先运行 `update`，再运行只读 `reconcile`。根据结果选择下一步。

| 刷新后的证据 | 动作 |
| --- | --- |
| `in-sync` | 运行不带令牌的 `apply` 记录一致。 |
| `source-updated` 且已证实只有仓库发生变化 | 使用确切的检查指纹应用审阅过的差异。缺少早期清单的旧回执无法证明这个方向。 |
| `needs-choice` 且 `local_updates_only` 为真 | 询问保存还是暂缓。接受保存时，按审阅过的选择执行精确备份和发布。 |
| 其他 `needs-choice` | [审阅差异并取得选择](#choose-between-differing-copies)。 |

报告无效的已启用状态。刷新失败或同步被暂缓时，保留文件及回执，报告停止的阶段，并继续独立且已获授权的工作。

## 准备和保存 Git 根目录的 OpenWiki <a id="prepare-and-save-the-git-root-openwiki"></a>

以已绑定的项目作为 `--target`，并确认有权写入它的 Git 根目录。Git 根目录有独立绑定时，Wiki 命令会拒绝从嵌套项目执行。保留嵌套项目的绑定、文件和备份状态，说明 Git 根目录下的项目负责这项工作，并停止嵌套项目的操作。维护 Git 根目录需要该项目的授权。已有 Wiki 任务仍由当前责任方处理，须先在其工作树中完成，再进行依赖它的准备或保存。

两种本地模式下，`wiki prepare` 完成相应的 Git 处理，维护到此结束。仓库模式下，准备新一轮运行或制定保存计划前，先满足[仓库访问条件](#inspect-or-choose-a-binding)，复用仍然有效的刷新证据，或运行 `update`。刷新失败时，保留两份副本并报告维护在哪一步停下。

Git 根目录下的项目使用普通项目快照。嵌套项目使用 `projects/<entry>/wiki/`，并在 Git 根目录使用单独的 `.agents/openwiki-config-sync.json` 回执。提供保存嵌套 Wiki 的选项前，或保存已完成的嵌套 Wiki 前，先确认备份基线，并对精确选定的范围成功运行 `wiki save` 预览。已有快照时，核实回执与选定的绑定和备份源相符，以便预览检查刷新后的备份是否仍与上次一致。没有回执时，`source_changed_since_sync` 也可能为假。首次保存时，确认刷新后的备份源确实没有嵌套 Wiki 快照。

如果 `wiki prepare` 返回 `needs-choice`，[审阅确切差异](#choose-between-differing-copies)。仅恢复的任务提供应用备份或保留现状。其他任务根据核实的变更方向和本次授权给出可执行的选项。

- 已绑定项目就是 Git 根目录时，对该快照运行普通 `reconcile` 或复用仍然有效的结果。结果为 `source-updated` 时，提供应用备份或保留现状。结果为 `needs-choice` 且 `local_updates_only` 为真时，提供保存或保留现状。两侧都变了或方向不明时，提供任务范围内受支持的写入选项，也允许保留现状。保存获接受后，走[普通的带保护采纳流程](#existing-entry)。
- 嵌套项目提供应用备份或保留现状。只有上述备份基线和预览检查均通过时，才额外提供保存选项。

应用已接受的备份时，把已审阅的检查指纹传给 `wiki prepare --accept-existing`。选择保留现状时，准备仍待处理。准备阶段选择保存时，保存后确认两侧一致，再次运行 `wiki prepare`。

仓库模式下保存已完成的 Wiki 时，先验证 Wiki，再审阅 `openwiki/`、`.openwikiignore` 以及明确选定的 Git 根目录 `AGENTS.md` 或 `CLAUDE.md` 的保存计划。保存时沿用相同选择和已审阅的计划指纹。仅发布本次操作已验证的范围。

```text
python "<maintain>" wiki prepare --target "<target-root>"
python "<maintain>" wiki prepare --target "<target-root>" --accept-existing "<inspect-fingerprint>"
python "<maintain>" wiki save --target "<target-root>" > "<wiki-plan.json>"
python "<maintain>" wiki save --target "<target-root>" --accept-plan "<plan-fingerprint>"
python "<maintain>" wiki publish --target "<target-root>" --plan "<wiki-plan.json>" --message "Back up OpenWiki"
```

方向未确定或保存被拒绝时，保留 Wiki 和已有备份工作。中断后，将已保存的内容与计划核对，必要时用 `wiki prepare` 记录一致状态。报告 Wiki 的实际保存和发布结果。
