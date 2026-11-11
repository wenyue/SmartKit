# Worktree 配置

这份受支持的引用文档涵盖配置准备、后续编辑和来源生命周期。从已加载的 SmartKit 安装中，将本 Skill 目录下的 `scripts/prepare_configuration.py` 解析为 `<prepare>`。阅读本文档不代表调用 worktree 创建流程。

## 从完成初始化的源准备配置

使用检出或携带已提供的 Git 共享配置（`local`）。对于 `local-only` 和 `repository`，从已接受且完成初始化的源检出中选择必要配置及支持文件。两种模式使用相同的本地准备流程，无需访问配置仓库。仅有 setup 标记不能证明源或宿主已就绪。

选择具体文件或配置目录，例如 `.agents/config.json`、`.agents/rules` 和 `.agents/skills`，而非包含 worktree 本地状态的整个 `.agents` 树。准备前检查检出特有的路径和必要使用方。操作期间独占访问所选源和目标。

```text
python "<prepare>" --help
python "<prepare>" prepare --source "<source-project>" --target "<target-project>" --path ".agents/config.json" --path ".agents/skills"
```

辅助脚本优先使用符号链接；平台不允许链接时，退回普通复制。复制会在遍历前排除 Git 元数据、已知缓存及依赖目录，以及 worktree 本地同步状态；必要的源文件必须位于所选范围内。已有目标内容会保留。辅助脚本在 worktree 私有 Git 目录中记录每条路径的实际方式和来源，并仅将已准备路径从业务 Git 中排除，不改变索引。

必要的宿主使用方不能使用链接时，对受影响路径使用 `--copy` 准备。它只能替换已记录且仍指向已接受来源的链接。

```text
python "<prepare>" prepare --source "<source-project>" --target "<target-project>" --path ".agents/config.json" --copy
```

失败会保留来源记录和部分路径。重试前先检查：保留相符的已复制文件，补齐缺失文件，冲突则需要解决。准备成功只证明所选文件可用；声明 worktree 就绪前，验证指令、Skill 和宿主实际可用。

## 按记录的来源编辑配置

在关联 worktree 中编辑项目 Agent 配置前，检查其来源。命令报告该 worktree 内每个项目的映射；没有记录时报告无映射，记录无效时则失败，不猜测来源。

```text
python "<prepare>" inspect --target "<worktree-or-project>"
```

编辑前验证记录的来源和当前链接目标。对于链接路径，编辑解析后的源文件并保留链接，包括编辑器通过原子替换写入文件的情况。对于副本路径，检查源和目标的当前内容，在同一次操作中将同一预期修改应用到两处，并在报告完成前验证两处。这包括已记录目录下的新增、重命名和删除。保留无关差异；冲突或源不可用时，配置编辑仍未完成。记录范围外的路径保留其通常的所有权。

重命名或删除已记录的根路径前，检查已登记 worktree 中的来源，并将所有受影响的链接或副本映射纳入已接受的修改；否则保留当前路径。重命名源和受影响的目标路径，调整符号链接的指向，并在所报告的 `record` 中，重命名 `projects[<project-relative-path>].paths` 下的各个键，保留其方式和本地 Git 排除。删除后，移除受影响的键及已清空的项目条目。以原子方式写入记录并保留其他条目，再次检查并验证所有受影响位置后，才能完成编辑。

## 清理时保护来源

只要其他 worktree 仍依赖某个链接源检出，就保持它可用。移除 worktree 前，检查仓库已登记 worktree 中的来源，包括嵌套项目映射，并处理依赖待移除检出的链接。移除副本所在 worktree 前，保留尚未反映到源中的配置修改。来源记录只确立关系，不证明副本仍一致，也不授权丢弃差异。
