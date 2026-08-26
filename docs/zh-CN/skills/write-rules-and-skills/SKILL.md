---
name: write-rules-and-skills
description: 编写或修订一个英文 Rule 或 Agent Skill，或以只读方式审查其所有权。
---

# 编写 Rule 和 Skill

为其有依据的所有者编写最小而完整的英文 Rule 或 Skill。应用 `writing-for-agents` 来处理信息层次、
有目的的 Markdown 和 Skill 机制。只读 Ownership Review 使用相同证据，并在写入候选项前退出。

当前 Agent 是 Controller。它负责编排访问、角色边界、Candidate Version、指纹、阶段转换、Revision
Impact Decision 和有界交接。它不编写候选项含义、不决定 finding 处置、不作出语义 verdict，也不
进行语义修复。

## 达到就绪状态并冻结 Run Contract

完整阅读 [`references/owner-gate.md`](references/owner-gate.md)，并建立一个有依据的 Rule 或 Skill
所有者。对于 Ownership Review，返回 verdict 并停止。`split` verdict 会成为两次独立的 Rule 和
Skill 编写运行；任何 Candidate Version 都不得跨越两者。

只读取一个候选项模型：

| 候选项 | 参考文件 |
| --- | --- |
| Rule | [`references/rule-semantics.md`](references/rule-semantics.md) |
| Skill | [`references/skill-semantics.md`](references/skill-semantics.md) |

候选项含义必须由已接受证据独立支持，并且不得让任何有效含义或术语只存在于非规范的环境词汇表中。

完整阅读 [`references/role-launch.md`](references/role-launch.md)，并应用其中的 Adapter 选择、静态
资格认定、冻结和冻结后资格门槛。直接调用选择 Default Fresh Role Adapter。每个更具体的调用方都
必须显式选择公共 Default Adapter（不需要覆盖机制时），或选择一个完整的调用方自有 Adapter；
缺失时就绪失败，而不是选择 fallback。为 Run Contract 解析候选项路径、模型和调用元数据、访问
权限及适用验证。

启动任何角色或更改候选文件前，在 Controller 上下文中解析并冻结一个完整 Run Contract，其中包含：

- 已接受结果、完整现有行为、要保留的义务、已接受变更、非目标和安全边界；
- 每项 `preserve`、`change`、`add`、`move` 和 `retire` 处置；
- 候选项所有权、准确路径和受影响表面，分别列出 `read`、`write`、`create` 和 `delete` 授权，并
  包含一个预授权更新范围；
- 可用角色容量和持续身份保留能力；
- 所选 Adapter、阶段顺序、通过和停止条件、验证计划及最终交接；以及
- 本次运行继续受冻结契约管辖这一规则：候选项编辑只能影响之后一次独立调用。

完整提供这些事实的已接受 Issue 或 Spec，或者唯一有依据的本地修复，可以建立一致性。如果仍存在
实质性的行为、所有权、权限、验证或退出歧义，应在启动角色或写入前返回 `ALIGNMENT_REQUIRED`，
指出未解决选择，并让用户显式调用 `grilling`。冻结后只能根据 Role Launch 更新范围添加非语义
Context Supplement；实质变更需要重新建立一致性并开始一次新运行。启动 Author 前，完成 Role
Launch 的冻结后资格门槛。

## 编写一个 Candidate Version

完整阅读 [`references/author.md`](references/author.md)。启动 Author 前，计算基线 Candidate
Fingerprint，并取得 Candidate Allowlist 的单一写入者锁。启动一个不继承父级 turn 的全新 Author，
并在每个 Candidate Version 中保留该身份。向其提供完整 Run Contract、管辖证据、所选模型、当前
候选项和明确的 Candidate Allowlist。所选 Adapter 和冻结的访问授权管辖 Author 的所有检查；
Author 只能直接编辑其 Candidate Allowlist。

每次 Author 回调后，执行 Role Boundary Audit，并为每个候选文件计算紧凑的 Candidate Fingerprint。
Author Change Summary 描述语义影响；指纹标识内容。只有这些信号不足以支持 Revision Impact
Decision 时，才使用有针对性的 diff；Controller 通常不检查完整 diff。

## 按顺序评估

完整阅读 [`references/correction-cycle.md`](references/correction-cycle.md)。每个审查阶段都使用
持续 Reviewer → Author 修正或拒绝 → 同一个 Reviewer 复查的循环，直到 PASS 或达到规定的停止条件。

按以下顺序评估一个 Candidate Version：

1. 阅读 [`references/quality-review.md`](references/quality-review.md)，并行运行其中的两个持续
   Reviewer。
2. 阅读 [`references/machine-validation.md`](references/machine-validation.md)，并在适用时运行。
3. 阅读 [`references/correctness-review.md`](references/correctness-review.md)，并行运行其中的
   两个持续 Reviewer。
4. 阅读 [`references/acceptance.md`](references/acceptance.md)。只有达到其证据门槛时才运行可执行
   Acceptance；否则记录 `NOT_REQUIRED` 并完全跳过该阶段。

## 完成

成功要求当前 Candidate Version 拥有每项适用阶段的 verdict，且没有未解决的值得修复的 finding。
简明的成功报告只包含候选项路径和类型、所有者、指纹、机器命令和退出状态或 `NOT_REQUIRED`、
审查 verdict、Acceptance verdict 或 `NOT_REQUIRED`、Role Boundary Audit、回退、上下文或访问
变更，以及未解决或未经测试的表面。终止报告还包括 Acceptance 和 Role Launch 最终处置要求的每项
状态和证据，包括适用的残留状态、证据捕获、审计、清理、teardown 和锁释放失败。Controller 报告
其所有者产生的状态和证据，不替换或重新解释这些所有者管辖的终止语义。

在取得锁或启动角色后的每次成功或终止报告前，应用已加载的 Role Launch 工作流最终处置契约。

将 Run Contract、prompt、finding 历史、diff 和临时证据保留在 Agent 上下文中。不要创建工作流
报告、复制的候选项树或永久评估 fixture。发布、安装、commit、push 和 release 留给其各自所有者。
