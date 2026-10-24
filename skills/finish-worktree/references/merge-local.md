# Merge Locally

## Establish a safe fast-forward

Read [History Preparation](history.md). If the authorized local target already contains the complete accepted result, verify and report that delivery without writing again. Otherwise its HEAD must be an ancestor of the accepted commit: this route is fast-forward only. Return divergence to the implementation workflow for synchronization and renewed acceptance.

Identify the physical target checkout and branch and the files the fast-forward can affect. A dirty target is eligible only when its local changes are disjoint and their preservation can be verified. Capture the affected files, complete index, relevant refs and any untracked or ignored state the operation could reach. Coordinate writers and recheck target identity and HEAD immediately before integration. If the target moved, reassess rather than merging against stale observations.

## Integrate once and verify the target

Retain the old target under an authorized, unique, expected-absent recovery ref, then run in the target checkout:

```text
git merge --ff-only <exact-accepted-oid>
```

Observe the target even after failure or a missing response. Verify its branch points to the accepted commit, its tree and affected files match, required target checks pass, and unrelated index entries, working files, untracked and ignored state remain preserved. A timeout alone does not justify repeating the merge.

Report delivery only after those checks. Retain the source and recovery ref while needed for continuation or recovery; remove them only under the entry's cleanup conditions. If cleanup fails, report the completed delivery separately so the next action is cleanup, not another integration.
