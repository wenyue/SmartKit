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

如果已接受输入仍存在实质性的行为、所有权、权限、验证或退出歧义，则在启动角色或写入 Candidate
之前返回 `ALIGNMENT_REQUIRED`。报告未解决的选择、现有证据、决策所有者以及每个选择的后果。只有当
每项未解决的实质选择都归用户所有，且 `grilling` 可用时，才引导用户显式调用它。当前调用仍以无效果的
`ALIGNMENT_REQUIRED` 结果结束；如果 `grilling` 关闭了每个实质分支，其共享决定将成为新编写运行的
已接受人工决策上下文。否则保持同一停止结果。这个由 Controller 所有的入口退出不同于有界更新请求和
语义角色的 `HUMAN_DECISION_REQUIRED`。

完整阅读公共
[`Frozen Job Design`](../../../skills/write-rules-and-skills/references/job-design.md)和
[`Role Runtime`](../../../skills/write-rules-and-skills/references/role-runtime.md)，以及
[`Evaluation Lifecycle`](../../../skills/write-rules-and-skills/references/evaluation.md)。应用 Frozen
Job Design 的 Run Contract、Job Graph、授权、Candidate 身份、基线、调用最终观察、
expected-proof-state、独立边界、来源/能力类别和有界更新合同。原样应用 Role Runtime，将其作为
唯一固定运行时和通用证据选择政策，包括其中的角色权威、Role Boundary Audit、直接通道、回调
组合、异常执行和工作流最终化机制。Evaluation 只应用 Machine Validation；Revision Impact 当前
闭合与兼容性；适用的证明 Owner 后备路径与重放；以及全局出口。公共 Quality、Correctness 和
Acceptance 角色及其语义生命周期不进入本工作流。

仅确认以下身份满足条件：Controller、一个从首次启动到最终化始终保留的全新常驻 Author，以及一个在其
修正循环中保留的全新 Static Reviewer。本地序列为 Author → 适用的 Machine Validation → Static
Reviewer。在公共 Machine 尚未为当前指纹达到当前闭合时，只启动 Author；达到该闭合后才启动
Reviewer。公共 Quality Review、Correctness Review 和可执行 Acceptance 不进入此工作流。如果
宿主无法保留这些身份、已加载的权威和访问契约或排期，则按 Role Runtime 停止；绝不替换常驻 Author。

把 Static Review 声明为 Role Runtime 中由调用方负责的评估扩展。本 Setup Skill 是它完整的语义
Owner：负责下文 finding schema 与分类、`repair`/`decline`处置、不动点与 PASS 映射、修正循环、
语义状态组合，以及持久 Reviewer 调度。公共 Quality 与 Correctness 保持由 Evaluation 负责的
语义，不向本工作流借用这些语义。Role Runtime 只传输、认证和审计 Static 回调及不含语义的控制
metadata；不负责其任何含义。

启动 Author 前，在 Frozen Job Design 下使用已接受输入、Setup 专属授权与有界更新 envelope 完成
Run Contract 与 Job Graph，同时保留 Author 的`network: none`边界。列举每个符合 Context
Supplement 条件的必要事实槽位，以及每个符合访问扩展条件的已授权本地路径类别、外部来源与能力
类别和已授权模式。冻结一个准确的 Candidate Allowlist，其中只包含`setup-assets/blueprints/`下
预期的契约；只有 Author 获得其写入权限。对于每个符合复用资格的 Setup Machine 证明类别，冻结
Job Design 的兼容性 manifest 与后备路径。Static `PASS`不具备兼容性资格，因为本工作流要求同一
Reviewer 在每次修正后复查完整当前 Candidate。

原样应用 Frozen Job Design 的 Design 关闭指纹绑定、实体化 Frozen Run Contract、单次冻结、冻结后
基线捕获与确认、持续不匹配结果，以及初始 expected proof state。Setup 向这些公共机制提供准确
Allowlist 与 Setup 专属输入；不增加身份、冻结、基线或不匹配转换。

只有当证据基础、仅用于判断的目标、身份、排期、allowlist、授权、发现类别、更新 envelope、预期
操作、冻结 Candidate 身份、不可变基线与初始 expected proof state 均已绑定，且不存在实质歧义时，
本步骤才完成。

## 2. 编写完整全 Allowlist Candidate

启动常驻 Author，并向其提供完整的已接受输入、当前蓝图或有证据的缺失创建基线、所选证据、编写指导、
准确 allowlist，以及一个 Authoring Scope 或有界 Repair Scope。Author 只编辑该 allowlist，负责
Candidate 含义和 finding 处置，并且不执行验证、审查、网络使用或委派。

Author 只返回 Role Runtime 四种状态之一及其完整的权威 payload 和全部三份公共报告。Operation
Report 是准确原始操作、受影响 Candidate 路径与写后观察的唯一记录。Author 不报告由 Controller
观察到的 Candidate 指纹或规范 delta。finding 处置只存在于公共直接讨论生命周期及其处置控制
metadata 中；它们不进入`COMPLETE` payload。

只有在 `CONTEXT_REQUIRED` 或 `ACCESS_REQUIRED` 请求符合冻结的有界范围时，才满足该请求，然后继续
同一个 Author。符合条件的更新不可用时，将该请求保留为停止结果。实质性的范围外变更返回
`ALIGNMENT_REQUIRED`，并要求开始新运行。角色启动后的每个终止结果都转到**完成**。

每次 Author 返回或完成终止后，原样应用 Frozen Job Design 的调用最终捕获、指纹与 delta 绑定、
expected-proof-state 转换，以及 Role Runtime 的 Operation Report 核对、Role Boundary Audit 和
穷尽回调组合。Setup 只增加本地 Author 结果排序和 Static 处置边界。只有公共可接纳`COMPLETE`
转换已经把当前全 Allowlist 指纹提升到 expected proof state，本步骤才完成。

## 3. 为该指纹建立 Machine 结果

根据有依据的确定性表面判断适用性。不存在此类表面时，为当前 Candidate 指纹记录 Machine
`NOT_REQUIRED`，并且不虚构检查。否则，运行每项适用的机器检查，但不修复 Candidate。在每条命令
执行前后立即对完整 Allowlist 计算指纹，并连同准确命令、最终退出状态和相关输出一起保留两个指纹，
再调用 Frozen Job Design 的独立边界结果组合。可归因于命令的变化返回
`ROLE_BOUNDARY_VIOLATION`；其他每项不匹配返回`CANDIDATE_CHANGED`。保留其证据，既不发送给
Author 修复，也不进入 Static Review。状态与 expected proof state 准确匹配时，失败会把命令证据
和有界 Repair Scope 返回给同一个 Author。通过第 2 步审计每次由此产生的 Author 回调。

对于每个已提升 Candidate 指纹，使用其 Change Summary、Operation Report，以及绑定的规范
baseline-to-current delta，判断它可能影响哪些 Machine 证据。重新运行失败的检查以及每项失效
或依赖检查；只有变更不能影响某项结果所证明的内容，且冻结机械判别器接纳把未变 Machine 结论
向前沿用到当前指纹的公共 Revision Impact 兼容性绑定时，才复用该结果。语义影响或不确定影响
在其冻结生命周期允许时使用 manifest 的预授权证明 Owner 路径；否则重跑受影响检查。初始失败
不算一轮。只有在失败 → 同一个 Author 修复 → 重新运行完成后，才完成一轮 Machine 修正。同一
失败在连续两个完整轮次中
持续存在，且没有新证据或有依据的方案时，以`NO_PROGRESS`停止。

只有公共 Machine 通过同指纹证明或授权兼容性绑定为当前 Candidate 指纹达到当前闭合，本步骤才
完成。之后才能启动 Static Reviewer。

## 4. 达到 Static Review 固定点

向持续存在的只读 Reviewer 提供完整的已接受要求、要保留的义务、管辖证据、当前完整全 Allowlist
Candidate 及其指纹，以及一个代表性 walkthrough 输入。它独立检查：

- **仅用于判断的形式：**契约描述所需含义和决定，但不规定 setup 的生成过程；
- **最小性：**删除任何指令都会改变有依据的生成或停止结果；
- **语义完整性：**每项会改变行为的目标义务都会被取得，或导致停止；以及
- **代表性 walkthrough：**一个有依据的目标输入在不虚构项目事实的情况下到达恰好一个生成或停止结果。

每个 finding 包含稳定 ID、问题和支持证据、具体反例、候选项位置、严重程度、估计的 Repair Scope、
有界修复方向、受影响的义务或表面，以及保留约束；字段不适用时，使用 `N/A` 并说明原因。严重程度为：

- `critical`：语义、权威、安全、所有权、可执行性或退出失败；
- `material`：有依据且明显降低信息质量、可维护性或可靠性的缺陷；或
- `advisory`：较小的改进，或存在多个有效方案的选择。

Static Reviewer 每次回调准确向 Controller 暴露一个结果：

- `PASS`表示其完整独立判断没有发现仍值得修复的 finding，每项先前 finding 都有冻结处置，没有
  已选修复等待写入，最新 finding 集合状态为`complete`，而且裁决指出当前 Candidate 指纹；
  它只映射到必需 Machine 结果之后的同指纹 Static 关闭；
- `FINDING_READY`表示一个具有固定稳定 ID 的完整 finding 已准备好进入 Role Runtime 的 metadata
  bootstrap；只有最后一项 finding 才把 finding 集合标记为`complete`，后续`reopened`状态必须
  由新获得的有支持证据触发，并至少增加一个不同 ID；它只映射到具名 Author↔Reviewer 通道的
  bootstrap；
- `CONTEXT_REQUIRED`或`ACCESS_REQUIRED`表示准确的通用 Role Runtime 请求，并且只映射到与其
  对应的冻结有界更新转换；或
- `HUMAN_DECISION_REQUIRED`表示准确的通用终止 payload，并且只映射到全局语义立即停止。

这些结果相互排斥且穷尽所有情况。缺失、畸形、未知或映射到多个结果的返回在 Role Runtime 下不可
接纳。`DISCUSSION_CLOSED`只是通道事件，绝不是 Static 结果或裁决。

critical 和 material finding 通常值得修复。如果有依据的 advisory 修复只涉及一两句话或一个小区块，
并且能保留语义，则默认值得修复。Reviewer 指出问题，而不撰写替换文本；它负责每个 finding，并决定该
finding 是否仍值得修复，而且通过 Role Runtime 的直接修正通道发送 finding。Author 独立选择 `repair`
或 `decline`，并负责每次 Candidate 修正；Controller 只处理冻结的控制平面。

任何 Static 讨论开始前，Reviewer 完成独立 review，并为所审 Candidate 指纹冻结完整 finding
集合、每个稳定 ID，以及证明集合完整的证据。随后通过 Role Runtime 的`FINDING_READY` bootstrap
发出每项 finding，且只在最后一项上设置完成标记。每个回调与最终完成标记都通过审计后，Controller
才为每项 finding 打开已声明的 Author↔Reviewer 配对。每个配对针对同一被审指纹完成直接交换及经
审计的`DISCUSSION_CLOSED`事件。任何通道仍开放时，Candidate 保持只读；任何 finding 都不能触发
会使其他 finding 过时的提前修正。

只有新获得的有支持证据为同一个未变 Candidate 指纹建立至少一个不同 finding 时，调用方自有的
`reopened`转换才可用。它会立即使先前 finding 集合完成标记失效。保留 Candidate，并结束每个当前
开放通道；只有其经审计的`DISCUSSION_CLOSED`事件完成后，同一个 Static Reviewer 才在该未变指纹
上恢复私下判断。Reviewer 冻结新获支持的不同 finding 集合，并通过`FINDING_READY`发出每一项；
只有最后一项新的发出才恢复 finding 集合`complete`。随后在同一生命周期下 bootstrap 并关闭每个
新通道。集合处于`reopened`时，或者所有当前与新通道关闭前，不得提供 Static Repair Scope、进行
Author 写入或返回`PASS`。

对于每项 finding，Author 准确冻结一个基于证据的`repair`或`decline`处置。`repair`选择写入；
`decline`不选择写入。Reviewer 独立冻结是否仍然坚持主张、严重级别与值得修复状态。只有 Reviewer
不再坚持一项不写入便仍值得修复的主张，或双方同意所选修复能够处理每个仍被坚持的部分、只待写入
和复查时，Static 不动点状态才是`reached`。若 Reviewer 仍坚持一项值得修复的主张，而 Author
拒绝或提出不能解决问题的修复，则状态为`not reached`；Static finding 绝不发出`not applicable`。
不写入且 reached 的结果关闭该 finding；选择修复且 reached 的结果进入修正循环；not-reached 结果
进入下一分歧轮或下文`NO_PROGRESS`规则。只有上文由 Reviewer 负责的`PASS`映射能关闭 Static Review。

每项初始与 reopened finding 都已发出、finding 集合完成状态为当前状态且每个通道都已关闭后，
先通过同指纹分歧轮解决每项 not-reached finding，之后才允许写 Candidate。每项 finding 都有冻结
且 reached 的处置后，把所有已选修复及其保留约束合并为准确一个绑定指纹的完整单元 Static Repair
Scope。只有此时才通过第 2 步调用同一个常驻 Author 一次，完成整个批次；绝不按 finding 拆分批次，
也不留下针对已被取代指纹的待处理已选修复。没有已选修复的批次不进行 Author 写入。

每次调用或继续 Reviewer 前，把全 Allowlist 与 expected proof state 比较，并调用 Frozen Job
Design 的独立边界结果组合。只有准确匹配后才启动。每次 Reviewer 回调后，应用 Role Boundary
Audit 与 Role Runtime 的正常非 Author 回调组合；不存在正常回调时，使用同一独立边界组合。完成
批量 Author 修正后，应用 Machine 失效规则，执行适用 Machine 重放，并为完整新 Candidate 的
指纹建立必需 Machine 结果，之后同一个 Reviewer 才复查完整 Candidate 与指纹。复查判断整个
单元，而不只判断已修复 finding。初始 finding 不算一轮。只有在 Author 处置 → 同一个 Reviewer
重新评估后仍未解决时，才完成一轮 Static 分歧。同一 finding 在连续两个完整轮次中持续存在，且
没有新证据或有依据的方案时，以`NO_PROGRESS`停止。

Revision Impact 兼容性绑定绝不能替代这项必需的 Static 全 Candidate 复查。

只有当同一个 Reviewer 返回绑定到当前 Candidate 指纹、针对完整 Candidate 的`PASS`，且公共 Machine 为该
指纹达到当前闭合时，本步骤才完成。结束 Reviewer；不启动其他公共评估角色。

## 5. 完成

角色启动后，对成功和每个终止停止原样应用 Role Runtime 工作流最终化，以及 Frozen Job Design 的
安全后和最终独立比较。Setup 不增加拆除或边界机制；在评估 Setup 成功前，由这些机制的准确终止
结果与残留结果支配。

成功要求 Static Reviewer PASS 绑定到当前完整全 Allowlist Candidate 指纹，并且公共 Machine 为该
指纹达到当前闭合。报告契约路径和 Owner、指纹、Machine 结果以及任何命令和退出状态、review
裁决、回退、Role Boundary Audit、未解决或未经测试的表面、身份拆除与残留状态、每个观察到的
指纹及其提升状态、每当 Machine 当前闭合使用兼容性绑定时由 Evaluation 负责的规范兼容性绑定
证据，以及最终 expected-proof-state 比较。将已接受的契约交给
`setup-project-agents`。生成、commit、push 和发布仍在此 Skill 范围之外。
