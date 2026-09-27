---
name: setup-project-agents
description: 跨 Codex、Cursor、Copilot 和 Qoder 设置或更新项目 Rules、Skills、Agents 和 MCP。
disable-model-invocation: true
---

# 设置项目 Agents

将项目声明的 Agent 配置收敛到干净且归属明确的状态。修改输入或获取来源之前，按调用方意图选择操作：

| 意图 | 操作 |
| --- | --- |
| 首次设置，或未限定的设置/更新 | 完整设置：依据不可变 Setup Authoring Blueprints 和当前项目证据，重新编写当前目录声明的全部项目 Rule 和 Skill，包括支持资源。 |
| 明确限定于本地 Rule/Skill 发现和项目 Agent/MCP 映射 | 仅项目同步。 |
| 明确限定于 `AGENTS.md` Rule 索引 | 独立 Rule 索引同步。 |

上游指纹未变或输出已存在，都不能跳过完整编写，也不表示意图仅限本地。反过来，本地同步请求也不授权完整设置。

## 输入与所有权 <a id="inputs-and-ownership"></a>

将已加载 Skill 目录解析为 `<skill-root>`，将仓库解析为 `<target-root>`。任一工作流开始前都阅读[所有权](references/ownership.md)。它定义项目输入、已记录所有权、生成输出退役、原生字段保护及就绪状态的限度。本地同步使用包含此已加载 Skill 的插件根作为 `source_root`；完整设置使用冻结会话返回的源根。

Setup 负责意图路由、合格项目证据、整套一致性、固定来源 writer 协调和交接。脚本负责来源选择、验证、映射、事务、恢复证据和命令状态。查看其接口并消费返回路径，不自行重建会话状态：

```text
python "<skill-root>/scripts/workflow.py" --help
```

## 执行完整设置

开始之前完整阅读[完整会话协议](references/session-protocol.md)。解决重要项目输入选择和缺失的效果授权；已接受的设置意图可能已经涵盖它们。如果 `start` 报告缺少 Matt 上下文，结束本次调用，请用户在目标中调用 `setup-matt-pocock-skills`。该工作流完成后，只能通过新的设置调用继续。

启动一个冻结会话。保留返回请求、来源出处和生成根，并确认完整请求生成集及项目输入符合已接受意图。

编写之前阅读[生成编写](references/generated-authoring.md)。Setup 结合相关 Skill 和全局策略，规划生成与保留 Rule 构成的结果集，再将合格的单 Candidate 工作交给固定来源的公共 writer 及其依赖。每个请求都必须取得独立 `COMPLETE`。先协调整套覆盖、职责和加载，再仅注册最终完整交接。任何必需但超出冻结生成范围的修正都会结束当前会话并交给其所有者。

按协议的事务和干净后置条件结束已注册会话。失败时遵循原尝试恢复分支；脚本负责带保护条件的回滚和私有会话清理。仅目标干净不能证明清理失败后的事务已经完成。

完整设置成功后，评估全部直接项目 Rule 的常驻上下文成本。只有当重要体量来自仅在可识别条件下才需要的策略时，才建议将确切分支迁移到原生 `rule-<domain>` Skill。仅凭文件大小，或对于无条件基线策略，都不足以支持迁移。

报告来源模式、根、指纹及存在时的提交；启用的主机；已改和已保留路径；外部出处；干净检查状态；上下文加载成本评估；以及任何恢复证据。将结果快照交给维护者审阅和提交。

## 执行明确要求的本地同步

### 项目发现和 Agent/MCP 映射

编辑受支持的本地源或 `.agents/config.json` 后，检查拟执行操作：

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>" --check
```

该操作验证当前项目发现，并同步自有 Rule 索引和声明的 Agent/MCP 映射。只退役声明已删除或改名的已记录项目映射。项目 Skill 保持直接发现路线，因此验证和保护可能不需要修改适配器。

获取、编写、蓝图重新生成或共享/插件/外部升级都不属于该操作。它不需要 Matt 预检或生成会话。项目映射所有权记录缺失或过旧时，必须先完整设置；外部 Skill 声明变化同样需要完整设置。报告该依赖，不扩大本地请求。

只有具备这些项目映射权限时才应用：

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>"
```

### 仅 Rule 索引

意图仅限 `AGENTS.md` 时，使用独立操作。完整设置之前也可使用，不需要会话或获取：

```text
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>" --check
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>"
```

### 解释并保留本地结果

两种操作都保留 `AGENTS.md` 自有 `## Project rules` 章节外的每个字节。应用是原子的，并带有幂等干净后置条件；检查模式绝不修改目标。退出 0 且 `check: clean` 证明收敛。退出 1 且 `check: drift` 报告拟变更路径。退出 2 报告拒绝或失败。

保留输入格式错误、所有权含糊、非托管冲突、相关并发漂移或回滚失败的确切证据。重试前在已接受范围内解决原因。应用及回滚期间保持对计划路径的独占访问：文件系统检查无法防止不合作的写入者在检查和修改之间介入。

报告操作、状态、变更路径、返回时提供的已保护来源，以及拒绝或恢复证据。将成功改动交给维护者审阅和提交。完整设置和本地同步都不授予提交、推送、发布、发版、依赖安装或目标仓库外安装权限。
