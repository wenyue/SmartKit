# Explicit Discard

Discard is a separate destructive route, not finalization. Enter only when the user explicitly
authorizes losing one exact isolated worktree and its observed local state.

1. Resolve and display the registered worktree path, branch, base, `HEAD`, complete unique commit
   range, publication, recovery refs, current lifecycle and cleanup owners, and every other worktree
   using the branch. Record complete index entries and blob OIDs for each staged path. Separately
   inventory every tracked-unstaged, untracked, and ignored item by path, status, file type, mode,
   applicable symlink target, content hash, and size. Prove deletion cannot address the unaffected
   target checkout; retain the object, index, ref, and bounded status evidence needed to detect an
   unexpected effect there.
2. Match authority to the observed loss. It must expressly cover every unpublished commit, staged,
   unstaged, untracked, or ignored item, worktree, branch, and recovery ref that removal would lose.
   If the request does not already name those exact targets and losses, obtain confirmation. Any
   later state change invalidates that authority and ends `stopped`.
3. Immediately before deletion, recheck the complete loss inventory, lifecycle and cleanup owners,
   and exact authority for every loss. Drift stops before deletion. A host-created worktree must be
   removed by its host under one reported logical attempt. For a Git-created worktree, use ordinary
   removal when clean; use forced worktree removal only when confirmed authority covers every
   inventoried item ordinary removal would reject or destroy. Worktree removal is one logical
   attempt. Only after proving the branch absent from every worktree may its exact ref be deleted as
   a separate logical attempt, through an expected-old-OID compare-and-swap. Require integration
   proof for ordinary discard or express authority abandoning the proven unmerged commits. Neither
   permits unconditional branch deletion.
4. Delete each workflow-owned recovery ref as its own logical attempt only when separately
   authorized and only through an expected-old-value check. Retain mismatched or unowned refs.
5. Prove the exact authorized worktree and branch are gone, relevant target object, index, and ref
   identities are unchanged, and bounded target status evidence shows no unexpected effect.

Re-observe every attempt. Never retry an interrupted or ambiguous effect; retain its observed
residual state for the effect owner. Commands within worktree removal or ref deletion remain child
effects, not additional attempts.

Return `history_result: inapplicable`, an explicit-discard `outcome_result`, and a `cleanup_result`
covering branch and recovery-ref disposition. Apply the main Skill's phase states and classification
while preserving every earlier proven deletion. Include exact discarded objects, retained refs or
paths, irreversibility, residual state, and next owner/action. Incomplete finalization authority or
a general cleanup request never becomes discard authority.
