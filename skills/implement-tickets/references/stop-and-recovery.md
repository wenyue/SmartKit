# Stop and Recovery

Enter whenever the main Skill routes a non-complete result here.

1. Preserve and report the Batch Worktree, target, claims, ticket boundaries, unmarked commit tail,
   local changes, branches, and recovery state, plus the exact failed operation and next owner.
2. Before Batch Delivery, use only the configured tracker's documented compare-and-set release in
   reverse dependency order. A missing safe operation or compare-and-set failure retains the
   remaining claims and stops release.
3. After Batch Delivery, retain unresolved claims and hand off the configured completion operation.
   Preserve the delivered commits and any recovery ref required to reconstruct consolidated ticket
   boundaries.
4. Perform no force operation, rebase, rollback, discard, or unconfigured tracker action without
   separate authorization.

This path exits `stopped` or `failed`; retained state and the handoff remain the recovery boundary.
