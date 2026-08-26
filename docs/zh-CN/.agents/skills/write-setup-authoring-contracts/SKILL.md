---
name: write-setup-authoring-contracts
description: 编写或修订 setup-assets/blueprints 下仅用于判断的 Setup Authoring Contract；不包括生成的目标和共享 SmartKit 工件。
---

# 编写 Setup Authoring Contract

创建最小而完整的描述性契约，使 setup 能根据目标仓库证据编写未来的项目 Rule 或 Skill。应用
`writing-for-agents`。这个项目私有 Skill 只负责 `setup-assets/blueprints/` 下的 Setup Authoring
Contract；它不编写生成的目标或共享 SmartKit 工件。

## 鉴定角色和契约

完整阅读 [`references/setup-authoring-contract.md`](references/setup-authoring-contract.md)。
使用已接受的变更、当前蓝图、setup catalog、管辖契约和代表性目标证据来应用其中的 Setup
Contract Frame 和仅用于判断的边界。

契约不得依赖 `CONTEXT.md`、`CONTEXT-MAP.md` 或仅由这些文档定义的术语。持久含义必须来自
已接受的用户决定、Issue、Spec、ADR、管辖契约、setup catalog 或可观察的实现证据。

完整阅读公共 [`Role Launch`](../../../skills/write-rules-and-skills/references/role-launch.md) 定义。
显式选择其 Default Fresh Role Adapter。应用 Role Launch Interface、Default Fresh Role Adapter、
Preauthorized Update Envelope、Role Boundary Audit 和工作流最终处置章节，以管辖访问、权威、有界
更新、审计和 teardown。

恰好鉴定三个身份：Controller、一个持续 Author 和一个持续 Static Reviewer。完整的本地序列是持续
Author → 适用的机器验证 → 一个持续 Static Reviewer；公共评估阶段不进入此流程。机器 PASS 前只
启动 Author，之后才启动 Static Reviewer。如果宿主无法保留这三个身份以及已加载的权威或访问契约，
则停止；不得替换持续 Author。只有 Author 获得候选项写入权限，Static Reviewer 保持只读。不要求
并行 Reviewer 容量。

## 编写和验证

在取得锁或启动 Author 前，冻结完整的已接受输入和已加载的更新范围：声明之后可由 Context Supplement
填充的每个语义证据或依赖槽位，以及之后可扩展的每个候选项自有准确访问范围、路径类别和操作模式。
候选项写入仍限于 `setup-assets/blueprints/` 下的明确 allowlist。启动角色前，将 Default Fresh Role
Adapter 的冻结后 Probe 记录为 `NOT_REQUIRED`。

取得候选项单一写入者锁，并将其保留到工作流最终处置完成。启动一个持续 Author。向其提供完整的
已接受输入、当前契约、所选目标证据和明确 allowlist。Author 只编辑该 allowlist，并为每个 finding
决定 `repair` 或 `decline`。它只返回以下一种状态：

- `COMPLETE`：Author Change Summary、变更路径、finding 处置，以及 Repair Scope 之外的任何
  不确定性；
- `CONTEXT_REQUIRED`：缺失的事实，以及编写为何需要该事实；或
- `ACCESS_REQUIRED`：准确的路径、访问模式和原因。

对于 `CONTEXT_REQUIRED` 或 `ACCESS_REQUIRED`，只从冻结范围中提供符合条件的有界更新，并继续
同一个持续身份。超出范围的实质变更返回 `ALIGNMENT_REQUIRED`，并要求开始新运行。符合条件的更新
不可用时，以该请求状态停止。取得锁或启动角色后的每次停止都遵循**完成**下的最终处置契约。Author
不验证或审查自己的工作。

每次 Author 回调后，应用已加载的 Role Boundary Audit，并强制只有一个候选项写入者。每次 Author
写入都会创建新的 Candidate Version；回调后，对每个候选文件计算紧凑的 Candidate Fingerprint。

启动 Static Reviewer 前，运行每项适用的机器检查，并保留每项检查的准确命令、最终退出状态和
相关输出。失败时，将该证据和有界 Repair Scope 交给同一个 Author。每次 Author 变更后，重复
审计和指纹计算，再使用变更路径、Author Change Summary 和变更前后的指纹，判断新的 Candidate
Version 可能影响哪些先前机器结果。重新运行失败的检查以及每项失效或依赖检查。只有变更不可能
影响某项结果所证明的内容时，才复用该结果。同一失败连续两轮存在且没有新的有依据方案时，因无
进展停止。只有每项适用机器检查都具有同一个当前 Candidate Version 的 PASS 证据时，才能启动
Static Review。

## 静态审查循环

启动一个全新的 Static Reviewer，并在整个修正循环中保留它。向其提供已接受要求、要保留的义务、
管辖证据、完整 Candidate Version 和一个代表性 walkthrough 输入。它检查：

- 仅用于判断的形式：契约描述所需含义和决定，但不规定生成过程；
- 最小性：删除任何指令都会改变有依据的生成或停止结果；
- 语义完整性：每项可以改变行为的目标义务都会被获取，或导致停止；以及
- 代表性 walkthrough：一个有依据的目标输入在不虚构项目事实的情况下，到达恰好一个生成或停止
  结果。

每个 finding 包含稳定 ID、问题和支持证据、具体反例、候选项位置、`critical`、`material` 或
`advisory` 严重程度、估计的 Repair Scope、受影响的义务或表面，以及保留约束。字段不适用时，
使用 `N/A` 并说明原因。`critical` 涵盖语义、权限、安全、所有权、
可执行性或退出失败。`material` 涵盖有依据且明显降低信息质量、可维护性或可靠性的缺陷。两者通常
都值得修复。`advisory` 涵盖较小的改进或存在多个有效方案的选择；如果有依据的修复仅涉及一两句
话或一个小区块，并且能保留语义，则默认值得修复。Reviewer 指出问题，而不提供替换文本。Author
决定 `repair` 或 `decline`；同一个 Reviewer 决定 finding 是否仍值得修复。

Static Reviewer 保持只读。每次 Reviewer 回调后，应用已加载的 Role Boundary Audit，并确认
Candidate Fingerprint 未变更。

Reviewer finding → 持续 Author 修正 → 同一个 Reviewer 复查，这一循环持续到没有 finding 值得
修复。每次 Author 写入后，重复边界审计和指纹计算。Reviewer 复查前，应用上述同版本机器结果
失效判断和机器失败修正循环。同一未解决 finding 连续两轮存在且没有新的有依据方案时，因无进展
停止。PASS 后结束 Static Reviewer。不要启动 Quality 审查者对、Correctness 审查者对或可执行
Acceptance。

## 完成

取得锁或启动角色后，在每次成功或终止停止时应用已加载的工作流最终处置契约。关闭持续 Author、
Static Reviewer 和其他每个可安全结束的身份，然后仅在它们的活动结束后释放候选项单一写入者锁。
报告任何 teardown 或锁释放失败，并且绝不为该结果声称干净成功。

成功要求同一个 Candidate Version 取得机器验证 PASS 和 Static Reviewer PASS。报告契约路径、
所有者、指纹、机器命令和退出状态、审查 verdict、回退、角色边界审计，以及未解决或未经测试的
表面。将已接受的契约交给 `setup-project-agents`；生成、commit、push 和发布留给其所有者。
