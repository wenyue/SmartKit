# Soft-Isolated Role Adapter

软隔离是一份由 prompt 强制执行的行为访问合同，不是文件系统、进程或安全边界。原样组合公共
[`Role Launch Interface`](../../../../skills/write-rules-and-skills/references/role-launch.md)、
[`Frozen Job Design`](../../../../skills/write-rules-and-skills/references/job-design.md)、
[`Evaluation Lifecycle`](../../../../skills/write-rules-and-skills/references/evaluation.md)，以及
条件式[`Executable Acceptance`](../../../../skills/write-rules-and-skills/references/acceptance.md)。
这些资源单独负责 bootstrap、容量与调度、通用 manifest 与报告、回调审计、通信、污染控制、
出口和最终化。本 Adapter 只负责下列收窄。

## 确认行为边界满足条件

静态确认公共 Adapter 的每项能力，以及下列 prompt、allowlist、授权和调用证据的执行机制。
公共封闭 Envelope 保持不变，Host Governance 通过组合保持只负责执行。无条件确认必需 Probe
的终止与残留状态证据；仅在 Acceptance 可达时应用公共 Runner 资格验证。

## 绑定精确的角色 prompt 与 allowlist

为每个角色冻结完整公共 prompt，并增加下列 Shared Input 与访问边界：

| 角色 | Prompt 与 allowlist 收窄 |
| --- | --- |
| Controller | 为运行控制平面所需的已冻结 Shared Input、Run Contract、Job Graph、manifest、Candidate 指纹、生命周期状态和宿主审计证据。除准确公共控制操作外，Candidate 与证据均只读；Candidate 含义与 finding 是否成立不属于 Controller 权威。 |
| Probe | 仅接收自身 manifest、必需报告、封闭 Envelope ID 和唯一控制指令。不接收任务证据、仓库或工具访问、网络权威、同级通道或委派权限。 |
| Author | 完整公共 Author payload、已接受 Shared Input、Candidate 与自有资源 allowlist，以及当前 Authoring Scope 或 Repair Scope 中逐路径的准确`read`、`write`、`create`和`delete`授权。不接收无关源项目内容，不执行 Machine 或 Acceptance，不使用网络或委派。 |
| Quality Reviewer | 公共 Quality payload、完整只读 Candidate 资源树、已接受 Shared Input、加载与分发 metadata、所选模型和写作指引。不接收 Author 推理、其他 Reviewer 工作或无关源内容，不使用网络或委派。 |
| Correctness Reviewer | 公共 Correctness payload、完整只读 Candidate 资源树、已声明依赖、已接受 Shared Input、管辖证据和代表性目标组合。不接收 Author 推理、其他 Reviewer 工作或无关源内容，不使用网络或委派。 |
| Runner | 公共只读 Candidate payload、不可变代表性用例所需的已声明输入和依赖、准确 fixture、捕获合同和用例自有效果。不接收无关源内容，不拥有判断、修复、角色控制、网络或委派权限；需要网络或外部影响的用例返回公共`EXECUTION_UNAVAILABLE`。 |

这些 allowlist 不会为公共角色合同增加通信边或权威。公共有界更新只有保持在适用 allowlist 内，
并保留已接受的源上下文排除与已声明依赖闭包时，才符合条件。

## 绑定每次调用

把每次 Probe、Author、Reviewer 和 Runner 调用或继续，绑定到该准确动作的完整公共
expected-operation manifest。在 manifest 中增加一份由 Adapter 所有的**Tool Boundary
Record**，且只包含三个字段：`physically available tools`、`prompt-authorized subset`和
`boundary`。

Tool Boundary Record 必须与未改动的公共三报告 Operation Summary 并列携带，绝不能放入
其中。消费回调前，对 manifest、Operation Summary 和伴随记录一起应用公共 Role Boundary
Audit。物理工具超集本身并非不匹配；超出 prompt 授权子集的行为才是边界违规。宿主证据可以
佐证行为，但本 Adapter 不要求宿主 hook，也不声称存在宿主级隔离。

## 运行必需 Probe

在公共冻结与静态资格验证之后、任何语义角色、锁或 Candidate 写入之前，使用所选 launcher
运行一个一次性 Probe。不要提供任务上下文。通过具有指令权威的 Controller 任务通道，给出
一条与 bootstrap envelope 和报告不同、每次调用唯一的指令，定义其准确可观察响应，并将二者
绑定到 Probe manifest。Probe 不执行文件、工具、网络、同级或委派操作。

若宿主提供预期 envelope 指纹，则使用它。否则把调用标记为`PROBE_BASELINE`；要求 Probe
报告消息角色与内容类别的有序指纹，但不报告内容；该指纹必须等于封闭配置，并成为后续调用的
比较基线。

Probe `PASS`要求准确的唯一控制响应与报告、惰性且可单独识别的 envelope、没有继承或未声明
内容、保留 Controller 通道权威与有界更新、已经确认终止与残留状态，且没有观察到与静态资格
验证冲突的能力。先审计回调：manifest 或预期控制不匹配时遵循公共边界路径；审计可接纳但未
满足 Probe 条件时遵循公共`PROBE_FAILED`。两种结果之后都不得启动语义角色。

## 返回公共污染控制

添加 Adapter 证据后，把每次调用与回调交回公共 Role Boundary Audit 和 Evaluation Lifecycle
的全局出口决策。所有公共角色独立性、通信、容量、人类停止、终止优先级和最终化语义均保持
不变。尤其要应用公共污染边界规则：只废弃能够证明受影响的最小单元；只有无法证明隔离时，
才把事故提升为整轮失效。本 Adapter 不增加分类、事故 taxonomy 或恢复流程。
