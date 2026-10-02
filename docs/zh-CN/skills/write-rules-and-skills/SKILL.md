---
name: write-rules-and-skills
description: 编写或修订一个英文 Rule 或 Agent Skill。
---

# 编写 Rule 与 Skill

编写能帮助 Agent 做好具体工作的工件：作出正确决策，理解重要约束，并取得有用的结果。好的 Rule 让政策便于应用；好的 Skill 提供任务所需的知识和方法。堆积所有可能适用的指令，并不能让它们变得更好。

每次调用产出一个 **Candidate** ：一份 Rule 或 Skill 及其范围内的配套资源。当前 Agent 担任 Controller。阅读 [Controller 契约](references/controller.md)，准备任务并管理整个过程直至交接。

## 工作如何推进

Controller 确立真实需求、可编辑范围、证据和完成条件。一位 [Author](references/author.md) 接收任务上下文和简洁的 brief，从初稿到修订都由其负责编写。brief 帮助定位工作，传达用户的要求及其原因，不规定如何组织内容。

Author 返回完整初稿且必要检查通过后，从三个不同视角审查：

| 视角 | 问题 |
| --- | --- |
| [Quality](references/quality-reviewer.md) | 预期读者能否顺利理解和使用它？ |
| [Change](references/change-reviewer.md) | 变更是否保留了应保留的含义，或有意修改了应修改的含义？ |
| [Correctness](references/correctness-reviewer.md) | 它是否满足真实需求，规定的行为能否奏效？ |

Reviewer 遵循[公共行为要求](references/reviewer.md)及各自的专业契约。他们指出有证据支持的缺陷；Author 选择连贯的修复方式。Controller 按任务需要安排独立身份，让所有判断对应同一版本，并解决需要用户决定的问题。需要观察实际行为时，Correctness 可以委派一个任务有界的 [Runner](references/runner.md)。

只要仍有实质性缺陷，且约定的迭代预算允许取得有效进展，就重复编写、检查和审查。验收标准保持不变。完成意味着同一份最终 Candidate 已通过必要检查和全部三项审查；初稿看起来有希望或预算已经耗尽，都不等于完成。

工作流返回 `COMPLETE`、`NEEDS_INPUT` 或 `BLOCKED`，并附上确切文件及支持证据。它在任务授权内运作。发布、安装、翻译、提交和其他下游操作仍需各自的授权。重写本 Skill 时，本次调用始终由其写入前的指令治理。
