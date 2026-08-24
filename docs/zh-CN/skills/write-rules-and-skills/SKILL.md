---
name: write-rules-and-skills
description: 在显式提供的上下文中编写或实质性修订一份 Rule 或 Agent Skill；不包括 Setup Authoring Contract 和共享可移植性资格认定。
---

# 编写 Rule 和 Skill

根据已接受意图和已验证证据，编写最小且完整的 Rule 或 Skill。应用 `writing-for-agents`
来处理信息层级、有目的的 Markdown 和 Skill 机制。此 Hybrid Skill 负责普通候选项编写和通用
资格门控；更具体的调用方可以增加范围证明，但不能削弱这些门控。

当前 Agent 是控制器，而不是语义 Author 或 Reviewer。它可以发现已授权的项目事实、选择证据、
启动 fresh Agent、原样应用返回内容并运行确定性检查。语义角色只接收显式 Context Packet。

## 建立义务和归属

编写前，建立：

- 请求结果、保留语义、已接受变更、非目标和安全边界；
- 当前和请求的工件归属、允许写入，以及受影响的加载、资源、发现、生成和分发表面；以及
- 适用 Rule、当前行为、验证 seam，以及会改变政策、作业、操作、目标或退出的环境事实。

对每项可独立变化的义务，在上下文中保留一行语义台账，包括证据、请求或当前归属，以及
`preserve`、`change`、`add`、`move` 或 `retire` 处置。不要把台账、编写模型、来源和审查
证据写入运行时工件。

完整阅读并应用 [`references/owner-gate.md`](references/owner-gate.md)。对于显式只读的 Ownership
Review，返回其裁决并停止。否则，仅在每个候选项都有一个受支持的 Rule 或 Skill 归属时继续。

## 路由并达到就绪

每个候选项都是直接使用的 Ordinary Artifact。完整阅读
[`references/ordinary-artifact.md`](references/ordinary-artifact.md)，然后只读取一份语义引用：

| 候选项 | 语义引用 |
| --- | --- |
| Rule | [`references/rule-semantics.md`](references/rule-semantics.md) |
| Skill | [`references/skill-semantics.md`](references/skill-semantics.md) |

当 Owner Gate 返回 `split` 时，创建用户选择的、分别归属的 Rule 和 Skill 候选项。只有在受支持
证据仍允许实质不同的行为、归属、写入、权限、副作用或退出时才提问；否则记录唯一受支持的事实并继续。

完整阅读 [`references/soft-isolation.md`](references/soft-isolation.md)。顶层控制器必须先获得一次
Soft-Isolation Probe `PASS`，才能启动 Behavior Control、Author、Pruner、Reviewer 或 Acceptance
Runner。更具体的调用方只能复用同一顶层运行和 fresh-Agent 启动机制产生的 `PASS`。Probe 失败后
绝不继续。

应用 Ordinary Artifact 引用要求的任何 Behavior Control。当选择的引用都可在没有实质未知项的
情况下应用时，就绪通过。

## 编写一个 Candidate Revision

为 Rule 构建临时 Policy Frame，或为 Skill 构建选定且受支持的 Skill Shape。把每项义务投影到
最窄且可靠的运行时归属和加载层级。让环境归属的事实可发现，只在触发条件出现时披露条件材料，并且仅对
重复、脆弱的确定性机制使用脚本。现有工件是遗漏证据，不是新大纲。

启动一个 Soft-isolated、无工具 Author，并给它一个 Context Packet，其中包含已接受结果、语义台账、
选择的 frame、存在时的完整当前候选项及归属资源、允许证据、适用编写指导和完整 canonical target
映射。对于项目感知编写，显式加入每项必需的项目事实或 Rule 正文。Author 返回
`CONTEXT_REQUIRED`，或者返回每个变更目标的完整替换内容；它不编辑文件。

收到 `CONTEXT_REQUIRED` 时，停止，或者构建完整替换 packet 并启动新的 fresh Author。否则，把
返回内容原样应用到已授权 canonical path，并在继续前验证结果。控制器写入时不得进行语义修正。

Candidate Revision 是已验证写入后的完整当前内容状态。不依赖前任版本或 diff 阅读它。只有当另一个
Agent 无需发明条件、事实、操作、归属或退出即可使用它时才继续。

独立分类每项阻塞 finding：

- `uniquely-forced`：当前证据确定唯一的范围内修正，无需新政策、权限、行为、范围或副作用；
- `decision-required`：证据仍允许实质不同的受支持结果，或者修正需要新意图、证据、权限、范围或
  外部操作。指出确切的未决选择、其决策归属，以及每种结果的证据。

## 精简、验证、审查和验收

1. 完整阅读 [`references/pruning-agent.md`](references/pruning-agent.md)。把候选项交给一个没有
   编写它的 Soft-isolated、无工具 Pruning Agent。在精简修正期间保持同一个 Agent。它之后不能进行
   Review 或 Acceptance。
2. 对每个变更归属和受影响表面运行调用方环境要求的机器检查。机器检查证明结构和执行，而不是自然语言
   含义。如果必需检查以非零退出，停止并报告确切命令、最终退出、相关输出、未运行门控和未验证表面。
3. 冻结写入。完整阅读 [`references/semantic-review.md`](references/semantic-review.md) 和
   [`references/acceptance-runner.md`](references/acceptance-runner.md)。向一个新的
   Soft-isolated、无工具 Reviewer 提供完整的有界证据。它在 Acceptance 开始前返回 Semantic
   Review `PASS` 或 `FAIL`。
4. 对每个选定 case 使用新的 Soft-isolated Acceptance Runner。Reviewer 判断其可观察结果，并返回
   独立的 Acceptance `PASS` 或 `FAIL`。

必需的 fresh Agent 不可用时停止。启用工具的 Acceptance case 属于例外，运行前必须满足 Acceptance
Runner 引用中的匹配 Probe 和 packet 规则。

## 修正直到稳定

遇到有效的 `decision-required` finding 时停止。当所有 finding 都是 `uniquely-forced` 时，把它们
一起交给 Author。Author 返回完整修订内容；控制器原样应用并验证。该写入创建新的 Candidate Revision，
并使每项依赖的机器、Review 和 Acceptance 结果失效。按顺序重跑门控，使用同一个 Pruning Agent、新的
Reviewer，以及每个受影响 case 的新 Runner。

同一 finding 原样复现或修正不会改变候选项时，以无进展停止。成功要求同一个 Candidate Revision 的
Pruning、机器验证、Semantic Review 和 Acceptance 全部通过。

报告工件类型、归属、保留和已接受变更、受影响表面、基线大小比较、确切命令和退出、Probe 与门控裁决、
修正，以及未解决或未测试表面。把 Context Packet、台账、Probe 结果和审查证据保留在 Agent 上下文中；
不创建工作流报告或临时编写目录。共享可移植性声明、Setup Authoring Contract 编写、发布、安装、
commit、push 和其他外部操作留给其归属方。
