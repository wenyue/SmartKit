# 机器验证

当确定性证据适用时，在 Quality Review 后运行 Machine Validation。适用情形包括变更的 schema 或
metadata、reference 或自有资源、script 或类似 script 的固定流程，以及足够具体或复杂的过程、工具、
权限、文件系统、状态或外部影响行为。笼统的判断指导和高置信度的简单步骤不需要专门的执行检查；
记录 `NOT_REQUIRED`，不要虚构检查。

根据受影响的所有者和表面选择检查：frontmatter 或 schema 验证、注册和 metadata 一致性、reference
和资源存在性、script、生成的 adapter、格式和仓库测试。机器检查证明结构和可观察执行，不证明自然
语言含义。

每次执行机器检查前，Controller 都立即计算 Candidate Fingerprint；检查返回后，Controller 立即重新
计算并比较指纹，再使用其结果。任何未授权或无法归因的 Candidate 变更都会停止工作流。保留变更后的
状态以供报告；不要还原或隐瞒它。只有紧凑指纹和可用操作记录不足以归因变更时，才使用有针对性的 diff。

为每个命令保留准确命令、最终退出状态和相关输出。失败时，将该证据和有界 Repair Scope 发送给持续
Author。Author 编辑候选项，但不运行检查。每次 Author 变更都会创建新的 Candidate Version。使用
其变更路径、Author Change Summary 和变更前后的指纹，判断变更可能影响哪些先前机器结果。重新运行
失败的检查以及每项失效或依赖检查。只有变更不可能影响某项结果所证明的内容时，才复用该结果。继续
执行，直到每项适用机器检查都具有同一个 Candidate Version 的 PASS 证据。

该 Candidate Version 的所有机器检查通过后，对更早的 Quality 证据应用共同 Revision Impact
Decision。同一失败经过两轮修复仍然存在且没有新的有依据方案时，因无进展停止。
