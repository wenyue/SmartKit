# Ponytail 设计参考

日期：2026-09-23。性质：面向维护者的非规范研究笔记，不改变 SmartKit 的规则、技能或授权边界。

后续采纳方案以 [规格 #5](https://github.com/wenyue/SmartKit/issues/5) 和
[ADR 0015](../adr/0015-patch-external-skill-snapshots.md) 为准；下文建议保留为早期分析，
不代表最终选择。后续核验已固定上游提交为 `e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156`。

## 来源与范围

本次阅读 DietrichGebert/ponytail 的 `main` 分支第一方源码；读取时
[package.json](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/package.json)
声明版本为 `4.10.0`。未取得提交 SHA，以下分支链接会随上游更新；未安装插件或运行其测试、基准。
项目流行程度、实际活跃用户数没有独立核验，不能据此推导设计正确性。

## 已确认的设计

Ponytail 并非单纯依赖 Agent 按需发现 Skill：
[指令构建器](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/hooks/ponytail-instructions.js)
直接读取核心 `SKILL.md`，移除 frontmatter，并按当前级别过滤其他级别的表格行和示例，保留其余正文。
读取失败时使用内置备用指令。
[Claude/Codex Hook 配置](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/hooks/claude-codex-hooks.json)
注册会话开始、子 Agent 开始和用户提交事件；
[启动实现](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/hooks/ponytail-activate.js)
负责激活状态并输出规则上下文。因此，“文件是 Skill”与“约束是否持续生效”是两个不同问题。

| Skill | 源码中的用途 | 对 SmartKit 的参考判断 |
| --- | --- | --- |
| [ponytail](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail/SKILL.md) | 持续的简化模式；按需求必要性、仓库已有实现、标准库、原生能力、已有依赖等顺序选择方案；有 lite/full/ultra 级别。 | 值得借鉴明确的选择次序；不宜把最少行数、文件数作为通用最优目标。 |
| [ponytail-review](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail-review/SKILL.md) | 审查 diff 的过度设计，列位置、删除或替代方案及预计减行数；不修复，不承担完整正确性审查。 | 借鉴聚焦检查及可操作输出；建议依需求、行为等价证据决定是否删除。 |
| [ponytail-audit](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail-audit/SKILL.md) | 把上述检查扩展到全仓库，按可能删减量排序；一次性报告。 | 借鉴区分变更审查与存量检查；全仓库覆盖与成本需要明确。 |
| [ponytail-debt](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail-debt/SKILL.md) | 扫描标记注释，按文件汇总简化内容、能力上限与升级触发条件，标出缺少触发条件的项目；默认只读。 | 最值得借鉴的是“局部记录 → 可检索清单”的闭环，而非品牌前缀。 |
| [ponytail-gain](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail-gain/SKILL.md) | 展示预先写入的基准成绩；明确禁止虚构当前仓库的节省值。 | 借鉴不制造不存在的对照基线；不建议新增只展示固定成绩的 Skill。 |
| [ponytail-help](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail-help/SKILL.md) | 展示模式、命令、配置及更新速查表，不改变状态。 | 插件入口较多时有用；内容应与实际入口保持同步。 |

## `ponytail:` 注释的含义

核心 Skill 规定：只在有已知限制的刻意简化处标注，例如全局锁、二次复杂度扫描、简单启发式，并写出限制及升级路径。
debt Skill 再把这些注释转成清单，并统计缺少升级触发条件的条目。
这不是编译器指令，也不是豁免验证、错误处理或安全要求的许可证。
依据：[核心 Skill](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail/SKILL.md)、
[debt Skill](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail-debt/SKILL.md)。

建议借鉴“目前选择为何足够、何时不再足够、届时如何改”的信息结构，而非强制给每个简洁实现打标。
正常使用标准库不等于欠债；源码里没有这种标记也不代表仓库不存在技术债。
未来若采用，应先区分永久设计理由、实际缺陷与有条件接受的限制，并沿用项目现有跟踪机制。

## 不能直接照搬的细节

- 核心 Skill 同时要求尊重明确需求，又鼓励先交付简化版再质疑复杂需求；审查还把单实现接口、单调用者层等列为搜索目标。它们适合作为调查线索，不能自动证明可删除，否则可能忽略契约、隔离边界和已确认需求。来源：核心与 review Skill。
- debt 的扫描示例主要覆盖 `#` 和 `//`，并要求按技术栈补充注释前缀；其默认输出只是即时视图，并非有稳定标识、生命周期和验收条件的完整债务系统。来源：debt Skill。
- 存在可见的资料不同步：gain 仍展示早期 5 个任务、3 个模型的 80–94% 减行数及 47–77% 降成本；当前
  [README](https://raw.githubusercontent.com/DietrichGebert/ponytail/main/README.md)
  已改为真实 Agent 编辑仓库、12 个任务、每任务 4 次、Haiku 4.5 的约 54% 减行数、20% 降成本，并说明旧测试基线会放大差距。这支持“帮助与指标保持单一数据来源”的建议，不支持声称 Ponytail 的效果可直接外推至 SmartKit。

## 对三个问题的结论

SmartKit 当前的 `rules/core-instruction-governance.md` 已将 `rule-<domain>` 定义为通过原生 Skill 发现机制暴露的 Rule；`skills/rule-code/SKILL.md` 和 `skills/rule-code-comment/SKILL.md` 分别拥有代码设计和注释约束。因此，需要分别判断约束的政策属性、加载方式以及是否产生独立任务成果；代码约束已经采用 rule-led Skill，并不需要再迁移成另一套重叠流程。

以下是建议，非上游事实：持续适用的约束保留在现有 Rule 所有者；需要明确触发、范围、产物及完成条件的审查、审计、债务汇总才采用任务 Skill。Ponytail 的 Hook 恰好说明，改成 Skill 文件本身并不能保证持续约束。
优先参考选择次序、窄范围审查、可检索的设计取舍记录；谨慎参考模式强度、减行数排名和固定成绩展示。未在本次研究中实施任何规则或技能变更。
