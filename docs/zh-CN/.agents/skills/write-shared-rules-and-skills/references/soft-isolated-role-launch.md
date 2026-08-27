# 软隔离角色启动

软隔离是一份由 prompt 强制执行的行为证据与访问合同，不是文件系统、进程、Host Governance 或
安全边界。原样应用公共 [`role-launch.md`](../../../../skills/write-rules-and-skills/references/role-launch.md)
中的不变生命周期。这个私有资源负责共享证据限制、Tool Boundary Record、Runner 收窄和必需 Probe。

## 保留强制 Host Governance

宿主提供的 AGENTS、recommended-plugin catalog 和环境 envelope 仍然实际存在，强制指令继续管辖
执行。envelope 仅仅存在，不能提供 Candidate 含义、证据、权限、依赖、Acceptance 事实或转换。
除非已接受的 Shared Input 独立确立某项源项目事实，否则该事实不能用作可移植含义。角色可以观察
实际存在的材料，但不会因此获得将其用作语义证据的权威。

## 确认行为证据边界满足条件

冻结前，除通用 Role Launch 就绪状态外，还要确认下列 prompt、allowlist、授权和调用证据的执行
机制。无条件确认 Probe 的启动、准确控制、报告、终止、静止和残留状态证据。只有 Acceptance 可达
时，才确认 Runner 终止与静止机制。

## 绑定准确的角色 prompt 与 allowlist

为每个角色冻结完整的公共 prompt，并增加下列 Shared Input 与访问边界：

| 角色 | Prompt 与 allowlist 限制 |
| --- | --- |
| Controller | 为运行控制平面所需的已冻结 Shared Input、Run Contract、Job Graph、manifest、Candidate 指纹、生命周期状态和宿主审计证据。除准确公共控制操作外，Candidate 与证据均只读；Candidate 含义与 finding 是否成立不属于 Controller 权威。 |
| Probe | 仅接收自身 manifest、必需报告、封闭 Envelope ID 和唯一控制指令。不接收任务证据、仓库或工具访问、网络权威、同级通道或委派权限。 |
| Author | 完整公共 Author payload、已接受 Shared Input、Candidate 与自有资源 allowlist，以及当前 Authoring Scope 或 Repair Scope 中逐路径的准确 `read`、`write`、`create` 和 `delete` 授权。不接收无关源项目内容、Machine 工作、Acceptance 工作、网络或委派。 |
| Quality Reviewer | 公共 Quality payload、完整只读 Candidate 资源树、已接受 Shared Input、加载与分发 metadata、所选模型和写作指引。不接收 Author 推理、其他 Reviewer 工作、无关源内容、网络或委派。 |
| Correctness Reviewer | 公共 Correctness payload、完整只读 Candidate 资源树、已声明依赖、已接受 Shared Input、管辖证据和代表性目标组合。不接收 Author 推理、其他 Reviewer 工作、无关源内容、网络或委派。 |
| Runner | 公共只读 Candidate payload、其不可变代表性用例所需的已声明输入与依赖、准确 fixture、捕获合同和归用例所有的影响。不接收无关源内容、判断、修复、角色控制、网络、外部影响权威或委派。需要网络或外部影响的用例在启动前返回公共 `EXECUTION_UNAVAILABLE`。 |

这些限制不会为公共角色合同增加通信边或权威。公共有界更新只有保持在适用 allowlist 内，并保留
已接受的源上下文排除与已声明依赖闭包时，才符合条件。

## 绑定每次调用

把每次 Probe、Author、Reviewer 和 Runner 调用或继续，绑定到该准确动作的完整公共
expected-operation manifest。在该 manifest 中绑定一份私有**Tool Boundary Record**，且只包含
以下字段：`physically available tools`、`prompt-authorized subset` 和 `boundary`。

Tool Boundary Record 必须与未改动的公共三报告 Operation Summary 并列携带，绝不能放入其中。
消费回调前，对 manifest、Operation Summary 和伴随记录一起应用公共 Role Boundary Audit。物理
工具超集本身并非不匹配；超出 prompt 授权子集的行为才是边界违规。宿主证据可以佐证行为，但本
合同不要求宿主 hook，也不声称存在宿主级隔离。

## 运行必需 Probe

冻结前，静态确认完整 Probe 生命周期满足条件。冻结后且在 Candidate 指纹计算、取得锁、任何语义
角色或 Candidate 写入之前，通过已冻结角色启动器启动一个一次性 Probe。不要提供任务上下文。
通过具有权威的 Controller 任务通道，给出一条与 bootstrap envelope 和报告不同、每次调用唯一的
指令；定义其准确可观察响应，并将二者绑定到 Probe manifest。Probe 不执行文件、工具、网络、同级
或委派操作。

若宿主提供预期 envelope 指纹，则使用它。否则把调用标记为 `PROBE_BASELINE`；要求 Probe 报告
消息角色与内容类别的有序指纹，但不报告内容；该指纹必须等于封闭配置，并成为后续调用的比较基线。

在消费 Probe 响应前，通过通用 Role Boundary Audit 审计调用与回调，并捕获每项可获得的响应和
报告。Probe 以任何模式返回后，都要保留这些证据、结束 Probe、确认静止、记录准确残留状态，并用
这些最终化事实完成审计。

只有此时，才能依据完整记录对底层 Probe 结果分类。manifest、预期控制、bootstrap、授权、报告或
行为边界不匹配时，遵循通用 `ROLE_BOUNDARY_VIOLATION`。否则，唯一响应、惰性 envelope、源排除、
终止、静止或残留状态标准失败时返回 `PROBE_FAILED`。Probe `PASS` 要求每项标准都具有肯定证据。

任何 Probe 启动都会激活通用工作流最终化，即使不存在锁或语义角色。若无法结束 Probe 或证明其
不活跃，通用最终化返回 `TEARDOWN_FAILED`，保留已经分类的底层 Probe 结果，包括
`ROLE_BOUNDARY_VIOLATION` 或 `PROBE_FAILED`，并阻止干净终止报告。在 `PROBE_FAILED`、
`ROLE_BOUNDARY_VIOLATION` 或拆除失败后，不得启动语义角色、取得锁、计算指纹或开展 Candidate
工作。

Probe 证据确立已冻结的启动器与软隔离证据政策。Candidate 编辑不会影响该证据所证明的内容，因此
Revision Impact 既不使其失效，也不重放它。启动器、证据政策、Shared Input 边界或 Probe 合同发生
实质变化时，需要开始一次新的对齐运行。

## 扩展私有出口优先级

首先应用通用 Role Boundary Audit 和条件式安全最终化。对于其他可接纳状态，把 `PROBE_FAILED`
插入到立即停止的 `HUMAN_DECISION_REQUIRED` 之后，以及 `LOCK_UNAVAILABLE` 或
`CANDIDATE_CHANGED` 之前。`TEARDOWN_FAILED` 保留底层结果并阻止干净成功。本资源不增加其他
分类或恢复流程。
