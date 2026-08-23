# Finalize History

Enter with a proven Finalization Contract and one reviewed source tree.

1. Refresh the target. Detect **Already Delivered** only through current ancestry or
   equivalent-change evidence plus required verification.
2. A moved target may be merged into the source branch only when accepted evidence determines
   conflict behavior. Inspect accepted behavior and both sides before invoking
   `resolving-merge-conflicts`. When evidence permits multiple results, restore pre-merge source
   state and request a decision. Synchronization invalidates review and returns the changed source
   to its implementation workflow for verification and formal review.
3. Require formal review of the accepted scope at the exact fixed point, source head, and tree,
   with no blocking finding.
4. For `preserve-commits`, require the target to be the parent boundary of the complete owned range;
   prove every preserved commit belongs to the accepted scope, the source is clean, and its head and
   tree equal the reviewed evidence. The source `HEAD` becomes the delivery head.
5. For `consolidate-checkpoints`, derive one commit message from the accepted scope and repository
   convention. Create a unique recovery ref and run
   `scripts/consolidate_worktree_history.py` against the exact target. Prove the resulting Delivery
   Commit has the target as its sole parent, a tree byte-identical to the reviewed source,
   successful hooks, and a clean source worktree. That commit becomes the delivery head.

Completion requires one proven delivery head or **Already Delivered**. Return the history policy,
owned source range, delivery head or Delivery Commit, tree, recovery data, and current target proof.
