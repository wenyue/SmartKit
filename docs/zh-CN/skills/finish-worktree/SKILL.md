---
name: finish-worktree
description: 通过包含 verified history、delivery、recovery 和 cleanup 的闭合契约，finalize 一个隔离的 linked Git worktree。
---

# 完成 Worktree

此 Procedure-led Skill 在保留 recovery data 和无关本地状态的同时，finalize 一个隔离 worktree。它
验证 evidence，应用一个 history policy，执行一个 authorized outcome，验证结果，并执行 owned
cleanup。调用方仍负责 implementation、formal review、ticket dependencies、tracker state 和 Issue
completion。

## 路由显式 Discard

只有收到单独的显式 destructive instruction 后，才读取并执行
[`references/discard.md`](references/discard.md)，不接受 Finalization Contract，也不 finalize history。

## 建立完成 Context

读取并应用 [`references/finalization-contract.md`](references/finalization-contract.md)。只有 common
contract 和 current-state proof 通过后才继续。

## Finalize Reviewed History

完整读取并执行 [`references/finalize-history.md`](references/finalize-history.md)。只有得到其已证明的
delivery head 或 **Already Delivered** 结果后才继续。

## 执行一个 Outcome

只读取由 `authorized_outcome` 选定的 procedure：

| Outcome | 完整读取 |
| --- | --- |
| `merge-locally` | [`references/merge-local.md`](references/merge-local.md) |
| `create-pull-request` | [`references/create-pull-request.md`](references/create-pull-request.md) |
| `keep-for-later` | [`references/keep-for-later.md`](references/keep-for-later.md) |
| `return-for-review` | [`references/return-for-review.md`](references/return-for-review.md) |

## 安全与恢复

- rewrite history 或改变 target working state 前创建 recovery data。只恢复 failed mutation 所有的
  状态；保留 ownership 未证明的每项状态。
- 不在 source 或 target branch 上使用 pull、stash、hard reset、clean、force push、rebase 或 merge
  commit。只 rewrite 已授权 consolidation 的完整 unpublished history range。
- 把 host-created worktree cleanup 委托给其 host；只有已证明 creation ownership 和 contract
  authority 时，才移除 Git-created worktree 或 branch。

## 结果

返回 `status`（`complete`、`stopped` 或 `failed`）、history policy、authorized outcome、source 和
target mutation 前后的 identities、final tree 的 evidence 和 verification、保留或删除的 recovery
refs、保留/移除的 worktrees 和 branches、`next_owner` 及准确 next action。非 complete 结果还包含
failed phase、mismatch 或 error，以及保留的 recovery state。选定的 outcome reference 提供其
delivery 和 handoff 字段。
