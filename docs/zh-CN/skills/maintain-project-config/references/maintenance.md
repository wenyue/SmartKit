# 项目配置维护

本参考及其命令供配置维护、完整 setup、启动同步和 OpenWiki 使用。`<maintain>` 指已加载插件中的 `skills/maintain-project-config/scripts/maintain.py`，`<target-root>` 指业务项目。用 `python "<maintain>" --help` 查看命令选项，按同一插件的 `setup-assets/catalog/project-config.schema.json` 确定项目支持哪些声明。所需资源不可用时，说明缺失项并暂缓依赖它的工作。

## 选择维护模式 <a id="choose-the-maintenance-mode"></a>

```text
python "<maintain>" inspect --target "<target-root>"
```

检查是只读操作，使用本地能取得的信息。项目尚未绑定时，用用户的语言同时列出三种模式。已有有效绑定时沿用该绑定。初始化要覆盖现有配置时，先请用户决定是否替换。

| 模式 | 存储值 | 配置保存位置 |
| --- | --- | --- |
| 随项目共享 | `local` | 保存在项目内，通过业务项目的 Git 仓库共享。 |
| 仅本机 | `local-only` | 保存在项目内，通过本地规则从 Git 中排除。 |
| 独立配置仓库 | `repository` | 保存在项目内，通过本地规则从 Git 中排除，并备份到个人私有 GitHub 仓库。 |

## 绑定或更换配置来源 <a id="bind-or-deliberately-change-a-source"></a>

```text
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<repository>" --branch "<branch>" --entry "<entry>"
```

仓库操作使用 Git 和 `gh`，需要在对应的 GitHub 或 GitHub Enterprise 主机上以仓库所有者的个人账号登录。确认仓库、分支和条目。github.com 可用 `owner/repository`，指定主机时使用不含凭证的 HTTPS 地址。只有用户明确授权创建指定仓库时才使用 `--create-repository`。`bind` 和 `publish` 会验证所有权和私有性。`update` 成功表示已核实本地工作副本并成功拉取，若对所有权或私有性有疑问，另行核实。

连接已有条目前，确认 `bind` 刷新后会使用的版本中存在 `projects/<entry>/manifest.json`。首次克隆时检查选定的远端分支。复用已有工作副本时，检查其中会保留的条目，它可能包含已获认可但尚未发布的工作。如果条目缺失或无法核实，暂缓连接，因为 `bind` 可能会把本地文件导入新条目。只有用户已同意切换绑定时才使用 `--replace-binding`。先解决未决差异，包括嵌套项目负责的 Git 根目录 Wiki，并保留已有工作和条目。

## 完整备份文件和目录 <a id="back-up-complete-files-and-directories"></a>

每个条目的 `manifest.json` 用 `files` 指定相对于目标项目的文件，用 `directories` 指定要递归备份的目录，内容保存在 `files/` 下。审阅文件的全部内容，留意凭证和本机路径。密钥应留在凭证管理工具中，同步记录应留在备份之外。选中的原生设置、MCP 文件和 `.agents/config.json` 均整份复制。备份范围由清单确定，配置锁文件不参与选择，单独设置 `ruleEntry` 也不会扩大范围。复制来的 setup 标记不能证明本机已完成 setup 或具备运行条件。遇到无法读取或不支持的状态，包括带版本字段的清单和同步记录，保留原状并报告。

### 将验证过的文件导入新条目 <a id="import-verified-files-into-a-new-entry"></a>

日常维护时，在首次执行 [`bind`](#bind-or-deliberately-change-a-source) 前，验证[所选文件的完整内容](#back-up-complete-files-and-directories)。重复使用 `--file` 指定文件或目录，也可以审阅实际的默认选择。如果选中了 `.agents/config.json`，备份将包含绑定后的配置。核对绑定结果，记下实际导入的文件和清单，以便使用 `--path` [发布](#publish-an-exact-verified-scope)。文件一致后，使用不带差异确认参数的 `apply` 记录一致状态。绑定失败时，配置仓库中可能已保存部分内容，应与业务项目的结果分别说明。

## 备份验证过的本地改动 <a id="back-up-verified-local-changes"></a>

满足[仓库访问条件](#bind-or-deliberately-change-a-source)后，刷新配置仓库并检查哪一侧有改动。刷新失败时停止备份。完整 setup 沿用自身在配置仓库中编写的流程。对本次操作已在配置仓库中产生且已获认可的改动，保留其来源依据。

```text
python "<maintain>" update --target "<target-root>"
python "<maintain>" reconcile --target "<target-root>"
```

`reconcile` 将两侧与上次记录的一致状态比较。如果之前有可靠的检查结果，也要将条目的 `source_fingerprint` 和 `scope` 与之核对。如果 `local_updates_only` 为真，且此前没有相反证据，就保存任务已授权且已验证的文件。如果上游条目有改动或无法判定哪一侧发生了变化，审阅两侧并请用户[选择同步方式](#apply-the-users-whole-synchronization-choice)。

使用本次检查的 `fingerprint` 限定要采纳的差异文件。核对[完整内容](#back-up-complete-files-and-directories)仍与验证时一致。检查受影响的备份路径和清单上已暂存、未暂存、未跟踪及待推送的改动。如果保存会覆盖任务以外尚未处理的工作，暂缓保存。实际范围有变时须先取得认可，包括删除文件会同时移除清单声明的情况。采纳改动可能会重写清单的格式，而其选择范围仍相同。对于检查范围外的新路径，须先就扩大范围取得认可，核实本地内容和备份目的位置均已审阅且保持稳定，再按确切路径执行不带指纹保护的采纳。

```text
python "<maintain>" adopt --target "<target-root>" --accept-existing "<inspect-fingerprint>" --file ".agents/rules/project.md" > "<adoption-result.json>"
python "<maintain>" apply --target "<target-root>"
```

第一条命令把选定文件保存到备份。第二条在不接受任何差异的情况下记录一致状态。保留采纳结果，然后[按确切范围发布](#publish-an-exact-verified-scope)。如果指定的文件和范围已备份，跳过采纳，按需记录一致状态。如果仍有差异，保留两侧内容，解决差异后再发布。

如果调用方获准保存 **全部** 已确认仅发生在本地的改动，可先生成计划，审阅完整文件范围后再执行。显式使用 `adopt --all` 会刷新整个声明范围，并移除已缺失文件的声明。仅在获准刷新整个范围时使用。

```text
python "<maintain>" reconcile --target "<target-root>" --adopt-local
python "<maintain>" reconcile --target "<target-root>" --adopt-local --accept-plan "<plan-fingerprint>"
```

## 显式恢复或启动时同步 <a id="restore-explicitly-or-synchronize-at-startup"></a>

用户明确要求恢复时，只有本机存在匹配的成功同步记录，才可沿用已有绑定。否则先取得用户选择的仓库、分支和已有条目，并在[绑定](#bind-or-deliberately-change-a-source)前核实条目。满足[仓库访问条件](#bind-or-deliberately-change-a-source)后运行 `update`，检查具体的新增、覆盖和删除，再应用用户接受的恢复。检查恢复后的文件、[Git 处理方式](#keep-personal-configuration-out-of-business-git)和本地前提条件。仅恢复时，复制用户接受的原始内容后即结束。生成配置、完整 setup 和保存本地改动各自独立。

启动同步默认关闭。已启用启动同步、绑定有效且有匹配同步记录的工作副本，可以刷新仓库后运行只读的 `reconcile`。只有 `source-updated` 能证明改动仅来自配置仓库时，才可使用本次检查的确切指纹直接应用。旧同步记录若缺少先前的清单，便无法证明这一点。结果为 `in-sync` 时，按需记录一致状态。只有本地有改动时，请用户选择保存或暂缓。启用状态无效时应报告。如果刷新失败或仍待用户选择，暂缓应用。

### 按用户选择处理整次同步 <a id="apply-the-users-whole-synchronization-choice"></a>

展示具体差异，包括二进制文件的差异。让用户选择保存已审阅的本地改动、应用已审阅的备份，或保留当前文件和同步记录。日常保存按[备份验证过的本地改动](#back-up-verified-local-changes)操作。应用有差异的备份时，使用本次检查的确切指纹。如果实际影响与此前审阅的内容不同，展示新差异并请用户重新选择。等待选择期间，暂缓受影响的同步，可以继续独立工作。

```text
python "<maintain>" apply --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

### 记录一致状态和启动同步偏好

两侧一致后，`apply` 将本地同步记录写入 `.agents/project-config-sync.json`。如果应用后更新 Git 排除规则失败，分别检查实际文件、同步记录和排除规则。需要设置该工作副本的启动同步偏好时，使用 `--auto-sync on` 或 `--auto-sync off`。如果已同意应用有差异的内容，同时传入差异确认指纹。

## 仅在需要时生成本地配置 <a id="render-local-configuration-only-when-required"></a>

只需更新自动生成的 `Project rules` 段落时，使用范围较小的命令。`ruleEntry` 决定更新 `AGENTS.md` 还是 `AGENTS.local.md`。本地生成使用已有输入并检查归属，不会执行完整 setup。

```text
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>"
```

在仓库模式下，两条命令都要求备份可读且与本地一致，只读的 `--check` 也一样。如果本地修改导致无法执行必要的生成或验证，仅在其他受支持的本地检查足以验证结果时才改用该检查。否则保留改动并暂缓备份。如果生成过程改动了选入备份的文件，先验证这些输出再保存。另行报告尚未满足的 setup 或迁移条件。

## 将个人配置排除在业务 Git 之外 <a id="keep-personal-configuration-out-of-business-git"></a>

个人模式使用目标项目限定范围的 Git `info/exclude` 规则。切换到项目共享模式时，只移除该目标由工具管理的规则区块。保留共享忽略文件和已经跟踪的配置。即使暂缓同步，也要检查相关路径，报告已经跟踪的文件和缺失的排除规则。绑定、应用和配置生成会维护这些规则。检查操作和 `--check` 都不会修复排除规则。

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

## 使用项目绑定维护 OpenWiki

将已绑定的项目作为 `--target`。命令会找到其 Git 根目录，并遵循该处已有的独立绑定。嵌套项目在 `projects/<entry>/wiki/` 下保存仓库备份，并在 Git 根目录使用独立的同步记录。准备前，确认授权覆盖对 Git 根目录的写入。已有 Wiki 任务正在进行时，先恢复该任务，再准备或保存备份。

仓库模式下，准备新一轮运行前先刷新仓库。结果为 `needs-choice` 时，按配置同步的方式处理。若用户已同意恢复有差异的内容，传入确切指纹。仓库模式下，验证已完成的 Wiki，审阅保存计划中的 `openwiki/`、`.openwikiignore`，以及明确选中的 Git 根目录 `AGENTS.md` 或 `CLAUDE.md`。保存时沿用相同的选择和已审阅的计划指纹。如果中断，将已保存内容与原计划核对，必要时通过 `wiki prepare` 记录一致状态。仅发布本次操作已验证的范围。

```text
python "<maintain>" wiki prepare --target "<target-root>"
python "<maintain>" wiki prepare --target "<target-root>" --accept-existing "<inspect-fingerprint>"
python "<maintain>" wiki save --target "<target-root>" > "<wiki-plan.json>"
python "<maintain>" wiki save --target "<target-root>" --accept-plan "<plan-fingerprint>"
python "<maintain>" wiki publish --target "<target-root>" --plan "<wiki-plan.json>" --message "Back up OpenWiki"
```

## 按已验证的确切范围发布 <a id="publish-an-exact-verified-scope"></a>

除非用户要求仅保存在本地，获准保存到配置仓库就包括按确切范围提交并正常推送。完成必要检查、确认两侧一致且满足[仓库访问条件](#bind-or-deliberately-change-a-source)后，用 `--plan` 传入已认可的采纳结果 JSON，或用 `--path` 逐个指定已认可的仓库相对路径。适用时将本次操作的导入、清单改动和删除一并纳入。没有新增改动时，可能没有内容需要发布。提交应排除无关的 Git 工作。命令会核验计划中的内容摘要、确切范围、两侧是否一致及远端结果。如果钩子修改了内容，重试前重新验证。

```text
python "<maintain>" publish --target "<target-root>" --plan "<adoption-result.json>" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

如果发布失败，检查返回的状态，并保留已经创建的提交。确认源、目标和远端状态都支持重试后，重试已核实的那次提交。若有已认可的计划，继续携带 `--plan`。Wiki 范围使用 `wiki publish`。报告本地修改、备份、同步记录和发布各自的实际结果。
