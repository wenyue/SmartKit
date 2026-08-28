# 评估生命周期

本 Design-time 合同负责阶段顺序与适用性、finding 修正、Machine Validation、Candidate Version、
Revision Impact、回退、重放、Scope Transfer 和全局出口。在启动任何角色或改变 Candidate 前，
将其冻结进 Job Graph。

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

finding 应记录稳定 ID、问题与有支持的证据及其 Owner 和来源、具体反例、Candidate 位置、
严重级别、估计 Repair Scope、受影响义务或表面、保留约束，以及有界修复方向，而不是替换文字。
仅当字段确实不适用时使用`N/A`并说明原因。

- `critical`：语义、权威、安全、归属、可执行性或出口失败。
- `material`：有支持的缺陷，实质降低信息质量、可靠性或可维护性。
- `advisory`：较小改进，或多个有效方案之间的选择。

critical 与 material 主张通常值得修复；默认认为保持含义且有支持的小修复值得做。只有 Author
负责处置。只有 finding Owner 决定主张是否仍成立并阻塞其裁决。完整 finding 只在同级间流动；
Reviewer 通过运行时`FINDING_READY → CHANNEL_OPEN`握手暴露它。

## 运行一个独立修正单元

1. **私下判断。**向每个 cohort 成员提供相同的完整 Candidate Version、已提供的证据、已冻结的
   证据选择政策与授权、单元、轮次和独立判断边界。每个成员在不接收 Author 推理或其他 Reviewer
   工作的情况下判断。分批保留这些共同输入。符合条件的有界更新会重新开始该身份的私下判断。
2. **打开 Owner 配对。**对每个已记录 finding 发出经审计、不含语义的`FINDING_READY`结果。
   Controller 为预绑定配对返回`CHANNEL_OPEN`后，Reviewer 才把完整 finding 直接发给 Author。
   任何 Reviewer 都不接收其他 Reviewer 的工作。
3. **私下选择。**Author 独立选择`repair`、`partial repair`或`decline`，并提供基于证据的理由。
   partial repair 还需指出保留的主张及原因。
4. **直接讨论。**只有 Author 与 finding Owner 交换语义内容，包括新发现且有支持的证据。双方
   分别独立评估主张、理由、支持依据和来源；传输不会赋予权威，一致意见必须是经过推理的双边
   不动点。任一讨论仍开放时禁止写 Candidate。
5. **关闭轮次。**Author 冻结处置，Owner 冻结主张状态，随后双方发出运行时不含语义的
   `DISCUSSION_CLOSED`metadata。只有无需改变 Candidate 时，Owner 才可在当前版本返回`PASS`；
   否则保留或修订后的 finding 在写入前一直待处理。信任、投票、其他 Reviewer 和 Controller
   解释都不能作出决定。
6. **授权一次写入。**每个 cohort 成员完成私下判断、每个 Owner 配对关闭后，Controller 发出
   一份完整的全单元 Repair Scope，包含单元、版本、选中写入的 finding ID 与处置 metadata、
   已授权路径和模式、冻结保留边界引用及就绪状态。它不转发语义正文。只有此时，同一个 Author
   才能应用所选修复。
7. **共同复查。**写入产生新的 Candidate Version；每个持久 cohort 成员分别独立复查完整
   Candidate。若无写入，不受影响的同版本`PASS`仍有效，而 finding Owner 重新判断。

共识是完整已声明 cohort 在相同的已提供证据、证据选择政策和授权下，对同一 Candidate Version
分别独立给出`PASS`。开放单元在 local PASS 后仍保持开放状态。重新打开失效的已关闭单元需要全新
完整 cohort；旧身份与裁决绝不返回。

### 人类停止与无进展

第一个 Author、Reviewer 或 Controller `HUMAN_DECISION_REQUIRED`会立即结束所有语义工作与
讨论。这是由 Owner 生成的终止控制请求，不是 finding 或讨论正文。只保留准确决策、证据或
权威为何无法解决、决策 Owner，以及每个当前选择的后果。临时 finding、处置和裁决全部失效。
完成审计与最终化，然后原样交付请求。人类回答会启动新运行。

Author 冻结处置且 finding Owner 重新判断后仍未解决，构成一轮分歧。初次判断不算一轮。同一
分歧连续两轮没有新证据或受支持方案时，停止并返回`NO_PROGRESS`。

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
阶段。接收方独立检查完整 Candidate 及其已授权的证据来源。可能影响已通过证明的 note 会使该
证明失效；note 本身不获得语义 Owner。

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
唯一的终止控制例外是：已认证、可归因且能取得准确请求的 Author 或 Reviewer
`HUMAN_DECISION_REQUIRED`。立即停止语义工作，保留并原样交付该请求，要求人类裁决后再新开
运行。不得消费其他回调内容或 Candidate 证据。按安全合同完成所有已开始的条件式执行并最终化
工作流；对外报告`HUMAN_DECISION_REQUIRED`，同时保留`ROLE_BOUNDARY_VIOLATION`作为底层
审计证据。若归因或准确请求无法证明，则不成立由 Owner 生成的人类请求，本例外不适用。

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
