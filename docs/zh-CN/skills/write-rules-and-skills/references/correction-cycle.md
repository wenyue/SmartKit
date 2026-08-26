# 修正循环

## Findings

每个 finding 包含：

- 稳定 ID；
- 问题和支持证据；
- 具体反例；
- 候选项位置；
- 严重程度：`critical`、`material` 或 `advisory`；
- 估计的 Repair Scope；
- 受影响的义务或表面；以及
- 保留约束。

字段不适用时，使用 `N/A` 并说明原因。Reviewer 指出问题和证据，而不提供替换文本。

`critical` 涵盖语义、权限、安全、所有权、可执行性或退出失败。`material` 涵盖有依据且明显降低
信息质量、可维护性或可靠性的缺陷。两者通常都值得修复。`advisory` 涵盖较小的改进或存在多个有效
方案的选择；如果有依据的修复仅涉及一两句话或一个小区块，并且能保留含义，则默认值得修复。Author
决定修复或拒绝；同一个 Reviewer 决定是否仍有任何 finding 值得修复。

## Reviewer 回调结果

每次 Quality 或 Correctness Reviewer 回调，以及每次判断 Candidate 的 Acceptance Reviewer 回调，
都只返回以下一种结果：`PASS`、findings、`CONTEXT_REQUIRED` 或 `ACCESS_REQUIRED`。
`CONTEXT_REQUIRED` 指出缺失的事实或内容及其用途；`ACCESS_REQUIRED` 指出准确的路径、访问模式
和原因。两种请求都不是 finding 或 `PASS`，也不会把 finding 或 verdict 权威转移给 Controller。
成功完成最终处置的 Acceptance 观察失败或无法确凿满足冻结的通过条件后，Acceptance Reviewer 可以
改为返回 [`acceptance.md`](acceptance.md) 定义的 Acceptance 专属 `fixture/environment defect`
或 `ambiguous` 分类。该 Reviewer 拥有分类权威；Controller 只根据完整的可操作载荷执行规定的尝试
编排，并用新的 Runner 证据恢复同一个 Reviewer。`candidate defect` 按四结果契约返回 findings。

Controller 只能通过冻结的 Role Launch 预授权更新范围满足请求，然后恢复同一个持续 Reviewer。
实质性请求或超出范围的请求会返回 `ALIGNMENT_REQUIRED`，并要求开始新运行。如果符合条件的更新
无法提供，应以适用的请求状态停止，而不是替换 Reviewer。调用方自有 Adapter 可以根据其冻结契约
进一步限制符合条件的更新。

## 持续修正循环

对于每个 Reviewer：

1. Reviewer 检查当前 Candidate Version，并返回上述四种回调结果之一；根据该契约处理任何上下文
   或访问请求并恢复同一个 Reviewer，只有 findings 或 `PASS` 可以进入后续循环。Acceptance 专属
   执行分类则遵循其尝试编排契约。
2. Controller 将相互一致的 findings 作为一个 Repair Scope 发送给持续 Author。
3. Author 直接修复有依据的 finding，使被拒绝的 finding 保持不变，并返回处置和 Author Change
   Summary。
4. 同一个 Reviewer 收到当前 Candidate Version、自己的先前 findings，以及
   [`author.md`](author.md) 定义的简短处置载荷，但不接收 chain-of-thought、预期文本、diff 或
   无关理由。
5. 重复，直到 Reviewer 找不到值得修复的问题。

如果有依据的 findings 看似不相容，Controller 会将冲突返回给负责的 Reviewer，以澄清证据或范围；
它不选择候选项含义。然后 Author 修复或拒绝每项已澄清的 finding。如果完整的已接受证据仍支持实质
不同的结果，应在再次写入前以 `ALIGNMENT_REQUIRED` 停止，并指出准确选择和决策所有者。同一未解决
finding 或冲突连续两轮存在且没有新的有依据方案时，因无进展停止。

审查单元是当前阶段的并行 Reviewer 对，或当前 case 的单个 Acceptance Reviewer。并行 Reviewer 对的
两个成员在该审查对的整个修正循环中都保持留存。循环内每次 Author 变更都会使两个本地 verdict 失效，
两个 Reviewer 都要复查完整 Candidate Version。只有两者对同一个 Candidate Version 都报告 PASS 时，
才结束该审查对。单个 Acceptance Reviewer 只在 case PASS 时结束；重放调度要求在 Stage-local PASS
后结束时，Acceptance 契约会先记录当前 case PASS。已结束的审查单元之后失效时，启动全新的 Reviewer
身份。

## Scope Transfer Notes

Reviewer 可以独立于其回调结果，将 Scope Transfer Notes 作为回调级元数据附加。Note 既不是 finding
字段，也不是回调结果，并且不影响发出它的 Reviewer 的 verdict。每个 note 都包含观察、证据、位置和
预期所有者。Controller 只路由该 note 一次：

- 立即交给当前另一个 Reviewer；
- 在后续阶段给出首次 verdict 或操作前交给该阶段；或
- 在当前阶段取得本地 PASS 后交给更早的已通过阶段。

接收方 Reviewer 决定该 note 是否支持 finding。对于 Controller 拥有的阶段，Controller 执行其现有
操作并使用该阶段的证据契约。可能影响已通过阶段的 note 会使该阶段失效并遵循正常回退；它不会创建
新的语义所有者。

## Candidate Version 和回退

每次 Author 写入都会创建新的 Candidate Version。Controller 在写入前后为每个候选文件计算紧凑
指纹，并强制执行单一写入者锁。Reviewer、Runner 和机器检查不得修改候选项。

Author 变更后，同一个 Reviewer 或保留的 Reviewer 对先复查当前完整 Candidate Version，并取得
case 或审查对级别的本地 PASS。随后，Controller 将 Author Change Summary、变更路径和指纹与更早
已通过的证据比较。返回证明可能不再成立的最早已通过阶段，并在那里启动全新 Reviewer；保留未受影响
的证据。只有紧凑信号不足时才检查有针对性的 diff。未来阶段尚未产生证据，因此不能失效。
