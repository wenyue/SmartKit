# 归属、对齐与 Candidate 模型

在此 Gate 关闭前，只有两类操作属于对齐且可以执行：按`Close alignment`的条件调用`grilling`；
以及开展该调用所需的只读 Agent 事实发现，包括分派事实调查。在对齐与建模关闭前，不得改变
Candidate、加锁、执行 Probe、启动验证阶段、启动 Author/Reviewer/Runner 角色，也不得产生
任何其他下游编写或证明影响。

## 路由到唯一 Owner

根据关注点、能力、制品和管辖证据发现 Owner。打包位置不产生语义归属。若适用更具体的编写
Owner，应把请求路由给它，除非已经取得它完成的交接。由调用方完成资格验证的续接必须明确
选择一个完整 Adapter。

对每项已接受义务进行分类：

| 裁决 | 含义与路由 |
| --- | --- |
| `rule` | 持久策略，在触发的 Job 之间约束决策；继续交给一个受支持的 Rule Owner。 |
| `skill` | 受触发、产出一个有界结果的工作；继续交给一个受支持的 Skill Owner。 |
| `split` | 策略与 Job 义务各有独立 Owner；返回彼此分离的 Rule 与 Skill 请求。一个 Candidate Version 不得横跨二者。 |
| `environment-owned` | 可靠事实属于代码、配置、schema、工具输出或另一活跃 Owner；指出该 Owner，不返回 Candidate。 |
| `ambiguous` | 证据支持互不兼容的 Owner，或与请求的制品冲突；返回`ALIGNMENT_REQUIRED`。 |

若存在归属冲突，报告管辖证据、加载与行为影响、受支持的保留/移动/拆分结果、当前选择和决策
Owner。人类偏好不能把策略变成受触发 Job，也不能免除所选模型与证明合同。

明确要求只读的 Ownership Review 应报告每个制品当前与受支持的 Owner、义务分类、证据、
影响、建议和缺失决策。对齐时返回`PASS`；否则返回`ALIGNMENT_REQUIRED`。确认没有文件变化，
并在加载或完成 Candidate 模型前停止。

## 完成对齐

为以下各项建立一个已接受值：

- 结果、当前与保留行为、变更、非目标、安全，以及按优先级排列的出口；
- Owner、准确 Candidate 资源、加载路径、分发边界，以及每项义务的`preserve`、`change`、
  `add`、`move`或`retire`处置；
- 依赖、权限、外部影响、验证职责、可移植性、代表性上下文和最终交接；以及
- 彼此独立的`read`、`write`、`create`和`delete`权威。

证据完备的要求应直接对齐。已接受的 Issue 或 Spec 可以提供这些值；具有唯一证据支持的本地
修复也可以补齐它们。先由 Agent 查明可发现的事实，再列出仍未解决的全部重要问题，并确定每个
问题的决策 Owner。若没有未解决问题，直接关闭对齐，无需调用`grilling`，也无需返回
`ALIGNMENT_REQUIRED`。若未解决问题中有任一项不由用户决策，则不得调用`grilling`；应返回
`ALIGNMENT_REQUIRED`，并为每个未解决选择给出证据、决策 Owner 和实质后果。只有全部未解决
问题都由用户决策时，才必须由模型发起一次且仅一次的`grilling`会话，覆盖完整的未决设计树。
若该 Skill 不可用，或会话未能关闭所有剩余的重要分支并取得用户明确确认，则返回带有相同信息
的`ALIGNMENT_REQUIRED`。用户明确确认已经形成完整的共同理解后，结束当前运行，只做一次交接：
把这份共同理解作为已接受的人类决策上下文，交给一次新的编写运行。每个实际生效的术语与含义
都需要独立、已接受的支持；环境中的词汇表或非规范词汇表绝不是权威。

准确选择下列一个 Candidate 模型。仅为跨项目 Candidate 增加 Portability 分支。

## Rule 模型

一个 Rule 负责一项持久策略。解决其**Policy Frame**：类别、Owner、强度、范围与适用性、
可观察的谓词到结果映射、例外、优先级和边界。为每个适用字段给出一个受支持值；只有证据证明
该字段不会影响策略时，才可省略。

- 先写管辖策略，并把每个谓词、结果和例外放在一起。
- 把每项要求放入范围最窄的 Owner，并明确写出受支持的覆盖关系。
- 使用可观察谓词与结果。针对每个阈值、重叠、例外和排除，拒绝最接近的误报与漏报。
- 把有序执行路由给 Skill。可发现事实留给环境 Owner，历史留在文档中，除非它会改变适用方式。
- 用标题表示稳定策略区域或真实分支，用列表表示同级项，用表格表示准确、重复的映射。

Correctness 会重建完整 Policy Frame。隐式或冲突字段、虚构谓词、缺乏支持的不适用、重复归属、
未声明覆盖、环境依赖和缺失结果都会失败。若 Acceptance 适用，应执行真实策略接缝并观察决策
或动作。

## Skill 模型

一个 Skill 负责一项完整的受触发 Job。解决目标、执行者、触发条件、证据、输入、前置条件、
结果、Owner、边界、完成、受阻、失败、验证和交接。只有顺序、恢复、资源或命令会改变执行时，
才解决这些内容。根据证据选择一种形态：

- 默认采用**Judgment-led**：Judgment Frame 提供证据、原则、不变量、决策边界和优先出口，
  同时把方法交给有能力的判断。
- 当顺序会改变正确性、安全、协议合规、协作、恢复或结果时，采用**Procedure-led**：由唯一
  规范 Job Graph 负责所有路径。
- 当 Judgment Frame 包含返回到判断的有界 Procedural Island 时，采用**Hybrid**。

历史顺序和表面完整性不能证明需要流程。应从入口投射完整 Job，把分支放在触发条件旁，只对
会产生后果的动作排序，并让每条路径都有可观察的完成、受阻、失败和停止结果。完成状态应包括
验证、清理、保留和交接。只声明有证据支持的恢复。

仅为重复、脆弱、确定性的工作使用脚本，并明确依赖、输入、输出、失败、恢复和安全的代表性
测试。使用`writing-for-agents`处理信息架构与调用。除非已接受证据改变选择，否则保留受支持的
调用方式，并在同一 Candidate Version 中对齐 metadata：

- **model-invoked：**在`SKILL.md`中省略`disable-model-invocation`，并在`agents/openai.yaml`
  中省略`policy.allow_implicit_invocation`；
- **user-only：**设置`disable-model-invocation: true`和
  `policy.allow_implicit_invocation: false`。

若自主路由本身属于合同，应保留已接受且显式的`policy.allow_implicit_invocation: true`；它不
等同于省略。保留受支持的界面 metadata，并在缺失时创建`agents/openai.yaml`。

Correctness 会重建完整 Job、形态、边界、分支和出口。完整 Job 执行是正常的 Skill Acceptance。
只有当完整执行会重新进入当前 Acceptance 图，或需要 Runner 被禁止的身份控制时，才有资格使用
**Finite Execution Projection**；Design 必须记录资格，并预授权由 Adapter 所有的 harness。
