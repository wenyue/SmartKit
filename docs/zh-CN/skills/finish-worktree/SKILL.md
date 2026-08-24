---
name: finish-worktree
description: 通过包含已验证的历史、交付、恢复和清理的闭合契约，完成收尾一个隔离的关联的 Git 工作树。
---

# 完成 Worktree

此流程主导型技能在保留恢复 data 和无关本地状态的同时，完成收尾一个隔离工作树。它
验证证据，应用一个历史政策，执行一个已授权的结果，验证结果，并执行自有的
清理。调用方仍负责实施、formal 审查、工单 dependencies、跟踪器状态和 Issue
完成。

## 路由显式 Discard

只有收到单独的显式 destructive instruction 后，才读取并执行
[`references/discard.md`](references/discard.md)，不接受收尾契约，也不完成收尾历史。

## 建立完成 Context

读取并应用 [`references/finalization-contract.md`](references/finalization-contract.md)。只有 common
契约和 current-state 证明通过后才继续。

## Finalize Reviewed History

完整读取并执行 [`references/finalize-history.md`](references/finalize-history.md)。只有得到其已证明的
交付提交头或**已交付**结果后才继续。

## 执行一个 Outcome

只读取由 `authorized_outcome` 选定的 procedure：

| Outcome | 完整读取 |
| --- | --- |
| `merge-locally` | [`references/merge-local.md`](references/merge-local.md) |
| `create-pull-request` | [`references/create-pull-request.md`](references/create-pull-request.md) |
| `keep-for-later` | [`references/keep-for-later.md`](references/keep-for-later.md) |
| `return-for-review` | [`references/return-for-review.md`](references/return-for-review.md) |

## 安全与恢复

- rewrite 历史或改变目标工作状态前创建恢复 data。只恢复失败修改所有的
  状态；保留归属未证明的每项状态。
- 不在源或目标分支上使用拉取、stash、hard reset、clean、强制 push、rebase 或合并
  提交。只 rewrite 已授权合并的完整 unpublished 历史范围。
- 把 host-created 工作树清理委托给其智能体宿主；只有已证明 creation 归属和契约
  authority 时，才移除 Git-created 工作树或分支。

## 结果

返回 `status`（`complete`、`stopped` 或 `failed`）、历史政策、已授权的结果、源和
目标修改前后的 identities、final 树的证据和验证、保留或删除的恢复
引用、保留/移除的工作树和分支、`next_owner` 及准确下一个操作。非完成结果还包含
失败 phase、不匹配或 error，以及保留的恢复状态。选定的结果 reference 提供其
交付和交接字段。
