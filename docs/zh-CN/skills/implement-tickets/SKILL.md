---
name: implement-tickets
description: 在一个隔离 worktree 中依次实施剩余 agent-ready tickets，在 Git 历史中标记可恢复的 ticket 边界，然后整批 review 并只 finalization 一次。
---

# 实施 Tickets

此 Procedure-led Skill 在一个 Batch Worktree 中把一个 Ticket Batch 作为依赖有序 pipeline 运行。
controller 负责 ticket 选择、claims、worker handoffs、batch evidence、finalization 和 tracker
completion。每个 fresh worker 负责共享顺序历史中一个 ticket 的改动；同一时间只能有一个 worker
使用 Batch Worktree。

## 建立运行

1. 读取已配置 issue-tracker 指令、引用的 Spec 或 parent source，以及所请求 effort 中的每个 ticket。
   只有 context 准确标识一个 ticket set 时才推断省略的 effort；否则询问。
2. 在 controller context 中记录所有 identifiers、published order、statuses、claims、blocking edges
   和 acceptance criteria。标识具名本地 target checkout 和 branch。要求已接受的 local-delivery
   权限；target 或 outcome 仍有歧义时，在 tracker 或 Git mutation 前只询问一次。

准确选择一个入口路径：

- **新 Batch**：只纳入 agent-ready 工作；排除 completed、rejected、human-owned、
  information-blocked 和 claimed tickets。要求每个 blocker 解析为一个 selected ticket 或 completed
  external dependency，要求 graph 无环，并用 published order 打破 readiness 并列。从准确 target
  `HEAD` 调用 `create-worktree`，为完整 selected scope 创建一个
  Batch Worktree；把该 commit 和 tree 记录为 immutable batch base。
- **Delivery 前中断**：标识当前或明确提供的 Batch Worktree，并把它与 target 的唯一 merge base
  推导为 immutable base；要求 target 仍等于该 commit。纳入当前 tracker claims 已证明由此准确 Batch
  所有的 tickets，以及 requested effort 中其他 eligible tickets；排除归其他 owner 的 claims。重建并
  验证 graph，然后在 worktree 的 first-parent history 中逐个重放 completed boundary。要求恰好一个
  `SmartKit-Ticket: <canonical-id>` trailer 标识最早发布的 dependency-ready ticket；否则停止。
  把没有标记的 commit tail 和本地改动视为当前 ticket 的 recovery state。
- **Delivery 后中断**：要求当前 tracker evidence 表明此 Batch 仍有 unresolved claims 或只完成了部分
  Ticket Completion，并证明 target 包含已交付结果。对于保留的历史，从已交付 first-parent range
  重建 ticket boundaries。对于经 consolidation 收束的历史，要求唯一保留的 workflow recovery ref，其 reviewed tree
  等于 Batch Commit tree，并从该 ref 的 first-parent range 重建 boundaries。根据这些 boundaries
  重建并重放 graph，然后从 `complete-run.md` 的 Ticket Completion 进入，不创建 worktree、不派发
  worker、不重复 review，也不调用 `finish-worktree`。

任何入口路径在 worktree 或 delivery evidence、immutable base、selected scope、claim ownership、
graph、history 或本地状态 ownership 有歧义时停止。

Delivery 前，只有 selected graph、未变化 target、Batch Worktree、已授权本地 outcome 和第一个
dependency-ready ticket 都已建立时，运行才 ready。仍有 unfinished tickets 但没有 ready ticket 时，
报告 unresolved edges，并在不创建新 claim 的情况下进入 **停止和恢复**。

## 执行 Batch

只有 selected blocker 的 Ticket Commit 存在于 Batch Worktree 的 first-parent history 中，或 tracker
证明它在本次运行前已完成，该 blocker 才满足。

1. 仍有 selected ticket 未完成时，完整读取并执行
   [`references/process-one-ticket.md`](references/process-one-ticket.md)。它返回
   `completed-in-batch` 后，选择 blockers 已满足且 published 最早的 ticket 并重复。
2. 每个 selected ticket 都有已证明 Ticket Commit 后，完整读取并执行
   [`references/complete-run.md`](references/complete-run.md)。
3. 出现任何非 complete 结果、缺少 decision 或 invariant 失败时，完整读取并执行
   [`references/stop-and-recovery.md`](references/stop-and-recovery.md)。此 exit 优先于下一个 ticket
   和 completion。

只能通过 `complete-run.md` 中的 completion criterion 完成。
