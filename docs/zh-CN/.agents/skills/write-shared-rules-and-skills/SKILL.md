---
name: write-shared-rules-and-skills
description: 编写或修订可移植的跨项目 SmartKit Rule 或 Skill；不包括项目本地制品和 Setup Authoring Contract。
---

# 编写共享 Rule 与 Skill

确认恰好一个可移植的跨项目 SmartKit Rule 或 Skill 符合条件，通过公共 [`write-rules-and-skills`](../../../skills/write-rules-and-skills/SKILL.md) 工作流编写，并在交接时闭合其可移植性义务。

## 原则

- **可移植性增量。**本 Skill 只负责资格判定和交接闭合。将已封闭的输入原样交给公共工作流，不改造或重建其机制，并保留其终止结果——`COMPLETE`、`NEEDS_INPUT` 或 `BLOCKED`——以及交接内容。

在判定请求资格和闭合公共交接时，都要完整阅读[可移植性参考](references/portability.md)。

## 1. 判定资格并准备输入

应用参考文件中的所有权、证据和输入封闭要求。只有得到一份已封闭的可移植性输入时才继续；否则遵循其中的终止路由并停止。

## 2. 调用公共工作流

使用已封闭的输入调用公共工作流，并等待其结果。

如果变更的是本 Skill 自身，整次运行都应使用 Author 开始工作前的公共和私有合同；编辑后的文本只在后续调用中生效。

## 3. 闭合可移植交接

应用参考文件中的交接闭合要求，不重新解释公共结果。保留公共交接，并附上得到的闭合说明。
