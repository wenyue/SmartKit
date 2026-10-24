# 结构

将 SmartKit 代码和指导放在其服务的职责旁。以下路径均相对于仓库根目录解析。

## 将功能上下文放在一起

将实现、策略数据和私有资源与解释它们的功能放在一起。优先使用已有功能目录，不要仅按文件类型建立新的顶层类别。例如，推荐工具策略属于 `runtime/recommended-tools/policies/`，因为检查和维护都使用该功能的决定。

当已有独立消费者需要同一能力、且其职责清晰时，再提取共享支持。共享机制，同时将选择、解释和任务特定行为留给各消费者。仅有未来复用的可能性，不足以建立共享目录。

将较长的 Agent 行为指令从运行时代码移到所属功能的 `prompts/` 目录；生成的元数据、表格和简短诊断留在代码中。从已安装功能的位置解析提示词，而不是从目标工作目录解析。资源不可用时，必须先遵循消费 Hook 或命令的错误契约，再记录交付成功。

## 由执行职责决定位置

| 职责 | 位置及边界 |
| --- | --- |
| Hook 所需的实现和资源，包括由 Hook 启动的持久服务 | 放在 `runtime/<feature>/`；`hooks/` 提供 Harness 生命周期接线。其他消费者可以复用该能力。 |
| 维护 SmartKit 自身源文件和分发元数据 | 放在 `scripts/`，包括仓库级同步器。 |
| Skill 的文档、辅助工具和资产 | 放在其 Skill 目录中。其他 Skills 可通过 [项目策略](project-policy.md) 定义的路径使用明确支持的资源；共享不要求新建 `shared/` 目录。 |
| 可移植的插件 Rules 和 Skills | 放在 `rules/` 和 `skills/`。 |
| SmartKit 维护者指导 | 放在 `.agents/`。 |
| 未来目标项目的蓝图、模板和目录 | 放在 `setup-assets/`；这些不是本仓库当前生效的 Rules。 |

共享命令入口本身不能确立 runtime 所有权。手动调用或本地状态变化，也不改变已有的 Hook 职责。

将 Hook 所需的只读解析和项目状态检查留在 runtime，供 Skills 复用。runtime 不得导入或调用 Skill 实现。它可以读取受支持的 Skill 所有数据和文档，或在输出中列出 Skill 命令；这些命令由消费工作流按其授权要求执行。

项目配置维护属于 [Maintain Project Config](../../skills/maintain-project-config/SKILL.md)，包括其参考资料、命令和更新引擎。[Setup Project Agents](../../skills/setup-project-agents/SKILL.md) 使用该能力完成完整 setup。保持依赖单向：维护不得依赖 setup 的实现、命令路径或工作流调用。

## 在派生文件中找到规范输入

能力目录可能同时包含源和生成输出。通过以下路径寻找所属输入；注册表和生成器负责当前成员及精确输出清单。

| 领域 | 规范输入 | 派生输出及所属工具 |
| --- | --- | --- |
| 插件 Agents | `agents/source/` 和 `agents/registry.json` | 通过 `scripts/sync_agent_adapters.py` 生成 `agents/<harness>/` |
| 插件 MCP | `mcp/registry.json` | 通过 `scripts/sync_mcp_adapters.py` 生成 `mcp/<harness>.json`；外部服务实现仍在此配置边界之外 |
| 第三方 Skills | `skills/registry.json` 中的来源声明，以及 `vendor/patches/` 中的补丁 | 通过 `scripts/update_external_skills.py` 生成选定的 `skills/` 快照、`licenses/` 和 `vendor/external-skills.lock.json` |
