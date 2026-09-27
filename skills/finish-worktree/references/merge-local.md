# Merge Locally

Place the accepted result on one authorized local target branch. Consume [History Preparation](history.md)
first. Its **Already Delivered** proof can establish delivery without a write; otherwise the target
must be an ancestor of the exact accepted delivery commit so integration is fast-forward only.
Divergence goes to the implementation owner for synchronization and renewed acceptance. This route
does not substitute rebase, pull, a merge commit or file transfer.

## Establish what the fast-forward can affect

Identify the physical target checkout and branch, then derive the fast-forward write set. A dirty
target is eligible when its local state is disjoint and preservation can be proved. Otherwise retain
it and stop before effects. Capture affected files, complete index, relevant refs and any ignored or
untracked state the Git operation could reach. Coordinate writers over that boundary.

Immediately before integration, recheck target identity and HEAD. Movement after history proof
leaves that history result intact but stops the outcome for the target-movement owner, unless
current **Already Delivered** evidence proves no write is needed.

## Integrate and prove delivery

Record the effect in the [external receipt](recovery.md). Create an authorized, unique,
expected-absent recovery ref for the old target, then run from the target checkout:

```text
git merge --ff-only <exact-delivery-oid>
```

Observe the target even if the command fails or its response is interrupted. Proof requires its
branch at the delivery OID, the accepted tree, required target verification and intended affected
files, with unrelated index, working, untracked and ignored state preserved. An ambiguous result
enters recovery; a timeout alone never justifies repeating integration.

This proof establishes authoritative delivery. Retain the source and recovery ref until their
owners release them. A later cleanup failure keeps the proven delivery classification, so the
caller can act on delivery without integrating again.
