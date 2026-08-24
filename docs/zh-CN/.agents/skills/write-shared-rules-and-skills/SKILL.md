---
name: write-shared-rules-and-skills
description: 通过探针合格的软隔离和显式可移植性证据，编写或实质性修订跨项目 SmartKit Rule 或 Skill；不包括项目本地工件和 Setup Authoring Contract。
---

# 编写共享 Rule 和 Skill

负责一个共享 SmartKit Rule 或 Skill 的源上下文排除、显式共享依赖和可移植性证明。公共
`write-rules-and-skills` Skill 负责普通编写、Pruning、机器验证、Semantic Review、Acceptance
和修正。本项目私有 Skill 提供更严格的共享 Context Packet 和共享通过条件。

候选项变更公共编写 Skill、其 Reviewer 契约或 Acceptance Standard 时，应完整阅读
[`references/standard-change.md`](references/standard-change.md)。

## 使软隔离合格

构建任何语义 packet 前，应用公共 Skill 的 Soft-Isolation Probe。Probe 必须通过随后供 Author、
Pruner、Reviewer 和 Acceptance Runner 使用的同一种 fresh-Agent 启动机制运行。出现任何项目 Rule
正文、SmartKit Rule 正文、Harness Rule 正文、完整 Skill 正文、继承的父级内容、无效对照、工具使用、
文件读取、委派或 fresh 启动不可用时，工作流都将失败，且没有 fallback。

## 构建共享编写输入

控制器只能检查源仓库以收集已接受意图、完整候选项及其拥有的资源、公共编写指导、显式选定的 SmartKit
共享 Rules 或 Skills、已声明的共享依赖和可移植性证据。它必须从每个语义 packet 中排除源项目 Rules、
项目特定政策、未声明文件、Author 推理和无关对话。

要求一个代表性目标上下文。只有行为依赖可变的项目 seam 且直接证据不足时，才增加第二个实质不同的
上下文。仅名称或布局不同的上下文不构成额外证据。每项候选依赖都必须出现在显式 packet 中；未声明的
依赖是阻塞性的可移植性失败。

## 调用公共工作流

以控制器身份调用 `write-rules-and-skills`，并复用当前顶层 Probe 的 `PASS`。它的 Soft-isolated、
无工具 Author 接收共享编写输入，并返回完整替换内容或 `CONTEXT_REQUIRED`。控制器将返回内容原样应用
到规范源路径并验证。所有语义修正都返回 Author；控制器绝不编辑其含义。

使用另一个 Soft-isolated Pruning Agent，为每个 Candidate Revision 使用新的 Soft-isolated
Reviewer，并为每个 case 使用新的 Soft-isolated Acceptance Runner。每个角色都接收完整的角色专用
Context Packet，且不接收源项目的环境证据。启用工具的 Acceptance 仍受公共 Skill 中匹配的 Probe
和停止规则约束。

## 证明可移植性并完成

除每项公共门控外，共享 Acceptance 还要求当前 Probe `PASS`、完整的已声明依赖闭包和代表性目标证据。
依赖虚构事实或仅源项目事实的 Candidate Revision 无法通过可移植性，即使其普通门控已经通过。

成功要求同一个规范 Candidate Revision 同时通过公共门控和共享可移植性检查。报告 Probe 结果、已声明
依赖、代表性上下文、机器命令和退出、语义裁决、修正以及未测试界面。将 packet 和证据保留在活动 Agent
上下文中。发布、commit、push 和 release 仍由其现有责任方负责。
