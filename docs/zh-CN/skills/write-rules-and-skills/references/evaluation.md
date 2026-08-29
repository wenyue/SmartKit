# 评估生命周期

本合同负责公共 Quality 与 Correctness 的 finding 语义与共识、证明顺序与适用性、Machine
Validation、Revision Impact 与重放、Scope Transfer 以及全局出口。后续视角合同负责资格与裁决
条件。Job Design 负责指纹、delta 与证明状态提升；
Role Runtime 负责传输与控制 metadata。在启动任何角色或改变 Candidate 前冻结全部内容。

## 冻结证明路径

| 顺序 | 阶段 | 适用性与关闭条件 |
| --- | --- | --- |
| 1 | Quality | 始终适用。激活已冻结的完整 cohort。当前闭合要求每项独立 PASS 与所需 coverage record 都绑定到同一 Candidate 指纹。 |
| 2 | Machine | 当变更涉及 schema 或 metadata、引用/资源、脚本、固定流程，或者足够具体/复杂的工具、权限、文件系统状态、流程或外部影响，并存在确定性证据时适用。广泛判断与高置信简单步骤可以是`NOT_REQUIRED`。 |
| 3 | Correctness | 始终在 Machine `PASS`或有效`NOT_REQUIRED`后适用。激活已冻结的完整全新 cohort；成员分别独立返回绑定到同一准确 Candidate 指纹的 PASS。 |
| 4 | Acceptance | 当运行时行为具体或足够复杂，而且缺乏高置信可行性证据时适用。Design 会将该阶段冻结为适用，并纳入其合同贡献的全部内容；否则冻结为`NOT_REQUIRED`。 |

Acceptance 信号包括固定多步顺序、有意义的分支、重试、恢复或出口、具体工具、变更、权限、
外部影响，或要求此类行为的 Rule。演练不符合条件。冻结每项适用性、资源、身份、依赖、转换和出口。

把本生命周期的修正与重放状态，以及后续视角合同的调度输入，贡献给 Job Design 的通用调度 manifest。

## 把 finding 视为由 Owner 负责的主张

finding 应记录其稳定 ID；问题及其支持证据、Owner 和来源；观察到的答案或有支持的反例；Candidate
位置；严重级别；Candidate 不变时的影响；估计 Repair Scope；受影响义务或表面；保留约束；以及
有界修复方向，而不是替换文字。仅在字段无法适用时使用带理由的`N/A`。Review 问题用于调查；
finding 是有支持的陈述性主张。

- `critical`：语义、权威、安全、归属、可执行性或出口失败。
- `material`：有支持的缺陷，实质降低信息质量、可靠性或可维护性。
- `advisory`：有支持的较小改进或有效选择机会，而且其完整修复与重放 scope 足够有界，值得
  呈现。

critical 与 material finding 会阻塞，并使用下文的双边生命周期。advisory 不阻塞；只有 Author
可以选择修复、部分修复或拒绝，并提供基于证据的理由。只有 finding Owner 负责主张的有效性与
严重级别，而且只有出现新的有支持证据时，才可升级 advisory。严重级别是 Candidate 不变时的
影响；估计 Repair Scope 是成本与风险，绝不会降低严重级别。合同违规无论修复规模多小都仍然是
critical。仅凭品味、对称性、文件长度或修复便宜，不能证明存在缺陷。完整 finding 只在同级间
流动，并通过`FINDING_READY → CHANNEL_OPEN`进入。

## 运行一个独立修正单元

1. **私下判断。**向每个成员提供共同的完整输入，此外只提供已冻结的 scope 专属证据。成员不接收
   Author 推理或其他 Reviewer 的工作，并固定自己的完整 finding 集合。分批时保留输入；有界
   更新会重新开始该身份的判断。
2. **打开 Owner 配对。**为每项 finding 发出经审计的`FINDING_READY`与完成证据。在收到
   `CHANNEL_OPEN`后，将 finding 直接发给 Author；任何 Reviewer 都不接收其他 Reviewer 的工作。
3. **私下选择。**Author 基于证据选择`repair`、`partial repair`或`decline`；partial repair
   还要指出并解释保留的主张。
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
5. **关闭通信轮次。**Author 冻结每项处置且 Owner 冻结每项主张的有效性与严重级别后，无论是否
   达到阻塞不动点，双方都发出运行时不含语义的`DISCUSSION_CLOSED`metadata。该事件只关闭通道与轮次，绝不表示
   主张已解决。只有结果符合上文定义并能解决 blocker 时，其不动点控制值才是`reached`；仍被
   坚持的 blocker 没有商定解决路径时为`not reached`；advisory 为`not applicable`。尚未解决的
   阻塞分歧继续阻塞，不选择任何写入。只有当前轮次关闭，且配对使用当前轮次与 Candidate 指纹
   metadata 再次执行`FINDING_READY → CHANNEL_OPEN`后，才可进入下一冻结轮次。

   关闭前，如果 Owner 根据新获得的有支持证据独立确定了另一项尚未报告的 finding，应固定该
   finding 及其不透明 ID，并把 finding 集合状态设为`reopened`；否则状态保持`complete`。重新
   打开会使先前的完成证据失效，只能由新获得的证据触发，而且必须增加至少一个不同 ID。当前
   所有开放通道关闭后，同一持久 Reviewer 使用累积的已授权证据，在未改变的 Candidate 指纹
   上重新开始私下判断；通过 Role Runtime 发出每项新固定的 finding，并在最后一次发出时恢复
   完成状态。advisory Owner 只有获得新的有支持证据时才可升级；升级后的主张转入阻塞生命周期。
   只有不存在尚未解决的阻塞 finding、自己负责的每项 advisory 均有冻结处置、最新 finding
   集合状态为 complete，而且没有已选修复等待写入时，Reviewer 才可为当前指纹返回`PASS`。
   信任、投票、其他 Reviewer 和 Controller 解释都不能作出决定。
6. **选择写入分支。**所有完成证据均已审计、最新 finding 集合均为 complete 且所有配对均关闭后，
   只检查 Role Runtime 经认证的 scope-control aggregate。没有选中任何写入时，不创建 Repair Scope，
   也不调用 Author；同指纹 Reviewer 符合条件时返回`PASS`，否则阻塞 Owner 进入下一授权轮次。
   选中一项或多项写入时，把该准确 aggregate 冻结复制进一份全单元 Repair Scope：单元、指纹、
   选中 ID 与处置控制、路径与模式、preservation-reference ID 和就绪状态——绝不包含语义正文。
   scope control 缺失或不匹配时，采用 Role Runtime 的不可接纳回调路径。只有此时，同一个 Author
   才能写入。
7. **共同复查。**授权写入后，可接纳的`COMPLETE`提升调用最终指纹，随后每个持久成员分别独立
   复查完整 Candidate。未提升的指纹不会启动证明；若未提升，不受影响的同指纹`PASS`与已拒绝
   advisory 保持关闭，而阻塞 Owner 重新评估。

共识是完整已声明 cohort 分别独立生成由 Owner 负责的`PASS`，每项结论都为 expected proof state
中同一个已提升 Candidate 指纹满足当前闭合，同时不存在尚未解决的 blocker，并且每项 advisory
均有冻结的 Author 处置。Quality 还要求其视角合同声明的每份机械接纳 coverage record；缺失或
不完整的记录不能成为`PASS`。开放单元在 local PASS 后仍保持开放。重新打开失效的已关闭单元
需要全新完整 cohort；旧身份与裁决绝不返回。

### 人类停止与无进展

第一个 Author、Reviewer 或 Controller `HUMAN_DECISION_REQUIRED`会立即结束所有语义工作与
讨论。保留其准确决策、未解决原因、Owner 与每个当前选择的后果；所有临时语义工作均失效。
若请求来自 Author，则应用 Job Design 的 human-stop 转换，并保留独立的不匹配分类。完成条件式
安全与最终化；若没有更高优先级的安全终止结果，则原样交付请求，只有在人类回答后的新运行中继续。

当两个同级都以`not reached`关闭轮次且主张仍未解决时，才计为一轮阻塞分歧；初次私下判断不算
一轮。同一 blocker 连续完成两个计数轮次，而且没有新证据或受支持方案时，停止并返回
`NO_PROGRESS`。advisory 在 Author 冻结修复、部分修复或拒绝后关闭，绝不会进入
分歧或`NO_PROGRESS`。

## 验证确定性事实

Machine 适用时，只运行受影响 Owner 支持且不会自动修复的检查：frontmatter 或 schema 验证、
注册/metadata 一致性、引用存在性、自有脚本、生成的 adapter、格式化和仓库测试。不要为了避免
`NOT_REQUIRED`而虚构检查。

每条命令前后计算指纹，并应用 Job Design 的独立不匹配结果组合；Machine 内不存在已授权的
Author 写入。出现不匹配时保留分类证据并停止。始终记录准确命令、退出状态和相关输出。把失败
证据放入一份完整 Machine Repair Scope，交给同一 Author；重跑失败、
已失效及依赖检查。一次 Machine 修正轮包含失败、修复和重跑。同一失败连续两轮没有新证据或
方案时，停止并返回`NO_PROGRESS`。

Machine 闭合要求每项检查或`NOT_REQUIRED`绑定到当前指纹，或通过准确的 Revision Impact 兼容性
绑定向前沿用。否则，在符合条件时使用预授权的证明 Owner 路径，或重跑检查，然后对 Quality
应用 Revision Impact。

## 转移 scope，但不转移判断

一条**Scope Transfer Note**只包含 Candidate 位置、预期 Owner 和检查职责——不得包含观察、
证据、理由、处置或裁决。只可将其路由一次：发给当前 cohort 的 Reviewer、尚未启动的后续阶段，
或在 local PASS 后发给此前已通过的阶段；接收方独立检查。

允许发往此前已通过单元的 note 会让该单元保持开放，并在转移窗口内暂停其 cohort；只恢复预期
Owner，并在所有可能 note 与检查均结束后关闭。note 本身不改变裁决。接收方支持的 blocker 采用
普通失效/重放；advisory 仍不阻塞，除非接受其写入后触发 Revision Impact。

## 修订、回退并重放

每次提升后，Revision Impact 使用 Author summary、Operation Report、当前已提升指纹、规范 delta
及其 baseline/proof-state 绑定；只有这些内容无法确定影响时，才直接比较 Candidate。

只有当某项证据的结论可能随 Candidate 字节、含义、路径或 delta 变化时，该证据才依赖内容。
指纹只用于身份时则不依赖内容；保留无关的传输、审计、生命周期和控制证据。

一份不可变的**Revision Impact 兼容性绑定**记录原始与目标指纹、未变的 Owner 结论与回调、
来源、规范 delta 和影响证据，以及根据该证明类别冻结 manifest 机械得出的不受内容影响判定。

只有 delta、表面和来源满足每项可观察谓词时，Controller 才能绑定；它不能推断标准，也不能改变
结论、回调、指纹或来源。该绑定既不改变 Candidate 身份和 Frozen Run Contract，也不改变控制证据。

语义影响或不确定影响不会生成兼容性绑定。只有身份与生命周期仍允许时，才通过证明 Owner 已有
的冻结评估或复查生命周期，把影响路由给显式预授权的证明 Owner；任何结果都必须由 Owner 重新
生成并绑定到当前指纹。否则，应用普通失效、回退与重放。

只有 Owner 生成的结论绑定到当前指纹，或未变的原始结论具有从其指纹到当前指纹的准确兼容性
绑定，证明才满足**当前闭合**。每次后续指纹变化都需要自己的绑定。受影响或影响不确定的证明
得不到绑定，并遵循已有失效、回退与重放路径。

Acceptance 修正会把控制权交还至此，同时保留其用例 Reviewer。Evaluation 按顺序恢复失效的
较早阶段，然后 Acceptance 重跑该用例，之后才再次判定影响；Acceptance 不编排任何较早阶段。

1. 受影响的活跃单元先在完整的新 Candidate 指纹上达到 local PASS。
2. 找出变化可能影响的最早已通过证明。未来阶段没有可失效的证明。只保留其冻结可观察标准以
   机械方式证明不受影响的证据，并为每个保留结论记录准确的 Revision Impact 兼容性绑定。
3. 按冻结顺序重新打开该最早失效阶段和所有中间依赖。变更指纹后新派生的 delta 只会使内容依赖
   结论可能受影响的 review、回调或其他证据失效；未变 no-op 按这些 Revision Impact 规则保留不受
   影响的证据。每个绑定到指纹的 delta 均保持不可变。
   在每个失效且已关闭的 Quality 或 Correctness 单元首次行动前，预绑定完整全新 cohort。反复
   失效时使用成员完全不同的全新 cohort；任何此前身份或裁决都不返回。
4. 应用每项条件式权威已冻结的保留与重放调度。保留且活跃的 worker 继续占用`P`；在剩余池中
   分批运行全新 cohort，不改变 cohort、指纹、已提供的证据或发现授权。

每次提升后重复。任何可能受到已提升变化影响的裁决都不得继续有效。

## 选择全局出口

消费 Role Runtime 审计后的回调结果，以及 Job Design 选定的证明状态转换。经认证的
`HUMAN_DECISION_REQUIRED`在其他任何结果前应用[人类停止](#human-stop-and-no-progress)；其他不可接纳
payload 一律丢弃。

只有在能证明污染边界且 Candidate 与 expected proof state 准确匹配时，Controller 才能局部遏制
其余事故；使最小受影响单元失效，保留其分类及边界外所有状态，并只通过已冻结的身份与生命周期
路径继续。已经成立的`SEMANTIC_ROLE_UNAVAILABLE`是整次运行的终止结果，因为其所需身份不可
替换。发生变更的 Author 调用若回调不可接纳，则属于整次运行的`ROLE_BOUNDARY_VIOLATION`；
其他事故若无法证明准确证明状态匹配与隔离，也属于整次运行。Controller 只判断边界遵循与遏制，
绝不判断 Candidate 含义或 finding。

发出任何全局结果前，先按安全合同完成每项已经开始的条件式执行。若产生安全终止结果，则它优先，
同时保留待处理的底层结果；安全最终化成功后，返回下列选择。然后选择第一个匹配结果：

1. 第一个`HUMAN_DECISION_REQUIRED`：结束语义工作，为新运行保留请求；
2. `CANDIDATE_CHANGED`：应用 Frozen Job Design 选定的不提升转换，然后停止；
3. 整次运行的`ROLE_BOUNDARY_VIOLATION`：保留其取证状态与审计证据，不作提升，并停止语义继续；
4. 整次运行的`SEMANTIC_ROLE_UNAVAILABLE`：语义角色触发已冻结异常执行条件，且没有边界违规证据；
   保留身份、通道、终止和残留证据；
5. `HOST_UNAVAILABLE`：宿主在启动 Author 前无法建立或提供经正确推导并冻结的容量、身份、认证
   通道、调度或证据；
6. 无法提供符合条件的`CONTEXT_REQUIRED`或`ACCESS_REQUIRED`；超出 envelope 的请求在新运行中
   变为`ALIGNMENT_REQUIRED`；
7. 阶段终止结果，例如`AMBIGUITY_UNRESOLVED`、`NO_PROGRESS`或`EXECUTION_UNAVAILABLE`；
8. 根据 Evaluation 的同指纹或兼容性规则达到阶段当前闭合：前进；只有图关闭并完成工作流最终化
   才允许成功。

Controller 超额调度遵循不可接纳边界路径，绝不是`HOST_UNAVAILABLE`。低优先级结果不能抹去
高优先级证据或必需的安全最终化。`TEARDOWN_FAILED`保留下层结果并阻止干净成功。
