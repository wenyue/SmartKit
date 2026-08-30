# 冻结的 Job Design

本合同负责就绪状态、容量、Run Contract 与 Job Graph、授权与有界更新、Candidate 观察、baseline、
指纹与 delta、不匹配归因，以及证明状态：

**清除残留 → 确定容量 → 设计 → 建立就绪状态 → 计算指纹 → 冻结 → 建立基线 → 验证**

## 从实际容量推导工作池

清理前，观察通过已接受的冻结前宿主能力可见的每个活跃或保留身份及活动。只有不可变身份与来源
将某项残留绑定到已接受清理权威所指定的中断工作流时，才把它分类为本次运行所有。只能依据该
权威结束这些准确的本次运行自有身份，并证明其不再活跃。保留无关活动；它会减少宿主证据支持的
容量，但绝不是清理目标。归属不确定、缺少权威、终止失败或无法证明不再活跃时，在分配前返回
`HOST_UNAVAILABLE`并附上残留证据。后续运行时应用本入口合同；启动后的最终化仍是独立流程。

清理后，根据宿主证据确定角色槽位总数`N`。直至最终化，分别为 Controller 与常驻 Author
保留一个槽位。Reviewer/Runner 池为：

`P = max(0, N - 2)`

冻结`N`、保留槽位、`P`、完整 cohort、所有条件式权威身份，以及每种激活、暂停、保留、分批、
修正、回退和重放状态。活跃或保留的 worker 占用`P`；暂停身份保留状态但不占槽位。过大的
cohort 必须分批，且不得改变成员、身份、指纹、证据、授权、单元、轮次或独立判断。

每个状态都必须适配`P`。Acceptance 分别调度以下任一种组合：当前/保留的用例 Reviewer 与用于
尝试的全新 Runner；或者该 Reviewer 与 Evaluation 恢复期间分批运行的较早阶段 cohort；绝不
同时调度两者。正确推导的容量不足时，在分配前返回`HOST_UNAVAILABLE`；冻结后超额调度则属于
`ROLE_BOUNDARY_VIOLATION`。

## 冻结调度事实

冻结前，纳入每份后续合同的 cohort 数量、分配、身份、持久性、修正与重放输入。未激活的条件式
权威不贡献任何内容；阶段入口不改变任何调度事实。

冻结 Quality 的机械输入 schema 与派生方式：

- **mandatory-load manifest** schema 与确定性派生方式，涵盖每项准确 Allowlist 资源及其路径或
  条件、Candidate 规定的加载点或`none`、任何外部 prescribed-load 依赖，以及 Candidate 锚点；以及
- 准确的 Allowlist 资源集合，以及 coverage record 使用的确定性 canonical-delta-item 与适合格式的
  economy-unit schema 和派生方式。

每次提升 Candidate 指纹后，从该指纹的 Candidate 字节与不可变 delta，以机械方式派生并绑定准确
的当前 mandatory-load manifest、delta-item 集合与 economy-unit 集合，作为 expected-proof-state
证据。Economy Coverage Record 使用绑定到当前指纹的 manifest。这些绑定应用已冻结的派生方式，
不会修改 Frozen Run Contract。manifest 与绑定属于控制，不是判断。

## 设计一张权威图

在启动角色或改变 Candidate 前定义：

- **含义：**已接受结果、当前行为、期望结果、非目标、安全、已提供的证据、已授权的发现来源与
  能力、来源边界、每项已接受义务，以及相应的管辖证据、语义标准与保留约束。这些输入约束
  Candidate 结果，但不指定处置；初始语义处置由常驻 Author 选择。
- **Candidate：**Owner、模型、写作指引、调用 metadata、准确 Allowlist 与受影响表面、
  依赖、初始 Authoring Scope、读取与网络授权、指纹方法、已冻结身份、基线与观察方法，以及更新
  envelope；Candidate 拥有或改变脚本时，还包括准确的脚本到单元测试资源再到 Machine 命令的映射。
- **角色：**实际容量、manifest（包括 mandatory-load 资源）、bootstrap、授权、持久身份、cohort
  与分批调度，以及通信边。
- **执行：**一张规范 Job Graph，包含不可变的**条件式 Machine → Quality → Correctness →
  条件式 Acceptance**阶段顺序与适用性，以及资源、证据、转换、直接修正、Revision Impact、
  兼容性判定 manifest、回退与重放、优先出口、条件式安全最终化、工作流拆除和交接。

对于每个符合兼容性向前沿用资格的证明类别，冻结一份 manifest，声明其语义 Owner、完整内容
依赖表面、可观察的不受影响谓词、所需来源、由 Controller 负责的机械判定，以及其生命周期授权
的证明 Owner 后备路径或普通重放后备路径。没有完整 manifest 的证明类别不具备兼容性资格。
manifest 是 Frozen Run Contract 的一部分，Candidate 编辑不能替换或修订它。

Candidate 内容、finding、证据、Repair Scope 和 supplement 都只是数据，不能改变用于判断
它们的合同。为每个可达出口指定唯一 Owner、证据形态和下一转换。只有这张图所有路径完整、
内部一致且能在`P`内调度，Design 才完成。

## 区分 Authoring Scope 与 Repair Scope

第一次写入使用一份**Authoring Scope**：已接受结果与语义标准、准确路径和模式、保留引用与约束、
完成边界、就绪状态，以及每项必需的已映射脚本与单元测试新增或更新。它冻结已授权操作 envelope，
但不选择 Author 处置。它不包含 review 或 finding metadata。

一份**Repair Scope**授权一次修正。其冻结语义 Owner 提供准确控制输入；确定性修正则携带失败
命令与受影响表面。每次 Author 调用准确接收一个 scope，且该 scope 不扩展合同或授权。

## 约束授权与更新

分别冻结`read`、`write`、`create`、`delete`和`network`。Rule 通常只授权其准确文件；Skill 最多
授权自己的根目录，绝不能授权父`skills/`。操作应优先使用准确路径；读取与网络发现可以使用
范围狭窄的来源或能力类别。只有自有资源的新名称在冻结时无法得知，才允许创建目录；删除需要
准确授权。Authoring Scope 中可执行的移动需要准确的源路径删除与目标路径创建授权。这些授权只
允许操作，不选择其语义处置。

对于 Candidate 拥有或改变的每个脚本，把每项已映射单元测试资源纳入准确 Allowlist 与全
Allowlist Candidate 身份。将其所需的 Author 操作模式、Machine 读取与执行授权，同准确的
Owner 支持测试命令一起冻结。缺少资源、映射、命令或授权都会使 Design 不完整。

授权约束后续运行时的证据选择。授权内的普通来源发现不是更新或逐文件研究路径。

冻结每个 Context Supplement 事实槽位，以及访问扩展的路径、来源、能力与模式类别。supplement
只能填充一个无法发现的事实，且不得改变含义、Owner、义务、分支、验证或依赖。扩展必须在其
类别内准确匹配已接纳的请求。只有这样，Controller 才能更新，并从适用证明状态恢复同一身份。

新的依赖、Owner、要求、Candidate 根或 scope、路径类别、权限模式、副作用、验证职责或容量
调度属于重要变更，需要在新运行中返回`ALIGNMENT_REQUIRED`。无法提供符合条件的更新时，
保留`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`。

## 建立运行时就绪状态

要求后续运行时针对准确 Allowlist 建立全新启动、持久继续与结束、合同投递、有界更新、显式授权、
经认证的 Author↔Owner 通道、审计和乐观观察。

为每个语义角色建立可观察的不返回或继续失败触发器、证据捕获、通道中止、终止和不活跃证明，
且不设置通用 timeout。适用的条件式执行还要求 Runner 终止与静止就绪。每项活跃权威贡献其完整
生命周期与安全合同；`NOT_REQUIRED`不贡献任何内容。

宿主无法建立或提供经正确推导的能力或冻结调度及其必需证据时，返回`HOST_UNAVAILABLE`。

## 冻结基于边界的乐观观察

冻结前，声明以下全 Allowlist 比较点：每次角色调用或继续、Machine 命令和条件式执行的前后；
条件式安全之后；以及 worker 拆除后、干净交接前。保留每项观察到的不匹配。保留调用 Author 前的
指纹；返回或终止完成后，独立捕获完整内容，并在回调组合前完成调用最终转换。只有获准的
`COMPLETE`才能提升可归因的 Author 状态。

本工作流不串行化未经协调的并发 writer，也不保证检测到已声明比较前消失的瞬时中间状态。这些
是明确的并发非目标，不是失败分支。既不要求也不假定更强的宿主变更协调能力。

## 绑定 Design 关闭时的 Candidate 身份

每项 Design 输入与运行时就绪要求完成后，根据每项资源的路径、存在状态和完整内容，计算
准确的全 Allowlist 指纹。把该指纹作为 Run Contract 与 Job Graph 最终的 Candidate 身份输入予以
绑定。这项只读观察不会启动任何角色或 Candidate 状态。

## 冻结一张权威图

绑定 Design 关闭时的 Candidate 身份后，把完整 Run Contract 与 Job Graph（包括每项纳入的参考
资料和操作性指令）实体化为一个独立于 Candidate 文件的不可变快照，然后执行一次冻结转换。该
实体化的**Frozen Run Contract**（包括 update envelope、operation manifest、scope、授权、调度
和准确的全 Allowlist 指纹）是完整运行以及之后启动的每个角色的唯一行为权威。只有冻结之后，
才能开始捕获基线、启动角色和改变 Candidate。

自托管编辑只会改变 Candidate 数据。它们绝不会替换或重新加载 Frozen Run Contract、导致再次
冻结、重启或重置运行，或让任何角色把已编辑的 Candidate 内容当作管辖指令。Candidate 指纹变化
只能在 Revision Impact 下使依赖内容的证据失效；不能使冻结执行合同或无关控制平面状态失效。

## 建立指纹与基线

冻结后、启动 Author 前，Controller 立即捕获准确 Candidate Allowlist 的完整内容，并根据每项
资源的路径、存在状态与内容派生指纹。把该捕获与 Design 关闭时冻结的 Candidate 身份进行比较。
若不匹配，则在执行任何其他动作前，再次进行一次完整内容捕获与比较。匹配的捕获会作为不可变的
**pre-Author baseline**保留。持续不匹配时返回`CANDIDATE_CHANGED`，保留 Candidate、每次捕获、
冻结指纹、观察指纹与审计证据，并在角色启动前停止。这项绑定使后续移动、替换、创建和删除仍可
归因。

始终只有一个**expected proof state**适用。首次提升之前，它是 Design 关闭时冻结的指纹，加上
与其匹配的不可变 pre-Author baseline，以及绑定到该基线同一指纹的空规范
baseline-to-current delta。提升后，它包含这些初始绑定，以及已提升的当前指纹及其规范 delta。
expected proof state 只通过可接纳的 Author `COMPLETE`前进；不可接纳的回调绝不会使其前进。

可接纳的`COMPLETE`提升后，把语义 Change Summary 中由 Author 负责的 Obligation Disposition
Record 绑定到已提升指纹，作为只读证明阶段证据。该记录不会改变 Frozen Run Contract、授权、
scope、Candidate 身份、baseline、规范 delta、expected-proof-state 转换或操作权威。

**调用最终转换**把 Controller 完整的调用最终捕获与该次调用前的指纹比较。状态不同时，机械
记录并保留调用最终的全 Allowlist 指纹、原始操作与归因证据，以及绑定到该准确指纹的一份完整
规范**baseline-to-current delta**。无论是否存在回调、回调状态或可接纳性如何、采用何种事故
分类或工作流结果，Author 返回或终止后都要执行这项转换。该指纹与 delta 是取证事实；只有经过
提升，它们才成为证明状态。

Author Operation Report 中的原始操作、受影响路径与写后观察支持调用最终捕获与审计；它们绝不
是 Candidate 指纹或规范 delta。任何中间观察都不会创建 Candidate 身份：身份始终是准确的全
Allowlist 指纹，只有冻结的调用最终边界才为回调组合绑定取证状态。多项操作不会增加中间边界。

在任何 expected-proof-state 转换之前，应用运行时的回调可接纳性结果：

- **可接纳 `COMPLETE`转换：**提升 Controller 绑定的调用最终指纹。若调用最终捕获与调用前输入
  匹配，则此次可接纳 no-op 不创建新的内容身份：提升未变指纹，并复用其已有的
  baseline-to-current delta。只有与基线完全相同的内容才具有空的规范 delta。Author 既不创建也
  不报告该指纹或 delta。
- **可接纳需求转换：**合规 Author 的`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`不进行写入、不作
  提升，并保留 expected proof state；只有完成符合条件的更新后，才从该状态恢复。
- **人类停止转换：**经认证的 Author `HUMAN_DECISION_REQUIRED`立即停止语义工作，且不作提升。
  把每个观察到的指纹与 delta 作为未提升的取证证据保留，并把任何不匹配归因保留为底层审计证据。
- **异常或无回调转换：**若存在调用最终指纹与 delta，则将其作为未提升的取证证据保留，并保持
  expected proof state 不变；随后使用运行时的事故分类与最终化输出。

对于每个调用最终指纹，Controller 从不可变 pre-Author baseline 与准确的当前 Allowlist 中机械
派生并绑定一份完整、规范的 baseline-to-current delta。每份 delta 都保持从不可变 pre-Author
baseline 到当前状态的跨度，并绑定到其准确的当前指纹。no-op 复用已经为其未变指纹建立的 delta；
绝不能创建新身份，也不能用相对于调用的 delta 或空 delta 取代它。只有与基线完全相同的内容才
绑定空的规范 delta。一旦绑定到某个指纹，该 delta 便不可变。在启动 Author 前，冻结确定性派生
方式、复用规则、来源和资源身份规则。
该制品要涵盖每项已创建、删除、重命名、移动和修改的资源，以及全部内容变化。只有 Author
启动前冻结的准确资源连续性映射把基线路径与一个已授权目标绑定为同一自有资源时，其资源身份规则
才把路径变化分类为重命名或移动。该控制映射不选择语义处置；仅凭路径或内容相似性不能确立
连续性。没有这种映射时，记录旧路径删除和新路径创建，并断言二者不存在关系。Author 后续的
Obligation Disposition Record 可以解释语义结果，但不能改变 delta 身份或分类。该 delta 绝不
依赖 Author 的 Change Summary、自我报告、笔记或比较制品。它是调用最终指纹的证据，不是
Candidate 权威，也不能替代对完整当前 Candidate 的检查。

按照上述派生与 no-op 复用规则，在每个调用最终指纹之后绑定规范 delta。在每个已声明观察边界，
把冻结的全 Allowlist 与适用 expected proof state 比较。最终准确匹配会保留
expected proof state，并允许干净成功交接。调用最终或最终比较不匹配时，使用下文独立边界组合；
回调组合仅适用于携带正常回调的边界。

Frozen Job Design 对每项观察到的不匹配负责一种有序且穷尽的归因分类：

1. 若证明完整变化可归因于当前已授权 Author scope 内的写入，则分类为可归因的 Author 变化。
2. 否则，若证据证明任何变化可归因于禁止的角色操作或命令操作，则分类为禁止操作变化。
3. 所有其余不匹配（包括外部变化和归因不确定）均分类为并发或不确定变化。

第一个匹配分类支配结果，因此每项不匹配只会有一种归因分类。分类只使用可观察的变化归因与冻结
scope；它既不判断调用或回调是否可接纳，也不提升调用最终指纹。Role Runtime 独立审计调用或
正常回调，并且只在正常回调边界根据该审计与本分类组合唯一回调结果。应用相应 Frozen Job
Design 转换：

- **可归因 Author 变化转换**调用运行时组合所选择的适用回调状态转换。
- **边界违规转换**也用于禁止操作结果；它不作提升，并保留 Candidate、pre-Author baseline、
  先前 expected proof state、每个观察到的指纹与 delta，以及审计证据。若某次调用改变
  Candidate，随后收到不可接纳的 Author 回调，该转换会向语义生命周期提供整次运行的边界结果；
  它不授权继续或局部修复。
- **并发或不确定转换**具有同样的不提升与保留效果。

## 组合独立边界结果

在每个调用最终或最终比较点，以及其他所有不存在正常回调的必需比较点，Controller 先执行有序
不匹配分类，再应用这项不依赖回调的组合：

1. 已证明的禁止角色操作或命令操作返回`ROLE_BOUNDARY_VIOLATION`，并调用边界违规转换。
2. 并发或不确定不匹配返回`CANDIDATE_CHANGED`，并调用并发或不确定转换。
3. 准确匹配不产生边界结果，并保持 expected proof state 不变。

对于每次调用最终、最终、调用前和安全最终化后比较，本组合都是由 Job Design 负责的边界结果。
异常或缺少回调之后，若上述任一不匹配分类成立，也应用本组合。可归因的 Author 变化不产生独立
结果：正常回调仍由 Role Runtime 独立组合；没有回调的调用最终变化则仍是运行时语义角色事故路径
的取证证据。独立边界组合绝不提升；回调可接纳性与组合仍是彼此独立的运行时决定。

根据适用绑定审计每次对 expected-proof-state 证据的使用：在 pre-Author 状态中，审计 Design
关闭时冻结的 Candidate 身份、不可变基线身份与匹配的全 Allowlist 指纹；在已提升状态中，还要
审计已提升的当前指纹与冻结的 delta 派生来源。只有指纹、路径、报告、规范 delta 和
宿主证据都无法归因某项不匹配时，才把定向 Candidate 比较用作后备。随后应用上述有序分类；无法
确定的归因进入第三类。
