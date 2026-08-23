---
name: finish-worktree
description: Finalize one isolated linked Git worktree through a closed contract with verified history, delivery, recovery, and cleanup.
---

# Finish Worktree

This Procedure-led Skill finalizes one isolated worktree while preserving recovery data and
unrelated local state. It validates evidence, applies one history policy, executes one authorized
outcome, verifies the result, and performs owned cleanup. Callers retain implementation, formal
review, ticket dependencies, tracker state, and Issue completion.

## Route Explicit Discard

Only after a separate explicit destructive instruction, read and execute
[`references/discard.md`](references/discard.md) without accepting a Finalization Contract or
finalizing history.

## Establish Completion Context

Read and apply [`references/finalization-contract.md`](references/finalization-contract.md).
Continue only when the common contract and current-state proof pass.

## Finalize Reviewed History

Read and execute [`references/finalize-history.md`](references/finalize-history.md) completely.
Continue only with its proven delivery head or **Already Delivered** result.

## Execute One Outcome

Read only the procedure selected by `authorized_outcome`:

| Outcome | Read completely |
| --- | --- |
| `merge-locally` | [`references/merge-local.md`](references/merge-local.md) |
| `create-pull-request` | [`references/create-pull-request.md`](references/create-pull-request.md) |
| `keep-for-later` | [`references/keep-for-later.md`](references/keep-for-later.md) |
| `return-for-review` | [`references/return-for-review.md`](references/return-for-review.md) |

## Safety and Recovery

- Create recovery data before rewriting history or changing target working state. Restore only
  state owned by the failed mutation; preserve every state item whose ownership is unproven.
- Use no pull, stash, hard reset, clean, force push, rebase, or merge commit on a source or target
  branch. Rewrite only the complete unpublished history range authorized for consolidation.
- Delegate host-created worktree cleanup to its host; remove a Git-created worktree or branch only
  with proven creation ownership and contract authority.

## Result

Return `status` (`complete`, `stopped`, or `failed`), history policy, authorized outcome, source and
target identities before and after, evidence and verification for the final tree, retained or
deleted recovery refs,
retained/removed worktrees and branches, `next_owner`, and exact next action. A non-complete result
also includes the failed phase, mismatch or error, and preserved recovery state. The selected
outcome reference supplies its delivery and handoff fields.
