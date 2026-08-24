# 项目工具

强度：`Mandatory`

适用范围：安全执行仓库命令、同步、已授权的状态修改、完整变更验证，以及已有 Skill 的交接。

从仓库根目录运行仓库命令。直接调用仓库自有的 Python 入口点前，应从活动环境中解析出 Python
3.10+ 启动程序；下文用 `<python>` 表示这个已验证的启动程序。能够自行解析启动程序的包装器负责满足
此前置条件。

## 需要同步的源文件变更

| 源文件变更 | 同步命令 | 只读漂移检查 | 必需的同步状态；审查每一项生成的 diff |
| --- | --- | --- | --- |
| `VERSION` | `<python> scripts/sync_plugin_version.py` | `<python> scripts/sync_plugin_version.py --check` | 每个生成的版本字段都与 `VERSION` 一致。 |
| `mcp/registry.json` | `<python> scripts/sync_mcp_adapters.py` | `<python> scripts/sync_mcp_adapters.py --check` | 每个宿主适配器都与 MCP 注册表一致。 |
| `agents/registry.json` 或 `agents/source/` | `<python> scripts/sync_agent_adapters.py` | `<python> scripts/sync_agent_adapters.py --check` | 每个智能体宿主适配器都与智能体注册表和源文件一致。 |
| `rules/registry.json` | `<python> scripts/sync_cursor_rule_adapters.py --update` | `<python> scripts/sync_cursor_rule_adapters.py --check` | 每个 Cursor Rule 适配器都与 Rule 注册表一致。 |

只有当规范源的变更属于已授权变更集，或用户明确授权根据当前规范源校正派生输出时，才运行会修改状态的
同步器；否则运行其只读漂移检查并报告任何差异。

## 维护者授权的修改

维护外部 Skill 时，运行 `<python> scripts/update_external_skills.py --check`。只有获得用户明确授权，
才能使用 `--update`，并可选择用 `--source owner/repository` 限定范围。应用 `Project Contracts`
中的外部 Skill 所有权边界；要求更新器报告收敛结果，并审查由此产生的每一项 Skill、锁文件和许可证
diff。

## 完整变更验证

在声称验证完成前，应覆盖已声明的比较基准、已暂存和未暂存的变更、未跟踪路径、工具生成的影响，以及
每个受影响的加载、生成、所有权、交付或运行时界面。列出每个未覆盖的路径或界面，运行每项必需的非修复
基线检查，以及任何受影响责任方或活动配置要求的额外非修复检查；在所有受影响路径和界面都被覆盖且每项
必需检查都通过前，不得声称验证完成。

基线验证包括上述 `VERSION`、智能体适配器和MCP 配置适配器的只读漂移检查，还包括：

| 用途 | 命令 |
| --- | --- |
| 仓库级契约测试 | `<python> -m unittest discover -s tests -p 'test_*.py'` |
| Diff 空白字符和冲突标记完整性 | `git diff <comparison-point> --check` |

## 已有 Skill 的交接

初始化或校正目标仓库的 `.agents` Rules、Skills、智能体、MCP 声明以及由 Setup 管理的智能体宿主投影时，
交给 `setup-project-agents` 处理。
