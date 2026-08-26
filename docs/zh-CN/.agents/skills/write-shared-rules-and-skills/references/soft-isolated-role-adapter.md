# Soft-Isolated Role Adapter

软隔离是用于共享编写、由 prompt 强制执行的行为访问契约。它不是硬文件系统或安全边界。

## Probe 机制

此 Adapter 要求执行一次可执行的启动和访问 Probe。

使用为共享角色选定的同一个全新、不继承 turn 的启动器，进行一次性启动和访问 Probe。要求它遵循
一个独特的控制指令、报告提供的上下文和可用工具，并避免文件访问、网络访问和委派。

在每次调用 Probe、Author、Reviewer 或 Runner（无论是初始启动还是之后的恢复）前，为该次准确调用
冻结一份带版本的预期操作 manifest。它包含 Controller 为该次调用提供的完整 prompt 和上下文，包括
任何 Repair Scope、Context Supplement、访问更新或 Runner 证据，以及 prompt 授权的每项工具、文件
和访问授权。将 manifest 版本绑定到该次调用及其输出。要求该次调用的自我报告分别指出物理上可用的
工具，并确认获授权的子集和边界。物理上可用的工具是其超集，本身并不构成不匹配。

在使用任何 Probe、Author、Reviewer 或 Runner 输出前，将自我报告和任何可用的启动器或宿主证据，
与绑定到该次准确调用的 manifest 版本比较，并针对每次调用作出行为审计决定。只有 Controller 权威、
提供的 prompt 和上下文，以及 prompt 授权的权限与该 manifest 一致，且证据足以支持该边界时，才能
PASS。只有证据充分时，可用的异常或无报告启动器或宿主证据才能替代自我报告。无法解释的不匹配、
缺少 manifest 绑定或证据不足会使 Adapter 终止性失效，且不得使用该输出。将比较结果保留为临时
Role Boundary Audit 证据。宿主证据是可选的佐证；不要求宿主 hook。这是行为证据，不是物理可见性
或隔离的证明。

启动任何角色前，资格认定还必须确认所选启动器能够结束每个全新 Runner，并在正常、失败、异常或
不返回的执行后确认其静止。如果该能力未得到证明、报告了父级 turn 内容、未遵循控制指令、无法保留
具有指令权威的 Controller 通道或有界更新、Candidate 或证据 payload 可以覆盖该通道，或者 Probe
与任何静态确认的持续性、访问或容量能力相矛盾，则失败。资格认定会得到有界的启动前结果：只有所有
条件都满足时才通过；否则失败，且不启动角色。Controller 在静态 PASS 后运行它；资格认定和之后的
Acceptance 证据都保持临时状态，不写入 Candidate。

## 构建角色契约

应用已加载的公共 Role Launch Interface 和角色契约。将每个共享角色限制为其完整 prompt、必需的
已声明语义上下文，以及 prompt 授权的最小仓库使用范围：Author 使用候选项和自有资源，Reviewer
使用候选项和已声明依赖，Runner 使用这些已声明共享输入及冻结的 case 和 fixture。

在每个角色的 allowlist 之外，该角色不得读取源项目 Rules、Skills、上下文文档、无关文件或父级
对话。它不使用网络，也不委派。

此 Adapter 绝不授予网络访问或外部影响权限。需要其中任一项的必需 Acceptance case，均根据公共
Acceptance 契约以 `EXECUTION_UNAVAILABLE` 停止。

对于 Acceptance，原样应用已加载的公共尝试生命周期，并由 prompt 授权该 case 准确的文件、工具和
机器检查权限。

应用公共预授权更新范围。其他方面符合条件的 Context Supplement 或访问扩展还必须保留共享源上下文
排除和已声明依赖闭包。拒绝会暴露源项目私有内容、无关路径或未声明依赖的更新。

## Adapter 失效

任何观察到的契约外读取、写入、创建、删除、工具调用、网络操作或委派都会使 Adapter 失效，并构成
终止性审计违规。Prompt 合规性是编写独立性的证据，不是安全声明。
