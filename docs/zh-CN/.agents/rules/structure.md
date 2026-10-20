# 结构

在 SmartKit 仓库中进行位置选择和职责划分时，使用本 Rule。以下路径均从仓库根目录解析。

## 将功能上下文放在一起

将实现、策略数据和其他私有资源放在解释它们的功能旁边。优先使用现有功能目录，而不是仅按文件类型新建顶层分类。例如，推荐工具策略应放在 `runtime/recommended-tools/policies/`：检查与维护使用的是同一功能的决策。

当现有的独立消费者需要同一种能力，且其职责清晰时，提取共享支持。将每个消费者的选择、解释和任务专属行为留在该消费者处，共享共同的机制。仅有未来可能复用的设想，不足以建立另一个共享目录。

将 runtime 代码中的长篇 Agent 行为指令提取到所属功能的 `prompts/` 目录。生成的元数据、表格和简短诊断保留在代码中。从已安装功能的位置解析 prompts，不依赖目标工作目录；记录交付成功之前，按照消费它的 Hook 或命令的错误契约处理资源不可用的情况。

## 按执行角色选择位置

将 Hooks 所需的实现和资源放在 `runtime/<feature>/`，包括由 Hook 启动的持久服务；将 Harness 生命周期接线放在 `hooks/`。其他消费者可以复用这些 Hook 所需的能力。仅有共享命令入口不足以确立 runtime 归属；手动调用和本地状态变更不会改变已有的 Hook 职责。

将 Hook 所需的只读解析和项目状态检查保留在 runtime，由 Skills 复用这些机制。runtime 不得导入或调用 Skill 的实现。它可以读取由 Skill 负责的受支持数据和文档，或在输出中指出 Skill 命令；命令执行仍由使用它的工作流负责，并遵守该命令的授权要求。

维护 SmartKit 自身源文件和分发元数据的工具放在 `scripts/`，例如仓库级同步器。Skill 的文档、辅助工具和资产保留在该 Skill 内。其他 Skills 可以按照 [项目政策](project-policy.md) 定义的插件路径和加载要求，使用其中明确受支持的资源；共享不需要新建 `shared/` 目录。

项目配置维护由 [维护项目配置](../../skills/maintain-project-config/SKILL.md) 负责，包括其参考文档、命令和用于更新项目配置的引擎。[设置项目 Agents](../../skills/setup-project-agents/SKILL.md) 在完整 setup 中使用这项底层能力。保持单向依赖：维护不能依赖 setup 的实现、命令路径或工作流调用。

可复用的插件 Rules 和 Skills 放在 `rules/` 和 `skills/`，SmartKit 自身的维护指导放在 `.agents/`。目标项目的设置蓝图、模板和目录清单放在 `setup-assets/`；它们描述未来的目标资产，而非本仓库当前生效的 Rules。

## 找到规范输入

能力目录中可能同时包含规范输入和生成输出。需要变更时，沿以下路径查找输入；注册表及其生成器中保存当前成员和精确的输出清单。

| 区域 | 规范输入 | 派生输出及负责的工具 |
| --- | --- | --- |
| 插件 Agents | `agents/source/` 和 `agents/registry.json` | 通过 `scripts/sync_agent_adapters.py` 生成 `agents/<harness>/` |
| 插件 MCP | `mcp/registry.json` | 通过 `scripts/sync_mcp_adapters.py` 生成 `mcp/<harness>.json`；外部服务实现仍在此配置边界之外 |
| 第三方 Skills | `skills/registry.json` 中的来源声明和 `vendor/patches/` 中的补丁 | 通过 `scripts/update_external_skills.py` 生成选定的 `skills/` 快照、`licenses/` 和 `vendor/external-skills.lock.json` |
