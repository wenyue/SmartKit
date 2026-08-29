# Quality 与 Correctness Review

本合同向 Frozen Job Design 贡献完整全新 cohort、分配与分批输入。每个 Reviewer 在修正期间保持
身份，并接收同一份完整 Candidate、指纹、共同证据、选择政策与授权，此外只接收自己的 scope
专属证据。它不接收 Author 推理、修复意图、私有笔记或其他 Reviewer 的工作，先作判断，再只与
常驻 Author 讨论自己负责的 finding。

Evaluation 负责共同 finding 生命周期与共识。本文件负责视角资格、coverage 证据、调查边界与
裁决条件；服从、投票、Controller 或其他 Reviewer 都不能决定主张或裁决。

较早的`PASS`只有通过 Evaluation 接纳的兼容性绑定才能继续有效。语义影响或不确定影响在身份与
生命周期仍符合条件时采用预授权的评估或复查；否则使用全新 cohort 重放。

使用自适应挑战问题，直到每个有支持的答案、矛盾、缺口或风险都穷尽所分配的 scope；不设固定
数量。问题是调查提示，不是 finding。按照 Evaluation 的完整通用 schema 记录 finding。

## Quality

Quality 贡献三名 Reviewer。所有成员均接收完整 Candidate 与指纹、路径、要求、保留义务、模型、
写作指引、证据与共同授权。Change Integrity 还接收不可变 baseline、规范 delta 与处置图。

在`PASS`前，每名 Reviewer 都返回一份绑定到其单元、身份与 Candidate 指纹的临时**Quality
Coverage Record**。Information Architecture and Economy 使用下述 Economy schema。Language
and Execution Usability 为每项准确 Allowlist 资源记录一行，包含三个字段：`actionable paths`、
`branches`和`exits`。每个字段要么是`none`，要么是一组唯一不透明 ID，并且每个 ID 映射到一个
或多个 Candidate 锚点。Change Integrity 为 Job Design 当前 expected-proof-state delta 绑定中的
每个 item 记录一行，其处置为`no quality effect`、`finding`或`transfer`；适用时还包含理由锚点
以及 finding 或 transfer ID。每份记录都带有 coverage-complete 标记。Role Runtime 只审计冻结
结构；Reviewer 负责选择、理由、coverage 与判断。记录是临时证据，绝不是 Candidate 制品。

把下列每个完整视角准确绑定给一名 Reviewer。每名 Reviewer 都只通过该视角对完整 Candidate
进行穷尽检查。视角之外的疑点应成为不含语义的 Scope Transfer Note，由相应 Owner 独立检查；
这不会扩大发送者的 scope。前两个视角只判断完整的当前 Candidate，不作 baseline-to-current 或
其他相对于变更的判断。

### 信息架构与经济性

负责整个 package 与资源内部的信息层级、加载与披露、放置与共同定位、内容蔓延与注意力成本、
单一来源语义归属、结构或语义重复与散落、陈旧缓存与依赖、维护接缝，以及保留行为的最小结构。
追踪每个入口、加载、指针、分支、依赖、缓存事实、操作性含义与同步编辑接缝。检查首次需要时
披露、规范归属、必要的局部增量与指针、可减少的重复、陈旧缓存、强制预加载、碎片化含义、脆弱
同步编辑，以及保留每条路径与提示的最小结构。

该 Reviewer 负责的 Quality Coverage Record 是**Economy Coverage Record**，内容如下：

在所审指纹下机械派生有限单元清单：Markdown 使用源文件中的每一条有编号物理行，包括空行或
仅含空白的行；换行分隔符不另算单元，空文件没有行单元。结构化数据使用准确 key path 下的每个
scalar field；其他文本使用每个非空行；不包含文本或结构化单元的资源使用显式值
`no operative units`。

- 每项 manifest 资源一行：身份、manifest 路径或条件、Candidate 规定的加载点、Reviewer 判定的
  首次需要点、证据锚点、处置`aligned`、`premature`或`late-or-unreachable`；非 aligned 行还需
  finding ID；
- 每项准确 Allowlist 资源一行：派生类别、完整 unit ID 或`no operative units`、repetition-group
  ID 或`none`，以及资源处置`necessary`、`stale cache`、`sprawl`、`attention cost`、`finding`
  或`transfer`；任何非 necessary 结果还需锚点以及 finding 或 transfer ID；
- 每个派生单元一行：资源与 unit ID、准确锚点、由 Reviewer 负责的`operative`/`nonoperative`
  分类，以及 economy 处置`necessary`、`no-op`、`stale cache`、`sprawl`、`attention cost`、
  `finding`或`transfer`；任何非 necessary 结果还需 finding 或 transfer ID；
- Reviewer 发现的每项重复操作性含义一行：不透明 group ID、所有 Candidate 位置、规范 Owner、
  分类`necessary local delta`、`necessary pointer`或`reducible duplication`、理由锚点，以及可减少
  重复的 finding ID；以及
- 通用 coverage-complete 标记。

每个非 aligned、可减少或非 necessary 行都必须在`PASS`前有已解决的 finding 或 transfer。
Controller 审计准确资源、派生单元、字段、标签、锚点与闭合交叉引用；只有 Reviewer 判断操作性、
必要性、证据、归属、重复、coverage 与分类。

只有解决每个有支持的架构或经济性问题，并返回完整 Economy Coverage Record 后，才算完成。

### 语言与执行可用性

负责陈述与段落的措辞、句法、力度、术语与表达层 no-op，以及全新 Agent 根据已陈述的输入、权威、
证据、依赖、动作、分支和结果执行工作的能力。信息层级与结构重复仍由架构视角负责。局部检查每项
操作性陈述，并遍历每条可执行路径与出口。检查歧义、执行者与条件是否可见、力度、术语稳定性、
触发条件与例外的位置、可观察的分支选择、依赖与权威、可区分的完成、恢复、受阻、失败和停止
出口，以及措辞层 no-op。

只有解决每个有支持的清晰度或执行可用性问题，并完成准确资源 coverage record 后，才算完成。

### Change Integrity

Change Integrity 是 Quality 中唯一感知 delta 的视角。它只负责必须依据 pre-Author baseline 与
当前 Candidate 的关系才能成立的质量主张：有用上下文、解释或限定的缺失；不合理或
无关的 churn；相对于变更产生的碎片化或重复；使共同定位或路由退化的移动或合并；以及只检查
当前状态可能无法暴露的清晰度、可用性或可维护性回归。它同时检查完整当前
Candidate 与完整规范 delta。delta 只提供不依赖 VCS 的辅助定位与证据，绝不能替代当前状态 review。

看到基线不会赋予管辖权威；已接受证据和处置仍是权威。通用证据排除项保持不变。仅凭文本删除、
变更规模、churn 数量、历史偏好或文本/结构相似性，不能形成 finding。检查每项已授权的改写、
删除、移动或合并是否造成有用上下文、限定、共同定位、路由质量或可维护性的当前损失；是否产生
由变更导致的碎片化、重复、注意力成本、歧义或间接表达；是否存在带受支持成本的无关 churn；
以及是否有能保留已接受含义与处置的有界修复/重放 scope。

Change Integrity finding 必须具有已接受证据及其来源、有支持的当前或由变更造成的质量成本、当前影响，
以及有界修复与重放 scope。它可以使用 Evaluation 下 Quality 的`critical`、`material`或
`advisory`严重级别。若某个问题仅凭当前 Candidate 就能得到支持，则应生成不含语义的 Scope
Transfer Note，交给相应的当前状态视角。

只有在检查当前 Candidate，并在 coverage record 中核算每项规范 delta item、解决每个有支持的
变更相对问题、转移每个当前状态问题后，才算完成。

Quality 使用 Evaluation 的`critical`、`material`和`advisory`分类及共同生命周期。本合同中的
各个视角决定 Quality finding 资格。

只有所审 Candidate 指纹上不存在尚未解决的 critical 或 material 主张、自己负责的每项
advisory 均有冻结的 Author 处置，而且每条已路由 note 都已根据 Evaluation 得到独立检查，
Quality Reviewer 才通过。路由给后续阶段的 note 仍不阻塞，而且按照 Evaluation 的定义既不阻塞
Quality，也不会使其失效。只有每项独立生成的`PASS`与所需 coverage record 都为同一个当前指纹
满足 Evaluation，Quality 才达到当前闭合。后续失效需要成员完全不同的全新完整 cohort。

## Correctness

Machine `PASS`或有效`NOT_REQUIRED`后，激活三名 Correctness Reviewer。所有成员均接收已接受
上下文、义务、处置图、管辖证据、模型、阶段证据、当前 Candidate 与指纹，以及共同授权。
Preservation and Regression Integrity 还接收不可变 baseline 与规范 delta。每名 Reviewer 仅
穷尽自己的 scope；跨 scope 或非阻塞疑点通过 Scope Transfer 路由，且不改变原裁决。

### Spec Fidelity and Semantic Integrity

负责静态合同保真度。把每项已接受的义务、含义、归属边界、适用条件、处置和依赖闭包要求映射
到 Candidate；再把 Candidate 的每项操作性承诺反向映射到已接受支持。检查遗漏、弱化、矛盾、
无支持的新增、错误归属或适用性、未声明路由、同时成立但不兼容的义务，以及不符合条件的证据。

只有两组映射都穷尽完整，并解决每个有支持的不一致，才算完成。

### Preservation and Regression Integrity

负责 baseline 到当前 Candidate 之间未经授权的语义损失。使用规范 delta 定位变更，但管辖证据
与已接受处置——而不是看到基线这一事实——才提供权威。通过每项已接受处置，把每项 baseline
承诺、删除、弱化、替换与移动追踪到当前含义、加载、适用性、可达性，以及涵盖每项变更资源且
绑定到指纹的完整 delta。

文本变更本身不是缺陷。finding 必须有受支持的语义损失、未经授权的 delta、缺失处置，或保留、
加载或适用性破坏。未解决的未分类 baseline 含义应通过现有有界请求或停止路径路由。只有把每项
baseline 承诺与变更通过完整 delta 追踪到已接受的当前结果，并解决每个有支持的问题后，才算完成。

### Critical Behavioral Integrity

负责已接受合同的动态执行。追踪每条关键与代表性路径，包括实质不同的同时触发条件、依赖、权限、
影响、验证、失败、恢复、路径中途停止、决策归属、保留与安全，以及可观察的成功、受阻、失败、
恢复和终止出口。

只有每条路径、同时触发情况、权限或影响边界、验证、恢复、停止与出口都有可观察轨迹，并且没有
有支持的矛盾，才算完成。

Correctness 只产生`critical`finding，每项都指出一个不可容忍场景与修复机制；修复规模绝不会
降低合同违规的严重级别。替换文本由 Author 负责。非阻塞改进转移给 Quality 独立检查。只有不再
有 blocker，Reviewer 才通过；只有三项独立`PASS`结论都在同一个当前指纹上满足 Evaluation，
Correctness 才达到当前闭合。后续失效需要全新三人 cohort。
