# 可执行 Acceptance

本合同在适用时是 Acceptance 工作的语义与执行 Owner。它负责 Acceptance 可见输入、用例设计、
尝试、捕获证据、Candidate 与设置分类、finding 与不动点判断、裁决、本地修正与重放、安全、
终止优先级和完成。Frozen Job Design 继续负责 scope、授权、身份、指纹与调度；Role Runtime
继续负责传输、报告、审计与回调；Evaluation 继续负责证明顺序、跨 Owner 修正、结果组合与
跨阶段重放。`NOT_REQUIRED`既不贡献任何内容，也不设置任何准入条件。

## 接收输入并确认执行满足条件

就绪状态要求一次性隔离、用例授权、捕获、全新 Runner 启动、每种模式下的终止与静止、清理和
有界恢复。调度必须分别容纳以下任一种情形：尝试期间同时运行全新 Runner 与当前用例 Reviewer；
或者 Evaluation 恢复期间同时保留用例 Reviewer 并分批运行较早阶段 cohort。它绝不同时调度
Runner、用例 Reviewer 和较早阶段 cohort。

每次激活用例时，在首次尝试前绑定实际的全新 Reviewer 身份与调度，但在该次尝试成功最终化前
不启动它。最多保留当前用例 Reviewer，绝不复用此前身份，并应用 Job Design 的容量与分批规则。

默认执行完整 Job；只有 Skill 模型证明符合**Finite Execution Projection**资格且 Design
拥有预授权 harness 时例外。最小合格 projection 必须执行每个受到实质影响的运行时接缝：

- Runner 把 Candidate 行为应用于冻结接缝输入，并产生可观察输出；
- harness 只执行预授权的身份与控制机制并捕获宿主证据；Runner 从不请求或控制身份；以及
- 一个递归边用例到达准确可观察的重新进入条件：Candidate 状态，加上将派发同一 Acceptance
  图的下一次调用。harness 在派发前终止；前置状态不足以满足条件。

缺失 harness 或接缝时返回`EXECUTION_UNAVAILABLE`；演练不能替代。网络或外部影响需要已接受
的权威与宿主能力。

## 冻结不可变用例

冻结覆盖重要运行时风险且按风险排序的最小组合：通常包括成功路径，以及每个实质不同的受影响
错误、恢复、出口和运行条件，并提供可观察通过条件。在阶段入口绑定不变用例单元，并优先执行
风险最高的用例。

用例定义和通过条件绝不改变。首次尝试前绑定每个用例单元。为每个符合兼容性资格的用例，在 Job
Design 的 manifest 中冻结其完整依赖表面、可观察的不受影响谓词、来源、机械生成者，以及生命周期
授权的 Reviewer 后备路径或重放后备路径。只有该判别器以机械方式证明不受影响，且 Revision
Impact 记录了绑定到当前指纹的不可变兼容性绑定，才可跨 Candidate 指纹变化保留已通过用例证据。
原始 Reviewer 结论、回调、指纹和来源均原样保留。语义影响或不确定影响在仍获允许时使用预授权
的用例 Reviewer 生命周期；否则重放该用例。

## 准备一次全新尝试

为每次尝试冻结一份**Attempt Contract**，其中包含：

- 一次性 Execution Isolation、fixture、安全清理，以及至多一次预授权有界清理恢复；
- 准确的用例级操作、工具、网络与外部影响授权；
- 只读 Candidate 及其指纹、不可变用例与通过条件，以及完整证据捕获；以及
- 全新 Runner 输入、终止与静止机制。

Candidate、用例、fixture 定义和通过条件是不可变的**设置输入**。只有准确归用例所有的执行
目标与影响可变。fixture 或环境修正是由 Controller 在两次尝试之间单独执行的动作。

缺失权限、安全隔离或必需能力时返回`EXECUTION_UNAVAILABLE`并指出未测试表面，绝不能返回
`PASS`或`NOT_REQUIRED`。为每项可获得观察、捕获失败、Runner 报告、终止与静止事实、Candidate
指纹与审计、残留状态、清理，以及恢复或不可用状态，定义一份**Capture Record**。不要虚构证据。

## 执行，然后始终最终化

启动一个全新 Runner。它只能针对准确归用例所有的目标执行已冻结用例影响。它不改变设置输入
或 Candidate，不扩展授权，不判断、修复或修正设置，不清理，不控制角色，也不委派。

发生任何成功、失败、异常、不返回或审计停止后：

1. 保留每项可获得的观察与报告；记录所有捕获失败。
2. 通过已冻结的 Role Runtime 机制结束 Runner，并用终止证据确认静止。
3. 完成 Role Boundary Audit，并再次执行 Candidate 指纹审计，即使没有报告或无法确认静止。
   应用 Frozen Job Design 的有序不匹配分类，并将其边界结果或 Candidate 变更结果保留为待处理，
   直至尝试安全最终化。
4. 只有确认静止后，才清理准确且已授权、归用例所有的目标。失败时最多执行一次安全、受支持、
   预授权的恢复。无法确认静止时禁止清理；边界违规不妨碍静止后的安全清理。
5. 按顺序选择尝试安全结果：非指纹审计违规或捕获失败 → `ATTEMPT_INVALID`；无法确认静止 →
   `RUNNER_NOT_QUIESCENT`；恢复后清理仍失败或没有可用恢复 → `CLEANUP_FAILED`；否则尝试最终化
   成功。两个待处理的 Candidate 不匹配结果都不会变为`ATTEMPT_INVALID`：完成上述每项终止、
   静止、审计和允许的清理操作时，保留其`ROLE_BOUNDARY_VIOLATION`或`CANDIDATE_CHANGED`
   分类。之后任何尝试安全终止结果都优先，同时保留该底层分类；尝试最终化成功时，则把待处理
   结果原样暴露给 Evaluation。

暴露出的`ROLE_BOUNDARY_VIOLATION`或`CANDIDATE_CHANGED`会停止 Acceptance。报告所有可获得
证据与残留状态；不启动重试或 Reviewer，不进行缺陷分类，也不发布用例`PASS`或`NOT_REQUIRED`。

只有冻结合同允许时，异常 Runner 才可省略规范化报告。记录缺失，并审计宿主与捕获证据。尝试
安全终止结果会停止 Acceptance。报告所有可获得证据、残留状态和恢复；不启动重试或 Reviewer，
不进行缺陷分类，也不发布用例`PASS`或`NOT_REQUIRED`。首次尝试时尚未启动任何用例 Reviewer；
其预绑定身份只受工作流最终化约束。后续尝试时，已经启动的当前用例 Reviewer 同样只受工作流
最终化约束。尝试最终化成功只是证据，不是 PASS。

## 判断并返回 Acceptance 结果

第一次尝试成功最终化后，启动预绑定的全新 Reviewer，并在后续尝试、分类、Candidate 修正、
fixture/环境修正、一次歧义观察和用例 PASS 全程保留同一身份。

向 Reviewer 提供完整 Candidate 及其指纹、已接受行为与证据、不可变用例与通过条件、fixture
和权限边界，以及所有捕获的执行与最终化事实。它独立判断归因、通过条件、权限、执行、终止、
静止、清理、残留状态和出口选择，并准确返回以下一种结果：

- 所有条件满足、不再有未解决的阻塞 Candidate finding，且每项 advisory 均有冻结的 Author
  处置时，返回通用`PASS`；
- 存在**Candidate defect**时，返回通用`FINDING_READY`，随后用运行时直接 finding 握手与
  通用 schema 正文；
- 通用`CONTEXT_REQUIRED`、`ACCESS_REQUIRED`或`HUMAN_DECISION_REQUIRED`；
- 仅在不存在未解决的阻塞 Candidate defect，且每项 advisory 均有冻结的 Author 处置时返回
  **fixture/environment defect**：缺陷及其准确、预授权、有界的设置修正，或确认没有修正；
- 仅在不存在未解决的阻塞 Candidate defect，且每项 advisory 均有冻结的 Author 处置时返回
  **ambiguous**：列出当前备选解释，以及一项定向观察、有界设置和当前权威内的捕获增量；或
- 该观察后仍有歧义时返回`AMBIGUITY_UNRESOLVED`，包含初始与最终备选解释、变化、两组证据、
  观察与捕获增量、剩余歧义和未测试表面。

拒绝一项 advisory 即满足冻结处置准入条件，既不阻止`PASS`，也不阻止其他分类。

Reviewer 直接、原样返回分类。对于 Candidate finding，本合同负责主张、严重级别、不动点评估
与裁决；Author 合同负责处置、理由与替换文本。Role Runtime 只执行 metadata bootstrap，
Evaluation 通过双边生命周期组合由 Owner 产生的结果。Controller 绝不接收、转发、概括或重新
解释 finding 或讨论内容。

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
全新 Runner 尝试和 Reviewer 重新评估。仅当同一缺陷持续存在时才计数。出现实质不同的缺陷或
方案时，连续计数重置。歧义观察不属于修正尝试。同一缺陷连续两次修正尝试后仍存在，或安全
恢复已耗尽时，停止并返回`NO_PROGRESS`。人类请求会触发全局语义立即停止，但每个已启动
Runner 仍要完成安全最终化。

## 回退并重放

**Stage-local PASS**表示当前 Reviewer 根据成功最终化证据，在当前用例上通过，且结果绑定到当前
Candidate 指纹。它关闭活跃修正循环，而不是关闭用例或 Acceptance。

Candidate 修正后：

1. 使用全新 Runner 与同一 Reviewer 运行当前用例，直到 Stage-local PASS 或停止。
2. 将当前已提升 Candidate 与当前用例的 Stage-local PASS 证据交给 Evaluation，供其进行跨阶段
   Revision Impact。Evaluation 判断 Machine、Quality 或 Correctness 是否失效。若均未失效，
   继续第 4 步。否则，Evaluation 恢复每个失效的非 Acceptance 阶段，再将控制权交回 Acceptance；
   Acceptance 按已冻结调度保留该 Reviewer，不启动任何较早阶段身份，也不执行任何较早阶段重放。
3. Evaluation 恢复失效的非 Acceptance 证明并交回控制权后，使用全新 Runner 与同一个保留的
   Reviewer 重跑当前用例，重新取得 Stage-local PASS，并把所得证据交给 Evaluation，再次进行
   跨阶段 Revision Impact 判定。如果 Evaluation 再次恢复较早证明，则重复本步骤；当它判定没有
   较早的非 Acceptance 证明失效时，继续第 4 步。
4. 记录当前用例 PASS，结束其 Reviewer，并检查此前每个已通过用例是否失效，无论位置。
5. 按冻结风险顺序重新开始最早失效用例：先取得一次成功最终化的全新尝试，再启动该用例的
   全新 Reviewer。只有冻结机械判别器通过其绑定到当前指纹的 Revision Impact 兼容性绑定所接纳
   的证据才可跳过。
6. 没有此前用例失效时，前进到下一个冻结用例。

保留当前 Reviewer 时不得启动其他用例 Reviewer。重放使用完整安全生命周期。只有 Reviewer
针对不受影响且成功最终化的证据生成`PASS`，并且该结论绑定到当前 Candidate 指纹，或通过准确的
Revision Impact 兼容性绑定原样向前沿用到该指纹，用例才达到当前闭合。

## 完成 Acceptance

只有每个冻结用例均达到当前闭合、没有证据失效、每个 Runner 都已静止、所有必需清理与审计成功，
并且不存在终止结果，Acceptance 才通过。通过 Evaluation 返回该结果，随后最终化工作流。
