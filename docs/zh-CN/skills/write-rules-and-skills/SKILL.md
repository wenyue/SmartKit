---
name: write-rules-and-skills
description: 编写或修订一份英文 Rule 或 Agent Skill。
---

# 编写 Rule 与 Skill

## 前沿 Agent 原则

面向有能力的当前前沿 Agent 设计并执行此工作流。写明语义权威、证据、不变量，以及省略后会实质改变正确性、安全、协议、归属、协调、外部影响、可执行性或交接的决策边界、约束或例外。把普通方法选择、证据遍历、可可靠推断的决策边界与边缘处理，以及局部判断留给 Agent。

这项原则支配每个阶段和参考资料。工作流采用 Hybrid：默认由判断主导，仅在顺序或协议会改变结果时设置有界的流程岛。

当前 Agent 是 Controller。它负责编排和边界强制落实，绝不负责 Candidate 含义或审查判断。一名常驻 Author 负责 Candidate 含义和写入。独立 Reviewer 负责 finding 与裁决。需要时，Runner 只执行一项已冻结的可执行 Acceptance 尝试。

## 渐进加载参考资料

辅助 Skill 的使用必须与正在编写的内容表面相匹配。编写 Rule 或 Skill 的契约——包括指令、语义、结构和正文——时，不得使用面向代码设计或代码编写的 Skill，包括 `codebase-design`。只有当 Skill 包含可执行脚本时，才可使用这些 Skill 设计、实现或验证脚本；其权威和产出仅限于脚本表面，不得决定或修改外层契约。插件公开、可见或可用并不会扩大这一边界。

在第一次需要时加载每份完整合同，而不是在入口一次性加载：

1. 处理归属、对齐和 Candidate 形态时，读取[模型](references/models.md)以及已安装的 writing-for-agents Skill。
2. 对齐关闭后，读取[Job Design](references/job-design.md)。Design 期间，在冻结身份生命周期与回调时读取[Role Runtime](references/role-runtime.md)，在冻结审查拓扑与视角时读取[Reviews](references/reviews.md)，然后在冻结证明适用性与出口时读取[Evaluation](references/evaluation.md)。如果 Evaluation 选择 Acceptance，则在冻结其模式、用例、身份或安全之前读取[Acceptance](references/acceptance.md)；否则保持未加载并标记为 NOT_REQUIRED。
3. 在常驻 Author 开始前立即读取[Author](references/author.md)。

每份参考资料负责一个具名合同，只陈述相对于前沿 Agent 原则新增的局部边界或例外；后续编排不重复陈述这些合同。当本 Skill 或另一份治理合同本身属于写入 scope 时，遵循[Job Design 的自托管冻结](references/job-design.md#freeze-self-hosting-authority)；否则保持上述渐进加载方式不变。

## 1. 对齐并建模

使用 Models 路由到唯一的 Rule 或 Skill Owner，并关闭结果、权威、证据、保留、安全、边界、授权、验证、加载和交接方面的所有重要问题。由 Agent 查明可解决的事实；对于 Agent 权威之外的任何重要选择，遵循 Models 唯一的对齐路径。只能在其对齐交接所授权的新运行中继续。

当一个受支持的 Candidate 模型和准确 Candidate 表面能够表达每项已接受义务，且没有尚未解决的重要决策时，本阶段完成。

## 2. 设计并冻结

冻结 Job Design 的紧凑 Run Contract：已接受含义；准确 Candidate Allowlist 与操作授权；一名常驻 Author；Reviews 的 Quality 与 Correctness 拓扑；Role Runtime 的身份生命周期；条件式 Machine 与 Acceptance；确定性检查；出口；外部影响安全；以及清理。证明顺序冻结为条件式 Machine、Quality、Correctness、条件式 Acceptance。

在 Author 工作前捕获准确的全 Candidate baseline 与指纹。若它与 Design 关闭时的 Candidate 不匹配，则在任何角色或写入开始前停止。

当每个可达角色、写入、证明、停止与清理动作都符合授权和可用容量时，本阶段完成。

## 3. 编写

向全新常驻 Author 提供已接受的语义输入、baseline、准确授权与 Authoring Scope，然后启动它。严格按照 Job Design 的要求，在写入前以及 Author 返回后立即验证完整 Candidate。只有授权内、可归因于 Author 的写入才能推进 Candidate 指纹。Author 返回调用指纹与语义 Change Summary；完成可接纳的提升后，Controller 把该 Summary 绑定到其派生的写后指纹。

当 Author 的 COMPLETE 被接纳并绑定到已提升指纹，或已选择一个终止状态时，本阶段完成。

## 4. 证明并修正

按照 Evaluation 冻结的顺序运行每个适用阶段：

- Machine 执行 Owner 支持的确定性、非修复检查。
- Quality 使用 Reviews 冻结的独立视角审查完整 Candidate。
- Correctness 使用 Reviews 合并后的独立视角审查完整的已接受合同；
- 只有仍存在重要不确定性时，Acceptance 才使用其已选择模式。

Reviewer 把有支持的 finding 直接发送给常驻 Author。把符合条件的修复合并到一份准确的 Repair Scope。Author 返回 COMPLETE 后，捕获新指纹，并从 Machine 开始按顺序，根据 Evaluation 的重放规则与 Role Runtime 的身份生命周期重新运行每个适用证明阶段。任何语义证明都不能跨修复沿用。

HUMAN_DECISION_REQUIRED 会立即停止语义工作，并且只能在新运行中继续。其他终止结果遵循 Evaluation。

当每个适用阶段都在最终指纹上通过、不再有阻塞 finding，且每项非阻塞 finding 都已有 Author 处置时，本阶段完成。

## 5. 最终化并交接

应用 Role Runtime 的最终化合同、Acceptance 对每项已开始尝试的安全合同，以及 Evaluation 的终止优先级。只有这些合同的关闭要求和最终全 Candidate 边界检查均通过后，才能声明成功。

返回简洁交接，其中包含：

- Candidate 类型、Owner、准确路径与最终指纹；
- 每个阶段的裁决，以及 Machine 命令与退出状态，或 NOT_REQUIRED；
- Acceptance 模式与证据，或 NOT_REQUIRED；
- 编写变更与修复；
- 未解决、不确定或未测试的表面；
- 外部影响清理与残留状态；
- 最终边界检查结果；以及
- 选定的终止结果、Evaluation 优先级所保留的每个下层终止结果或其他结果，以及适用时准确的 HUMAN_DECISION_REQUIRED 请求。

本工作流不授予发布、安装、commit、push、release、翻译或其他下游影响的权限。不要把临时工作流证据写入 Candidate。
