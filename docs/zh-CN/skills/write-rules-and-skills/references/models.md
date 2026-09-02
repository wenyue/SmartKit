# 归属、对齐与 Candidate 模型

本合同负责入口 Gate 与 Candidate 模型。

## 路由到唯一 Owner

根据已接受的关注点、结果和治理证据确定归属；仅凭打包位置不能确立归属。

| 裁决 | 含义与路由 |
| --- | --- |
| Rule | 一项持久策略，在触发的工作之间约束决策。继续使用 Rule 模型。 |
| Skill | 一项受触发、产出有界结果的工作。继续使用 Skill 模型。 |
| Split | 策略义务与工作义务各有不同 Owner。返回分开的请求；一个 Candidate 不能横跨二者。 |
| Environment-owned | 代码、配置、schema、工具输出或另一活跃 Owner 已经负责该事实。指出该 Owner，不返回 Candidate。 |
| Ambiguous | 有支持的证据允许互不兼容的 Owner，或与所请求制品矛盾。返回 ALIGNMENT_REQUIRED。 |

存在更具体的编写 Owner 时优先使用它。可以把该 Owner 完成的交接作为输入；本工作流不会静默吸收其工作。

## 关闭对齐

为结果、当前与请求的行为、非目标、准确 Candidate 资源与加载路由、分发与暴露边界、受支持的公共/项目本地/共享 writer 上下文、治理证据、保留与兼容约束、依赖、权限、外部影响、验证、安全、出口和交接建立已接受值。分别冻结 read、write、create、delete、move 与 network 权威。每项已接受 move 都要指定准确源和目标，绝不能从 create 或 delete 权威推断。准确公共路径与交付约束不授予任何下游发布或安装权限。

证据只能通过其语义 Owner 与来源获得权威。旧 Candidate 文本是完整性与回归证据，不是设计权威。非规范上下文和环境中的仓库可见性不提供任何操作性含义。Author 随后要为每项继承或新增义务选择 preserve、change、add、move 或 retire。

宿主与仓库指令负责执行已获授权的操作。catalog 与环境 metadata 是惰性的。它们都不提供 Candidate 含义、证据权威、scope、授权、权限、角色判断或工作流转换。独立归属的 Rule、已接受 Spec、实现、测试和外部来源，只能通过自身的权威与来源提供含义。

由 Agent 解决可发现的事实。对于每项尚未解决的重要选择，指出证据、决策 Owner、当前选项与后果。决策不由用户所有时返回 ALIGNMENT_REQUIRED。全部未决选择均由用户所有时，使用合乎比例的可用交互关闭完整决策树；grilling 可在有帮助时选用。如果没有关闭每个重要分支，则返回 ALIGNMENT_REQUIRED。明确确认会结束本次调用，并为新运行形成一份已接受的对齐交接；它不授权同一运行继续编写，也不是立即返回 HUMAN_DECISION_REQUIRED 的捷径。

只有一个准确 Candidate 表面能够在可用权威内满足每项已接受义务时，才继续。

## Rule 模型

一个 Rule 负责一项策略。其 Policy Frame 只包含会改变适用方式的字段：Owner、强度、scope、可观察谓词与结果、例外、优先级和边界。

先写治理策略。把每项谓词与其结果和例外放在一起。写明有支持的覆盖关系，并拒绝最近的实质性误报与漏报。把有序执行路由给 Skill，把可发现的环境事实留给其 Owner。

Correctness 必须能够重建完整 Policy Frame，并把每项实际生效的承诺追溯到已接受证据。Acceptance 是条件式的：只有场景或真实执行的不确定性达到重要程度时才使用。

## Skill 模型

一个 Skill 负责一项受触发的工作。其 Job Frame 写明目标、执行者、触发条件、已接受证据、输入、前置条件、结果、归属、边界、验证、出口和交接。只有在省略后可能根据前沿 Agent 原则改变结果时，才写明顺序、资源、命令、恢复或详细分支。

默认采用 Judgment-led。只有顺序或协议会改变正确性、安全、归属、协调、恢复、外部影响、可执行性或交接时，才使用 Procedural Island。当一个或多个这样的流程岛位于 Judgment Frame 内时，形成的 Skill 是 Hybrid。

使用 writing-for-agents 处理加载和信息层级。除非已接受证据改变选择，否则保留受支持的调用方式与界面 metadata：

- model-invoked：保留面向模型的 description，省略 disable-model-invocation，并且省略 policy.allow_implicit_invocation，除非明确的自主路由本身属于合同；
- user-only：把 disable-model-invocation 设置为 true，并把 policy.allow_implicit_invocation 设置为 false。

授权 Candidate 之外的 metadata 是必须保留的约束，不是隐含的写入授权。

Correctness 必须能够重建完整工作、重要分支、边界和出口。当语义具有高置信度且不再有重要场景或运行时不确定性时，Acceptance 为 NOT_REQUIRED。不能仅仅因为 Candidate 是 Skill 就自动要求 Acceptance。
