# 证明与修正生命周期

本合同负责证明适用性与顺序、finding 严重级别、修正、重放和全局出口。默认依靠判断；下述有序证明与修正步骤属于流程，因为改变其顺序可能使证据失效或授权不安全的写入。

## 选择并运行证明

在 Author 工作前冻结适用性，并在同一个当前指纹上按以下顺序运行阶段：

| 顺序 | 阶段 | 适用性与关闭条件 |
| --- | --- | --- |
| 1 | Machine | 条件式。只有 Machine 不适用时才为 NOT_REQUIRED。适用时，只有每项已选非修复命令均成功退出才为 PASS；一项或多项已选命令失败时返回 FAIL，并进入下述 Machine 修正。 |
| 2 | Quality | 始终执行。Reviews 冻结的 Quality 拓扑在同一指纹上独立通过完整 Candidate。 |
| 3 | Correctness | 始终执行。Reviews 冻结的 Correctness 拓扑在该指纹上通过完整已接受合同。 |
| 4 | Acceptance | 按 Acceptance 合同选择 Static Scenario、Executable 或 NOT_REQUIRED。 |

Machine 可报告的阶段裁决为 PASS、FAIL 或 NOT_REQUIRED。

Machine 可以检查 schema、metadata、引用、固定流程、脚本和 Owner 支持的测试。它绝不为了避免 NOT_REQUIRED 而虚构检查，也绝不修复 Candidate。记录准确命令、退出状态与相关输出。Machine 期间发生 Candidate 变化属于边界停止，不是测试结果。

当判断或分支行为、工具或环境可行性、权限、文件系统状态、外部影响、恢复或运行时出口仍存在重要不确定性时，选择 Acceptance。高置信语义且没有重要运行时不确定性时为 NOT_REQUIRED。无论 Rule 还是 Skill，Acceptance 都是条件式的。

## Finding 与严重级别

有支持的 finding 要写明问题、治理证据与来源、Candidate 位置、不变时的影响、严重级别、受影响义务或路径、保留约束和有界修复方向。它不提出替换文本。

Quality 可以返回：

- critical：正确性、权威、安全、归属、可执行性或终止结果失败；
- material：实质降低信息质量、执行可用性或可维护性的有支持缺陷；
- advisory：有界的非阻塞改进或有效选择机会。

Critical 与 material finding 会阻塞 Quality。Correctness 与 Acceptance 的 Candidate 缺陷仅使用 critical。估计修复规模不能降低严重级别。仅凭品味、对称性、行数或文本差异不能确立缺陷。

Q1 或 Q2 所负责视角内的每项有支持 critical、material 或 advisory 主张都是 finding，并遵循本处置生命周期。deferred surface 超出该 Reviewer 的视角或裁决权威；它不能替代其负责的 advisory，也不能满足 Quality PASS Gate。可能阻塞的跨视角问题遵循 Reviews 的非语义检查请求路径。该请求既不是 finding 也不是证据，但在所属视角独立检查该指纹上所指出的 Candidate 位置前，证明不能关闭。

## 修正一个指纹

对于每项有支持的 finding：

1. Reviewer 把完整 finding 直接发送给常驻 Author。
2. Author 独立返回 repair、partial repair 或 decline，并给出有证据支持的理由。
3. Reviewer 判断其阻塞主张是已解决、由拟议修复有条件解决，还是未改变。新的有支持证据可以细化 finding。
4. 阻塞仍存在时，同一配对继续讨论，直到达到不动点。若连续两轮具有相同主张、证据、处置与方法，则返回 NO_PROGRESS。
5. advisory 在 Author 作出处置后关闭，不进入 NO_PROGRESS。

任一参与者返回 HUMAN_DECISION_REQUIRED 都会立即停止。保留请求，并且只能在新运行中继续。

所有讨论关闭后，把每项已同意的阻塞修复和每项由 Author 选择的 advisory 修复合并为一份准确 Repair Scope。常驻 Author 可以在授权内独立实现这些结果。只有 Reviewer 同意拟议变更后不再保留任何阻塞部分时，partial repair 才符合条件。decline 绝不授权写入。

Author 的 COMPLETE 可接纳后，捕获并提升新指纹，并将返回的语义 Change Summary 一次性绑定到它。之前每项语义阶段裁决均失效。从 Machine 开始按顺序重新运行全部适用证明。仍保持开放的审查阶段会在修正与复查期间保留其 Reviewer 身份；每个因修复而失效或重新打开的、先前已 PASS 并关闭的审查阶段，都要根据 Role Runtime 使用全新身份。Acceptance 身份遵循 Acceptance 合同。语义裁决不能沿用。

Machine FAIL 使用相同的常驻 Author，并使用一份包含失败命令与受影响路径的准确 Repair Scope。如果同一失败在两轮修复与重跑后依然存在，且没有新证据或方法，则以 NO_PROGRESS 停止。

## 选择出口

选择任何结果前，完成已开始的可执行 Acceptance 安全流程与 Role Runtime 最终化。选择第一项有支持的结果：

1. ATTEMPT_INVALID、RUNNER_NOT_QUIESCENT、CLEANUP_FAILED 或另一项已开始尝试的安全终止结果；把同时出现的人类、Candidate 或边界结果保留为下层结果；
2. CANDIDATE_CHANGED 或 ROLE_BOUNDARY_VIOLATION；
3. TEARDOWN_FAILED；把同时出现的低优先级终止结果保留为下层结果；
4. HUMAN_DECISION_REQUIRED；
5. SEMANTIC_ROLE_UNAVAILABLE 或 HOST_UNAVAILABLE；
6. 无法满足的 CONTEXT_REQUIRED 或 ACCESS_REQUIRED；
7. ALIGNMENT_REQUIRED、NO_PROGRESS、AMBIGUITY_UNRESOLVED 或 EXECUTION_UNAVAILABLE；
8. 只有全部适用证明都在最终指纹上通过、每项 advisory 都有 Author 处置、清理完成且最终边界检查匹配时，才为 COMPLETE。

低优先级结果不能抹去高优先级的安全、边界或残留状态证据；每项同时出现但被覆盖的终止结果都保留为下层结果。
