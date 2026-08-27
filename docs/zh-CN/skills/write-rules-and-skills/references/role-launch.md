# 角色启动

这是公共角色组合表面，负责 Host Governance、身份生命周期、调度、语义通道、规范化报告、
Default Adapter、Role Boundary Audit、语义角色失败、条件式角色组合和工作流最终化。

下列准确的三报告回调 schema 具有规范效力。调用方泛称的**Operation Summary**指 Operation
Report、Peer Report 和 Host-Governance Report 组成的完整 bundle；绝不省略或替换 Peer
Report。调用方泛称的**bootstrap report**就是 Host-Governance Report。
[`acceptance.md`](acceptance.md)负责 Acceptance 用例设计、尝试、判断、修正与重放；本表面
负责 Acceptance 所组合的共享角色启动、审计、身份和最终化机制。这些映射不增加第二套 schema
或 Owner。

调用方 Adapter 中的**每个全新 Runner**，指活跃 Acceptance 组件可以到达的每个 Runner 身份。
Acceptance `NOT_REQUIRED`证明不存在这些冻结身份，不产生 Runner 专用 launcher 资格验证。
Acceptance 适用时，Design 必须在冻结和启动任何角色前，证明每种已声明正常、失败、异常和不
返回模式之后都能终止并确认静止。必需 Probe 自身的终止与残留安全资格验证始终是无条件的。

## 保持 Host Governance 只负责执行

公共 bootstrap 只允许一个 user-role envelope，并准确包含以下有序类别：

1. recommended-plugin catalog metadata；
2. repository `AGENTS` instructions；
3. environment metadata。

catalog 与环境 metadata 只读、单独报告且保持惰性。强制宿主或项目指令只约束已获授权操作的
执行方式。它们均不能提供或改变 Candidate 语义、文本、证据、scope、权威、权限、依赖、
Acceptance 事实、角色工作或冻结转换；也不能授权操作或访问。更早轮次、无关任务和未声明内容
类别不属于 envelope。调用方 Adapter 可以收窄这些类别，但不能增加类别或扩大任一类别。

在资格验证期间，Adapter 负责规范的封闭 bootstrap 表示，并生成一个不可变**Envelope ID**。
把它冻结进每份 expected-operation manifest，并向角色与 Controller 提供相同值。角色只引用
该 ID，不序列化或散列 envelope。下列报告证明观察到的一致性与使用方式，而不是语义权威。

## 保留身份与容量

冻结模板包含：从启动到最终化保持不变的一个全新常驻 Author；每个 review unit 的一个完整
全新持久 Reviewer cohort；以及各条件式权威声明的所有身份。Controller 与常驻 Author 在此
期间持续占用各自保留槽位。首次动作前绑定完整 cohort。单元开放期间成员不变，每个身份贯穿该
单元的修正循环。失效的已关闭单元重新打开时，需要全新的完整 cohort。

为每个批次与轮次绑定单元、完整 cohort、活跃子集、Candidate Version、证据、阶段、独立就绪
事件、允许的 Author↔Reviewer 配对与方向，以及讨论状态。暂停会保留身份与状态，但不占用活跃
worker 槽位。保留使身份保持活跃并占用一个`P`槽位。分批不会改变 cohort、身份、版本、证据、
单元、轮次或独立判断。Reviewer 不接收其他 Reviewer 的工作。

只有 Controller 操作生命周期机制与有界更新。每个派发和保留状态都必须符合已冻结`P`。宿主
无法提供经正确推导的容量、身份、认证通道、调度或证据时，返回`HOST_UNAVAILABLE`。Controller
绑定、启动或保留超出冻结调度或`P`的状态时，返回控制平面`ROLE_BOUNDARY_VIOLATION`。绝不
替换常驻 Author 或开放 cohort 的成员。

## 保留角色权威

为 Controller、Author、每个 Reviewer 和每个 Runner 冻结角色专用 prompt。每份 prompt 都要
说明该角色的目的、已授权上下文与动作、通信边界、必需报告和停止条件，并纳入适用的 manifest、
scope、身份、版本与证据。Controller prompt 要求逐案判断 Author 与 Reviewer 行为，只允许为
执行冻结控制平面与污染控制而适度介入；Candidate 含义、finding 和经过推理的不动点仍由各自
语义 Owner 负责。

向 Author 提供完整 Run Contract、Candidate 模型、写作指引、已接受证据、当前 Candidate、
授权，以及准确一个当前 Authoring Scope 或 Repair Scope。Author 只能在其中工作，不执行
Machine Validation、Acceptance，不使用网络或委派。只有 Author 负责 Candidate 含义、finding
处置与 Candidate 编辑。

Author 准确返回一种状态：

- `COMPLETE`：语义 Change Summary、准确的变更/创建/删除路径，以及当前判别 scope 外的不确定性；
- `CONTEXT_REQUIRED`：缺失事实及其编写用途；
- `ACCESS_REQUIRED`：准确路径、模式和理由；或
- `HUMAN_DECISION_REQUIRED`：准确决策、证据或权威为何无法解决、决策 Owner，以及每个当前
  选择的后果。

Reviewer 独立判断完整已授权输入，并负责 finding、分类和裁决。Runner 只执行冻结用例，不拥有
判断、修复、设置修正、清理、角色控制或委派权威。只有 Controller 能启动、恢复、暂停、保留或
结束身份；授权访问；或提供有界更新。

## 关闭语义角色异常执行

对于每次 Author 或 Reviewer 调用与继续，冻结 Adapter 都要声明一个可观察的不返回、身份丢失
或继续失败触发条件及其证据。它可以使用受支持的宿主终止状态或预先声明的有界检测器；本合同
不提供任意 timeout。

触发后，Controller 保留所有可获得报告、通道记录、宿主事实和 Candidate 指纹；通过不含语义的
控制 metadata 中止每个开放讨论；尝试由 Adapter 负责的终止；并审计所有可获得证据。缺失回调
不提供 payload，应记录而非虚构。在作出污染控制决定前，不得启动替代身份、Candidate 写入、
新讨论或后续阶段。

存在边界违规证据时把事故分类为`ROLE_BOUNDARY_VIOLATION`；否则分类为
`SEMANTIC_ROLE_UNAVAILABLE`。把分类送入全局出口的污染控制决策。无法结束身份或证明其不活跃
时，在最终化期间变为`TEARDOWN_FAILED`。保留不可变 cohort 成员、常驻 Author 连续性、
Candidate 状态和底层事故证据。

## 通过 metadata 打开直接修正

不冻结 Reviewer↔Reviewer 边。每个 finding 使用以下两步 bootstrap：

1. 私下判断固定完整 finding 和不透明稳定 ID 后，Reviewer 发出经审计、不含语义的
   `FINDING_READY`回调，只包含单元、轮次、Candidate Version、Reviewer 身份、finding ID 和
   三份正常报告。
2. Controller 根据冻结配对与 manifest 审计回调后，向该 Author↔Owner 配对返回`CHANNEL_OPEN`
   metadata。只有此时 Reviewer 才把完整 finding 直接发送给 Author。

Author 与 Owner 直接交换语义主张、处置、基于证据的理由、问题、异议和反驳。双方分别独立判断
反馈与理由。一致意见是经过推理的双边不动点，绝不是盲目接受。Controller 只看到控制 metadata；
它绝不接收、解释、概括、仲裁或转发 finding 正文、处置或讨论内容。配对通过经审计的
`DISCUSSION_CLOSED`metadata 关闭，其中包含单元、轮次、Candidate Version、身份、finding ID、
处置类别、投递状态和不动点状态，但没有语义正文。同级通信不能操作角色、改变授权或引入证据。

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
- Author 与 Reviewer 的**Peer Report：**单元、轮次、Candidate Version、就绪事件、阶段、身份、
  方向、消息类型、投递和 Author 参与情况；禁止同级通信时使用`none`。不得包含语义正文或裁决。
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
证据。Probe 控制响应属于其 manifest：缺失或不同的响应因此是边界违规，不是可接纳的 Probe
标准失败。除非已经开始的条件式权威拥有更高安全终止结果，否则向全局出口的污染控制决策返回
`ROLE_BOUNDARY_VIOLATION`。保留 Candidate、状态和证据，不得回退、修复或掩盖。

## Default Fresh Role Adapter

Default 启动角色时不继承父任务轮次，只提供封闭 bootstrap envelope 与冻结 Envelope ID。
Author 与 Reviewer 接收冻结只读权限；只有 Author 获得 Candidate 操作授权。二者均不使用网络
或委派。条件式执行角色不委派。Adapter 提供经审计的全新/持久身份生命周期、暂停与保留、直接
通道、语义角色异常执行检测与终止、实际容量与调度的宿主证据，以及资格验证时选择的一个宿主
支持有界锁。其 Probe 为`NOT_REQUIRED`。适用的条件分支组合其已声明机制；不活跃分支不增加
任何内容。

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
