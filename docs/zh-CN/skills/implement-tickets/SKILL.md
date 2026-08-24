---
name: implement-tickets
description: 在一个隔离工作树中依次实施剩余智能体就绪工单，在 Git 历史中标记可恢复的工单边界，然后整批审查并只收尾一次。
---

# 实施 Tickets

此流程主导型技能在一个批次工作树中把一个工单批次作为依赖有序 pipeline 运行。
控制器负责工单选择、归属声明、执行智能体交接、批次证据、收尾和跟踪器
完成。每个新的执行智能体负责共享顺序历史中一个工单的改动；同一时间只能有一个执行智能体
使用批次工作树。

## 建立运行

1. 读取已配置 issue-tracker 指令、引用的 Spec 或 parent 源，以及所请求 effort 中的每个工单。
   只有上下文准确标识一个工单 set 时才推断省略的 effort；否则询问。
2. 在控制器上下文中记录所有 identifiers、已发布顺序、statuses、归属声明、blocking edges
   和验收条件。标识具名本地目标检出目录和分支。要求已接受的 local-delivery
   权限；目标或结果仍有歧义时，在跟踪器或 Git 修改前只询问一次。

准确选择一个入口路径：

- **新 Batch**：只纳入智能体就绪工作；排除已完成、已拒绝、人工负责、
  information-blocked 和 claimed 工单。要求每个阻塞问题解析为一个选定的工单或已完成
  外部 dependency，要求图无环，并用已发布顺序打破就绪并列。从准确目标
  `HEAD` 调用 `create-worktree`，为完整选定的范围创建一个
  批次工作树；把该提交和树记录为不可变的批次基点。
- **Delivery 前中断**：标识当前或明确提供的批次工作树，并把它与目标的唯一合并基点
  推导为不可变的基点；要求目标仍等于该提交。纳入当前跟踪器归属声明已证明由此准确 Batch
  所有的工单，以及 requested effort 中其他 eligible 工单；排除归其他归属的归属声明。重建并
  验证图，然后在工作树的第一父提交历史中逐个重放已完成边界。要求恰好一个
  `SmartKit-Ticket: <canonical-id>` trailer 标识最早发布的 dependency-ready 工单；否则停止。
  把没有标记的提交 tail 和本地改动视为当前工单的恢复状态。
- **Delivery 后中断**：要求当前跟踪器证据表明此 Batch 仍有未解决的归属声明或只完成了部分
  工单完成，并证明目标包含已交付结果。对于保留的历史，从已交付第一父提交范围
  重建工单边界。对于经合并收束的历史，要求唯一保留的工作流恢复引用，其已审查的树
  等于批次提交树，并从该引用的第一父提交范围重建边界。根据这些边界
  重建并重放图，然后从 `complete-run.md` 的工单完成进入，不创建工作树、不派发
  执行智能体、不重复审查，也不调用 `finish-worktree`。

任何入口路径在工作树或交付证据、不可变的基点、选定的范围、归属声明归属、
图、历史或本地状态归属有歧义时停止。

Delivery 前，只有选定的图、未变化目标、批次工作树、已授权本地结果和第一个
dependency-ready 工单都已建立时，运行才就绪。仍有 unfinished 工单但没有就绪工单时，
报告未解决的 edges，并在不创建新归属声明的情况下进入**停止和恢复**。

## 执行 Batch

只有选定的阻塞问题的工单提交存在于批次工作树的第一父提交历史中，或跟踪器
证明它在本次运行前已完成，该阻塞问题才满足。

1. 仍有选定的工单未完成时，完整读取并执行
   [`references/process-one-ticket.md`](references/process-one-ticket.md)。它返回
   `completed-in-batch` 后，选择阻塞问题已满足且已发布最早的工单并重复。
2. 每个选定的工单都有已证明工单提交后，完整读取并执行
   [`references/complete-run.md`](references/complete-run.md)。
3. 出现任何非完成结果、缺少决定或 invariant 失败时，完整读取并执行
   [`references/stop-and-recovery.md`](references/stop-and-recovery.md)。此 exit 优先于下一个工单
   和完成。

只能通过 `complete-run.md` 中的完成 criterion 完成。
