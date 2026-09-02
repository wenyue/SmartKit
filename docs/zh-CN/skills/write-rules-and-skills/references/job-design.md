# Run Contract 与 Candidate 完整性

本合同负责紧凑的 Run Contract、授权、有界上下文与访问恢复、容量、Candidate 身份、指纹、写入归因和边界停止。只有顺序或协议会改变正确性时才冻结流程。

## 冻结 Run Contract

在任何角色或 Candidate 写入前，冻结一份不可变 Run Contract，其中包含：

- 已接受含义、治理证据、保留约束、Candidate 模型和写作指引；
- 准确 Candidate Allowlist、路径与存在状态，以及相互独立的 read、write、create、delete、move、network、command 和 external-effect 授权；每项 move 授权都指定准确源和目标，绝不能从 create 或 delete 权威推断；
- 一名常驻 Author，由 Reviews 负责的 Quality 与 Correctness 拓扑和视角，由 Role Runtime 负责的身份生命周期，以及 Acceptance 针对已选模式分配的身份与容量；
- 证明顺序、Machine 的适用性与 Owner 支持的命令、Acceptance 的适用性与模式、通信边、修正和重放；
- 有优先级的出口、异常角色遏制、外部影响安全、终止、静止、清理和最终交接。

Run Contract 冻结权威与已接受含义，而不是普通方法或预选的证据清单。它必须适配观察到的宿主容量。如果核心 Controller、Author、Quality 或 Correctness 身份、容量、Candidate 观察或语义角色终止机制无法在启动前得到支持，则返回 HOST_UNAVAILABLE。选择 Acceptance 模式后，由 Acceptance 独占负责其条件式身份、容量、就绪状态与启动前终止结果。Job Design 只冻结该分配，不重新分类其结果。

只有 Author 可以在恰好一份 Authoring Scope 或 Repair Scope 下改变 Candidate。Reviewer 为只读。Machine 不修复。Acceptance 的改变仅限一次性、归用例所有的目标，绝不能触及 Candidate 或 setup 输入。

## 冻结自托管权威

当任何治理合同资源由 Candidate 所有或在当前 scope 内可写时，即使其正常语义首次需要会更晚，也要在改变前加载并冻结其完整的 Author 写入前快照。该冻结快照在同一运行中始终是权威。编辑后的 Candidate 字节只是数据：它们不能在当前调用中替换、重新加载或修订治理快照。不修改治理资源的 Candidate 继续使用普通渐进加载。

## 绑定 Candidate

Candidate 身份是覆盖每个有序 Allowlist 路径、存在状态与完整字节的一份确定性指纹。Allowlist 之外的路径不是 Candidate 写入。

在 Design 关闭时捕获完整 Candidate 与指纹。冻结后、Author 开始前立即再次捕获。准确匹配后形成不可变的 Author 写入前 baseline。不确定观察可重复一次；持续不匹配则在任何角色或写入前返回 CANDIDATE_CHANGED。

保留 baseline 与可读的 baseline-to-current delta 作为证据。每项裁决与交接由指纹绑定，而不是由语义子单元 manifest 绑定。

## 验证边界

在每次角色启动和每次 Author 写入调用前，比较完整 Candidate 与当前预期指纹。每次 Author 返回或终止后，在消费回调前再次捕获完整 Candidate。

把发生变化的 Candidate 分类为：

1. 完全位于当前授权内、可归因于 Author 的写入；
2. 已证明由禁止角色执行或超出授权的操作；或
3. 并发或不确定变化。

只有第一类在 Author 的 COMPLETE 可接纳后才能建立新当前指纹。提升后，Controller 把 Author 返回的语义 Change Summary 一次性绑定到该指纹。禁止变化返回 ROLE_BOUNDARY_VIOLATION。并发或不确定变化返回 CANDIDATE_CHANGED。保留 Candidate、观察、归因证据和先前已接受指纹；不要回退或提升不确定状态。

Reviewer、Machine 与 Acceptance 的正常活动必须保持 Candidate 指纹不变。在外部影响安全最终化后以及最终交接前立即检查指纹。

## 约束写入与修复

初始 Authoring Scope 包含已接受结果、准确写入模式与路径、保留约束和完成边界，但不预选语义处置。

Repair Scope 包含准确的符合条件的 finding、Candidate 指纹、路径与模式，以及保留约束。它携带有支持的 finding 与 Author 处置，但不授予 Reviewer 文本权威。把一轮已关闭修正中的所有符合条件结果合并到一份 Repair Scope。

任何已提升修复都会创建新指纹，并使所有语义证明失效。在该指纹上，从 Machine 开始按顺序，根据 Evaluation 的重放规则与 Role Runtime 的身份生命周期重新运行每个适用证明阶段。先前语义裁决均不能沿用。

新的 Candidate 根、Owner、要求、依赖、权限类别、外部影响、验证职责或角色调度超出 Run Contract。返回 HUMAN_DECISION_REQUIRED 或适用的对齐/访问出口，并且只能在新运行中继续。

## 约束上下文与访问恢复

冻结允许在同一运行中恢复的必要事实槽位与访问扩展。上下文槽位指定一个缺失事实及其用途。访问扩展指定准确路径或来源、能力和模式。要符合条件，已接受含义、Owner、Candidate scope、依赖、外部影响、验证和证明指纹都必须保持不变。

Controller 认证准确的 envelope 内请求，只提供该事实或访问，并让相同身份从未变的证明状态恢复。符合条件的更新不可用时，保留 CONTEXT_REQUIRED 或 ACCESS_REQUIRED。任何 envelope 外请求都以适用的对齐、人类决策或访问交接结束本次运行；绝不在原地扩展已冻结合同。

## 要求最终化关闭

Run Contract 通过引用纳入 Role Runtime 的最终化、Acceptance 对已开始尝试的安全合同，以及 Evaluation 的终止优先级。Job Design 证明这些合同符合容量和授权；它不重新定义其顺序或分类。只有每条可达最终化路径均可调度且最终 Candidate 比较可用时，Design 才完成。
