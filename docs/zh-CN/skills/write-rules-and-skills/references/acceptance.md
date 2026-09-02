# Acceptance 合同

本合同负责条件式场景与运行时验证。使用能够解决重要不确定性的最轻模式；只有必须观察真实工具、环境、权限、影响或运行时边界时，才引入流程式执行。

Acceptance 在 Design 时恰好有三种结果：

- 对于高置信语义，且没有重要场景或运行时不确定性，使用 NOT_REQUIRED；
- 对于需要独立场景验证的判断或分支行为，但不需要观察真实工具、权限、文件系统、环境、外部影响、清理或运行时可行性，使用 Static Scenario Acceptance；或
- 只有必须观察上述真实条件之一时，才使用 Executable Acceptance。

## 建立模式就绪状态

选择模式后，Acceptance 独占负责其条件式身份、容量、就绪状态与启动前终止结果：

- NOT_REQUIRED 不分配 Acceptance 身份或容量。
- Static Scenario Acceptance 恰好分配一名全新独立 Reviewer，不分配 Runner。该 Reviewer 在修正与复查期间持续存在。如果无法建立其身份、生命周期或一个必需槽位，则返回 SEMANTIC_ROLE_UNAVAILABLE，并列出未测试场景。
- Executable Acceptance 为每个活跃用例分配一名全新持久 Reviewer，并为每次尝试分配一名可与该 Reviewer 同时活动的全新 Runner。任何时刻只能有一名用例 Reviewer 处于活跃状态；其身份持续到该用例的修正与复查结束，在用例关闭时终止，且绝不能用于实质不同的另一用例。如果无法建立任一身份或槽位、Runner 终止、静止、一次性隔离、清理、恢复或另一项必需执行能力，则在启动前返回 EXECUTION_UNAVAILABLE，并列出未测试表面。

演练不能替代所需的 Executable Acceptance。任何 Acceptance 就绪失败都不能重新分类为 HOST_UNAVAILABLE。

## 冻结用例

无论哪种模式，都要冻结能够解决重要不确定性的、按风险排序的最小用例集合。每个用例写明已接受证据、输入与运行条件、分支或接缝、可观察通过条件，以及重要错误、恢复与出口变体。用例含义与通过条件在运行期间保持不变。

Acceptance finding 都是 critical Candidate defect。它们使用 Evaluation 的直接修正循环与常驻 Author。任何修复都会创建新的 Candidate 指纹，并在 Acceptance 复查前把证明返回 Machine。

## Static Scenario Acceptance

启动已冻结的 Static Reviewer，并向其提供完整 Candidate 与指纹、已接受义务与证据、冻结用例及通过条件。

Reviewer 把 Candidate 应用于每个场景，记录所选决策或行为、其 Candidate 依据，以及每项可观察条件是否都能在没有无支持假设的情况下成立。它返回 PASS、有支持的 Candidate finding、CONTEXT_REQUIRED、ACCESS_REQUIRED、HUMAN_DECISION_REQUIRED 或 AMBIGUITY_UNRESOLVED，并提供完整用例 coverage 以及未测试或不确定表面。

只有每个冻结用例都在当前指纹上通过，并且没有 critical finding 或重要歧义时，Static Acceptance 才通过。如果发生修复，相同的持久 Reviewer 会在较早证明恢复后复查全部冻结用例。

## Executable Acceptance

只有在具备准确用例级授权、可观察捕获、安全终止、静止、清理与恢复的一次性隔离中，才能使用 Executable Acceptance。network 与外部影响需要已接受权威和宿主能力。

每次尝试都使用当前活跃用例的冻结持久独立 Reviewer 和一名全新、不作判断的 Runner。Runner 只执行相应用例；它不能改变 Candidate 或 fixture 定义、判断、修复、清理、控制身份、扩展授权或委派。

安全且不会递归时，优先执行完整工作。只有完整执行会重新进入本 Acceptance 工作流或要求 Runner 控制身份时，才使用 Finite Execution Projection。冻结的 projection 必须执行每个受到实质影响的接缝，并到达可观察的递归或身份控制边界；文字模拟或前置状态并不充分。

### Attempt Contract

每次尝试前冻结：

- Candidate 指纹、不可变用例与通过条件；
- 一次性 fixture 与准确、归用例所有的可变目标；
- 工具、命令、权限、network 与外部影响授权；
- 对输出、影响、终止、静止、清理和残留状态的捕获；以及
- 终止、清理和至多一条预授权安全恢复路径。

启动一名全新 Runner。每次成功、失败、异常返回、不返回或审计停止后：

1. 保留每项可获得观察与捕获失败；
2. 终止 Runner 并确立静止；
3. 验证 Candidate 指纹与角色边界；
4. 只有静止后，才清理准确、归用例所有的影响，并在安全时尝试冻结恢复；
5. 记录残留状态并选择安全结果。

完成安全流程后，按顺序选择尝试结果：导致证据不可信的捕获失败或非指纹审计失败返回 ATTEMPT_INVALID；无法确立静止时返回 RUNNER_NOT_QUIESCENT；在允许恢复后仍清理失败时返回 CLEANUP_FAILED；否则安全最终化通过。如果清理的安全依赖于停止活动，则静止失败时禁止清理。Candidate 或角色边界不匹配仍作为下层结果保留。

每项已开始尝试都要在任何重试、语义结果或工作流退出前完成这套流程。任何安全终止结果都支配同时出现的其他结果。ATTEMPT_INVALID 不允许启动 Reviewer、进行语义分类或重试；它会停止 Acceptance，同时保留每项可获得观察与残留事实。

### 判断尝试

尝试安全最终化后，向持久用例 Reviewer 提供完整 Candidate、已接受行为、冻结用例、通过条件、捕获结果、权限、终止、静止、清理与残留状态证据。由 Reviewer 而非 Runner 或 Controller 作出分类：

- 每项条件均被观察到且不存在 critical Candidate defect 时，返回 PASS；
- 返回一项有支持的 Candidate finding；
- 返回 fixture 或 environment defect，并给出一项准确的预授权修正，或者确认不存在适用修正且不再有安全的有界恢复；
- 返回 CONTEXT_REQUIRED、ACCESS_REQUIRED 或 HUMAN_DECISION_REQUIRED；或
- 返回 AMBIGUITY_OBSERVATION_REQUIRED，并给出一项准确的定向观察、有界 setup 与 capture delta，以及现有权威内的证据需要；完成该观察后仍有任何重要歧义时，返回 AMBIGUITY_UNRESOLVED。

fixture 或 environment 修正发生在两次尝试之间，不能改变 Candidate、用例或通过条件。使用一名全新 Runner 与相同 Reviewer 重试。如果同一缺陷经过两次修正尝试后依然存在，且没有新证据或方法，则以 NO_PROGRESS 停止。

用例已经尝试后，如果 fixture 或 environment defect 没有准确的预授权修正，也没有安全的有界恢复，则返回 NO_PROGRESS。启动前发现缺少必需能力时，仍按模式就绪规则返回 EXECUTION_UNAVAILABLE。

对于 AMBIGUITY_OBSERVATION_REQUIRED，Controller 不作解释地把 Reviewer 负责的请求复制进一份新的冻结 Attempt Contract。由一名全新 Runner 按完整尝试安全流程执行，再由相同 Reviewer 重新评估所得证据。每个用例与指纹只允许进行一次该转换；它不改变用例含义或通过条件。

只有每个冻结用例都在当前指纹上通过、每名 Runner 都已静止、清理完成、不存在不安全残留状态且所有边界检查均匹配时，Executable Acceptance 才通过。最终交接记录用例、尝试、观察证据、清理与残留状态。
