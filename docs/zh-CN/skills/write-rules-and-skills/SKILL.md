---
name: write-rules-and-skills
description: 编写、修订或重写一个英文 Rule 或 Agent Skill。
---

# 编写 Rule 与 Skill

编写能帮助 Agent 做好具体工作的指导。用最少的必要指导，让具备一般能力的读者在通常使用中极大概率形成预期的一致理解。理解对齐优先于简洁：保留已接受的结果、后果重要的边界，以及有助于这种理解的解释。依靠实际判断把握这个度，而不追求确保每一种可能的误读都不会发生。

每次调用产出一个 **Candidate** ：一份 Rule 或 Skill 及其范围内的配套资源。当前 Agent 担任 Controller；阅读 [Controller 契约](references/controller.md)，确立请求、权限、证据和完成条件。一位常驻 [Author](references/author.md) 负责设计和编写，并持续承担后续修复。

重写时，从工件当前的目标和必要约束出发，重新考虑其内容、结构和机制。文件布局和 Skill 元数据也属于这一设计。合理的选择可以保留，但仅润色现有句子不算完成重写。目标 Skill 有 `AUTHORING.md` 时先阅读它。只有当某个有意的取舍很可能被后来的编写者撤销、且误撤代价高昂时，才创建或更新这份记录；显而易见或容易撤回的选择不必记录。记录决定及其理由，只有值得记住时才补充备选方案或后果。正常使用目标 Skill 时不加载这份记录。

完整初稿通过必要检查后，取得三项判断：

| 视角 | 问题 |
| --- | --- |
| [Quality](references/quality-reviewer.md) | 预期读者能否顺利理解和使用它？ |
| [Change](references/change-reviewer.md) | 变更是否保留了应保留的含义，或有意修改了应修改的含义？ |
| [Correctness](references/correctness-reviewer.md) | 它是否满足真实请求，规定的行为能否奏效？ |

Reviewer 遵循[公共行为要求](references/reviewer.md)及各自的专业契约。他们指出有证据支持的缺陷；Author 选择修复方式。Controller 选择所需的独立身份，让所有判断对应同一版本，并将属于用户决定的问题交给用户。需要观察行为时，Correctness 可以委派一个任务有界的 [Runner](references/runner.md)。

在约定的迭代预算内重复编写、检查和审查。验收标准保持不变；可选改进不必延迟交付已经通过验收的结果。只有同一份最终 Candidate 通过全部必要检查和三项审查，才能返回 `COMPLETE`。否则返回 `NEEDS_INPUT` 或 `BLOCKED`，指出未解决的依赖并保留证据。

本工作流不授予任何下游发布、安装、翻译、提交或其他权限。重写本 Skill 时，本次调用由其完整的写入前指令治理。
