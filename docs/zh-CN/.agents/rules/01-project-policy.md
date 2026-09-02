# 项目政策

**强度：** Mandatory  
**适用范围：**项目拥有的生成、交付或安装表面；Setup 管理的状态；当前契约的移除；公开暴露；
以及对这些变更的验证。下文中的规范所有权、契约与暴露及验证义务不适用于由
`.agents/skills/write-shared-rules-and-skills/**` 或
`.agents/skills/write-setup-authoring-contracts/**` 负责的工作。

## 规范所有权

每个受影响的生成、交付或安装表面必须有唯一的规范所有者。修改其规范输入，并使用所属的生成器或
同步器。保留以下源文件映射：

- `VERSION` -> `scripts/sync_plugin_version.py`
- `mcp/registry.json` -> `scripts/sync_mcp_adapters.py`
- `agents/registry.json` 或 `agents/source/` -> `scripts/sync_agent_adapters.py`
- `rules/registry.json` -> `scripts/sync_cursor_rule_adapters.py --update`

由 Setup 管理的写入和删除必须限于已声明的所有权范围内，保留无关状态、用户拥有的状态和机密，
并在出现所有权或摘要冲突时停止。

## 契约与暴露

移除当前契约时，必须同时移除其已退役的实现、文档、测试和处理逻辑。仅当已接受的当前契约有要求时，
才添加兼容性支持。

表面必须通过其声明的所有者和路由进行交付和暴露。目标状态不得成为插件的规范权威，公开清单只能
暴露已声明的公开表面。

## 验证

更改项目自有的英文 Rule 或 Skill 后，必须使用 `smartkit:translate-agent-artifacts` 同步其简体中文文档镜像。

运行受影响的所有者和表面所要求的、与变更规模相称的非修复检查，审查生成的 diff，并运行
`git diff <comparison-point> --check`。所有必需检查必须通过，才能报告完成或成功。如果必需检查失败或
无法运行，应修正范围内的原因并重新运行；否则应停止并报告失败或阻塞项，且不得声称已完成。
