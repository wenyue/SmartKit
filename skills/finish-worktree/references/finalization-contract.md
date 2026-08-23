# Finalization Contract

Accept exactly one closed contract. It supplies:

- `source` worktree, branch, exact base, `head` and `tree`, `creation_owner`, and `scope_owner`;
- `target` checkout, branch, `expected_head`, and `target_policy`;
- `evidence` fixed point, acceptance sources, review kind and result, reviewed head and tree,
  verification commands and results, and findings;
- `history_policy` equal to `consolidate-checkpoints` or `preserve-commits`, with its complete
  owned range;
- recovery refs and current and next owners;
- authorized cleanup and retained state; and
- one `authorized_outcome` equal to `merge-locally`, `create-pull-request`, `keep-for-later`, or
  `return-for-review`.

Reject unknown policies or outcomes, missing values, tracker data, and implicit remote authority.

## Prove Current State

Re-derive every named Git identity, clean owned state, ancestry, range, publication, evidence,
recovery fact, and owner. Snapshot each affected checkout's branch, `HEAD`, index tree, staged,
unstaged, and untracked state. Immediately before every mutation, recheck the facts it depends on.
Stop on stale, ambiguous, published, or unrelated state.

The contract passes only when the exact source and target, complete owned history, current evidence,
authorized recovery and cleanup, and preserved unrelated state are proven.
