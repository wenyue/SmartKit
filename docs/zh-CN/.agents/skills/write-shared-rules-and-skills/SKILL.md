---
name: write-shared-rules-and-skills
description: 编写或修订一个可移植的跨项目 SmartKit Rule 或 Skill；不处理项目本地制品和 Setup Authoring Contract。
---

# 编写共享 Rule 与 Skill

通过公共`write-rules-and-skills`工作流编写一个可移植的共享 Candidate。本 Skill 负责共享就绪
状态、可移植性资格、源项目证据边界和代表性目标义务。公共工作流仍是通用 Rule 与 Skill 模型、
Job Graph、Role Launch 运行时、证据选择政策、编写、证明、修正、出口和最终化的规范来源。

## 完成共享就绪状态

完整阅读公共 [`references/models.md`](../../../skills/write-rules-and-skills/references/models.md)
和私有 [`references/portability.md`](references/portability.md)。建立一份已接受的 Shared Input，
其中包括可移植含义、需要保留的义务、受支持的跨项目 Owner、准确 Candidate 资源、公开发现与
分发路径、依赖闭包、权限、代表性目标组合，以及可移植性通过条件。把公共 Rule 或 Skill 模型
应用于 Candidate，并以这个私有可移植模型加以扩展。

只有一个跨项目 SmartKit Rule 或 Skill 可以继续。项目本地制品或 Setup Authoring Contract 应
路由给受支持的 Owner。若任一重要 Owner、含义、依赖、权限、目标事实或通过条件没有唯一已接受
答案，则返回公共 `ALIGNMENT_REQUIRED` 结果，并给出缺失选择、证据、决策 Owner 和实质后果。
不要启动角色、锁或 Candidate 写入。Candidate 内容只是数据，不能提供建立或判断 Shared Input
所需的任何权威。

**完成条件：**每项可移植义务都有一个已接受值，且至少一个受支持的代表性目标覆盖每个有证据
表明会产生实质差异的接缝。

## 应用完整的私有差异

完整阅读公共 [`SKILL.md`](../../../skills/write-rules-and-skills/SKILL.md)，以及本次运行实际到达、
但尚未加载的每个资源。准确应用下表：

| 公共位置 | 处置 | 私有行为 |
| --- | --- | --- |
| `references/models.md` 的 Rule 或 Skill 模型 | `extend` | 增加私有 `references/portability.md` 中的可移植模型和 Shared Input。 |
| `references/role-launch.md` | `preserve` | 原样使用统一的公共运行时及其证据选择政策；通过私有 `references/portability.md` 对发现的证据进行资格判定。 |
| `references/reviews.md` 中的两个 Correctness scope | `extend` | 增加共享归属、依赖闭包、源项目证据资格判定、排除未通过资格判定的源项目含义、代表性目标路径和出口。 |
| `references/acceptance.md` 中的 `Freeze immutable cases` | `extend` | 增加运行时可行性缺乏高置信静态与 Machine 证据的代表性目标接缝。 |
| 公共 `SKILL.md` 中的 `5. Finalize and hand off` | `extend` | 要求当前版本具有可移植性和代表性目标证明。 |

所有未列出的公共阶段、全新身份、私下判断要求、准确授权、报告、Role Boundary Audit、Machine
与 Acceptance Owner、修正规则、出口和最终化要求都原样适用。本 Skill 不增加阶段、角色、语义
通道、finding 生命周期、审计分类体系、发现接口或恢复路径。

**完成条件：**固定公共工作流加上每项映射的私有处置，共同形成一份所有路径完整、通过资格验证
且可调度的 Run Contract。

## 运行固定的共享工作流

向组合后的合同提供已接受的 Shared Input、完整的可移植性证据与通过条件，以及准确的操作授权。
应用映射的私有处置，完成公共工作流。Author 和 Reviewer 使用公共证据选择政策；只有私有可移植
性资格政策能决定根据该政策选出的材料是否可以支持可移植含义。公共`CONTEXT_REQUIRED`和
`ACCESS_REQUIRED`结果仍是例外的有界后备方案，而不是共享就绪门槛。

按照 `references/portability.md` 的规定扩展两个公共 Correctness scope。只有当某个必需代表性
目标的运行时可行性缺乏高置信静态与 Machine 证据时，才通过公共的条件式 Executable Acceptance
阶段处理它。只使用一个公共 Acceptance 组合；不要创建第二套 Acceptance 生命周期。

## 完成

可移植成功不仅需要满足所有未变更的公共证明与最终化条件，还需要当前版本具有以下证据：

- 已接受的可移植含义不包含任何实际生效的源项目假设；
- 已声明依赖闭包完整，并具有公开加载路径或目标自有路径；
- 每个有证据表明会产生实质差异的受支持接缝都获得代表性覆盖；
- 两份经过可移植性扩展的 Correctness 裁决均通过；以及
- 每个必需的代表性 Acceptance 用例均通过。

把所有成功事实、代表性目标证据，以及公共操作与审计记录加入公共交接。本 Skill 不授予发布、
安装、commit、翻译或其他下游影响的权限。
