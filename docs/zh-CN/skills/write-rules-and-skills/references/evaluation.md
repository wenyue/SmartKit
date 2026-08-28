# 评估生命周期

本 Design-time 合同是 finding 分类、处置、不动点、关闭、修正与共识的唯一语义 Owner。它还
负责阶段顺序与适用性、Machine Validation、Candidate Version、Revision Impact、回退、重放、
Scope Transfer 和全局出口。[`role-launch.md`](role-launch.md)负责经认证的传输及其不含语义的
控制 metadata。在启动任何角色或改变 Candidate 前，把两者都冻结进 Job Graph。

## 冻结证明路径

| 顺序 | 阶段 | 适用性与关闭条件 |
| --- | --- | --- |
| 1 | Quality | 始终适用。激活已冻结的完整全新 cohort；成员分别独立通过同一个 Candidate Version。 |
| 2 | Machine | 当变更涉及 schema 或 metadata、引用/资源、脚本、固定流程，或者足够具体/复杂的工具、权限、文件系统状态、流程或外部影响，并存在确定性证据时适用。广泛判断与高置信简单步骤可以是`NOT_REQUIRED`。 |
| 3 | Correctness | 始终在 Machine `PASS`或有效`NOT_REQUIRED`后适用。激活已冻结的完整全新 cohort；成员分别独立通过同一个 Candidate Version。 |
| 4 | Acceptance | 当运行时行为具体或足够复杂，而且缺乏高置信可行性证据时适用。在 Design 期间加载`acceptance.md`，或冻结为`NOT_REQUIRED`。 |

Acceptance 信号包括固定多步顺序、有意义的分支、重试、恢复或出口、具体工具调用、变更、权限
边界、外部影响，或要求此类行为的 Rule。静态演练不是 Acceptance。只有每项适用性、资源、
身份调度、依赖、转换和出口都已冻结，Design 才关闭。

在 Design 期间完整加载本资源和`reviews.md`。其中 cohort 数量、分配、修正职责与重放状态是
不可变调度输入。阶段入口激活这些冻结事实，不得增加身份、分配、容量或转换。

## 把 finding 视为由 Owner 负责的主张

finding 应记录稳定 ID、问题与有支持的证据及其 Owner 和来源、观察到的答案或有支持的反例、
Candidate 位置、严重级别、Candidate 不变时的影响、估计 Repair Scope、受影响义务或表面、
保留约束，以及有界修复方向，而不是替换文字。仅当字段确实不适用时使用`N/A`并说明原因。
Review 问题只是调查机制；finding 才是由此得到且有支持的陈述性主张。绝不能为了完成记录而
捏造反例。

- `critical`：语义、权威、安全、归属、可执行性或出口失败。
- `material`：有支持的缺陷，实质降低信息质量、可靠性或可维护性。
- `advisory`：有支持的较小改进或有效选择机会，而且其完整修复与重放 scope 足够有界，值得
  呈现。

critical 与 material finding 会阻塞，并且必须遵循下文的双边生命周期。advisory finding 不
阻塞；只有 Author 可以选择修复、部分修复或拒绝，并提供基于证据的理由。只有 finding Owner
负责主张的有效性与严重级别，而且只有出现新的有支持证据时，才可升级 advisory。严重级别说明
Candidate 保持不变时的影响。估计 Repair Scope 说明成本与风险，绝不会降低严重级别；合同违规
无论修复规模多小都仍然是 critical。仅凭品味、对称性、文件长度或修复便宜，不能证明存在缺陷。
完整 finding 只在同级间流动；Reviewer 通过运行时`FINDING_READY → CHANNEL_OPEN`握手暴露它。

## 运行一个独立修正单元

1. **私下判断。**向每个 cohort 成员提供相同的完整 Candidate Version、已提供的证据、已冻结的
   证据选择政策与授权、单元、轮次和独立判断边界。每个成员在不接收 Author 推理或其他 Reviewer
   工作的情况下判断，并在发出任何 finding 前固定自己的完整 finding 集合。分批保留这些共同
   输入。符合条件的有界更新会重新开始该身份的私下判断。
2. **打开 Owner 配对。**对每个已记录 finding，发出 Role Launch 中经审计、不含语义的
   `FINDING_READY`结果以及 finding 集合完成证据。Controller 为该预绑定配对返回
   `CHANNEL_OPEN`后，Reviewer 才把完整 finding 直接发给 Author。任何 Reviewer 都不接收其他
   Reviewer 的工作。
3. **私下选择。**Author 为每项 finding 独立选择`repair`、`partial repair`或`decline`，并提供
   基于证据的理由。partial repair 还要指出保留的主张及原因。
4. **评估自有结果。**对于 critical 或 material finding，只有 Author 与 finding Owner 可以
   直接斟酌语义内容，包括新发现且有支持的证据。双方分别独立评估主张、理由、支持依据和来源；
   传输不会赋予权威。对于阻塞 finding，只有在 Owner 不再坚持任何不写入就仍成立的阻塞主张，
   或双方分别独立同意所选修复或部分修复能够处理每个仍被坚持的阻塞部分、只待写入和复查时，
   才形成经过推理的双边不动点。如果 Owner 仍坚持 blocker，而 Author 拒绝、保留一个阻塞部分，
   或提出的路径被 Owner 判断为不能解决问题，则没有达到不动点，也不会从这条未解决路径中选择
   任何写入。对于 advisory，Owner 可以回答或澄清主张，但只有 Author 冻结其处置和理由；双边
   不动点不适用。任何通道仍开放时，禁止写 Candidate。只改变当前主张的证据留在该主张的生命
   周期中。只有新获得的有支持证据独立支持另一项尚未报告的 finding 时，才应用下文重新打开
   finding 集合的转换。
5. **关闭通信轮次。**Author 冻结每项处置且 Owner 冻结每项主张状态后，无论是否达到阻塞不动点，
   双方都发出运行时不含语义的`DISCUSSION_CLOSED`metadata。该事件只关闭通道与轮次，绝不表示
   主张已解决。只有结果符合上文定义并能解决 blocker 时，其不动点控制值才是`reached`；仍被
   坚持的 blocker 没有商定解决路径时为`not reached`；advisory 为`not applicable`。尚未解决的
   阻塞分歧继续阻塞，不选择任何写入；当前轮次关闭后，可以在下一冻结轮次中通过既有的
   `FINDING_READY → CHANNEL_OPEN`握手继续。

   关闭前，如果 Owner 根据新获得的有支持证据独立确定了另一项尚未报告的 finding，应固定该
   finding 及其不透明 ID，并把 finding 集合状态设为`reopened`；否则状态保持`complete`。重新
   打开会使先前的完成证据失效，只能由新获得的证据触发，而且必须增加至少一个不同 ID。当前
   所有开放通道关闭后，同一持久 Reviewer 使用累积的已授权证据，在未改变的 Candidate Version
   上重新开始私下判断；通过 Role Launch 发出每项新固定的 finding，并在最后一次发出时恢复
   完成状态。advisory Owner 只有获得新的有支持证据时才可升级；升级后的主张转入阻塞生命周期。
   只有不存在尚未解决的阻塞 finding、自己负责的每项 advisory 均有冻结处置、最新 finding
   集合状态为 complete，而且没有已选修复等待写入时，Reviewer 才可在当前版本返回`PASS`。
   信任、投票、其他 Reviewer 和 Controller 解释都不能作出决定。
6. **授权一次写入。**每个 cohort 成员都提供 Role Launch 中经审计的 finding 集合完成证据、
   每个最新 finding 集合状态均为 complete，且所有已发出的 Owner 配对均已关闭后，把所有已接受
   的阻塞与 advisory 修复汇总进一份完整的全单元 Repair Scope。它包含单元、版本、选中写入的
   finding ID、处置控制 metadata（分类与是否选中写入）、已授权路径和模式、冻结保留边界引用，
   以及就绪状态；不转发任何语义处置正文。只有此时，同一个 Author 才能应用所选修复。
7. **共同复查。**写入产生新的 Candidate Version；每个持久 cohort 成员分别独立复查完整
   Candidate。若无写入，不受影响的同版本`PASS`仍有效，而阻塞 finding Owner 重新评估；已被
   拒绝的 advisory 保持关闭。

共识是完整已声明 cohort 在相同的已提供证据、证据选择政策和授权下，对同一 Candidate Version
分别独立给出`PASS`，同时不存在尚未解决的阻塞 finding，并且每项 advisory 均有冻结的 Author
处置。开放单元在 local PASS 后仍保持开放状态。重新打开失效的已关闭单元需要全新完整 cohort；
旧身份与裁决绝不返回。

### 人类停止与无进展

第一个 Author、Reviewer 或 Controller `HUMAN_DECISION_REQUIRED`会立即结束所有语义工作与
讨论。这是由 Owner 生成的终止控制请求，不是 finding 或讨论正文。只保留准确决策、证据或
权威为何无法解决、决策 Owner，以及每个当前选择的后果。临时 finding、处置和裁决全部失效。
完成审计与最终化，然后原样交付请求。人类回答会启动新运行。

当两个同级都关闭轮次、不动点控制值为`not reached`且主张仍未解决时，才计为一轮阻塞分歧。
初次私下判断不算一轮。同一阻塞分歧连续完成两个计数轮次，而且没有新证据或受支持方案时，停止
并返回`NO_PROGRESS`。advisory 的修复、部分修复或拒绝在 Author 冻结处置后关闭，绝不会进入
分歧或`NO_PROGRESS`。

## 验证确定性事实

Machine 适用时，只运行受影响 Owner 支持且不会自动修复的检查：frontmatter 或 schema 验证、
注册/metadata 一致性、引用存在性、自有脚本、生成的 adapter、格式化和仓库测试。不要为了避免
`NOT_REQUIRED`而虚构检查。

每条命令前后立即计算指纹。出现无法归因或未获授权的变化时，保留证据并停止。记录准确命令、
退出状态和相关输出。把失败证据放入一份完整 Machine Repair Scope，交给同一 Author；重跑失败、
已失效及依赖检查。一次 Machine 分歧轮包含失败、修复和重跑。同一失败连续两轮没有新证据或
方案时，停止并返回`NO_PROGRESS`。

只有所有适用检查在同一 Candidate Version 上通过，Machine 才通过。后续变化不能影响某项
证明时才保留其证据，随后对 Quality 应用 Revision Impact。

## 转移 scope，但不转移判断

Reviewer 可以附加一条**Scope Transfer Note**，其中只包含 Candidate 位置、预期 Owner 和需要
检查的职责。它不是 finding，不包含观察、论证、证据、处置、理由或裁决。只可将其路由一次：
发给当前 cohort 中另一 Reviewer、尚未开始的后续阶段，或在当前 local PASS 后发给此前已通过
阶段。接收方独立检查完整 Candidate 及其已授权的证据来源。

当冻结图允许后续阶段向此前已通过的单元发送 note 时，local PASS 后该单元仍保持开放，并在已
声明的转移窗口内暂停其完整 cohort。只恢复预期职责 Owner，由它独立检查已路由的 note；已关闭
单元中的身份绝不返回。只有不会再有后续 note 到达且没有待处理的路由检查时，才关闭此前单元。
没有产生有支持 finding 的 note 会使已通过证明继续有效。note 本身不会改变裁决或使证明失效，
也不获得语义 Owner。由接收方支持的阻塞 finding 通过普通 finding、回退与重放生命周期使受影响
的既有证明失效。由接收方支持的 advisory 仍不阻塞：拒绝时保留既有证明，接受写入时则使用普通
Revision Impact。

## 修订、回退并重放

Revision Impact 使用 Author Change Summary、变更路径、全 Allowlist 指纹、操作记录，并仅在
必要时使用定向 diff。每次写入后：

1. 受影响的活跃单元先在完整新 Candidate Version 上达到 local PASS。
2. 找出变化可能影响的最早已通过证明。未来阶段没有可失效的证明；只保留可证明不受影响的证据。
3. 按冻结顺序重新打开该最早失效阶段和所有中间依赖。为每个失效且已关闭的 Quality 或
   Correctness 单元绑定完整全新 cohort。
4. 应用每项条件式权威已冻结的保留与重放调度。保留且活跃的 worker 继续占用`P`；在剩余池中
   分批运行全新 cohort，不改变 cohort、版本、已提供的证据或发现授权。

每次写入后重复。任何可能受到变化影响的裁决都不得继续有效。

## 选择全局出口

Role Boundary Audit 首先决定调用和回调是否可接纳。不可接纳的回调通常不能贡献 payload 结果。
当该审计确定 Role Launch 中可归因的终止控制例外成立时，立即停止语义工作，保留并原样交付
准确的人类请求，并要求裁决后再新开运行。不得消费其他回调内容或 Candidate 证据。按安全合同
完成所有已开始的条件式执行并最终化工作流；对外报告`HUMAN_DECISION_REQUIRED`，同时保留
`ROLE_BOUNDARY_VIOLATION`作为底层审计证据。其他所有经审计的不可接纳状态均遵循下文的普通
路径。

对于其他所有不可接纳调用或回调，以及每个语义角色事故，先按安全合同完成已经开始的条件式
执行；若存在更高安全终止结果，以其为准。否则废弃不可接纳 payload，保留 Candidate、审计与
残留状态。Controller 逐案判断 Author 或 Reviewer 行为是否处于冻结边界内，并可适度介入以
执行控制平面与污染控制；它绝不决定 Candidate 含义、finding 是否成立或语义不动点。能够证明
污染边界时，只使最小受影响单元失效，同时保留其分类以及边界外所有已建立状态。已经成立的
`SEMANTIC_ROLE_UNAVAILABLE`是整轮终止结果，因为其所需身份不可替换。无法证明隔离时，
其他每种事故分类都会成为整轮终止结果，并最终化工作流。不可接纳调用或回调属于
`ROLE_BOUNDARY_VIOLATION`。

对于可接纳状态，选择第一个匹配结果：

1. 第一个`HUMAN_DECISION_REQUIRED`：结束语义工作，为新运行保留请求；
2. `LOCK_UNAVAILABLE`或`CANDIDATE_CHANGED`：在 Author 改变 Candidate 前停止并保留锁/基线证据；
3. 已开始的条件式执行：完成安全最终化；其终止结果优先，成功最终化则返回阶段生命周期；
4. 整轮`SEMANTIC_ROLE_UNAVAILABLE`：语义角色触发已冻结异常执行条件，且没有边界违规证据；
   保留身份、通道、终止和残留证据；
5. `HOST_UNAVAILABLE`：宿主无法建立或提供经正确推导并冻结的容量、身份、认证通道、调度或证据；
6. 无法提供符合条件的`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`；超出 envelope 的请求在新运行中
   变为`ALIGNMENT_REQUIRED`；
7. 阶段终止结果，例如`AMBIGUITY_UNRESOLVED`、`NO_PROGRESS`或`EXECUTION_UNAVAILABLE`；
8. 同版本阶段`PASS`或有效`NOT_REQUIRED`：前进；只有图关闭并完成工作流最终化才允许成功。

Controller 超额调度遵循不可接纳边界路径，绝不是`HOST_UNAVAILABLE`。低优先级结果不能抹去
高优先级证据或必需的安全最终化。`TEARDOWN_FAILED`保留下层结果并阻止干净成功。
