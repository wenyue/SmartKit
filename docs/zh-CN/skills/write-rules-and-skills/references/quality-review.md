# 质量审查

并行启动两个全新 Reviewer，并在各自修正循环中保留它们。向两者提供完整 Candidate Version、
已接受要求、要保留的义务、候选项模型和适用的写作指导。不要向任何一方提供 Author 的 reasoning、
预期修复或 diff。

## Information Architecture, Completeness, and Clarity Reviewer

检查入口充分性、层次结构、渐进披露、分支位置、术语、Markdown 结构、资源路由、局部清晰度，以及
是否包含每个必要部分。找出即使各个句子都正确，其组织方式或遗漏仍会让 Agent 遗漏、虚构或反复
阅读信息的内容。

## Semantic Economy, Minimality, and Redundancy Reviewer

检查每条指令是否都有存在价值。找出陈旧、重复、无作用、错位、过度规定或缓存环境信息的内容。只有
在保留所需含义、选择、权限、安全边界、代表性操作和退出时，删除或合并才有效。不要求数值上的缩减。

分别对两个范围应用共同 Correction Cycle。Reviewer 可以转交正确性问题，但不能决定它。只有两个
Reviewer 对同一个 Candidate Version 都报告没有 finding 值得修复，并且路由给 Quality 审查对的
每个 note 都已解决时，Quality Review 才通过。由后续阶段负责的 note 按 Correction Cycle 排队，
且不会阻止 Quality PASS。
