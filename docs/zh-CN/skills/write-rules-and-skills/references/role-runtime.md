# 角色运行时合同

这份可移植合同服务于公共、项目本地和共享 writer。它负责身份、证据访问、通信、正常回调、边界审计、异常执行和最终化。让普通角色执行由判断主导，只有需要确立权威、归因或安全时才要求详细审计。

## 强制落实宿主输入边界

[Models 的证据权威规则](models.md#close-alignment)是宿主与仓库输入唯一的语义 Owner。执行角色时，强制落实该已接受边界与冻结授权；强制指令只能约束 Run Contract 已授权操作的执行方式。在受支持 writer 上下文之间移植，不会改变权威、路径、兼容性或下游交付授权。

## 身份与独立性

启动一名全新常驻 Author，并在本次运行中保持该身份。启动从 Reviews 冻结的 Quality 与 Correctness 拓扑。每名 Reviewer 首次启动时均为全新身份，并在其阶段保持开放期间持续参与修正与复查。如果已 PASS 并关闭的阶段因下游修复或阻塞性跨视角检查请求而失效或重新打开，则为该阶段启动全新的 Reviewer 身份；已关闭的身份不会返回。Acceptance 独占分配其所选模式的身份、容量和启动前终止结果；本运行时只启动该冻结分配，不重新分类它。Reviewer 不接收 Author 推理，也不接收另一名 Reviewer 的 finding、裁决、推理、笔记、coverage 证明或预选结论。Quality 的当前关闭状态及其指纹只属于 Controller 的启动 Gate metadata，不作为证据提供给 Correctness。

Controller 负责生命周期与容量。角色不能委派、扩展授权、操作另一角色或改变 Run Contract。暂停会保留身份。如果阶段仍保持开放时所需身份无法继续，则返回 SEMANTIC_ROLE_UNAVAILABLE，而不是在阶段中途替换一名新裁判。

## 证据与授权

提供已接受要求、治理证据、保留约束、当前完整 Candidate、指纹，以及角色的准确授权。Author 还接收当前 Scope 与 baseline。Q2 和 Correctness 接收 baseline 与完整 delta。Runner 只接收其冻结用例与 attempt contract。

角色根据需要在授权内选择证据。来源可见或同级传输不能赋予权威。Controller 传输证据并强制落实边界，但不解释 Candidate 含义或 finding。

一个必要但无法发现的事实缺失时，角色返回 CONTEXT_REQUIRED；一个准确来源、路径、能力或模式无法访问时，返回 ACCESS_REQUIRED。写明其重要性。会改变已接受含义、归属、Candidate scope、权限类别、外部影响或验证的扩展，返回 HUMAN_DECISION_REQUIRED，并交给新运行。

Controller 把每项请求与[Job Design 的冻结恢复 envelope](job-design.md#bound-context-and-access-recovery)比较。准确匹配时提供有界更新，并在未变指纹上恢复相同身份；其他请求都遵循该合同的新运行交接。

## 正常回调

正常回调保持简洁：

- 角色状态或裁决，以及提供给它的调用指纹；
- Author 的语义 Change Summary 与变更路径，或 Reviewer finding 与全 Candidate coverage 证明；
- 未解决、不确定或未测试的表面；以及
- 对于 Machine，命令、退出状态与相关失败输出；对于 Acceptance，模式与用例证据。

不要要求空的 operation 行、peer 行、host 行、不透明 coverage ID 或逐资源 manifest。只有在需要确立写入归因、来源、边界不匹配、异常执行、外部影响、清理或其他重要权威/安全事实时，才记录原始读取、写入、消息、宿主事实和操作细节。

消费回调前，认证身份、角色、指纹、授权与允许的通信。把 Author 变更路径与 Job Design 的返回后捕获进行核对。重要边界证据缺失或无法核对时，返回 ROLE_BOUNDARY_VIOLATION。

原样传输 Acceptance Reviewer 的 AMBIGUITY_OBSERVATION_REQUIRED，并携带其准确观察、有界 setup 与 capture delta、证据需要、用例和指纹。Controller 可以把该 payload 复制进下一份冻结 Attempt Contract，但不能解释或修改其语义内容。

仅当 Reviews 把一项非阻塞观察分类为超出 Reviewer 视角或裁决权威时，才将其作为 deferred surface 传输。Controller 为最终交接原样保留它，不作解释，不路由给其他 Reviewer，不将其视为 finding，也不改变当前证明。

把 Reviews 分类的阻塞性跨视角检查请求只传输给其所属视角。请求仅包含 Candidate 位置、目标视角与指纹，不包含发起方的推理、评估或结论。它不是 finding 或证据；接收方 Reviewer 按 Evaluation 的关闭 Gate 独立检查 Candidate。

## 直接修正

Reviewer 在私下判断后，把每项有支持的 finding 直接发送给常驻 Author。只有该配对讨论相应主张。Controller 知道 finding 标识、指纹、通道状态、最终 Author 处置、阻塞不动点状态与拟议 Repair Scope；它不决定或重写语义内容。

任何讨论尚未关闭时，Candidate 写入保持关闭。所有通道关闭后，Controller 只能把 Evaluation 判定符合条件的 finding 合并到准确 Repair Scope。Reviewer 之间绝不通信。

经过认证的 HUMAN_DECISION_REQUIRED 会立即停止语义工作，即使其他回调证据尚不完整。原样保留请求，只执行安全和最终化。

## 异常执行与边界

每个角色启动前，都要建立可观察的不返回、身份丢失或无法继续的检测方式，以及获授权的终止路径。可执行 Acceptance 还要建立 Runner 静止与清理机制。

发生异常执行时，保留可获得的 Candidate 观察、回调、外部影响、通道与宿主证据；关闭通道；终止角色；并证明其不再活动。已证明违反授权、身份、通信、Candidate 写入或调度时，返回 ROLE_BOUNDARY_VIOLATION。否则，语义身份失效时返回 SEMANTIC_ROLE_UNAVAILABLE。Runner 安全终止结果仍由 Acceptance 负责。

普通回调不需要完整复述审计。只有异常执行、边界不匹配、外部影响，或需要确立权威、归因、清理或残留安全时，才在交接中包含详细 operation、peer 与 host 证据。

## 最终化

启动任何角色后：

1. 完成每项已开始 Acceptance 尝试的安全流程；
2. 关闭通道，并结束活跃或暂停的角色；
3. 确立静止、清理与残留活动；
4. 执行安全后与最终 Candidate 比较；以及
5. 安全时由 Controller 最后退出。

根据 Evaluation 的终止优先级，无法结束某个角色或证明其不再活动时，TEARDOWN_FAILED 会覆盖同时出现的非安全、非边界结果，同时保留被覆盖的结果和残留状态。安全结束其他所有角色，报告准确的残留角色与状态，并允许 Controller 退出。这是完整 teardown 与 Controller 最后退出规则的唯一例外。
