# 可执行 Acceptance

本条件式权威负责 Acceptance 设计、用例身份与组合、尝试、判断、Candidate 与设置修正、重放、
安全最终化和终止优先级。只有 Design 把 Acceptance 冻结为适用时，它才贡献自己的阶段、
能力、身份、调度、用例、转换和激活。Design 冻结为`NOT_REQUIRED`时，它不贡献其中任何内容，
也不会对任何运行设置准入条件。

## 确认执行与身份满足条件

扩展具体 Role Launch 就绪性，使其包含一次性隔离、准确用例授权、证据捕获、全新 Runner 启动、每种
返回模式下的终止与静止、清理，以及有界恢复。证明冻结 worker 调度能在保留当前用例 Reviewer
时运行一个全新 Runner，也能在保留该 Reviewer 时，通过剩余`P`槽位分批运行完整、全新的较早
阶段 cohort。

每个用例定义一个全新持久 Reviewer。首次尝试前绑定其身份与调度，但只有该尝试安全最终化后
才启动。最多只有当前用例 Reviewer 处于活跃或保留状态。每个 Runner 和保留的 Reviewer 占用
一个`P`槽位；所有其他工作分批运行，但不改变 cohort、版本或证据。`HOST_UNAVAILABLE`表示
宿主无法提供正确推导的能力或冻结调度。Controller 超出`P`派发属于控制平面
`ROLE_BOUNDARY_VIOLATION`。

默认执行完整 Job；只有 Skill 模型证明符合**Finite Execution Projection**资格且 Design
拥有预授权 harness 时例外。最小合格 projection 必须执行每个受到实质影响的运行时接缝：

- Runner 把 Candidate 行为应用于冻结接缝输入，并产生可观察输出；
- harness 只执行预授权的身份与控制机制并捕获宿主证据；Runner 从不请求或控制身份；以及
- 一个递归边缘用例到达准确可观察的重新进入条件：Candidate 状态，加上将派发同一 Acceptance
  图的下一次调用。harness 在派发前终止；前置状态不足以满足条件。

缺失 harness 或运行时接缝时返回`EXECUTION_UNAVAILABLE`；演练不能替代。网络或外部影响需要
已接受用例权威与经证明的宿主能力。

## 冻结不可变用例

在 Design 期间冻结覆盖重要运行时风险且按风险排序的最小组合：通常包括成功路径，以及每个
实质不同的受影响错误、恢复、出口和运行条件。定义可观察通过条件，不强制任意用例数量。在
阶段入口绑定这些不变用例单元，并从最高风险起顺序执行。

用例定义和通过条件绝不改变。首次尝试前绑定每个用例单元。只有 Revision Impact 证明变化
不会影响某项证据所证明的内容，才可跨 Candidate Version 保留已通过用例证据。

## 准备一次全新尝试

为每次尝试冻结一份**Attempt Contract**，其中包含：

- 一次性 Execution Isolation、fixture、安全清理，以及至多一次预授权有界清理恢复；
- 准确的用例级操作、工具、网络与外部影响授权；
- 只读 Candidate Version、不可变用例与通过条件，以及完整证据捕获；以及
- 全新 Runner 输入、终止与静止机制。

Candidate、用例、fixture 定义和通过条件是不可变的**设置输入**。只有准确归用例所有的执行
目标与影响可变。fixture 或环境修正是尝试之间由 Controller 单独执行的动作。

缺失权限、安全隔离或必需能力时返回`EXECUTION_UNAVAILABLE`并指出未测试表面，绝不能返回
`PASS`或`NOT_REQUIRED`。为每项可获得观察、捕获失败、Runner 报告、终止与静止事实、Candidate
指纹与审计、残留状态、清理，以及恢复或不可用状态，定义一份**Capture Record**。不要虚构证据。

## 执行，然后始终最终化

启动一个全新 Runner。它只能针对准确归用例所有的目标执行已冻结用例影响。它不改变设置输入
或 Candidate，不扩展授权，不判断、修复或修正设置，不清理，不控制角色，也不委派。

无论成功、失败、异常、不返回或审计停止，之后都必须：

1. 保留每项可获得的观察与报告；记录所有捕获失败。
2. 通过已冻结的 Role Launch 机制结束 Runner，并用终止证据确认静止。
3. 完成 Role Boundary Audit，并再次执行 Candidate 指纹审计，即使没有报告或无法确认静止。
4. 只有确认静止后，才清理准确且已授权、归用例所有的目标。失败时最多执行一次安全、受支持、
   预授权的恢复。无法确认静止时禁止清理；边界违规不妨碍静止后的安全清理。
5. 按顺序选择尝试结果：边界或审计违规，或捕获失败 → `ATTEMPT_INVALID`；无法确认静止 →
   `RUNNER_NOT_QUIESCENT`；恢复后清理仍失败或没有可用恢复 → `CLEANUP_FAILED`；否则尝试最终化成功。

只有冻结合同允许时，异常 Runner 才可省略规范化报告。记录缺失，并审计宿主与捕获证据。终止
尝试结果会停止 Acceptance：报告所有可获得证据、残留状态和恢复；不得重试或启动 Reviewer；
不得进行缺陷分类；不得发布用例`PASS`或`NOT_REQUIRED`。预绑定 Reviewer 此时只受工作流最终化
约束。尝试最终化成功只是证据，不是 PASS。

## 判断已最终化证据

第一次尝试成功最终化后，启动该用例的预绑定 Reviewer，并在后续尝试、分类、Candidate 修正、
fixture/环境修正、一次歧义观察和用例 PASS 全程保留同一身份。

向 Reviewer 提供完整 Candidate Version、已接受行为与证据、不可变用例与通过条件、fixture
和权限边界，以及所有捕获的执行与最终化事实。它独立判断归因、通过条件、权限、执行、终止、
静止、清理、残留状态和出口选择，并准确返回以下一种结果：

- 所有条件满足且不支持 Candidate finding 时，返回通用`PASS`；
- 存在**Candidate defect**时，返回通用`FINDING_READY`，随后用运行时直接 finding 握手与
  通用 schema 正文；
- 通用`CONTEXT_REQUIRED`、`ACCESS_REQUIRED`或`HUMAN_DECISION_REQUIRED`；
- 仅在不存在 Candidate defect 时返回**fixture/environment defect**：缺陷及其准确、预授权、
  有界的设置修正，或确认没有修正；
- 仅在不存在 Candidate defect 时返回**ambiguous**：命名当前备选解释，以及一项定向观察、
  有界设置和当前权威内的捕获增量；或
- 该观察后仍有歧义时返回`AMBIGUITY_UNRESOLVED`，包含初始与最终备选解释、变化、两组证据、
  观察与捕获增量、剩余歧义和未测试表面。

Reviewer 直接、原样返回分类。只有 Candidate finding 使用仅含 metadata 的运行时 bootstrap，
随后才把语义正文发给常驻 Author。Author 与 Reviewer 通过通用双边生命周期，分别独立判断
主张和理由。Controller 只执行所选生命周期转换；它绝不接收、转发、概括或重新解释 finding
或讨论内容。

## 修正并重新评估

- Candidate finding 使用直接 Author↔Reviewer 生命周期。完整全单元 Repair Scope 授权所选
  修复后，必须由全新 Runner 和同一 Reviewer 重新取得当前用例 Stage-local PASS，之后才执行
  Revision Impact。
- 对于 fixture/environment defect，Controller 只应用 Reviewer 选中的预授权设置修正，启动
  全新尝试并恢复同一 Reviewer。缺少能力返回`EXECUTION_UNAVAILABLE`；没有安全有界恢复返回
  `NO_PROGRESS`。
- 对于`ambiguous`，只增加给定设置与捕获增量，运行准确一次全新定向观察并恢复同一 Reviewer。
  任何剩余重要歧义都返回`AMBIGUITY_UNRESOLVED`，即使备选解释减少、改变或变得明显。

一次**Acceptance correction attempt**包含一次 Candidate 修复或选定的 fixture/环境修正、其
全新 Runner 尝试和 Reviewer 重新评估。仅在同一缺陷持续时计数。缺陷或方案发生实质变化时，
连续计数重置。歧义观察不算修正尝试。同一缺陷连续两次修正后仍存在，或安全恢复已耗尽时，
停止并返回`NO_PROGRESS`。人类请求会触发全局语义立即停止，但每个已启动 Runner 仍要完整安全
最终化。

## 回退并重放

**Stage-local PASS**表示当前 Reviewer 根据成功最终化证据，在当前用例与 Candidate Version 上
通过。它关闭活跃修正循环，但既不是用例 PASS，也不是 Acceptance PASS。

Candidate 修正后：

1. 使用全新 Runner 与同一 Reviewer 运行当前用例，直到 Stage-local PASS 或停止。
2. 应用 Revision Impact。较早的非 Acceptance 证明失效时，保留该 Reviewer，为每个失效已关闭
   单元绑定完整全新 cohort，并通过剩余`P`槽位分批运行。恢复每个中间阶段，重跑当前用例并
   重新取得 Stage-local PASS，之后才可再次判断 Revision Impact。
3. 收敛时记录当前用例 PASS，结束其 Reviewer，并检查此前每个已通过用例是否失效，无论位置。
4. 按冻结风险顺序重新开始最早失效用例：先取得一次成功最终化的全新尝试，再启动该用例的
   全新 Reviewer。只有可证明不受影响的证据才可跳过。
5. 没有此前用例失效时，前进到下一个冻结用例。

保留当前 Reviewer 时不得启动其他用例 Reviewer。重放使用完整安全生命周期。只有 Reviewer
根据当前 Candidate Version 上未失效且成功最终化的证据返回 PASS，用例才通过。

只有每个冻结用例均记录 PASS、没有证据失效、每个 Runner 都已静止、所有必需清理与审计成功，
并且不存在终止结果，Acceptance 才通过。通过 Evaluation Lifecycle 返回该结果，随后执行工作流
最终化。
