# Explicit Discard

Discard only the exact worktree and observed losses covered by explicit authority. General cleanup
authority is insufficient. Keep the target and other owners' state outside the removal boundary.

## Match the grant to the actual loss

Establish physical registration, branch, HEAD, base, unique commits, publication, recovery refs,
ownership and every checkout using the branch. Inventory staged, unstaged, untracked and ignored
contents, including bytes or content identities, types, modes and symlink targets. Establish that
the unaffected target is unreachable by the removal and record the evidence needed to prove its
preservation afterward.

Reuse an existing grant covering these exact full contents and disclose the losses. Ask only about
material losses outside that grant. Changed observations need a fresh match against authority,
not an automatic repeat of an already settled decision. Unmerged work requires explicit abandonment
authority or proof that its result has been integrated.

## Remove within the observed boundary

Persist the [recovery receipt](recovery.md) before effects. Immediately before removal, refresh
identity and loss inventory; drift stops removal until its boundary is resolved. Use the host for a
host-created worktree, or ordinary Git removal for a Git-owned one. Force removal requires explicit
authority over the exact full loss it would cause.

Observe worktree removal before considering branch deletion. A branch must be absent from all
worktrees, and deletion must match its expected old OID. Treat each branch or recovery-ref deletion
as a separate effect. A mismatch retains the ref; an ambiguous result requires observation before
retry. Removal of one item never silently grants removal of another.

Prove the worktree is gone and the unaffected target's HEAD, complete index and local state are
preserved. History is inapplicable. The outcome is explicit discard; cleanup accounts for every
remaining ref and other lifecycle item. If later work fails, retain proven deletions and any
irreversible loss in the report, with residual locations and owners. Do not describe already lost
state as recoverable merely because another item was retained.
