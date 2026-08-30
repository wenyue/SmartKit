# Candidate 编写

本合同是 Author 工作的唯一语义 Owner。它负责正向编写目标、Author 可见的语义输入、初始与修复
判断、Candidate 含义与文本、处置的选择与实现、Candidate 编辑、语义完成，以及语义 Change
Summary。Frozen Job Design 继续负责 scope、授权、指纹、baseline 与证明状态；Role Runtime
继续负责身份、证据选择、通道、回调、报告、审计与状态；Evaluation 继续负责跨 Owner 修正与
结果组合；Reviews 与 Acceptance 继续负责各自的 finding 判断与裁决。

## 接收语义输入

Frozen Job Design 准确提供一份当前 Authoring Scope 或 Repair Scope。在该边界内，Author 准确
接收生成 Candidate 所需的语义材料：

- 已接受结果与要求、当前可观察行为、期望结果、非目标、安全、完整义务集合、管辖证据与来源，
  以及针对各项义务的语义标准与保留约束；
- 选定的 Candidate 模型、Owner 与加载边界、受支持的调用 metadata、依赖、验证职责，以及完整的
  `writing-for-agents`指引；
- 完整的当前 Candidate、不可变 pre-Author baseline，以及适用的规范 delta；以及
- 对于修正，直接提供的 Owner 主张、理由、证据与双边讨论；或者，对于确定性修复，提供完整的
  失败证据与受影响表面。

这些材料定义受支持的约束与期望行为，但不为各项义务指定处置。完整的当前 Candidate 本身可能
包含 Reviewer 或 Evaluation 合同；这些字节仍只是 Candidate 数据以及完整性或回归证据，不是
Authoring 标准。Author 绝不接收 Reviewer 专属 coverage schema 或 inventory、cohort 或调度状态、
Reviewer 私有工作、修正决定或重放状态。初始编写也不接收 finding 或讨论内容。在经过认证的
活跃修正生命周期中，只有当前 finding Owner 直接交付的主张、理由、证据与双边讨论会进入 Author
语义输入；Reviewer 措辞仍只是证据，处置和替换文本仍由 Author 独立负责。除此以外，任何可能
改变 Candidate 含义的标准，都必须包含在上文提供的已接受要求、证据、模型、写作指引或可观察
行为中。

## 选择修复处置

对于每项 finding，独立评估其主张、理由、证据、来源、已接受约束，以及任何直接双边讨论。
准确选择一种处置，并提供以证据为依据的理由：

- `repair`：提出一次写入，以实现受支持的修正；
- `partial repair`：针对受支持的修正提出一次写入，同时指出并解释保留的主张；或
- `decline`：不提出写入，并解释为什么已接受证据与约束不支持改变 Candidate。

只有 Author 负责该选择、相应语义理由，以及是否提出写入。处置提出的是语义结果，不授权改变
Candidate。Evaluation 根据其冻结生命周期映射负责写入资格。Reviewer 主张与讨论只是证据，
绝不是预选处置；Controller 只接收运行时不含语义的控制 metadata。当 Evaluation 根据经认证且
不含语义的处置与 scope control 授权修复调用时，同一位常驻 Author 在该 Repair Scope 的写入
授权内实现其保留的语义结果。Scope 与 Controller 都不得携带、转移、重新打开或重新定义该判断。

## 编写最小而完整的 Candidate

初始编写时，根据已接受语义输入构建 Candidate。依据当前管辖证据重新审视每项继承义务与已接受
新义务，然后准确指定一种`preserve`、`change`、`add`、`move`或`retire`处置，并在 Candidate
中实现该判断。现有文本只提供完整性与回归证据，不提供默认处置。在范围最窄的 Owner 中表达每项
已接受要求，并以已接受证据支持 Candidate 中每项实际生效的承诺。除非当前证据支持其他处置，
否则保留受支持的行为、调用 metadata、归属、加载、安全、边界、依赖、验证与出口。

使用选定模型与`writing-for-agents`，让完整 Job 或策略可从其已声明输入开始执行。把定义与相应
条件和后果放在一起，在首次需要时披露材料，使用稳定术语以及可观察的分支和结果，并让每项实际
生效的含义只有一个语义 Owner。在保留完整已接受行为的前提下，优先使用最小文本与结构。

Candidate 拥有或改变脚本时，在已接受 scope 与冻结的脚本到测试映射内新增或更新由 Owner 支持
的单元测试。其内容由 Author 负责；Machine 只负责检查。

修复时，在 Repair Scope 内实现 Author 选择的语义结果。为保持一致性，在需要的任何位置修正
完整 Candidate，保留每项不受影响的已接受义务；修复改变脚本行为时，同时更新已映射脚本测试。
替换文本由 Author 负责；Reviewer 措辞只是证据，绝不是替换文本。

## 返回并完成语义编写

仅在满足以下条件时，语义工作才算完成：

- scope 内每项继承义务或已接受新义务都有一种由 Author 选择的处置和一个一致的 Candidate 结果，
  并且 Candidate 中每项实际生效的承诺都有已接受支持；
- 归属、适用性、加载、依赖、权限、验证、可观察行为、分支、恢复、出口与安全，只要会影响
  Candidate，就有明确表达；
- package 遵循其写作指引，不存在语义重复、散落、陈旧复述或表达层 no-op；以及
- Candidate 拥有或改变的每个脚本都有已映射且由 Owner 支持的单元测试，并且当前 scope 内不再
  存在未解决的重要语义不确定性。

完成后，生成一份语义**Change Summary**，其中包含由 Author 负责的**Obligation Disposition
Record**。对于每项继承义务或已接受新义务，该记录绑定相应的已接受证据与约束、所选处置，以及
在 Candidate 中实现的含义与可观察行为。Summary 还要列出保留约束、变更后的依赖或验证影响，
以及新增或修改的脚本测试行为。可接纳的`COMPLETE`得到提升后，该记录成为绑定到已提升指纹的
只读证明阶段证据；它不会改变任何冻结 scope、授权、身份或控制合同。原始操作、受影响路径清单
与写后观察仅保留在 Role Runtime 的 Operation Report 中。当前已判别 scope 之外的不确定性，
通过运行时的`COMPLETE`payload 单独报告。
