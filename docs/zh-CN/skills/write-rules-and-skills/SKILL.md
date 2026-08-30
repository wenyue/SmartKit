---
name: write-rules-and-skills
description: 编写或修订一份英文 Rule 或 Agent Skill。
---

# 编写 Rule 与 Skill

通过一个流程主导型 Job，产出最小而完整的 Candidate：

**确定归属 → 对齐 → 建模 → 设计 → 计算指纹 → 冻结 → 建立基线 → 编写 → 证明 →
最终化**

当前 Agent 是**Controller**。它负责控制平面，但绝不负责 Candidate 含义。全新常驻 Author
遵循 Author 合同；全新、持久的 Reviewer 负责 finding 与裁决；全新 Runner 执行已冻结的
Acceptance 用例，但不作判断。

## 加载编写参考资料

Controller 在下列边界分别读取每份资源一次，绝不提前读取：

1. 进入时读取[`references/models.md`](references/models.md)，并读取和应用已安装的
   `writing-for-agents` Skill。
2. 对齐与建模关闭后、Design 开始前，按以下顺序各完整读取一次：
   [`references/author.md`](references/author.md)、
   [`references/job-design.md`](references/job-design.md)、
   [`references/role-runtime.md`](references/role-runtime.md)、
   [`references/evaluation.md`](references/evaluation.md)，然后是
   [`references/reviews.md`](references/reviews.md)。
3. 在 Design 期间，根据 Evaluation 的信号判定 Acceptance 适用性。若为`NOT_REQUIRED`，则不
   加载任何内容，也不贡献任何 Acceptance 事实。若适用，则在纳入其任何用例、身份、授权、
   调度、转换、安全、终止、静止、清理或就绪事实之前，完整读取
   [`references/acceptance.md`](references/acceptance.md)。之后完成同一次 Design 并执行唯一一次冻结。

这些文件分别负责与其名称对应的合同。Author 负责 Candidate 编写与修复判断；Reviews 负责
Quality 和 Correctness 判断与裁决；Acceptance 在适用时负责可执行行为验证。Evaluation 对这些
结果进行排序与组合，Role Runtime 则负责传输与审计。后续章节只提供编排增量；需要定义时遵循
相应 Owner。

## 1. 确定归属、对齐并建模

在相应 Gate 内完成 Ownership Review。只有存在一个受支持的`rule`或`skill`Owner 时才可继续；
否则采用 Gate 的路径或对齐结果。

解决选定模型要求的每项输入，并关闭 Models 所规定的基线与语义输入对齐。初始义务处置留给
常驻 Author 判断。任何重要答案尚未解决时，使用`Close alignment`。

**完成条件：**一个受支持的 Owner 与模型覆盖所有义务，而且 Author 作出判断所需的管辖证据、
语义标准、保留约束与操作边界都有已接受值。

## 2. 设计、计算指纹并冻结

应用 Frozen Job Design，从其残留发现与清理入口开始，依次完成容量、就绪状态、Candidate 身份，
并对**条件式 Machine → Quality → Correctness → 条件式 Acceptance**执行唯一一次冻结。其 Run
Contract 与 Job Graph 必须覆盖全部 Candidate 输入、授权、角色、通信、修正、重放、出口、安全、
拆除和交接。冻结来源授权而非预选证据集；Role Runtime 负责按需选择。冻结每份兼容性 manifest，
绑定全 Allowlist 身份，实体化完整合同，并执行唯一一次冻结。

Host Governance 可以约束某项已授权操作的执行方式，但不能提供 Candidate 含义或工作流权威。

**完成条件：**每个可达状态均已获得授权、内部一致且可以调度，并且尚未启动任何角色或
Candidate 状态。

## 3. 验证基线并编写

冻结后：

1. 严格按 Frozen Job Design 的要求捕获并验证不可变的 pre-Author baseline。确认不匹配时，在
   Author 启动前返回`CANDIDATE_CHANGED`。
2. 按 Author 合同向全新常驻 Author 提供完整已冻结输入与初始 Authoring Scope，然后启动它。
3. 每次返回或终止时，应用 Frozen Job Design 的调用最终转换，以及 Role Runtime 的审计与结果
   组合。只有可接纳的`COMPLETE`才会提升 expected proof state，并把由 Author 负责的义务处置
   记录公开为绑定到指纹的证明阶段证据。只有经过符合条件的有界更新或完整 Repair Scope，才能
   继续使用同一个 Author；其他所有结果都遵循其 Owner 定义的路径。

**完成条件：**经审计的 Author 结果已提升 expected proof state，或者已选择可达的最高
优先级停止结果。

## 4. 证明、修正并重放

按冻结顺序激活各阶段。应用 Evaluation 的修正、当前闭合、兼容性、Revision Impact、重放、
Scope Transfer 与出口规则；仅在相应条件式权威处于活跃状态时应用它。Candidate 写入要求所有
通道均已关闭，并有一份完整的全单元 Repair Scope。只有当前独立 cohort 达成共识后才能前进。

对`HUMAN_DECISION_REQUIRED`应用 Evaluation 的全局立即停止规则。

**完成条件：**所有适用证明均处于当前闭合且彼此兼容，不存在尚未解决的阻塞 finding，并且每项
advisory 都已有冻结处置。

## 5. 最终化并交接

启动任一角色后，都必须在交接前完成 Role Runtime 的最终化合同。

报告 Candidate 类型、Owner、路径和最终指纹；各阶段裁决；每当通过兼容性向前沿用建立当前闭合
时所使用的、由 Evaluation 负责的规范兼容性绑定证据；Machine 命令及退出状态或
`NOT_REQUIRED`；Acceptance 证据或`NOT_REQUIRED`；Role Boundary Audit；回退与有界更新；
尚未解决或测试的表面；Host-Governance 影响；身份拆除与残留状态；每个观察到的指纹及其提升
状态；以及最终 expected-proof-state 比较。对任何由 Owner 生成的终止结果，都不得重新解释。

临时工作流材料只保留在 Agent 上下文中。不要创建工作流报告、复制的 Candidate 或永久 fixture。
本 Job 不授予发布、安装、commit、push、release、翻译或其他下游影响的权限。
