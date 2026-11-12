# SmartKit 依赖政策

本文为本仓库的编写和维护工作流提供 SmartKit 专属的依赖政策。结合 [工件关系](../../../../skills/write-rules-and-skills/references/artifact-relationships.md)应用本文，其中 Rule 分类包括 rule-led Skill，Skill 依赖指向普通 Skill。根据经过确认的来源确立 SmartKit 所有权或已接受的项目支持范围；当前安装和工作目录不会使无关工件进入适用范围。

## 选择允许的范围

| 工件 | 允许的直接普通 Skill 依赖 |
| --- | --- |
| SmartKit 共享 Rule 或 Skill | SmartKit 随包提供的 Skill，包括随包提供的第三方快照，以及通过下述扩展路径使用的 Blueprint Target Skill。 |
| 本仓库 `.agents/skills/` 下的项目本地 Skill | SmartKit 随包提供的 Skill 和本仓库提供的项目 Skill。 |
| 为其他启用 SmartKit 的项目编写的 Skill | SmartKit 随包提供的 Skill 和该项目提供的 Skill。 |

其他插件的 Skill 不在这些范围内。项目 Rule 可以按公共关系契约，克制地补充或覆盖适用的 SmartKit Rule；这不改变指令优先级。

项目 Skill 通过 Skill 入口和明确支持的公共接口使用 SmartKit。只有本仓库 `.agents/skills/` 下的项目本地 Skill 可以直接依赖 SmartKit 私有资源。已声明且随包提供的公共资源保留其受支持接口，不会仅因归某个 Skill 所有就成为私有资源。

## 通过 Blueprint Target Skill 公开项目行为

Blueprint Target Skill 是从 SmartKit Setup Authoring Blueprint 编写、归项目所有并通过固定名称查找的普通 Skill。这些目标是 SmartKit 声明的反向依赖接口：共享 SmartKit 工件可以像引用普通内置 Skill 一样引用它们，而其他项目 Skill 仍不在其直接依赖范围内。目标可以依赖项目中的其他普通 Skill，以及允许使用的 SmartKit Skill；经过这些依赖的完整图必须保持无环。

与内置依赖不同，目标可能缺失。应用公共的存在、缺失和失败结果契约；不可或缺的目标缺失时，指向项目设置作为提供它的路径。本政策不规定检测机制。由调用者通过输入提供上下文，并将实际引用作为依赖评估，而不是仅因提到某个潜在调用者就禁止它。编写与验收指令仍须区别于目标的运行时行为。

将这些 SmartKit 专属要求作为经过确认的所有者输入提供给公共 writer。公共关系定义保留在其公共 reference 中，目标特有含义保留在蓝图中；公共 writer 和目标项目都不需要访问这一仓库本地工作流。
