---
name: write-shared-rules-and-skills
description: 使用可移植性证据编写或修订跨项目 SmartKit Rule 或 Skill；不包括项目本地工件和 Setup Authoring Contract。
---

# 编写共享 Rule 和 Skill

编写一个不引入源项目假设的跨项目 SmartKit Rule 或 Skill。这个项目私有 Skill 负责共享依赖闭包、
源上下文排除、代表性目标证据和 Soft-Isolated Role Adapter。公共 `write-rules-and-skills` Skill
负责共同 Authoring Protocol 和有序评估阶段。

## 建立共享就绪状态

完整阅读 [`references/portability.md`](references/portability.md)。建立已接受的共享含义、规范候选项
路径、自有资源、已声明共享依赖、要保留的义务、代表性目标上下文，以及每项可移植性特定通过条件。
在写入候选项前，拒绝项目本地所有者或 Setup Authoring Contract。

完整阅读公共 [`role-launch.md`](../../../skills/write-rules-and-skills/references/role-launch.md)，
然后完整阅读
[`references/soft-isolated-role-adapter.md`](references/soft-isolated-role-adapter.md)。
在冻结的 Run Contract 中提供该 Adapter、完整共享证据和可移植性通过条件。不要通过公共 Skill
暴露共享分支或其隔离政策。

## 运行共同协议

使用已接受的共享输入和已选定的 Adapter 调用 `write-rules-and-skills`，原样应用其完整协议。

共享可移植性不增加 Reviewer 阶段。把可移植性参考文件中的证据、检查和通过条件注入现有的
Semantic Fidelity and Ownership 及 Agent Executability and Behavioral Closure 角色契约。把任何
必需的代表性执行 case 注入唯一的条件式 Acceptance 阶段。通用公共 Reviewer 范围保持不变。

## 完成

只有当前 Candidate Version 具有合格的 Soft-Isolated Role Adapter、完整的已声明依赖闭包、两个
扩展的 Correctness verdict，以及每个必需的代表性 Acceptance case 时，可移植性才通过。将这些
事实添加到公共交接中。
