---
name: write-rules-and-skills
description: 编写或修订一个英文 Rule 或 Agent Skill。
---

# 编写 Rule 与 Skill

**制品**指一个 Rule 或 Skill。**Candidate**指当前正在编写和审查的制品及其范围内的配套资源。

当前 Agent 是 Controller。对齐任务之前，阅读 [Controller 角色](references/controller.md)，并在整个工作流中遵循该契约。

## 原则

- **独立判断。**Author 负责 Candidate，Reviewer 负责各自的判断，需要时由 Runner 提供运行时事实。Controller 负责理解任务、分配职责和编制 Author brief；它不编写 Candidate，也不替代专业结论。
- **权限有界。**在仓库中可见不代表拥有含义或权限。除非用户另行授权，否则本工作流不授予发布、安装、commit、push、release、翻译、网络访问或任何其他下游操作的权限。
- **同一指纹上验收。**只有三个专业视角在同一指纹上全部返回 `PASS`，并且自动验证也在该指纹上通过时，才能成功结束。

## 1. 对齐任务

遵循 Controller 契约完成任务对齐。只有当一个 Candidate 和一份自包含的 Author brief 能够表达已接受的结果、所有者依赖的状态明确，并且不再缺少任何实质性选择、事实、访问条件或权限时，才进入冻结阶段。否则返回 `NEEDS_INPUT`，准确指出尚未解决的输入。

## 2. 冻结 Candidate 和审查范围

将当前已加载 Skill 的目录解析为 `<skill-root>`，并调用 `python "<skill-root>/scripts/candidate_evidence.py" --help`。

首次写入之前，使用该 Python CLI 捕获完整 Candidate 基线和指纹。基线快照、审查记录和验证日志等临时工作流证据应保存在 Candidate 文件范围之外，使其与交付物分离，并且不影响 Candidate 指纹。分别冻结写入范围、验证命令和权限；允许新增和删除并不等于允许移动。保留无关的 staged、unstaged 和 untracked 工作。

如果 Candidate 包含本 Skill 或其他治理指令，还要冻结其完整的写前文本，并在本次运行余下阶段以该副本为权威。新编写的文本在下一次调用前仍只是 Candidate 证据，不能支配对自身的审查。

为整项任务分配同一个常驻 Author。依据 Controller 的[审查独立程度标准](references/controller.md#choose-review-independence)选择审查拓扑。

Controller 管理这一拓扑，但不代替专业判断。采用 Integrated Review 时，启动一个身份，并向其提供 Reviewer 公共合同和全部三个专业合同。采用 Independent Review 时，启动三个身份，每个身份都获得公共合同，但只获得自己的专业合同。各身份自行打开分配给自己的文件；Controller 不打开这些文件。

## 3. 编写并验证

确认 Candidate 仍与基线一致，然后启动 Author，并将 Author brief 作为其唯一的会话上下文。同时提供基线位置、当前指纹和 [Author 角色](references/author.md)的指针；不要提供完整的用户意图证据。只有该 Author 可以写入 Candidate。

Author 返回后，再次捕获完整 Candidate。只有经过身份确认、由 Author 返回 `COMPLETE`，并且变更可归因于该 Author 且符合冻结的写入范围时，才能继续。Author 返回 `NEEDS_INPUT` 或 `BLOCKED` 时，应在完成边界检查和清理后以该结果结束任务；保留任何局部变更作为证据，但不得将其接纳为验证或审查对象。范围外或无法确定归属的变更应视为 `BLOCKED`，并且不得回退状态不明确的内容。

在审查前运行已冻结、由所有者支持且不会自动修复内容的自动验证。开始审查和最终返回 `COMPLETE` 前，当前指纹上的每条适用命令都必须成功。记录每条命令及其退出状态。如果失败由 Candidate 引起，将证据交给同一个 Author 进行一次连贯修复，然后重新应用 Author 返回门槛、捕获指纹并执行验证。缺少用户控制的事实、访问或权限时返回 `NEEDS_INPUT`；其他未解决的失败，或在没有新证据和进展的情况下反复修正时，返回 `BLOCKED`。这两种情况都不授予写入 Candidate 的权限，也不允许继续审查。

## 4. 审查并修正

### 启动审查

在同一指纹上按照选定拓扑启动审查。向每个审查身份提供 [Reviewer 公共合同](references/reviewer.md)，并按照拓扑分配以下专业合同：

- [Quality Reviewer](references/quality-reviewer.md)
- [Change Reviewer](references/change-reviewer.md)
- [Correctness Reviewer](references/correctness-reviewer.md)

向每个审查身份提供分配的视角、审查拓扑、Candidate 路径、当前指纹和审查轮次。Change 和 Correctness 还应获得基线位置。对于文件中已有的证据，只提供位置而不复制内容；每份专业合同自行决定相应视角要读取哪些稳定证据。

只传递 Reviewer 无法从这些来源恢复的会话上下文：

- 对两种制品类型，Quality 都接收已接受的目标、仅存在于会话中的质量或表达约束，以及职责分配及其证据位置、受支持加载方式的假设、所有者依赖状态和调用方提供的职责分配规划（如有）。这些内容独立于 Author brief 提供；Quality 不依赖于收到该 brief。
- Change 接收要求的变更、保留与兼容性决策，以及 Author 的语义变更摘要。
- Correctness 接收完整的权威用户意图证据和 Author brief，并将二者作为不同输入；同时接收仅存在于会话中的关键行为与安全决策，以及自动验证结果。

Independent Reviewer 只接收其专业视角所需的上下文；Integrated Reviewer 接收三个视角所需上下文的并集。

### 执行审查轮次

只要拓扑不变，最多三轮审查都沿用相同身份。Reviewer 的证据、沟通和结果遵循公共合同与专业合同。Author 等待所有身份返回后，再进行一次连贯修复。Controller 只跟踪角色是否完成和审查轮次；它不转述，也不判断语义内容。

每次修复后都应用 Author 返回门槛，并在进入下一轮审查前运行自动验证。修复会产生新指纹，因此当前拓扑中的每个身份都要重新检查其完整证据。最多允许三轮；第三轮后仍有阻塞性 finding 时，返回 `BLOCKED`。

当 Reviewer 返回 `INDEPENDENT_REVIEW_REQUIRED`、Correctness 证明 Author brief 遗漏或曲解了用户意图、因实质性的意图歧义需要返回 `NEEDS_INPUT`，或 Correctness 返回 `RUNTIME_REQUIRED` 时，加载 [审查升级](references/review-escalation.md)中相应的分支。

每个 Reviewer 和 Runner 返回后，都要确认 Candidate 指纹没有变化。

## 5. 完成

当必需角色不可用、角色越界、Candidate 状态不可信，或者已启动的运行时检查无法终止或清理时，应安全停止。结束所有活动角色，记录任何残留状态，并执行最终 Candidate 边界检查。

只返回有用的交接内容：

- Candidate 类型和准确路径；
- Integrated 或 Independent Review，以及每个专业视角的最终结果；
- 自动验证命令和结果；
- 使用 Runner 时的场景和观察；
- Correctness 视角对用户意图的覆盖情况和一致性结果；
- Author 最终的语义变更摘要，并原样绑定到最终指纹；
- 剩余风险和残留状态；
- 最终指纹；以及
- `COMPLETE`、`NEEDS_INPUT` 或 `BLOCKED`。
