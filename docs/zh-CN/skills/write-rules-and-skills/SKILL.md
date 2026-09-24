---
name: write-rules-and-skills
description: 编写或修订一个英文 Rule 或 Agent Skill。
---

# 编写 Rule 与 Skill

交付一个**Candidate**：一份 Rule 或 Skill 及其范围内的配套资源。当前 Agent 担任 Controller；对齐前阅读 [Controller 契约](references/controller.md)，并在整个流程中遵守。

只有 Author 负责编写。Quality、Change 和 Correctness 判断结果；Correctness 可委派 Runner 获取有界观察。Controller 管理对齐、证据、角色、轮次和收尾，各角色保留自己的判断权。

在已确立的用户授权内工作。仓库可见性不代表权限；未经用户另行授权，本工作流不授予发布、安装、提交、推送、发行、翻译、网络访问或其他下游效果的权限。

## 1. 对齐

按照 Controller 契约确定 Candidate、所有者、依赖和自包含的 Author brief。写入前解决实质性的选择、事实、访问和权限问题。如果无法完成对齐，返回 `NEEDS_INPUT` 并指出准确缺口。

## 2. 冻结任务

将 `<skill-root>` 解析为本次加载的 Skill 目录，并查看 `python "<skill-root>/scripts/candidate_evidence.py" --help`。在任何 Candidate 写入前，冻结以下内容：

- **基线：**使用该 CLI 捕获完整 Candidate 和指纹。快照、审查记录和验证日志保存在 Candidate 范围之外。
- **权限：**记录准确的获准操作与权限、不自动修复的验证命令，以及有限的运行时和资源边界。移动需明确授权；允许新增和删除不等于允许移动。保留无关的已暂存、未暂存和未跟踪工作。
- **治理文本：**完整保留 Candidate 中所有治理指令的写入前副本，包括本 Skill。本次调用由该副本治理；编辑后的文本仅在后续调用中生效。

指定一位常驻 Author 负责编写和修复。选择 [Integrated 或 Independent Review](references/controller.md#choose-and-adjust-review-topology)，让每个身份阅读分配给自己的契约。

## 3. 编写与验证

确认 Candidate 仍与基线一致。启动 Author 时，将 brief 作为唯一会话上下文，另提供基线位置、指纹和 [Author 契约](references/author.md)。完整用户意图记录由 Controller 和 Correctness 保留。

**每次 Author 返回后**，捕获完整 Candidate 并应用以下门槛：

| 返回或证据 | 行动 |
| --- | --- |
| 经确认来自 Author 的 `COMPLETE`，且可归属的变更均在冻结范围内 | 运行验证。 |
| `NEEDS_INPUT` 或 `BLOCKED` | 检查边界，将部分变更保留为证据，清理并返回该结果。 |
| 越界或无法确定归属的变更 | 保留不确定状态，返回 `BLOCKED`。 |

以不自动修复的方式运行每条已冻结、由所有者支持的验证命令。记录命令、退出状态和当前指纹；全部通过后才能开始审查。

- **Candidate 导致的失败：**将证据交给同一位 Author，完成一次连贯修复，再重复返回门槛检查和验证。
- **缺少用户控制的输入或权限：**返回 `NEEDS_INPUT`。
- **其他未解决的失败，或修正未带来新证据或进展：**返回 `BLOCKED`。

## 4. 审查与修正

让所有 Reviewer 在同一指纹上开始审查，提供[公共 Reviewer 契约](references/reviewer.md)、各自的专业契约及其中要求的证据输入：

| 视角 | 判断 |
| --- | --- |
| [Quality](references/quality-reviewer.md) | 当前工件是否清楚、精练、可用？ |
| [Change](references/change-reviewer.md) | 变更是否保留并实现了已接受的含义？ |
| [Correctness](references/correctness-reviewer.md) | 结果是否忠实、安全地实现用户意图？ |

提供拓扑、Candidate 路径、指纹、轮次、稳定的文件证据，并向 Change 和 Correctness 提供基线位置。Independent 身份仅接收各自视角的上下文；Integrated 身份接收三者的并集。拓扑不变时保留相同身份，最多**三轮**。

每轮有三个步骤：

1. **审查。**Reviewer 将 finding 和必要问题直接交给负责角色。跟踪返回，不判断或转述 finding；每次 Reviewer 返回后，验证 Candidate 指纹未变。
2. **修复。**仍有 finding 时，Author 等待所有适用角色返回，再做一次连贯修复。
3. **重新验证。**应用 Author 返回门槛和全部冻结检查。下一轮，每个审查身份重新检查完整的新指纹。

第三轮后仍有阻断性 finding，返回 `BLOCKED`。需要[切换拓扑](references/controller.md#choose-and-adjust-review-topology)或遇到[对齐问题](references/controller.md#maintain-alignment-and-handle-blockers)时，遵循 Controller 契约。Correctness 在冻结边界内负责运行时证据。

## 5. 收尾与交接

每条退出路径都要收尾。必要角色不可用、越过边界、Candidate 状态不再可信，或运行时工作无法终止或清理时，安全停止。结束活动角色，记录残留状态，并检查最终 Candidate 边界。

返回：

- Candidate 类型、准确路径、最终指纹，以及绑定该指纹的 Author 语义摘要；
- 拓扑和分别列出的 Quality、Change、Correctness 结果，包括 Correctness 对意图忠实性的覆盖；
- 验证命令和结果，以及使用 Runner 时的场景与观察；
- 剩余风险、残留状态，以及 `COMPLETE`、`NEEDS_INPUT` 或 `BLOCKED`。

只有三个视角都返回 `PASS`，且每条验证命令都在同一最终指纹上通过，才能返回 `COMPLETE`。
