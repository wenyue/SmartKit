# 可执行 Acceptance

## 判断是否需要 Acceptance

只有当候选项管辖具体或足够复杂的运行时行为，而且静态审查、机器检查或已接受机制尚不能高置信度
确立其可行性时，才运行 Acceptance。相关信号包括固定的多步骤顺序、有意义的分支、重试、恢复、
退出、具体工具调用、文件修改、权限边界、外部影响，或强制此类行为的 Rule。

笼统的判断指导、简单的非工具过程，或已有高置信度支持的行为不需要 Acceptance。记录
`NOT_REQUIRED` 并完全跳过该阶段。不要用名为 Acceptance 的静态 walkthrough 代替它。

## 冻结案例组合

执行前，冻结代表性 case 和可观察的通过条件。使用覆盖实质运行时风险的最小案例组合：通常包括成功
路径，以及候选项影响的每种实质不同的错误、恢复或退出。不要规定固定 case 数量。按风险从高到低
顺序执行 case。

## 执行和判断

每次尝试都由 Controller 按所选 Adapter 的要求准备一次性 Execution Isolation、fixture、准确限定
到 case 的 `read`、`write`、`create`、`delete` 和工具授权、可观察证据捕获及清理。保持 Candidate
不可变。如果任何必需权限、安全隔离或既有授权不可用，则以 `EXECUTION_UNAVAILABLE` 停止，报告
未经测试的表面，并且不得给出 `PASS` 或 `NOT_REQUIRED`。只有已接受任务已为该 case 授予明确权限，
并且所选 Adapter 支持时，才可以使用网络访问或产生外部影响。

每次尝试都在该 Execution Isolation 中启动一个全新 Runner，只向其提供只读 Candidate、冻结 case、
fixture、准确的 case 授权和允许的工具，以及该 case 所需的可观察通过条件。Runner 负责执行；它不
判断或修复 Candidate、fixture 或环境。

### 最终处置每次已启动的尝试

Runner 一旦启动，无论它成功、失败还是无法正常返回，也无论证据捕获或 Role Boundary Audit 成功
还是失败，Controller 都进入该次尝试的最终处置。首先保留所有可取得的可观察证据，包括任何可用的
Runner 终止报告，并记录任何捕获失败。然后使用所选 Adapter 完成、停止或以其他方式结束 Runner，
并确认其静止，包括异常执行或不返回的执行。保留任何额外的终止证据。只有确认静止后，Controller
才能使用已经为一次性隔离授权、准确、安全且由 case 拥有的目标和授权尝试清理；绝不扩大权限，也不
使用不安全或宽泛的删除。如果清理失败，最多进行一次有依据的有界恢复尝试，而且仅在该尝试安全且已
获授权时进行。这是该次尝试唯一的清理恢复额度。

Role Boundary Audit 违规具有终止优先级，但 Runner 静止时并不禁止安全清理。如果无法确认静止，
保留所有可取得的证据并跳过清理。完成终止尝试、指纹审计，以及静止状态所允许的任何清理后，按以下
优先级选择尝试结果：

1. 任何 Role Boundary Audit 违规或证据捕获失败都会产生 `ATTEMPT_INVALID`，无论静止或清理结果
   如何。
2. 否则，无法确认静止会产生 `RUNNER_NOT_QUIESCENT`。
3. 否则，经过一次安全、已授权且有界的恢复后清理仍失败，或没有这种恢复方式，会产生
   `CLEANUP_FAILED`。
4. 否则，最终处置成功。

对于任何终止结果，报告所有可取得的证据、任何违规或捕获失败、静止状态和残留状态、清理结果，以及
已尝试的那一次有界清理恢复，或没有可用恢复方式的原因。停止，不创建或恢复 Reviewer，也不启动另
一次尝试。任何终止结果都不是 Candidate PASS、`NOT_REQUIRED` 或 fixture/environment defect。

如果一个 case 的第一次尝试得到终止结果，则停止且不启动 Acceptance Reviewer。只有证据捕获、审计、
Runner 静止和必需清理全部成功完成，最终处置才成功。最终处置成功本身不会使 case PASS。第一次尝试
成功完成最终处置后，启动一个全新的 Acceptance Reviewer，并向其提供完整 Candidate Version、已接受
行为和管辖证据、冻结 case 和可观察通过标准、fixture 和权限边界，以及捕获的执行和最终处置证据。
该 case 后续每次尝试成功完成最终处置后，用新捕获的证据恢复同一个 Reviewer。在分类、Candidate
修正、fixture 或环境恢复、歧义观察和 case PASS 的整个过程中保留该 Reviewer。只保留当前 case 的
Reviewer；case PASS 后将其结束。复查时应用共同 Correction Cycle packet。

当观察满足冻结的通过条件且不支持任何 Candidate finding 时，Reviewer 返回正常的 `PASS`。
Candidate 缺陷会按完整的共同 finding schema 返回一个或多个 findings；Controller 将其作为一个
Repair Scope 发送给持续 Author，并继续同一个 Reviewer 的 Correction Cycle。当没有证据支持
Candidate 缺陷，但观察失败或无法确凿满足冻结的通过条件时，Reviewer 只返回以下两种 Acceptance
专属分类之一：

- `fixture/environment defect`：载荷指出有证据的缺陷，并给出准确、已授权且有界的 fixture 或环境
  修正，或者说明没有可用修正。Controller 只执行所提供的修正，依据正常尝试契约启动全新 Runner，
  完成该次尝试的最终处置并恢复同一个 Reviewer；没有可用修正时，使用下述适用的优先退出，而不凭空
  发明恢复方式；或
- `ambiguous`：Controller 将载荷中准确、有针对性的观察作为一次普通的全新 Runner 尝试启动。载荷
  指出未解决的备选解释，以及区分它们所需的有界设置和证据捕获差异。该尝试保持在现有权限内，并使用
  必需的设置、审计、证据捕获、清理和最终处置；随后 Controller 恢复同一个 Reviewer，如果分类仍然
  模糊则停止。

在 fixture/environment 恢复期间保持冻结 case 和通过标准。每次有依据的修正尝试只变更有界的
fixture 或环境。如果同一缺陷在连续两次修正尝试后再次出现，或没有新的安全有界恢复方式，则以
`NO_PROGRESS` 停止；如果必需的环境能力不可用，则改用 `EXECUTION_UNAVAILABLE`。报告这些尝试和
终止证据。上述单次有针对性的全新观察仍是模糊分类唯一允许的重试。

## 回退并重放 case

Stage-local PASS 表示当前 Acceptance Reviewer 在成功最终处置后，认为当前 Candidate Version 的
该 case 没有值得修复的问题。重放调度要求时，它会结束该 Reviewer 的修正循环，但它不是 Acceptance
PASS。

Author 修正后，应用共同的持续复查，并在 Controller 执行 Revision Impact Decision 前为当前 case
保留同一个 Reviewer、运行一次全新尝试并取得 Stage-local PASS。只有取得该 PASS 后：

- 如果早先的非 Acceptance 阶段失效，则把当前 case 的 Reviewer 作为唯一暂停的第五个身份保留，
  同时为已结束的审查单元使用全新 Reviewer，恢复最早失效阶段和中间阶段。然后恢复同一个 Acceptance
  Reviewer 前，先再次运行该 case 并成功完成最终处置；再用成功完成最终处置的证据恢复同一个
  Acceptance Reviewer，取得 Stage-local PASS，然后执行下一次 Revision Impact Decision。
- 如果早先已通过的 Acceptance case 失效，不要在保留当前 case Reviewer 的同时启动它的全新
  Reviewer。在同一个 Candidate Version 上，于 Stage-local PASS 时记录当前 case PASS 并结束其
  Reviewer，然后按照冻结的从高风险到低风险顺序，从最早失效的 Acceptance case 重新开始顺序评估。
  除非之后的 Author 变更可能影响当前 case 的证据，否则保留该证据；正常 Revision Impact 会使每个
  受影响 case 失效并重新运行。依次到达每个失效 case 时，先运行第一次全新 Runner 尝试并成功完成
  最终处置，再启动其全新 Reviewer；保留并跳过其他未受影响 case 的证据。
- 如果没有更早的阶段或 case 失效，则记录 case PASS 并结束当前 Reviewer。

重放期间，只让一个 Acceptance Reviewer 处于当前或保留状态。重放修正会重复 Stage-local-PASS-first
规则，绝不会在保留一个 case Reviewer 的同时启动另一个，也绝不会需要超过已鉴定的唯一暂停第五
身份。只有当前 Candidate Version 的每个冻结 case 都具有 Reviewer 所有的 case PASS，并由成功
最终处置和未受影响的证据支持时，Acceptance 才通过。
