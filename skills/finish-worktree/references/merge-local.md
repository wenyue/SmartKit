# Merge Locally

Advance the recorded local target branch to the verified delivery head. When the scope is
**Already Delivered**, recheck that the local target still points to the proven commit, perform only
cleanup authorized by this outcome, report the proof and preserved state, and stop.

1. Confirm the target checkout is on the recorded target branch. If any scope path overlaps staged,
   unstaged, or untracked target-local work in a way the merge could overwrite, leave both
   checkouts unchanged and offer return-for-review instead.
2. Require the recorded target `HEAD` to equal the Finalization Contract's `expected_head` and to
   be the delivery head's required history boundary. A moved target returns to **Finalize Reviewed
   History**.
3. Run `git merge --ff-only <source-branch>` from the target checkout.
4. Rerun relevant verification from the target checkout. Prove the target now points to the
   delivery head and every unrelated target-local change still matches its snapshot.
5. After verification passes, ask the recorded lifecycle owner to remove a host-created worktree.
   For a Git-created worktree, remove that exact clean worktree from the target checkout and delete
   the now-merged source branch with Git's safe branch deletion.

If fast-forward integration or post-merge verification fails, preserve the source branch,
worktree, and recovery refs and report the resulting target state. Do not rewrite or roll back the
target automatically.
