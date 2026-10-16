# 结构

在 SmartKit 仓库中进行位置选择和职责划分时，使用本 Rule。以下路径均从仓库根目录解析。

## 将功能上下文放在一起

将实现、策略数据和其他私有资源放在解释它们的功能旁边。优先使用现有功能目录，而不是仅按文件类型新建顶层分类。例如，推荐工具策略应放在 `runtime/recommended-tools/policies/`：检查与维护使用的是同一功能的决策。

当现有的独立消费者需要同一种能力，且其职责清晰时，提取共享支持。将每个消费者的选择、解释和任务专属行为留在该消费者处，共享共同的机制。仅有未来可能复用的设想，不足以建立另一个共享目录。

## 按执行角色选择位置

通过 Hooks 或共享资源入口调用的已安装插件实现放在 `runtime/<feature>/`，Harness 生命周期接线放在 `hooks/`。运行时操作可以由用户手动调用，也可以改变本机状态；这些性质不会使它成为仓库维护工具。

维护 SmartKit 自身源文件和分发元数据的工具放在 `scripts/`，例如仓库级同步器。Skill 的私有辅助工具和资产留在该 Skill 内。只有实际消费者足以支持这一职责边界时，才将其移到共享运行时支持中。

可复用的插件 Rules 和 Skills 放在 `rules/` 和 `skills/`，SmartKit 自身的维护指导放在 `.agents/`。目标项目的设置蓝图、模板和目录清单放在 `setup-assets/`；它们描述未来的目标资产，而非本仓库当前生效的 Rules。

## 找到规范输入

能力目录中可能同时包含规范输入和生成输出。需要变更时，沿以下路径查找输入；注册表及其生成器中保存当前成员和精确的输出清单。

| 区域 | 规范输入 | 派生输出及负责的工具 |
| --- | --- | --- |
| 插件 Agents | `agents/source/` 和 `agents/registry.json` | 通过 `scripts/sync_agent_adapters.py` 生成 `agents/<harness>/` |
| 插件 MCP | `mcp/registry.json` | 通过 `scripts/sync_mcp_adapters.py` 生成 `mcp/<harness>.json`；外部服务实现仍在此配置边界之外 |
| 第三方 Skills | `skills/registry.json` 中的来源声明和 `vendor/patches/` 中的补丁 | 通过 `scripts/update_external_skills.py` 生成选定的 `skills/` 快照、`licenses/` 和 `vendor/external-skills.lock.json` |
