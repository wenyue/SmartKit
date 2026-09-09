---
name: setup-project-agents
description: 在 Codex、Cursor、Copilot 和 Qoder 之间设置或更新仓库的 Rules、Skills、Agents 和 MCP；未要求完整设置时，按明确意图同步项目自身的变化。
---

# 设置项目 Agent

首次设置以及每次未限定范围的设置或更新，默认都执行全量设置。它依据不可变的 Setup Authoring Contracts 和当前项目证据，重新编写 catalog 当前声明的全部项目 Rules 和 Skills，包括配套资源。上游指纹未变或输出已经存在，都不会跳过编写。

调用者明确将意图限定为本地 Rule/Skill 发现及项目 Agent/MCP 映射时，使用项目同步。仅涉及 `AGENTS.md` Rule 索引的请求，应保持在这个更小的操作范围内。上游未变不能推导出局部同步意图，局部同步请求也不能推导出全量设置权限。

## 输入与所有权 <a id="inputs-and-ownership"></a>

将当前已加载 Skill 的目录确定为 `<skill-root>`，将仓库确定为 `<target-root>`。执行任一工作流前，阅读[所有权](references/ownership.md)。它定义项目输入、记录的所有权、生成输出的退役、原生字段的保留，以及就绪检查的边界。本地同步中的 `source_root` 是包含当前 Skill 的插件根目录；全量设置使用冻结会话返回的源根目录。

本 Skill 负责意图分流、项目证据、整组内容的一致性、固定来源的 writer 协调和交接。脚本负责选择、验证、映射、事务、恢复证据和命令状态。使用脚本帮助和返回路径，不要自行重建协议状态：

```text
python "<skill-root>/scripts/workflow.py" --help
```

## 全量设置

1. 阅读[完整会话协议](references/session-protocol.md)。解决实质性的项目输入选择和缺失的操作授权。已接受的设置意图可能已经涵盖这些操作。若 `start` 报告缺少 Matt 上下文，结束本次调用，请用户调用 `setup-matt-pocock-skills`；完成后，通过新的设置调用继续。
2. 启动一个冻结会话，保存它返回的请求、来源信息和生成目录。开始编写前，确认完整生成集合及项目输入符合已接受的意图。
3. 阅读并执行[生成内容编写](references/generated-authoring.md)。从固定来源加载公共 writer 及其依赖，将生成和保留的 Rules 与相关 Skills 一起规划，并为每个请求取得独立的 `COMPLETE` 结果。注册前，解决整组内容的覆盖缺失和职责重叠，只注册最终完整交接。生成范围之外的修正仍属于所有者依赖，并会结束本次会话。
4. 按协议，通过事务和干净后置条件完成已注册的会话。发生任何失败时，进入协议中的停止与恢复分支；脚本负责安全回滚和会话清理。
5. 报告来源模式、根目录、指纹和存在时的提交；已启用的宿主；变更与保留路径；外部来源信息；干净检查状态；以及任何恢复证据。将项目快照交给维护者审查并提交。

## 明确指定的项目同步

编辑受支持的项目源文件或 `.agents/config.json` 后，使用本地操作：

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>" --check
```

它验证当前项目的发现结果，更新所负责的 Rule 索引和已声明的 Agent/MCP 映射，并且只为已删除或重命名的声明移除记录中的项目映射。项目 Skills 使用既有的直接发现方式；验证和保留可能不需要修改适配器。该操作不获取外部内容、不编写或重新生成契约产物，也不升级共享、插件或外部资产；不需要 Matt 前置检查或生成会话。项目映射所有权记录缺失或版本较旧时，必须先执行全量设置。外部 Skill 声明发生变化时，也必须执行全量设置。应报告这一要求，不得暗中扩大局部同步意图。

取得这些项目映射的变更权限后，执行应用操作：

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>"
```

意图仅限于 `AGENTS.md` 时，使用独立的 Rule 索引操作。即使尚未执行全量设置，也仍可使用这条无需会话、无需获取外部内容的路径：

```text
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>" --check
```

```text
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>"
```

两个本地操作都会保留 `AGENTS.md` 中所负责的 `## Project rules` 节之外的每个字节，以原子方式应用，并满足幂等的干净后置条件。检查模式从不修改目标。退出码为 0 且返回 `check: clean`，证明已经收敛；退出码为 1 且返回 `check: drift`，报告拟变更路径；退出码为 2，报告拒绝或失败。对输入格式错误、所有权不明确、与未托管内容冲突、相关状态并发漂移或回滚失败，保留准确证据。重试前，在已接受的范围内解决原因。应用和回滚期间，应保持对计划路径的独占访问；文件系统检查无法防止不配合的写入者在检查与修改之间插入操作。

报告所选操作、状态、变更路径、返回的保留源文件，以及任何拒绝或恢复证据。成功后，将变更交给维护者审查并提交。本 Skill 不授予 commit、push、发布、release、依赖安装或目标仓库之外的安装权限。
