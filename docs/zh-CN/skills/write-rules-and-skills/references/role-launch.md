# 角色启动

这个唯一固定运行时由公共、项目本地和共享 writer 原样使用。它负责 Host Governance、身份生命
周期、调度、通用的按需证据选择、语义通道、规范化报告、Role Boundary Audit、语义角色失败、
条件式角色组合和工作流最终化。调用方自有的证据资格政策可以收窄 Candidate 证据，但不得改造
本运行时。

下列准确的三报告回调 schema 具有规范效力。**Operation Summary**指 Operation Report、Peer
Report 和 Host-Governance Report 组成的完整 bundle；绝不省略或替换 Peer Report。
**bootstrap report**就是 Host-Governance Report。[`acceptance.md`](acceptance.md)负责
Acceptance 用例设计、尝试、判断、修正与重放；本运行时负责这些尝试所使用的共享启动、审计、
身份和最终化机制。这些映射不增加第二套 schema 或 Owner。

Acceptance 适用时，Design 必须在冻结和启动任何角色前，证明每种已声明的 Runner 正常、失败、
异常和不返回模式之后都能终止并确认静止。

## 保持 Host Governance 只负责执行

每次角色调用都包含一个由宿主提供的 user-role envelope，其中准确包含以下有序类别：

1. recommended-plugin catalog metadata；
2. repository `AGENTS` instructions；
3. environment metadata。

catalog 与环境 metadata 只读、单独报告且保持惰性。强制宿主或项目指令只约束已获授权操作的
执行方式。它们均不能提供或改变 Candidate 语义、文本、证据、scope、权威、权限、依赖、
Acceptance 事实、角色工作或冻结转换；也不能授权操作或访问。独立归属的 Rule、Spec、实现或
外部来源仍可通过其已确立的来源与冻结发现授权提供证据。更早轮次、无关任务和未声明内容类别
不属于角色的语义输入。

冻结前，把规范的封闭 bootstrap 表示绑定到每份 expected-operation manifest 中一个不可变的
**Envelope ID**，并向角色与 Controller 提供相同值。角色只引用该 ID，不序列化或散列 envelope。
下列报告证明观察到的一致性与只负责执行的使用方式，而不是语义权威。

## 保留身份与容量

每个语义身份都以全新状态启动，不继承父任务轮次。冻结模板包含：从启动到最终化保持不变的一个
常驻 Author；每个 review unit 的一个完整全新持久 Reviewer cohort；以及各条件式权威声明的
所有身份。Controller 与常驻 Author 在此期间持续占用各自保留槽位。首次动作前绑定完整 cohort。
单元开放期间成员不变，每个身份贯穿该单元的修正循环。失效的已关闭单元重新打开时，需要全新的
完整 cohort。

为每个批次与轮次绑定单元、完整 cohort、活跃子集、Candidate Version、已提供的证据、发现授权、
阶段、独立就绪事件、允许的 Author↔Reviewer 配对与方向，以及讨论状态。暂停会保留身份与状态，
但不占用活跃 worker 槽位。保留使身份保持活跃并占用一个`P`槽位。分批不会改变 cohort、身份、
版本、已提供的证据、发现授权、单元、轮次或独立判断。Reviewer 不接收其他 Reviewer 的工作。

当冻结图允许后续阶段把 Scope Transfer 路由给此前已通过的单元时，该单元在 local PASS 后仍
保持开放，并在已声明的转移窗口内暂停其完整 cohort。只恢复预期职责 Owner，由它独立检查已
路由的 note。只有不会再有后续 note 到达且没有待处理的路由检查时，才关闭该单元并结束其 cohort。
这是同一个开放单元的延续，绝不是已关闭单元中的身份再次返回。

只有 Controller 操作生命周期机制与有界更新。每个派发和保留状态都必须符合已冻结`P`。宿主
无法提供经正确推导的容量、身份、认证通道、调度或证据时，返回`HOST_UNAVAILABLE`。Controller
绑定、启动或保留超出冻结调度或`P`的状态时，返回控制平面`ROLE_BOUNDARY_VIOLATION`。绝不
替换常驻 Author 或开放 cohort 的成员。

## 按需选择证据

Author 和 Reviewer 从已提供的任务、Candidate 与证据开始。当前角色中的适用指令或具体需要
要求时，每个角色都可以在已冻结的读取与网络授权以及适用宿主能力范围内，独立检查与任务相关的
Candidate 资源、管辖 Rule、已接受的 Issue 或 Spec、自有实现、测试、配置、仓库约定或外部来源。
他们不会主动检查无关的仓库内容、追随环境中的引用，或在没有这种需要时使用可用工具。

Reviewer 在不接收 Author 推理或其他 Reviewer 工作的情况下独立寻找反证；不同角色选择的来源和
发现不必相同。发现的来源可以支持 Candidate 判断，也可以在 finding 或直接讨论中引用。证据只能
从其已确立的 Owner 和来源获得权威，绝不能因为它在仓库或上下文中可见、存在于宿主 envelope、
被发现或经同级传输而获得权威。除非管辖合同允许其用于狭窄用途，否则非规范上下文文档仍不属于
证据基础。调用方自有的可移植性政策或其他证据政策可以进一步限定 Candidate 证据。Controller
不解释或转述项目证据。

使用[`job-design.md`](job-design.md)中冻结的准确读取与网络授权，或范围狭窄的自有来源与能力
类别。在这些授权内选择来源属于普通的独立发现，而不是有界更新或逐文件研究路径。仅在当前已
授权来源与能力无法发现必要事实时使用`CONTEXT_REQUIRED`。缺少访问权限时使用
`ACCESS_REQUIRED`。Context Supplement 和访问扩展仍是已冻结 Job Design envelope 下的例外
有界后备方案；超出 envelope 的请求需要开始一次新的对齐运行。

Author 只能通过准确的当前 Authoring Scope 或 Repair Scope 获得 Candidate 操作权限。Reviewer
保持只读。Machine 命令和 Acceptance 影响仍由相应公共阶段的 Owner 负责，不进入 Author 或
Reviewer 授权。每项操作都通过本运行时报告并接受审计。

## 保留角色权威

为 Controller、Author、每个 Reviewer 和每个 Runner 冻结角色专用 prompt。每份 prompt 都要
说明该角色的目的、已授权上下文与动作、通信边界、必需报告和停止条件，并纳入适用的 manifest、
scope、身份、版本与证据。Controller prompt 要求逐案判断 Author 与 Reviewer 行为，只允许为
执行冻结控制平面与污染控制而适度介入；Candidate 含义、finding 和经过推理的不动点仍由各自
语义 Owner 负责。

向 Author 提供完整 Run Contract、Candidate 模型、写作指引、已提供的证据、当前 Candidate、
授权，以及准确一个当前 Authoring Scope 或 Repair Scope。Author 只能在其中工作，不执行
Machine Validation、Acceptance 或委派。只有 Author 负责 Candidate 含义、finding 处置与
Candidate 编辑。

每份 Author 和 Reviewer prompt 都纳入并遵守
[**按需选择证据**](#select-evidence-by-need)中的已冻结通用证据选择政策。当该政策要求
`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`时，角色通过本运行时返回对应状态。

`CONTEXT_REQUIRED` payload 准确标识一个已冻结的必要事实槽位、缺失事实，以及它在特定角色
中的用途。Controller 把这些字段与已冻结的更新 envelope 比较，不判断语义是否成立，并原样
保留由 Owner 生成的 payload。

`ACCESS_REQUIRED` payload 准确标识一个缺失的访问目标：本地访问使用准确路径和模式，外部
访问使用准确来源、能力和网络模式。两种形式都包含理由。

Author 准确返回一种状态：

- `COMPLETE`：语义 Change Summary、准确的变更/创建/删除路径，以及当前判别 scope 外的不确定性；
- `CONTEXT_REQUIRED`：上述通用必要事实 payload；
- `ACCESS_REQUIRED`：上述通用缺失访问 payload；或
- `HUMAN_DECISION_REQUIRED`：准确决策、证据或权威为何无法解决、决策 Owner，以及每个当前
  选择的后果。

Reviewer 独立判断完整已授权输入，并负责 finding、分类和裁决。他们既不接收 Author 的推理，
也不接收其他 Reviewer 的工作。Author 与 Reviewer 绝不委派；使用网络需要已冻结的网络授权和
适用的宿主能力。Runner 只执行冻结用例，绝不委派，也不拥有判断、修复、设置修正、清理、角色
控制或角色启动权威。只有 Controller 能启动、恢复、暂停、保留或结束身份；授权访问；或提供
有界更新。

## 关闭语义角色异常执行

对于每次 Author 或 Reviewer 调用与继续，冻结一个可观察的不返回、身份丢失或继续失败触发条件
及其证据。它可以使用受支持的宿主终止状态或预先声明的有界检测器；本合同不提供任意 timeout。

触发后，Controller 保留所有可获得报告、通道记录、宿主事实和 Candidate 指纹；通过不含语义的
控制 metadata 中止每个开放讨论；尝试已冻结的终止操作；并审计所有可获得证据。缺失回调不提供
payload，应记录而非虚构。在作出污染控制决定前，不得启动替代身份、Candidate 写入、新讨论或
后续阶段。

存在边界违规证据时把事故分类为`ROLE_BOUNDARY_VIOLATION`；否则分类为
`SEMANTIC_ROLE_UNAVAILABLE`。把分类送入全局出口的污染控制决策。无法结束身份或证明其不活跃
时，在最终化期间变为`TEARDOWN_FAILED`。保留不可变 cohort 成员、常驻 Author 连续性、
Candidate 状态和底层事故证据。

## 通过 metadata 打开直接修正

不冻结 Reviewer↔Reviewer 边。每个 finding 使用以下两步 bootstrap：

1. 私下判断固定完整 finding 集合和每个不透明稳定 ID 后，Reviewer 为每项 finding 发出一次经
   审计、不含语义的`FINDING_READY`回调。每次回调只包含单元、轮次、Candidate Version、
   Reviewer 身份、finding ID、finding 集合完成标记，以及三份正常报告。仅在最后发出的一项
   finding 上设置该标记；空集合使用既有的当前版本`PASS`结果。该标记只证明发出已完成，绝不
   证明 finding 含义或裁决。
2. Controller 根据冻结配对与 manifest 审计回调后，向该 Author↔Owner 配对返回`CHANNEL_OPEN`
   metadata。只有此时 Reviewer 才把完整 finding 直接发送给 Author。

[`evaluation.md`](evaluation.md)是主张、处置、不动点、advisory 升级、关闭与修复选择的语义
Owner。本运行时负责传输直接交换并审计其边界。**处置控制 metadata**只包括处置分类（`repair`、
`partial repair`或`decline`）以及是否选中写入。基于证据的理由、保留主张说明、证据、论证和
修复方向共同组成**语义处置正文**，并且只在同级间流动。

Author 与 Owner 直接交换 Evaluation 授权的语义内容。双方分别独立判断反馈、支持依据和来源。
Controller 只看到控制 metadata；它绝不接收、解释、概括、仲裁或转发 finding 正文、语义处置
正文或讨论内容。配对通过经审计的`DISCUSSION_CLOSED`metadata 关闭，其中包含单元、轮次、
Candidate Version、身份、finding ID、处置分类、投递状态、不动点状态和 finding 集合状态，但
没有语义正文。不动点状态允许的值为`reached`、`not reached`和`not applicable`；finding 集合
状态允许的值为`complete`和`reopened`。两种语义映射都由 Evaluation 负责。这些值是控制
metadata，不是语义角色状态或裁决。`DISCUSSION_CLOSED`只关闭通信通道和轮次；它不会解决主张。
两个同级事件均通过审计后，通道才关闭，符合条件的同版本重启或下一冻结轮次可以使用既有握手。
同级通信不能操作角色，也不能改变已冻结的合同、权威或授权。传输会让接收方可以使用证据，但
不会赋予证据权威。

Quality 或 Correctness Reviewer 每次只向 Controller 暴露一个判断结果：`PASS`、
`FINDING_READY`、`CONTEXT_REQUIRED`、`ACCESS_REQUIRED`或`HUMAN_DECISION_REQUIRED`。
Acceptance 只增加其已声明分类。`DISCUSSION_CLOSED`是每个同级发出的通道生命周期事件，不是
语义角色结果或 finding 正文。context、access 与 human 请求是由 Owner 生成的控制或终止
payload，不是 finding 或讨论正文。Controller 只能检查应用冻结资格或终止转换所需内容，并
原样保留与交付 payload；它绝不判断语义是否成立。Controller 自己产生的
`HUMAN_DECISION_REQUIRED`具有相同的全局立即停止效果。

## 消费回调前先审计

每次正常回调都必须携带以下三份报告：

- **Operation Report：**准确列出`read`、`write`、`create`、`delete`、`network`、`delegation`
  和`machine checks`操作；空类别使用`none`。
- Author 与 Reviewer 的**Peer Report：**始终包含单元、轮次、Candidate Version、就绪事件、阶段
  和身份；另须包含方向、消息类型、投递和 Author 参与情况。禁止或没有同级通信时，准确为后面
  这四个通信字段使用`none`。报告不得包含语义正文或裁决。
- **Host-Governance Report：**冻结 Envelope ID、观察到的一致性或准确偏差、catalog 与环境
  metadata 保持惰性的证据、所读项目指令及其只负责执行的影响或`none`，并确认 governance
  未提供任何禁止的语义或权威输入。

消费 payload 前，将这些报告与冻结 expected-operation manifest 比较，并根据可用宿主证据审计
调度一致性、身份连续性、授权、bootstrap、Candidate 指纹和通信 metadata。条件式权威可以
明确允许异常执行后缺少报告；记录缺失并审计所有可获得事实。

唯一的终止控制例外保留无条件人类停止，但不接纳 Candidate payload。经认证归因证明 Author
或 Reviewer 产生了`HUMAN_DECISION_REQUIRED`，且能取得准确请求时，即使另一审计字段使回调
不可接纳，也要保留并原样交付请求。立即停止语义工作，不消费其他回调内容，也不把它用作
Candidate 证据或权威。对外报告`HUMAN_DECISION_REQUIRED`，并把
`ROLE_BOUNDARY_VIOLATION`保留为底层审计证据。无法证明归因或准确请求时，不成立由 Owner
产生的人类请求，采用普通不可接纳路径。

除上述可归因终止控制处理外，下列任何情况都会使调用或回调不可接纳：禁止操作、超额派发、
调度或授权违规、无法归因的 Candidate 变化、缺失或不一致的必需报告、禁止的同级边、Envelope
ID 不匹配、绑定 manifest 的预期控制不匹配、bootstrap 或 governance 违规，以及无法调和的
证据。除非已经开始的条件式权威拥有更高安全终止结果，否则向全局出口的污染控制决策返回
`ROLE_BOUNDARY_VIOLATION`。保留 Candidate、状态和证据，不得回退、修复或掩盖。

## 最终化工作流

启动任何角色、成功取得锁，或取得结果可能留下锁状态后，均适用最终化：

1. 按各自安全与终止优先级合同，完成每项已经开始的条件式执行。
2. 结束每个活跃、保留和暂停的身份，同时保留报告、证据与 Candidate 状态。
3. 确定准确残留活动。只有所有角色活动结束后，才通过冻结接口释放锁并记录可归因证据。
   Controller 最后退出。

无法结束身份或证明其不活跃，或者无法安全释放锁时，返回`TEARDOWN_FAILED`。保留下层结果、
准确残留身份/活动与锁状态、证据，以及安全的拆除/释放尝试。残留活动可能与 Candidate 工作竞争
时继续持锁。若残留 Runner 或语义角色阻止完整拆除，Controller 可以在安全结束其他所有内容后
发出终止报告并退出；这是最后退出规则的唯一例外。只声明已经确认的静止、清理、拆除和释放。
