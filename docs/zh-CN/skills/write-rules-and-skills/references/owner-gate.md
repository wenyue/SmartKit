# Owner Gate

Owner Gate 判断已接受的义务属于 Rule、Skill、两者还是两者都不属于。它在 Run Contract 冻结前运行，
也为父 Skill 提供只读 Ownership Review 出口。

## 路由更具体的编写所有者

在对义务分类前，确定管辖 Rule 或活动调用方是否确立了适用的更具体编写所有者。如果存在此类所有者，
而当前调用没有该所有者完成的预分类交接，则返回一项指出所有者和有依据路由的交接，然后在建立 Run
Contract、启动角色或写入候选项前停止。经调用方鉴定的调用只有在携带已完成的交接和显式 Adapter
选择时才能继续；分类前验证该所有者路由。

没有更具体的所有者适用时，继续使用此通用 gate。直接调用之后可以依据 Role Launch 契约选择 Default
Fresh Role Adapter；该默认项绝不能替代必需的所有者交接。

## 对义务分类

使用已接受的请求、要保留的义务、现有工件（如果存在）、更广和更窄的所有者，以及可发现的环境事实。
分别对每项义务分类：

- `rule`——约束多个已触发 job 中决策的持久政策；
- `skill`——从触发条件开始并产生一个有界结果的工作；
- `environment-owned`——可从代码、配置、schema、工具输出或另一个活动所有者可靠获得，因此不值得
  缓存在工件中的事实；或
- `ambiguous`——当前证据仍支持实质不同的所有者。

返回一个完整 verdict：`rule`、`skill`、`split`、`environment-owned` 或 `ambiguous`。`split`
要求至少一项独立拥有的 Rule 义务和一项独立拥有的 Skill 义务。

对于 `split`，在写入候选项前停止，并将 Rule 和 Skill 义务作为两个候选请求返回。每个请求启动一次
独立的编写运行，拥有自己的语义模型、Candidate Version、指纹和评估结果。

## 比较所有权

将有依据的 verdict 与请求的所有者比较；对于现有工件，还要与其当前所有者比较。

- 两者一致且 verdict 为 `rule` 或 `skill` 时，不提出所有权问题并继续。
- 两者冲突时，解释证据、每个有依据的位置带来的行为和加载影响，以及建议的保留、移动或拆分结果。
  在启动角色或写入前返回 `ALIGNMENT_REQUIRED`。
- verdict 为 `ambiguous` 时返回 `ALIGNMENT_REQUIRED`。不要用请求的包装方式解决语义所有权。

完整 verdict 为 `environment-owned` 时，指出活动所有者和可发现证据，返回无候选项结果，并在不
写入 Rule 或 Skill 的情况下停止。

所选所有者仍须满足其 Rule 或 Skill 语义及每个适用的评估阶段。用户选择解决的是所有权意图；它
不会把持久政策变成已触发 job，也不会免除语义门槛。

## 返回 Ownership Review

对于明确的只读审查，检查所选工件以及检测重复或错位所需的相关所有者。为每个工件返回：

- 当前所有者和有依据的所有者；
- 每项义务的分类和完整 verdict；
- 证据、影响、建议和任何准确的缺失决定；以及
- 所有权一致时返回 `PASS`，否则返回 `ALIGNMENT_REQUIRED`。

声明没有修改文件并停止，不冻结 Run Contract，也不启动角色。
