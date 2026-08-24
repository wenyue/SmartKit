# Rule

Rule 负责一项持续生效的政策。本 reference 应用于候选工件本身。

## 确立 Policy Frame

根据已接受意图、当前 Rule schema 和治理证据，确定 Rule 的 class、owner 与 strength、scope 与
applicability、可观察的 predicate-to-outcome 映射、exceptions、precedence 和 ownership
boundaries。这些部分共同构成 Policy Frame。每个适用字段都需要一个有依据的值；只有当证据证明
字段不会改变政策时才省略它。

## 编写一项政策

- 以治理政策开头。把每个谓词与其要求的结果和例外放在一起。
- 每项要求保留在拥有它的最窄 Rule 中；不要复制或悄然覆盖更具体的 Rule。
- 使用可观察的谓词和结果。对于每个 threshold、overlap、range、exception 和 exclusion，拒绝
  最近的 false positive 和 false negative，不要依赖未定义标签。
- 把有序执行流程放在 Skill 中。
- 把可发现的环境事实留在其活动 owner 中。把理由和决定历史保留在其文档 owner 中，除非它们会
  改变政策的适用方式。
- 使用 heading 表示稳定政策区域或真实适用分支，使用 list 表示并列要求，仅使用 table 表示精确
  映射或重复字段对比。

## 审查并验收 Rule 语义

Semantic Review 根据候选工件和证据重建每个适用字段及条件到结果的映射。以下情况应判定失败：字段
隐含、缺少依据的不适用、虚构谓词、重复 owner、未声明 override，或者相同事实产生两个结果或没有
结果。

只选择风险最高的相关案例：

- 一个 included 或 applicable 案例，以及最近的 excluded 或 inapplicable 案例；
- 一个受影响的 threshold、range、overlap、exception 或 owner boundary；以及
- 当另一个 Rule 可以改变结果时，一个 precedence 或 conflict 组合。

在真实政策接缝应用通用 Acceptance Runner 协议，并要求产生可观察的决定或动作；解释 Rule 内容
不属于应用。
