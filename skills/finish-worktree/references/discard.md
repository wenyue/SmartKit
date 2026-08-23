# Discard

Discard only the exact local isolated worktree and branch named by an explicit user request.

1. Show the resolved worktree path, source branch, owned commit range, publication state, and every
   commit not reachable from the base. Obtain confirmation unless the accepted request already
   names these exact targets and clearly authorizes their loss.
2. Require a clean source worktree and prove the branch is not checked out by another worktree. Stop
   when any dirty or untracked content, target identity, or lifecycle ownership is ambiguous.
3. Delegate removal of a host-created worktree to that host. For a Git-created worktree, remove only
   the exact recorded worktree; use safe branch deletion when its history is already integrated, or
   forced local branch deletion only when the confirmed discard necessarily abandons unmerged
   commits.
4. Verify the base checkout and all its local state remain unchanged and the exact local worktree
   and branch are gone.
5. Delete only workflow-owned recovery refs through expected-old-value checks. Retain and report
   any ref whose expected value or ownership does not match.
