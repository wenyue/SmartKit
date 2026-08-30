# 归属、对齐与 Candidate 模型

每次调用都从本 Gate 内部的一次 Ownership Review 开始。只有它确认了一个受支持的`rule`或
`skill`Owner，才可继续。其他任何裁决都应遵循下文对应路径，或返回其对齐结果；这项审查不是
独立调用、`PASS`或交付物。

在此 Gate 开放期间，只允许由对齐负责的只读 Agent 事实发现（包括分派事实调查），以及按
`Close alignment`的条件调用`grilling`。在对齐与建模关闭前，不得改变 Candidate、启动
验证阶段或 Author/Reviewer/Runner 角色，也不得产生下游编写或证明影响。

## 路由到唯一 Owner

根据关注点、能力、制品和管辖证据发现 Owner；打包位置不会赋予归属。除非已经取得更具体编写
Owner 的完整交接，否则应路由给该 Owner。

对每项已接受义务进行分类：

| 裁决 | 含义与路由 |
| --- | --- |
| `rule` | 持久策略，在触发的 Job 之间约束决策；继续交给一个受支持的 Rule Owner。 |
| `skill` | 受触发、产出一个有界结果的工作；继续交给一个受支持的 Skill Owner。 |
| `split` | 策略与 Job 义务各有独立 Owner；返回彼此分离的 Rule 与 Skill 请求。一个 Candidate 不得横跨二者。 |
| `environment-owned` | 可靠事实属于代码、配置、schema、工具输出或另一活跃 Owner；指出该 Owner，不返回 Candidate。 |
| `ambiguous` | 证据支持互不兼容的 Owner，或与请求的制品冲突；返回`ALIGNMENT_REQUIRED`。 |

若存在归属冲突，报告管辖证据、加载与行为影响、受支持的保留/移动/拆分结果、当前选择和决策
Owner。人类偏好不能把策略变成受触发 Job，也不能免除受支持的模型与证明合同。

## 完成对齐

为以下各项建立一个已接受值：

- 结果、当前行为、期望结果、非目标、安全，以及按优先级排列的出口；
- Owner、准确 Candidate 资源、加载路径、分发边界，以及每项 Candidate 义务的管辖证据、
  语义标准与保留约束；
- 依赖、权限、外部影响、验证职责、适用的运行环境和最终交接；以及
- 彼此独立的`read`、`write`、`create`和`delete`权威。

证据确立要求时，直接接受该要求；已接受的 Issue 或 Spec 可以做到这一点，具有唯一证据支持的
本地修复也可以。先由 Agent 查明可发现的事实，再列出每项仍未确定的重要答案及其决策
Owner。若列表为空，直接关闭对齐，无需调用`grilling`，也无需返回`ALIGNMENT_REQUIRED`。
若任一未决事项不由用户决策，则不得调用`grilling`；应返回`ALIGNMENT_REQUIRED`，并为每个
未解决选择给出证据、决策 Owner 和实质后果。若全部未决事项都由用户决策，则必须由模型发起
一次且仅一次的`grilling`会话，覆盖完整的未决设计树。若该 Skill 不可用，或会话未能关闭所有
剩余的重要分支并取得用户明确确认，则返回相同的`ALIGNMENT_REQUIRED`payload。确认后结束
当前运行，只做一次交接：把完整的共同理解作为已接受的人类决策上下文，交给一次新的编写运行。
每个实际生效的术语与含义都需要独立、已接受的支持；环境词汇表或非规范词汇表绝不是权威。

旧 Candidate 是完整性与回归证据，绝不是设计权威。对齐阶段确定用于重新审视每项继承义务与
已接受新义务的证据、标准与约束，但不选择语义处置。常驻 Author 负责为每项义务作出初始
`preserve`、`change`、`add`、`move`或`retire`判断；不能仅因某项内容已经存在就保留它。

准确选择下列一个 Candidate 模型。

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
会产生后果的动作排序，并让每条路径都有可观察的完成、受阻、失败和停止结果，其中包括验证、
清理、保留和交接。只声明有证据支持的恢复。

仅为重复、脆弱、确定性的工作使用脚本，并明确依赖、输入、输出、失败、恢复和由 Owner 支持的
单元测试。使用`writing-for-agents`处理信息架构与调用。除非已接受证据改变选择，否则保留受支持的
调用方式，并在由一个全 Allowlist 指纹标识的 Candidate 中对齐 metadata：

- **model-invoked：**在`SKILL.md`中省略`disable-model-invocation`，并在`agents/openai.yaml`
  中省略`policy.allow_implicit_invocation`；
- **user-only：**设置`disable-model-invocation: true`和
  `policy.allow_implicit_invocation: false`。

若自主路由本身属于合同，应保留已接受且显式的`policy.allow_implicit_invocation: true`；它不
等同于省略。保留受支持的界面 metadata，并在缺失时创建`agents/openai.yaml`。

Correctness 会重建完整 Job、形态、边界、分支和出口。完整 Job 执行是正常的 Skill Acceptance。
只有当完整执行会重新进入当前 Acceptance 图，或需要 Runner 被禁止的身份控制时，才有资格使用
**Finite Execution Projection**；Design 必须记录资格，并预授权 harness。
