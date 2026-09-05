# Explicit Discard

Remove one exact isolated worktree and only the observed losses the user has authorized. General
cleanup or incomplete finalization authority is insufficient to authorize loss.

Identify the registered physical worktree, branch, HEAD, base and unique commits, publication and
recovery refs, lifecycle owner, and every checkout using the branch. Inventory staged, unstaged,
untracked and ignored contents that removal could lose, including bytes or content identity, file
type, mode and symlink target. Prove the removal cannot reach the unaffected target checkout and
capture preservation evidence there.

Match the accepted request to that inventory. Existing explicit authority covering the exact
worktree and all its local contents need not be requested again; disclose the observed losses.
Ask only when a material loss, branch/ref deletion, or owner lies outside that authority. New or
changed losses require a fresh match to authority before deletion, not automatic reconfirmation of
an unchanged request. Unmerged commits require express abandonment authority or integration proof.

Read [recovery](recovery.md) and record the external receipt before removal. Recheck the loss
inventory and target identity immediately before each effect. Drift stops. The host removes a
host-created worktree. For a Git-created worktree use ordinary removal when possible; forced removal
is eligible only when existing explicit loss authority covers everything it would destroy.

Observe removal before deleting a branch. A branch must be absent from every worktree and may be
deleted only through an expected-old-OID update. Treat branch deletion and each separately authorized
owned recovery-ref deletion as separate effects; retain refs on mismatch. Never repeat ambiguous
removal based only on an interrupted response.

Prove the authorized items are gone and the unaffected target's HEAD, index and local state are
preserved. Return `history_result: inapplicable`, the discard `outcome_result`, and a `cleanup_result`
covering branch and recovery-item disposition. Proven discard is `classification: explicit discard`;
retain earlier proven deletions and report residuals and irreversibility when later work fails.
