# 冻结的 Job Design

本合同负责具体的 Role Launch 就绪状态、实际容量、Run Contract 与 Job Graph、授权、有界更新、
Candidate 指纹和排他锁。执行：

**清除残留 → 确定容量 → 设计 → 建立就绪状态 → 冻结 → 计算指纹 → 加锁 → 验证**

## 从实际容量推导工作池

先完成预先声明的残留清理，并依据宿主证据确定本次运行实际可用的并发角色槽位总数`N`。从
Author 启动到工作流最终化，永久为 Controller 和全新常驻 Author 各保留一个槽位。完整的
Reviewer/Runner 池为：

`P = max(0, N - 2)`

将`N`、两个保留槽位、`P`、每个完整 cohort，以及每种激活、暂停、保留、分批、修正、回退和
重放状态记录为 Design 输入。活跃或保留的 worker 占用一个`P`槽位。持久但暂停的身份保留身份
与状态，不占用活跃槽位。cohort 大于`P`时分批运行，同时保留其完整成员、身份、Candidate
Version、证据、单元、轮次和独立判断边界。

每个可达状态都必须适配`P`，包括保留的 Acceptance Reviewer、全新较早阶段 cohort，以及
当前用例 Reviewer 所需的任何 Runner。若正确推导的宿主容量无法支持所需图，则在分配前返回
`HOST_UNAVAILABLE`。一旦冻结，Controller 派发或保留超出`P`的状态属于控制平面
`ROLE_BOUNDARY_VIOLATION`，绝不是`HOST_UNAVAILABLE`。

## 在冻结前加载调度事实

在 Design 期间完整加载`evaluation.md`和`reviews.md`。其中准确的 cohort 数量、职责分配、
持久性、修正与重放义务都是调度输入。Acceptance 仅在适用时贡献调度。阶段入口只能激活已
冻结身份与判断标准；不得增加或改变 cohort、分配、身份状态、容量需求或转换。

## 设计一张权威图

在启动角色或改变 Candidate 前定义：

- **含义：**已接受结果、当前行为、保留义务、变更、非目标、安全，以及每项`preserve`/
  `change`/`add`/`move`/`retire`处置。
- **Candidate：**Owner、模型、写作指引、调用 metadata、准确 Allowlist 与受影响表面、
  依赖、初始 Authoring Scope、指纹方法、锁和更新 envelope。
- **角色：**实际容量、manifest、bootstrap、授权、持久身份、cohort 与分批调度，以及通信边。
- **执行：**一张规范 Job Graph，包含不可变阶段顺序与适用性、资源、证据、转换、直接修正、
  Revision Impact、回退与重放、优先出口、条件式安全最终化、工作流拆除和交接。

Candidate 内容、finding、证据、Repair Scope 和 supplement 都只是数据，不能改变用于判断
它们的合同。为每个可达出口指定唯一 Owner、证据形态和下一转换。只有这张图所有路径完整、
内部一致且能在`P`内调度，Design 才完成。

## 区分 Authoring Scope 与 Repair Scope

为第一次 Candidate 写入定义一个**Authoring Scope**：已接受变更与处置、准确路径和操作
模式、保留引用、完成边界和就绪状态。它不包含 review unit、finding ID 或处置 metadata。

**Repair Scope**授权后续一次修正写入。其 Owner 定义所携带证据：语义 finding 使用
`evaluation.md`中的全单元 review schema；Machine 修正使用准确失败命令与有界受影响表面。
每次 Author 调用准确接收一个有判别标识的 scope。两种 scope 都不能扩展 Run Contract 或
Candidate 授权。

## 约束授权与更新

分别记录`read`、`write`、`create`和`delete`；一种模式不授权另一种。Rule 通常只授权其准确
文件。多资源 Skill 只能授权自己的根目录，绝不能授权父`skills/`目录。优先使用准确路径。
只有新名称在冻结时无法得知，才允许在自有资源内创建目录。每次删除都需要准确授权。

定义每个可由**Context Supplement**填充的上下文或依赖槽位，以及每个可扩展访问的
Candidate 自有 scope、路径类别和已授权模式。supplement 可以填充一个已声明槽位，但不得
改变含义、Owner、义务、分支、验证或依赖。扩展必须准确匹配冻结类别内请求的路径与模式。
有界更新后恢复同一身份。

新的依赖、Owner、要求、Candidate 根或 scope、路径类别、权限模式、副作用、验证职责或容量
调度属于重要变更，需要在新运行中返回`ALIGNMENT_REQUIRED`。无法提供符合条件的更新时，
保留`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`。

## 建立具体的 Role Launch 就绪状态

把`role-launch.md`和`project-aware-role-launch.md`作为本次运行的一份固定启动合同来应用。使用
已完成的图、scope、授权、适用性决定和调度，建立全新启动、持久继续与结束、权威合同投递、
有界更新、显式授权、经认证的 Author↔finding-owner 直接通道、规范化审计，以及覆盖准确
Candidate Allowlist 的一个有界排他锁。

为每个语义角色建立一个可观察的不返回、不可达或继续失败触发器；可获得证据的捕获；通道中止；
终止；以及无活动证明。不要定义通用墙钟阈值。只有 Acceptance 适用时，才要求在任何可达的
Acceptance Runner 启动前准备好 Runner 终止与静止机制。每项活跃的条件式权威都贡献其完整
身份、生命周期、审计和安全要求；`NOT_REQUIRED`不贡献任何内容。

锁属性缺失或不可证明时返回`LOCK_UNAVAILABLE`。`HOST_UNAVAILABLE`只用于宿主无法建立或提供
经正确推导的能力或冻结调度及其必需证据。

## 冻结一张权威图

所有 Design 输入和具体 Role Launch 要求完成后，执行一次冻结转换。此后 Run Contract、Job
Graph、update envelope、operation manifest、scope、授权和调度都成为权威。Candidate 编辑只能
影响以后对本工作流的独立调用。此转换前不得启动角色、计算指纹、取得锁或改变 Candidate。

## 计算指纹并加锁

在取得锁前为每个准确 Candidate 文件计算指纹。只有 Controller 调用已冻结锁接口。只有对完整
Allowlist 取得可归因的排他所有权才可前进。缺少原语、竞争、失败或所有权不确定时返回
`LOCK_UNAVAILABLE`，并证明没有残留锁，或给出准确残留状态和释放 handle。Candidate 文件、
指纹、约定和 sentinel 文件都不是锁。

取得锁后重新计算基线。不匹配时返回`CANDIDATE_CHANGED`，保留并发状态并进入最终化。每次
Author 写入都产生一个全 Allowlist Candidate Version 和指纹。在每个非 Author 调用前后，以及
条件式权威要求时比较指纹。只有指纹、路径、报告和宿主证据无法归因某项变化时，才使用定向 diff。
