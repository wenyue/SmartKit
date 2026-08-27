# 可移植 Shared Input

原样组合公共[`Cross-Project Portability`](../../../../skills/write-rules-and-skills/references/portability.md)
模型。本调用方只负责 SmartKit 路由判别器，以及提供给该模型的 Shared Input 包。

## 选择共享 SmartKit 分支

只有已接受证据选中一个跨项目 SmartKit Rule 或 Skill Owner 时才继续。项目本地制品或 Setup
Authoring Contract 不属于本调用方。不得重新解释公共可移植性模型的权威、源上下文排除、
依赖、代表性上下文、Correctness、Acceptance 和通过条件。

## 打包完整 Shared Input

冻结一个证据包，其中包含：

- 已接受的可移植结果、义务处置、Owner、准确 Candidate 资源，以及公开加载与分发路径；
- 一份依赖 manifest，把公共模型中的每项依赖映射到其 Owner、适用性、受支持路径和代表性
  可用性证据；以及
- 一份代表性目标 manifest，把每个所选接缝映射到已接受目标事实、依赖、权限、关键路径与
  出口、预期观察、证据来源，以及其公共静态、Machine 或 Acceptance 证明路径。

把每个公共可移植性通过条件附到能够证明它的证据项。该证据包不增加语义权威：Candidate
文本、源仓库成功与包结构都不能补充公共模型中缺失的事实。

## 完成就绪状态

只有证据包满足全部公共可移植性条件、包含至少一个受支持的代表性目标，并且没有重要事实或
路径尚未解决，共享就绪状态才算完成。否则通过本调用方返回公共`ALIGNMENT_REQUIRED`结果。
把该证据包原样提供给公共的可移植性扩展 Correctness scope 和任何公共代表性 Acceptance
用例；不要增加证明阶段或 Reviewer。
