# 正确性审查

并行启动两个全新 Reviewer，并在各自修正循环中保留它们。向两者提供完整 Candidate Version、
完整的已接受用户决定上下文、要保留的义务、管辖证据、候选项模型和适用证据。不要向任何一方提供
Author 的 reasoning、预期修复或 diff。

## Semantic Fidelity and Ownership Reviewer

检查每项所需含义都被保留或有意变更、每个新增都有证据，以及每项义务都位于正确的所有者和适用
范围中。找出遗漏、无依据新增、意外的语义削弱、矛盾结果、隐藏依赖，以及错位的政策或过程。

## Agent Executability and Behavioral Closure Reviewer

检查符合条件的 Agent 能否进入、选择有依据的分支、使用允许的工具和资源、遵守权限和副作用边界、
恢复或停止、验证，并到达恰好一个有优先级的退出。找出缺失的触发条件、前置条件、依赖、权限、操作、
失败、恢复、验证或完成边界。

分别对两个范围应用共同 Correction Cycle。Reviewer 可以把问题转交给另一个范围，但不能决定它。
只有两个 Reviewer 对同一个 Candidate Version 都报告没有 finding 值得修复，并且路由给 Correctness
审查对的每个 note 都已解决时，Correctness Review 才通过。由其他阶段负责的 note 按 Correction
Cycle 排队或回退，并且只在该契约规定的情况下阻止通过。
