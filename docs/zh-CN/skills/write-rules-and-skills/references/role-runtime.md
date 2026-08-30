# 角色运行时

这个固定运行时服务于公共、项目本地和共享 writer。它负责 Host Governance、身份与调度的强制
落实、按需证据选择、通道、三份回调报告、Role Boundary Audit、回调可接纳性与组合、语义角色
失败和最终化。Frozen Job Design 负责 Candidate 指纹、delta、证明状态转换与独立边界结果。
后续语义合同负责 finding、判断、修正与重放。

任何活跃 Runner 合同都必须在冻结与角色启动前，证明每种正常、失败、异常和不返回模式之后均能
终止并确认静止。

## 保持 Host Governance 只负责执行

每次角色调用都包含一个由宿主提供的 user-role envelope，其中准确包含以下有序类别：

1. recommended-plugin catalog metadata；
2. repository `AGENTS` instructions；
3. environment metadata。

catalog 与环境 metadata 只读、单独报告且保持惰性。强制宿主或项目指令只约束已获授权操作的
执行方式。它们均不能提供或改变 Candidate 语义、文本、证据、scope、权威、权限、依赖、
条件式执行事实、角色工作或冻结转换；也不能授权操作或访问。独立归属的 Rule、Spec、实现或
外部来源仍可通过其已确立的来源与冻结发现授权提供证据。更早轮次、无关任务和未声明内容类别
不属于角色的语义输入。

冻结前，直接在每份 expected-operation manifest 中冻结规范的封闭 bootstrap 表示，并将其连同
该 manifest 一起提供给角色与 Controller。下列报告证明观察到的符合情况或偏差，以及只负责执行
的使用方式，而不证明语义权威。

## 保留身份与容量

每个语义身份都以全新状态启动，不继承父任务轮次。冻结一个常驻 Author、每个 review unit 的
一个完整全新持久 cohort，以及所有条件式权威身份。首次动作前绑定完整 cohort；单元开放期间
成员不可变，每个成员贯穿修正。失效的已关闭单元使用预绑定且成员完全不同的全新 cohort；此前
身份绝不返回。

为每个批次与轮次绑定单元、cohort、活跃子集、指纹、证据、发现授权、阶段、就绪事件、允许的
Author↔Reviewer 配对与方向，以及讨论状态。暂停保留身份与状态；保留状态占用活跃槽位。应用
Job Design 的容量规则。Reviewer 不接收其他 Reviewer 的工作。

当冻结图允许后续阶段把 Scope Transfer 路由给此前已通过的单元时，该单元在 local PASS 后仍
保持开放，并在转移窗口内暂停其完整 cohort。只恢复预期职责 Owner 进行独立检查。只有不会再有
后续 note 到达且没有待处理的路由检查时，才关闭该单元并结束其 cohort。这是同一个开放单元的
延续；已关闭单元中的身份不会返回。

只有 Controller 操作生命周期与有界更新。每个派发和保留状态都必须适配已冻结调度；应用 Job
Design 的不可用与超额调度结果。绝不替换常驻 Author 或开放 cohort 的成员。

## 按需选择证据

Author 和 Reviewer 从已提供的任务、Candidate 与证据开始。适用指令或具体角色需要有此要求时，
每个角色都可以在已冻结的读取与网络授权以及适用宿主能力范围内，独立检查与任务相关的
Candidate 资源、管辖 Rule、已接受的 Issue 或 Spec、自有实现、测试、配置、仓库约定或外部来源。
他们不会主动检查无关内容、追随环境中的引用，或在没有这种需要时使用工具。

Reviewer 在不接收 Author 推理或其他 Reviewer 工作的情况下独立寻找反证；不同角色选择的来源和
发现不必相同。发现的来源可以支持 Candidate 判断，也可以在 finding 或直接讨论中引用。证据只能
从其 Owner 和来源获得权威，绝不能因为它在仓库或上下文中可见、存在于宿主 envelope、
被发现或经同级传输而获得权威。除非管辖合同允许其用于狭窄用途，否则非规范上下文文档仍不属于
证据基础。Controller 不解释或转述项目证据。

使用 Job Design 的准确授权或范围狭窄的来源/能力类别。在其中选择来源属于普通发现。只有必要
事实无法发现时使用`CONTEXT_REQUIRED`，缺少访问权限时使用`ACCESS_REQUIRED`；两种有界更新
及新运行边界均由 Job Design 负责。
Author 只能通过准确的当前 Authoring Scope 或 Repair Scope 获得 Candidate 操作权限。Reviewer
保持只读。确定性命令和条件式影响仍由相应阶段的 Owner 负责，不进入 Author 或
Reviewer 授权。每项操作都通过本运行时报告并接受审计。

## 保留角色权威

为每个角色冻结 prompt，包含目的、上下文、动作、通信、报告、停止条件，以及相应 manifest、
scope、身份、指纹与证据。Controller 只能适度介入，以强制落实或遏制已冻结控制平面；语义 Owner
继续负责 Candidate 含义、finding 与不动点。

向 Author 提供 Author 合同定义的完整冻结输入，以及准确一份当前 Authoring Scope 或 Repair
Scope。Author 不执行 Machine Validation、条件式执行或委派。每名 Author 与 Reviewer 都应用
[**按需选择证据**](#select-evidence-by-need)，并在必要时返回对应的缺失上下文或访问状态。

`CONTEXT_REQUIRED` payload 准确标识一个已冻结的必要事实槽位、缺失事实，以及它在特定角色
中的用途。Controller 把这些字段与已冻结的更新 envelope 比较，不判断语义是否成立，并原样
保留由 Owner 生成的 payload。

`ACCESS_REQUIRED` payload 准确标识一个缺失的访问目标：本地访问使用准确路径和模式，外部
访问使用准确来源、能力和网络模式。两种形式都包含理由。

Author 在改变 Candidate 前请求缺失的上下文或访问，并在符合条件的更新后，从未变的 expected
proof state 恢复。

Author 准确返回一种状态：

- `COMPLETE`：Author 合同规定的语义 Change Summary、当前判别 scope 外的不确定性，以及随附
  Operation Report 的引用；payload 不重复任何原始操作、受影响路径或写后观察字段；
- `CONTEXT_REQUIRED`：上述通用必要事实 payload；
- `ACCESS_REQUIRED`：上述通用缺失访问 payload；或
- `HUMAN_DECISION_REQUIRED`：准确决策、证据或权威为何无法解决、决策 Owner，以及每个当前
  选择的后果。

Reviewer 独立负责 finding、分类与裁决，不接收 Author 推理或其他 Reviewer 的工作。Author 与
Reviewer 绝不委派，只能在授权与宿主能力内使用网络。Runner 只执行冻结用例；绝不委派，也不
负责判断、修复、设置修正、清理或角色控制。只有 Controller 操作身份、授权访问或提供有界更新。

## 关闭语义角色异常执行

对于每次 Author 或 Reviewer 调用与继续，冻结一个可观察的不返回、身份丢失或继续失败触发条件
及其证据。它可以使用受支持的宿主终止状态或预先声明的有界检测器；本合同不提供任意 timeout。

触发后，Controller 保留所有可获得报告、通道记录、宿主事实和 Candidate 指纹；通过不含语义的
控制 metadata 中止开放讨论；尝试已冻结的终止操作；并审计所有可获得证据。记录缺失回调，不得
虚构 payload。在作出遏制决定前，不得启动身份、写入 Candidate、讨论或启动后续阶段。

Author 异常执行并完成终止后，完成 Job Design 的完整内容调用最终捕获，并派生取证指纹与规范
delta。Reviewer 异常执行并完成终止后，通过 Job Design 的独立组合，把全 Allowlist 与 expected
proof state 比较；不派生 Candidate 指纹或规范 delta。

已证明的违规返回`ROLE_BOUNDARY_VIOLATION`；否则返回`SEMANTIC_ROLE_UNAVAILABLE`。把事故
送入 Evaluation 的遏制决定，且不替换常驻 Author 或开放 cohort 成员。无法结束身份或证明其不
活跃时，最终化期间可能变为`TEARDOWN_FAILED`。保留不可变 cohort 成员、常驻 Author 连续性、
Candidate 状态和事故证据。

## 通过 metadata 打开直接修正

不冻结 Reviewer↔Reviewer 边。每个 finding 使用以下两步 bootstrap：

1. 私下判断固定完整 finding 集合和每个不透明稳定 ID 后，Reviewer 为每项 finding 发出一次经
   审计、不含语义的`FINDING_READY`回调。每次回调只包含单元、轮次、Candidate 指纹、
   Reviewer 身份、finding ID、finding 集合完成标记，以及三份正常报告。仅在最后发出的一项
   finding 上设置该标记；空集合使用绑定到当前指纹的`PASS`。该标记只证明发出已完成，绝不
   证明 finding 含义或裁决。
2. Controller 根据冻结配对与 manifest 审计回调后，向该 Author↔Owner 配对返回`CHANNEL_OPEN`
   metadata。只有此时 Reviewer 才把完整 finding 直接发送给 Author。

Author 合同提供处置与 proposed-write 判断；当前 review 合同提供主张、严重级别与不动点判断；
Evaluation 把双方的准确最终结果映射为写入资格。本运行时不选择任何结果。**处置控制 metadata**
为`repair`、`partial repair`或`decline`，并带 proposed-write `true`或`false`。
**写入资格控制**为`eligible`或`ineligible`。理由、主张、证据、论证与修复方向仍是只在同级间
流动的语义正文。

Author 与 Owner 直接交换语义内容，并分别独立判断。Controller 只看到控制 metadata。双方用经
审计的`DISCUSSION_CLOSED`关闭配对，其中包含单元、轮次、指纹、身份、finding ID、准确最终
处置与 proposed-write 控制、投递状态、由 Owner 产生的不动点状态（`reached`、`not reached`或
`not applicable`）、由 Evaluation 派生的写入资格控制，以及 finding 集合状态（`complete`或
`reopened`），但不含语义正文。对于具备写入资格的结果，两个 event 还携带匹配且不含语义的
scope control：准确 Candidate 路径与模式、preservation-reference ID 和就绪状态。Controller
根据冻结授权与 Evaluation 映射认证并比较这些字段；缺失、不匹配或超出授权的控制会使回调不可
接纳。所有配对关闭后，Author 发出一份由 eligible ID 与匹配 scope control 组成的经认证
aggregate；Controller 只能把该准确并集冻结复制进 Repair Scope。

`DISCUSSION_CLOSED`只关闭通道与轮次；同指纹的另一轮必须再次执行
`FINDING_READY → CHANNEL_OPEN`。同级通信不能操作角色或改变权威；传输不会赋予权威。

每个回调从其冻结语义合同中暴露一个结果。`DISCUSSION_CLOSED`是生命周期事件，不是结果或
finding。原样保留 Owner 生成的请求；Controller 只检查转换字段，绝不判断语义是否成立。任何经
认证的 Controller、Author 或 Reviewer `HUMAN_DECISION_REQUIRED`都会触发后续语义生命周期的
立即停止。

## 消费回调前先审计

每次正常回调都必须携带以下三份报告：

- **Operation Report：**它是准确原始`read`、`write`、`create`、`delete`、`move`、`network`、
  `delegation`和`machine checks`操作的唯一 schema Owner；空类别使用`none`。Author 还要报告准确
  的变更、创建、删除与移动路径身份及其写后观察。只读调用在这些变更字段中报告`none`。若一次
  原始`write`未改变内容，该操作仍保留在原始`write`记录及其内容未变的写后观察中；它不会创建
  变更路径身份。它绝不报告或创建由 Controller 观察到的 Candidate 指纹或规范 delta。
- **Peer Report：**Author 与 Reviewer 始终包含单元、轮次、一个有判别标识的 expected-proof-state
  引用、独立就绪事件、阶段和身份。适用状态为 pre-Author 的每次 Author 调用或继续都报告不可变
  基线身份、冻结的 Design-close 全 Allowlist 指纹，以及与其匹配的 pre-Author baseline 全
  Allowlist 指纹。适用状态已提升的每次 Author 或 Reviewer 调用都报告 Controller 提供的适用
  Candidate 指纹。Author 的写后观察只存在于 Operation Report；它绝不声称拥有由 Controller
  派生的调用最终指纹或规范 delta。Runner 把单元映射到冻结的
  用例单元，把轮次映射到尝试序号，把 expected-proof-state 引用映射到 Attempt
  Contract 的 Candidate 指纹，把就绪事件与阶段映射到 manifest 绑定的准确 Runner 启动/尝试
  值，并把身份映射到 Runner 身份。每个角色还要包含方向、消息类型、投递和 Author 参与情况；
  禁止或没有同级通信时，准确为这四个通信字段使用`none`。报告不得包含语义正文或裁决。
- **Host-Governance Report：**观察到的封闭 bootstrap 符合情况或准确偏差、catalog 与环境
  metadata 以惰性方式使用的证据、所读项目指令及其只负责执行的影响或`none`，并确认 governance
  未提供任何禁止的语义或权威输入。

Frozen Job Design 将某项 Reviewer `PASS`标记为携带 coverage 时，Controller 只验证其冻结结构
manifest：单元、身份、指纹、标记、准确输入集合、必需字段、允许标签、非空锚点、唯一不透明 ID，
以及闭合的 ID 交叉引用。提升后的 coverage 使用 Job Design 当前 expected-proof-state delta-item
与 economy-unit 绑定。数据缺失、多余、陈旧或不一致时，回调不可接纳。Controller 不判断任何
语义价值或完整性。

每次 Author 返回或终止完成后，捕获全 Allowlist，并在回调组合前调用 Job Design 的调用最终转换。
把已报告操作、路径与观察同该捕获及宿主事实核对。只把报告视为声称；即使回调缺失或不可接纳，
也要在消费语义 payload 前执行这项审计。

依据 expected-operation manifest，审计报告与宿主证据中的调度、身份、授权、bootstrap、指纹、
写入、通信，以及 Job Design 适用的证明状态绑定与 delta 来源。证据缺失、陈旧、不完整或不匹配
时，回调不可接纳。条件式合同允许异常执行后缺少报告时，记录缺失并审计所有可获得事实。

经认证且可归因的`HUMAN_DECISION_REQUIRED`属于终止控制：立即停止语义工作，即使存在其他审计
缺陷也原样交付请求，并且不消费其他 payload。若请求来自 Author，则调用 Job Design 的 human-stop
转换。只完成审计与最终化；保留禁止操作或并发/不确定不匹配分类。无法准确归因时，采用普通不可
接纳或异常路径。

除此以外，任何禁止操作、超额调度、调度/授权/同级边违规、报告缺失或不一致、manifest/bootstrap/
governance 不匹配或无法调和的证据，都会使回调不可接纳；除非条件式安全支配结果，
否则向语义生命周期提供`ROLE_BOUNDARY_VIOLATION`。对于 Author，调用 Job Design 的边界转换，
不得回退 Candidate 或证据。

Author 回调异常或缺失时，调用 Job Design 对应转换与独立不匹配结果。另行把角色事故分类为：
已证明违规时为`ROLE_BOUNDARY_VIOLATION`，否则为`SEMANTIC_ROLE_UNAVAILABLE`；保留两项已成立
结果，并遵循异常执行遏制与最终化。

对于其他每个正常 Author 回调，先应用 Job Design 归因，再执行审计。未知或畸形状态不可接纳。
发生变更的调用加上不可接纳回调，始终在条件式安全后采用整次运行的边界转换，不消费 payload、
不作提升且不允许继续；只有与 expected proof state 准确匹配时才可局部遏制。

- 可接纳的`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`要求不存在不匹配，并使用需求转换。可归因的
  Author 变化采用边界转换；并发或不确定变化通过相应转换返回`CANDIDATE_CHANGED`。
- 可接纳的`COMPLETE`在存在可归因的 Author 变化或准确匹配时使用完成转换；准确匹配时复用 Job
  Design 的规范 delta。边界证据采用边界转换，并发或不确定不匹配返回`CANDIDATE_CHANGED`。

对于非 Author 回调，边界证据支配结果；禁止操作不匹配返回其边界结果，其他不匹配均返回
`CANDIDATE_CHANGED`，准确匹配则允许冻结转换。不匹配绝不提升。只有本组合负责归因不确定性。

在角色启动前和条件式安全之后，把全 Allowlist 与 expected proof state 比较，并应用 Job Design
的独立组合。只有准确匹配后才启动；这些检查绝不使用回调组合，也绝不提升状态。

## 最终化工作流

启动任何角色后，均适用最终化：

1. 按各自安全与终止优先级合同，完成每项已经开始的条件式执行。
2. 结束每个活跃、保留和暂停的身份，同时保留报告、证据与 Candidate 状态。
3. 确定准确残留活动。
4. 条件式安全最终化后，在选择待处理结果前，调用 Frozen Job Design 的安全后全 Allowlist 比较
   与独立边界结果组合。
5. 所有非 Controller 角色活动都已完成，且没有安全或拆除终止结果时，在干净成功交接之前立即
   调用 Frozen Job Design 的最终全 Allowlist 比较与独立边界结果组合。独立边界绝不提升状态。
6. Controller 最后退出。

无法结束身份或证明其不活跃时，返回`TEARDOWN_FAILED`。保留下层结果、准确残留身份与活动、
证据，以及安全的拆除尝试。若残留 Runner 或语义角色阻止完整拆除，Controller 可以在安全结束
其他所有内容后发出终止报告并退出；这是最后退出规则的唯一例外。只声明已经确认的静止、清理、
拆除，以及最终 expected-proof-state 匹配。
