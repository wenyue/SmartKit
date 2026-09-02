# Explicit Discard

This destructive route is not finalization. Enter only when the user explicitly authorizes loss of
one exact isolated worktree and its exact local state.

1. Resolve and display the registered worktree path, branch, base, `HEAD`, complete unique commit
   range, staged/unstaged/untracked inventory, publication, recovery refs, creation owner, and every
   other worktree using the branch. Snapshot the unaffected target checkout and local state.
2. Match the authority to the observed loss. It must explicitly cover every unpublished commit,
   dirty or untracked item, worktree, branch, and recovery ref that would be removed. If the request
   does not already name the exact targets and loss, obtain confirmation. Any later state change
   invalidates that authority and exits `stopped`.
3. A host-created worktree is removed by its host under one reported logical attempt. For a
   Git-created worktree, recheck the complete
   inventory and ownership immediately before removing that exact path. Use ordinary removal when
   clean; use forced worktree removal only when the confirmed authority covers the inventoried dirty
   state. Worktree removal is one logical attempt. After proving the branch is absent from every
   worktree, delete its exact ref as a separate logical attempt only through an expected-old-OID
   compare-and-swap. Require integration proof for ordinary discard, or express authority
   abandoning the proven unmerged commits; neither permits an unconditional branch deletion.
4. Delete each workflow-owned recovery ref as its own logical attempt only when separately
   authorized and only through an expected-old-value check. Retain mismatched or unowned refs.
5. Prove the exact authorized worktree and branch are gone and the target checkout, all unrelated
   refs, and all unrelated local state match their snapshots.

Re-observe every attempt. An interrupted or ambiguous effect is not retried; retain its observed
residual state for the effect owner. Commands within worktree removal and ref deletion are child
effects rather than additional attempts.

Return `history_result: inapplicable`, an `outcome_result` for explicit discard, and a
`cleanup_result` covering branch and recovery-ref disposition. Bind overall `complete`, `stopped`,
or `failed` to the active terminal attempt while preserving every earlier proven deletion. Include
the exact discarded objects, retained refs or paths, irreversibility, residual state, and next
owner/action. Never reinterpret incomplete finalization authority or a general cleanup request as
discard authority.
