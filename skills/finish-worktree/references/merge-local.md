# Merge Locally

Deliver the accepted result by fast-forwarding one authorized local target branch.

Identify the target checkout, branch and expected HEAD. Use [history preparation](history.md) to
establish a scope-owned delivery commit with its accepted-state evidence. The target must be its
ancestor. Divergence returns to the implementation workflow for synchronization and acceptance under
that evidence contract. This route never rebases, pulls, creates a merge commit, or substitutes a
transfer.

Determine the fast-forward write set. A dirty target is eligible only when its local state is
outside that set and before/after evidence can prove its preservation; otherwise retain both
checkouts and stop. Capture affected files, complete index evidence, refs and relevant Git state,
including ignored or untracked material an update could reach. Coordinate with other writers.

Recheck target identity and HEAD just before the effect. If movement occurs after history has been
proven, retain `history_result` and stop for the target-movement owner unless current evidence
proves **Already Delivered**. For that case, record the authoritative proof and make no integration
write. Otherwise create an authorized unique recovery ref at the old target OID through an
expected-absent update, record it, and run from the target checkout:

```text
git merge --ff-only <exact-delivery-oid>
```

Observe the actual result even when Git reports failure or the call is interrupted. Prove the target
branch now points to the delivery commit, the tree is the accepted tree, required target
verification passes, affected files match the intended update, and unrelated index, working,
untracked and ignored state is preserved. Only that proof establishes `outcome_result: proven` and
`classification: authoritative delivery`. An ambiguous result goes to [recovery](recovery.md); never
rerun the merge based only on a missing success response.

Proceed to authorized cleanup or retention. Keep the source and recovery ref until their lifecycle
owners release them; preserve delivery proof if cleanup fails.
