# 处理一个 Ticket

进入时应有选定的 dependency-ready ticket、准确的当前 Batch Worktree 和 controller 当前 ticket
graph。此路径只有一个 `completed-in-batch` exit；其他结果都进入主 Skill 中的 **停止和恢复**。

## Claim 并 Handoff

1. claim 前立即重新读取 ticket 及其 blockers。status、requirement 或 edge 有实质变化时停止。
2. 使用已配置 tracker 记录的 compare-and-set Ticket Batch claim 和 Ticket Commit proof。记录 prior
   state 和 claim；没有记录安全 claim operation 时停止。
3. 记录 Batch Worktree path、branch、准确 `HEAD`、tree、immutable base、clean 或归属明确的 recovery
   state，并把 selected ticket 作为其唯一当前 scope。另一个 worker 仍拥有该 worktree 或较早 ticket
   有 unresolved state 时停止。

## 派发一个 Worker

启动一个 fresh write-capable worker Agent，并提供一个完整 handoff：

- `ticket`：canonical identifier、完整 contract、acceptance sources 和 blocker proof；
- `batch`：worktree、branch、准确 `head` 和 `tree`、immutable base 和 controller identity；
- `history`：既有 ticket boundaries、当前 ticket base、准确的
  `SmartKit-Ticket: <canonical-id>` completion trailer 和 worker commit authority；
- `verification`：focused 和 repository-required commands；
- `tracker_boundary`：worker 不执行 claim、release、completion 或其他 tracker transition。

worker 在其现有 Agent context 中执行此完整生命周期：

1. 复核提供的 Batch Worktree、ticket base、prior ticket boundaries、ownership 和本地状态。只在该
   Batch Worktree 中工作，并且只处理此 ticket。
2. 建立当前 mechanism 和 seams，只实施该 ticket；behavior 有 testable seam 时使用 `tdd`；通过正常
   commit workflow 创建任何有用且可恢复的 Checkpoint Commits。
3. 实施期间运行 focused verification，并在最后运行每个 repository-required check。
4. 根据 acceptance criteria self-review 完整 ticket diff，并修正每个 observed mismatch。worker 不调用
   正式 `code-review`。
5. 结束时 worktree 必须 clean，并有一个最终、通过 hooks 验证且准确包含所提供 completion trailer 的
   Ticket Commit。该 ticket 可以有之前的 Checkpoint Commits。没有剩余内容可 commit 时，创建一个
   通过 hooks 验证的 empty Ticket Commit，不重写另一个 ticket 的历史。
6. 返回准确 Ticket Commit、ticket 和 worker identities、当前 Batch Worktree head 和 tree、
   verification 与 self-review evidence。

Ticket Commit 得到证明前的任何阶段出现非 complete 结果或缺少 decision 时，返回一个 structured
Worker Recovery Handoff，其中包含：

- `status`（`stopped` 或 `failed`）、ticket 和 worker identities、`completed_phase` 和
  `failed_phase`；
- Batch Worktree path、branch、immutable base、ticket base、`HEAD`、tree 和归属明确的本地状态 facts；
- 准确的当前 ticket Checkpoint Commit range、trees、publication facts 和 uncommitted state；
- 每个 verification command、result 及关联 `HEAD` 和 tree，加上 self-review evidence 和 unresolved
  findings；
- 每个 retained branch、commit、recovery ref 和其他有用 recovery state；
- 准确 blocker、mismatch、error 或缺少的 decision；
- `next_owner` 和准确 next action。

保留所有已报告 Git 和 recovery state。controller 在进入 **停止和恢复** 前，不替换 worker，也不处理
另一个 ticket。

## 验证 Ticket 边界

1. 要求完整 worker result，并独立验证 worker 与 ticket mapping、准确 trailer、commit ancestry、
   evidence、clean Batch Worktree，以及 supplied ticket base 之后的每个 commit 都属于此 ticket。
   任何 mismatch 都进入 **停止和恢复**。
2. 保持 ticket claimed。已证明的 Ticket Commit 可以在本次运行中解锁 dependants，但它既不是 Batch
   Delivery，也不是 Ticket Completion。
3. 重新读取 selected contracts。实质 contract change 进入 **停止和恢复**；否则向主 Skill 返回
   `completed-in-batch` exit。
