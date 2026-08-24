---
name: write-setup-authoring-contracts
description: 编写或实质性修订本仓库 setup-assets/blueprints 下的 Setup Authoring Contract；生成的项目 Rule 或 Skill，以及共享 SmartKit Rule 或 Skill，分别由其他责任方负责。
---

# 编写 Setup Authoring Contract

创建最小且完整的生成输入，使 `setup-project-agents` 能够使用公共 `write-rules-and-skills` Skill，
根据目标仓库证据编写一个项目本地 Rule 或 Skill。对该契约应用 `writing-for-agents`。本项目私有的
Hybrid Skill 负责契约编写及其静态资格认定。

## 建立契约

使用已接受变更、存在时的当前蓝图、Setup 目录条目和代表性目标证据。编写前完整阅读
[`references/setup-authoring-contract.md`](references/setup-authoring-contract.md)。

当引用的 frame 仍有多个受支持含义时停止。应用公共编写 Skill 的 Soft-Isolation Probe，然后向一个
无工具 Author 提供完整的项目感知 Context Packet，其中包含已接受变更、当前契约、Setup 目录证据、
选定目标证据、引用的 frame 和规范目标。Author 返回完整替换内容或 `CONTEXT_REQUIRED`；控制器只在
`setup-assets/blueprints/` 下原样应用返回内容并进行验证。

## 验证与审查

运行并要求每个受影响界面的仓库机器检查通过。然后向一个新的 Soft-isolated、无工具 Reviewer 提供
完整 Context Packet，其中包含已接受结果、完整契约、未来目标语义类型、治理证据和一个代表性 walkthrough
输入。不得向其提供预期答案、疑似缺陷或 Author 推理。

同一个 Reviewer 分别返回以下判断：

- minimality：删除任何一条指令都会改变受支持的生成或停止结果；
- semantic completeness：契约会获取每项可能改变行为的目标义务，或因其停止；以及
- representative walkthrough：一个受支持的目标输入无需虚构项目事实，就能到达唯一一个生成或停止
  结果。

不要启动 Pruning Agent 或 Acceptance Runner，也不要仅为认定契约合格而生成目标。内容变更会使机器
结果和整个静态审查失效。通过 Author 一次性应用所有 `uniquely-forced` finding，并为修订后的候选项
使用新的 Soft-isolated Reviewer；遇到任何 `decision-required` finding 或重复且未变化的 finding
时停止。

成功要求同一个 Candidate Revision 的机器验证和全部三项静态判断都通过。将已接受契约交给
`setup-project-agents`。
