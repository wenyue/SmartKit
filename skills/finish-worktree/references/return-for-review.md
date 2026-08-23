# Return for Review

Materialize the delivery head's net result in the target working tree without advancing its branch
or changing its index. When the scope is **Already Delivered**, recheck that the target still has no
scope diff, leave its working tree and index unchanged, retain the source branch and worktree as
review evidence, report the proof and preserved state, and stop.

1. Record the target `HEAD`, index tree, staged changes, unstaged changes, and untracked paths. Back
   up every scope path outside the repository and record original file types and absent paths in a
   manifest.
2. Derive the accepted result from the complete diff between the recorded target boundary and the
   delivery head's tree. For scope paths without target-local changes, check the transfer first,
   then update only the working tree
   through a mode that leaves the index unchanged.
3. For overlapping text paths, three-way merge the merge-base content, current base working file,
   and accepted result in temporary files. Treat a shared pathname alone as mergeable evidence, not a
   conflict.
4. Resolve only unambiguous, scope-owned, verifiable merges. Stop for delete/modify conflicts,
   complex renames, binary conflicts, mutually exclusive behavior, ambiguous generated output, or
   any result that cannot be verified. Regenerate generated files from source only when the project
   provides a deterministic generator and that mutation is separately authorized.
5. Run only known non-mutating checks in the target checkout. When adequate checks are unavailable,
   report the limitation instead of running a formatter, generator, or fixer.
6. Prove the recorded target `HEAD` and index tree are unchanged, original staged state is preserved,
   merged files contain both compatible local and accepted work, and returned scope changes are unstaged
   or untracked.
7. Keep the source branch, worktree, and external backup. Report their locations so the source and
   recovery data remain independently inspectable until the user accepts the review result.

If transfer fails before a complete result exists, restore only touched paths from the external
backup. If verification fails after transfer, preserve the returned result and all recovery data
for manual review.
