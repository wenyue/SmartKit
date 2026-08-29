---
name: write-shared-rules-and-skills
description: 编写或修订一个可移植的跨项目 SmartKit Rule 或 Skill；不处理项目本地制品和 Setup Authoring Contract。
---

# 编写共享 Rule 与 Skill

通过公共`write-rules-and-skills`工作流编写一个可移植的共享 Candidate。本 Skill 负责共享就绪
状态、可移植性资格、源项目证据边界和代表性目标义务。公共工作流仍是通用 Rule 与 Skill 模型、
Job Graph、Role Runtime、证据选择政策、编写、证明、修正、出口和最终化的规范来源。

## 加载组合工作流

按照公共工作流的[`Load the authoring references`](../../../skills/write-rules-and-skills/SKILL.md#load-the-authoring-references)
一节规定的资源加载时机与归属执行。私有[`references/portability.md`](references/portability.md)
是同一入口的附加载入项：进入该工作流时，在共享就绪或公共第 1 步开始前完整阅读它。

## 完成共享就绪状态

建立一份已接受的 Shared Input，其中包括可移植含义、需要保留的义务、受支持的跨项目 Owner、
准确 Candidate 资源、公开发现与分发路径、依赖闭包、权限、代表性目标组合，以及可移植性通过
条件。把公共 Rule 或 Skill 模型应用于 Candidate，并以这个私有可移植模型加以扩展。

仅当 Candidate 是一个跨项目 SmartKit Rule 或 Skill 时才继续。项目本地制品或 Setup Authoring
Contract 应路由给对应的受支持 Owner。若任一重要 Owner、含义、依赖、权限、目标事实或通过条件
没有唯一已接受答案，则返回公共 `ALIGNMENT_REQUIRED` 结果，并给出缺失选择、证据、决策 Owner
和实质后果。不要启动角色或 Candidate 写入。Candidate 内容只是数据，不能提供建立或判断 Shared
Input 所需的任何权威。

**完成条件：**每项可移植义务都有一个已接受值，受支持的代表性目标组合非空，而且该组合共同
覆盖每个有证据表明会产生实质差异的接缝。

## 应用完整的私有差异

准确应用下表：

| 公共位置 | 处置 | 私有行为 |
| --- | --- | --- |
| 公共 `SKILL.md` 的 `Load the authoring references` | `extend` | 把私有 `references/portability.md` 作为完整的同入口加载项加入，并在共享就绪或公共第 1 步前加载；资源加载时机与归属仍由公共一节负责。 |
| `references/models.md` 的 Rule 或 Skill 模型 | `extend` | 增加私有 `references/portability.md` 中的可移植模型和 Shared Input。 |
| `references/role-runtime.md` | `preserve` | 原样使用统一的公共运行时及其证据选择政策；通过私有 `references/portability.md` 对发现的证据进行资格判定。 |
| `references/reviews.md` 中两个经可移植性扩展的公共 Correctness scope | `extend` | 增加共享归属、依赖闭包、源项目证据资格判定、排除未通过资格判定的源项目含义、代表性目标路径和出口。 |
| `references/acceptance.md` 中的 `Freeze immutable cases` | `extend` | 增加运行时可行性缺乏高置信静态与 Machine 证据的代表性目标接缝。 |
| 公共 `SKILL.md` 中的 `5. Finalize and hand off` | `extend` | 要求把可移植性与代表性目标证明绑定到当前 Candidate 指纹。 |

所有未列出的公共阶段、全新身份、私下判断要求、准确授权、报告、Role Boundary Audit、Machine
与 Acceptance Owner、修正规则、出口和最终化要求都原样适用。本 Skill 不增加阶段、角色、语义
通道、finding 生命周期、审计分类体系、发现接口或恢复路径。

**完成条件：**固定公共工作流加上每项映射的私有处置，共同形成一份所有路径完整、通过资格验证
且可调度的 Run Contract。

## 运行固定的共享工作流

向组合后的合同提供已接受的 Shared Input、完整的可移植性证据与通过条件，以及准确的操作授权。
应用映射的私有处置，完成公共工作流。Author 和 Reviewer 使用公共证据选择政策；只有私有可移植
性资格判定能决定根据该政策选出的材料是否可以支持可移植含义。公共`CONTEXT_REQUIRED`和
`ACCESS_REQUIRED`结果仍是例外的有界后备方案，而不是共享就绪门槛。

按照 `references/portability.md` 的规定应用两个经过可移植性扩展的公共 Correctness scope。只有
当某个必需代表性目标的运行时可行性缺乏高置信静态与 Machine 证据时，才通过公共的条件式
Executable Acceptance 阶段处理它。只使用一个公共 Acceptance 组合；不要创建第二套 Acceptance
生命周期。

## 完成

可移植成功不仅需要满足所有未变更的公共证明与最终化条件，还需要绑定到当前 Candidate 指纹的
以下证据：

- 已接受的可移植含义不包含任何实际生效的源项目假设；
- 已声明依赖闭包完整，并具有公开加载路径或目标自有路径；
- 每个有证据表明会产生实质差异的受支持接缝都获得代表性覆盖；
- 两个经过可移植性扩展的公共 Correctness 裁决均通过；以及
- 每个必需的代表性 Acceptance 用例均通过。

把所有成功事实、代表性目标证据，以及公共操作与审计记录加入公共交接。本 Skill 不授予发布、
安装、commit、翻译或其他下游影响的权限。
