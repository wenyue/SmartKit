---
name: write-setup-authoring-contracts
description: 编写或修订 setup-assets/blueprints 下仅用于判断的 Setup Authoring Contract；不包括生成的目标和共享 SmartKit 工件。
---

# 编写 Setup Authoring Contract

编写最小而完整的描述性契约，使 setup 能依据目标仓库证据生成未来的项目 Rule 或 Skill。全程应用
`writing-for-agents`。这个项目私有 Skill 只负责 `setup-assets/blueprints/` 下的 Setup Authoring
Contract；生成的目标和共享 SmartKit 工件仍由各自的编写者负责。

## 1. 建立契约和工作流

完整阅读 [`references/setup-authoring-contract.md`](references/setup-authoring-contract.md)。使用已接受的
变更、存在时的当前蓝图、setup catalog、管辖契约和代表性目标证据，应用其中的 Setup Contract Frame
和仅用于判断的边界。对于已获授权的创建路径，以仓库证据确认不存在当前蓝图，作为明确基线。除非已接受
意图要求变更，否则保留有依据的现有语义。取得每项可能改变生成或停止结果的事实；遇到缺失时停止，不得
虚构目标事实、所有者、政策或操作。

持久含义必须来自已接受的用户决定、Issue、Spec、ADR、管辖契约、setup catalog 或可观察的实现证据。
`CONTEXT.md` 和 `CONTEXT-MAP.md` 不提供语义权威、证据、验证输入、依赖或持久术语。

如果已接受输入仍存在实质性的行为、所有权、权限、验证或退出歧义，则在取得锁、启动角色或写入 Candidate
之前返回 `ALIGNMENT_REQUIRED`。报告未解决的选择、现有证据、决策所有者以及每个选择的后果。只有当
每项未解决的实质选择都归用户所有，且 `grilling` 可用时，才引导用户显式调用它。当前调用仍以无效果的
`ALIGNMENT_REQUIRED` 结果结束；如果 `grilling` 关闭了每个实质分支，其共享决定将成为新编写运行的
已接受人工决策上下文。否则保持同一停止结果。这个由 Controller 所有的入口退出不同于有界更新请求和
语义角色的 `HUMAN_DECISION_REQUIRED`。

完整阅读公共
[`Frozen Job Design`](../../../skills/write-rules-and-skills/references/job-design.md)和
[`Role Launch`](../../../skills/write-rules-and-skills/references/role-launch.md)。应用 Frozen Job
Design 的授权、来源/能力类别和有界更新合同。原样应用 Role Launch，将其作为唯一固定运行时和
通用证据选择政策，包括其中的角色权威、Role Boundary Audit、直接通道、异常执行和工作流最终化
机制。

仅确认以下身份满足条件：Controller、一个在每个 Candidate Version 中保留的全新常驻 Author，以及一个在其
修正循环中保留的全新 Static Reviewer。本地序列为 Author → 适用的 Machine Validation → Static
Reviewer。当前版本取得 Machine PASS 或有依据的 `NOT_REQUIRED` 前只启动 Author，取得该结果后才
启动 Reviewer。公共 Quality Review、Correctness Review 和可执行 Acceptance 不进入此工作流。如果
宿主无法保留这些身份、已加载的权威和访问契约或排期，则按 Role Launch 停止；绝不替换常驻 Author。

在取得锁或启动 Author 前，根据 Frozen Job Design 冻结完整的已接受输入，并实例化 Setup 专属的
授权与有界更新 envelope，同时保留 Author 的`network: none`边界。列举每个符合 Context
Supplement 条件的必要事实槽位，以及每个符合访问扩展条件的已授权本地路径类别、外部来源与能力
类别和已授权模式。冻结一个准确的 Candidate Allowlist，其中只包含`setup-assets/blueprints/`下
预期的契约；只有 Author 获得其写入权限。
取得一个排他的 Candidate writer 锁。如果冻结接口能够明确证明没有取得锁，也不可能遗留锁状态，
则在启动 Author 前返回`LOCK_UNAVAILABLE`；如果某次尝试可能遗留锁状态，则转到**完成**。取得锁后
且 Author 进行任何写入前，Controller 对完整 Allowlist 计算指纹，并将该基线绑定到初始 Candidate
Version。在整个工作流最终化期间保留该锁。

只有当证据基础、仅用于判断的目标、身份、排期、allowlist、授权、发现类别、更新 envelope、预期
操作、锁接口和写入前指纹均已冻结，且不存在实质歧义时，本步骤才完成。

## 2. 编写一个完整 allowlist 的 Candidate Version

启动常驻 Author，并向其提供完整的已接受输入、当前蓝图或有证据的缺失创建基线、所选证据、编写指导、
准确 allowlist，以及一个 Authoring Scope 或有界 Repair Scope。Author 只编辑该 allowlist，负责
Candidate 含义和 finding 处置，并且不执行验证、审查、网络使用或委派。

Author 只返回 Role Launch 四种状态之一及其完整的权威 payload。`COMPLETE` 在适用时还包含 finding
处置。

只有在 `CONTEXT_REQUIRED` 或 `ACCESS_REQUIRED` 请求符合冻结的有界范围时，才满足该请求，然后继续
同一个 Author。符合条件的更新不可用时，将该请求保留为停止结果。实质性的范围外变更返回
`ALIGNMENT_REQUIRED`，并要求开始新运行。可能取得锁或启动角色后的每次停止都转到**完成**。

每次 Author 回调后，应用 Role Boundary Audit，并确认 Author 仍是唯一的候选项写入者。将绑定到上一
Candidate Version 的指纹作为写入前状态；发生写入时，分配新的 Candidate Version，对完整 Allowlist
计算指纹，并将写入后状态绑定到该版本。只有当可采纳的 `COMPLETE` 描述了当前完整 allowlist 的版本及其
指纹时，本步骤才完成。

## 3. 建立该版本的 Machine 结果

根据有依据的确定性表面判断适用性。不存在此类表面时，为当前 Candidate Version 记录 Machine
`NOT_REQUIRED`，并且不虚构检查。否则，运行每项适用的机器检查，但不修复 Candidate。在每条命令执行
前后立即对完整 Allowlist 计算指纹，并连同准确命令、最终退出状态和相关输出一起保留两个指纹。任何变化
都会使结果失效，并作为无法归因的 Candidate 变更按 Role Boundary Audit 停止；保留其证据，既不发送给
Author 修复，也不进入 Static Review。指纹未变时，失败会把命令证据和有界 Repair Scope 返回给同一个
Author。审计每次由此产生的 Author 回调并计算指纹。

对于每个新的 Candidate Version，使用变更路径、Change Summary 和变更前后指纹，判断它可能影响哪些
机器证据。重新运行失败的检查以及每项失效或依赖检查；只有变更不可能影响某项结果所证明的内容时，才复用
该结果。初始失败不算一轮。只有在失败 → 同一个 Author 修复 → 重新运行完成后，才完成一轮 Machine
分歧。同一失败在连续两个完整轮次中持续存在，且没有新证据或有依据的方案时，以 `NO_PROGRESS` 停止。

只有当一个当前 Candidate Version 取得有依据的 Machine `NOT_REQUIRED`，或每项适用检查都具有 PASS
证据时，本步骤才完成。之后才能启动 Static Reviewer。

## 4. 达到 Static Review 固定点

向持续存在的只读 Reviewer 提供完整的已接受要求、要保留的义务、管辖证据、当前完整 allowlist 的
Candidate Version，以及一个代表性 walkthrough 输入。它独立检查：

- **仅用于判断的形式：**契约描述所需含义和决定，但不规定 setup 的生成过程；
- **最小性：**删除任何指令都会改变有依据的生成或停止结果；
- **语义完整性：**每项会改变行为的目标义务都会被取得，或导致停止；以及
- **代表性 walkthrough：**一个有依据的目标输入在不虚构项目事实的情况下到达恰好一个生成或停止结果。

每个 finding 包含稳定 ID、问题和支持证据、具体反例、候选项位置、严重程度、估计的 Repair Scope、
有界修复方向、受影响的义务或表面，以及保留约束；字段不适用时，使用 `N/A` 并说明原因。严重程度为：

- `critical`：语义、权威、安全、所有权、可执行性或退出失败；
- `material`：有依据且明显降低信息质量、可维护性或可靠性的缺陷；或
- `advisory`：较小的改进，或存在多个有效方案的选择。

critical 和 material finding 通常值得修复。如果有依据的 advisory 修复只涉及一两句话或一个小区块，
并且能保留语义，则默认值得修复。Reviewer 指出问题，而不撰写替换文本；它负责每个 finding，并决定该
finding 是否仍值得修复，而且通过 Role Launch 的直接修正通道发送 finding。Author 独立选择 `repair`
或 `decline`，并负责每次 Candidate 修正；Controller 只处理冻结的控制平面。

每次 Reviewer 回调后，应用 Role Boundary Audit，并确认 Candidate Fingerprint 未变更。对于 finding，
继续 Reviewer finding → 同一个 Author 修正 → 适用的机器重放 → 同一个 Reviewer 复查。Author 写入后，
重复完整 allowlist 审计和指纹计算，然后在复查前应用 Machine 失效规则。初始 finding 不算一轮。只有在
Author 处置 → 同一个 Reviewer 重新评估后仍未解决时，才完成一轮 Static 分歧。同一 finding 在连续
两个完整轮次中持续存在，且没有新证据或有依据的方案时，以 `NO_PROGRESS` 停止。

只有当同一个 Reviewer 对同一个 Candidate Version 返回 PASS，且该版本取得 Machine PASS 或有依据的
Machine `NOT_REQUIRED` 时，本步骤才完成。结束 Reviewer；不启动其他公共评估角色。

## 5. 完成

角色启动、成功取得锁，或取得尝试可能遗留锁状态后，对成功和每个终止停止应用 Role Launch 工作流最终
处置。结束常驻 Author、Static Reviewer 和每个可安全结束的其他身份，同时保留报告和证据。只有在所有
角色活动结束后才释放锁。残留身份或无法释放的锁返回 `TEARDOWN_FAILED`；报告准确的残留状态，并且不得
声称干净成功。

成功要求同一个完整 allowlist 的 Candidate Version 取得 Static Reviewer PASS，以及 Machine PASS
或有依据的 Machine `NOT_REQUIRED`。报告契约路径和所有者、指纹、Machine 结果以及任何命令和退出状态、
审查 verdict、回退、Role Boundary Audit，以及未解决或未经测试的表面。将已接受的契约交给
`setup-project-agents`。生成、commit、push 和发布仍在此 Skill 范围之外。
