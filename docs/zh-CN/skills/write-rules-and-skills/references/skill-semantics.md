# Skill

Skill 拥有一项完整的已触发 job。本参考文件适用于候选项本身。

## 建立 job 和 Skill Shape

从已接受意图、活动 Skill 机制和管辖证据中，解析目标、执行者、触发条件、证据、输入、前置条件、结果、
所有者、边界、完成、停止、失败、验证和交接。只有当证据显示操作、顺序、恢复、资源和命令可以改变
执行时，才解析它们。每个适用字段都需要一个有依据的值；只有证据证明某字段不可能改变 job 时才
省略它。

选择一种 Skill Shape：

- **Judgment-led**是默认选择。从目标、证据、原则、不变量、决策边界和有优先级的退出构建 Judgment
  Frame，并将方法留给 Agent 判断。
- **Procedure-led**只有在过程会改变正确性、安全、外部协议合规性、协调、恢复或已接受结果时，
  才使用 Job Graph 和 Execution Path。
- **Hybrid**从 Judgment Frame 开始，只添加有界 Procedural Island。每个 island 在其有优先级的
  退出后将控制权交还给 Agent 判断。

Author 偏好的大纲、希望显得完整，或未经验证的历史顺序，都不能证明规定过程是合理的。

## 解析调用元数据

第一次写入候选项前，将 model invocation 视为默认设置，并依据已接受意图和证据判断是否需要
user-only invocation。保持两种 Harness 表示一致：

- 对于新 Skill，继续使用 model invocation 而不提出选择，除非证据显示不应自动发现或调用 Skill。
  在这个例外中，主动建议 user-only invocation，解释实质权衡，并停止直到用户选择。
- 对于现有 Skill，保留其有依据的调用选择。当证据支持改变该选择或当前表示冲突时，提出建议和影响，
  然后停止直到用户选择。否则继续而不提出该选择。
- 使用活动的 `writing-for-agents` 机制处理通用调用 frontmatter 编码。省略
  `policy.allow_implicit_invocation` 仍是 model invocation 的有效默认值。当自主路由或另一个
  Skill 到达该 job 是其契约的一部分时，建议明确设置 `policy.allow_implicit_invocation: true`，
  并将省略视为不同。已解析的 user-only 选择要求 `policy.allow_implicit_invocation: false`。

在同一个 Candidate Version 中维护 Skill 的 `agents/openai.yaml`。缺失时创建它，更新时保留有依据
的界面 metadata，并且只通过上面解析的选择改变调用政策。

## 投射一个完整 job

- 让主文件具备 Entry Sufficiency：识别 Skill Shape、目标或入口、适用的 Judgment Frame 或
  Execution Path，以及每个有条件要求的资源，而不加载无关细节。
- 对于 Judgment-led 工作，说明证据、原则、不变量、决策边界和有优先级的退出，而不规定无依据的方法。
- 对于 Procedure-led 工作，保持每条实际 Execution Path 可见且 Path-sufficient。将每个分支与其
  触发条件放在一起，并且只有顺序改变正确性、安全或结果时才使用有序步骤。
- 对于 Hybrid 工作，以 Judgment Frame 为主，只在到达各自触发条件时披露 Procedural Island。
- 为每个 Judgment Frame 和 Execution Path 提供一个有优先级的完成、停止或失败退出。说明条件同时
  发生时哪个退出优先；完成不能绕过必需的验证、清理、保留要求或交接。
- 只为已验证且授权恢复的失败说明恢复。保留有用的部分状态，并将缺失的决定、权限或范围交给其所有者。
- 只有工作是重复、脆弱且确定性的，才使用自有 script。定义其依赖、输入、输出、失败、恢复和安全的
  代表性测试。
- 只引用运行时 job 所需的资源，并说明何时读取或执行它们。将持久政策保留在单独拥有的 Rule 中。
- 用标题表示 job 阶段或真实分支，用编号列表表示有序操作，用项目符号表示独立要求。

## 审查并验收 Skill 语义

Correctness Review 从候选项和管辖证据中重建完整 job、所选 Skill Shape、Judgment Frame 和适用的
Execution Path。如果存在隐含字段、无依据的规定过程、虚构的操作、命令、依赖、所有者、恢复、结果、
无依据的环境依赖、缺失的有优先级退出、无法到达的退出或过早完成，则失败。

只选择风险最高的相关 case：

- 正常完成；以及
- 候选项影响的未完成路径，例如缺失前置条件、停止、失败、恢复、交接或条件同时发生。

需要可执行 Acceptance 时，针对冻结的代表性 case 和可观察通过条件运行已触发 job。
