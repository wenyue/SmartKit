# Complete the Run

Enter before delivery only after every selected ticket has one proven Ticket Commit in the Batch
Worktree's first-parent history. A post-delivery recovery enters at step 5 only after the main Skill
has reconstructed the same ordered boundaries and proven Batch Delivery.

1. Run full verification and invoke `code-review` using the immutable batch base as the fixed point
   and the complete Spec and selected tickets as acceptance sources.
2. Address blocking findings as Checkpoint Commits in the same Batch Worktree. After every
   correction, rerun full verification and the same whole-batch review. Continue only when both
   gates pass for the same final `HEAD` and tree; an unresolved finding or failed gate enters
   **Stop and Recovery**.
3. Invoke `finish-worktree` once in the controller's Agent context with a complete generic
   Finalization Contract derived from current evidence. Supply no mode. Bind the selected
   `preserve-commits` or `consolidate-checkpoints` policy to the complete batch-owned range from the
   immutable base through the reviewed `HEAD`, and select the locally authorized outcome without
   adding tracker data. For consolidation, retain the workflow-owned recovery ref at the reviewed
   Batch Worktree head until every Ticket Completion and claim removal is proven.
4. Independently prove the exact selected outcome and target verification. For
   `consolidate-checkpoints`, require one Batch Commit with the immutable base as its sole parent and
   a tree equal to the reviewed Batch Worktree. For `preserve-commits`, require the delivery head and
   complete owned range to remain unchanged. Any mismatch enters **Stop and Recovery**.
5. Only after Batch Delivery proof, complete tracker tickets in dependency order. On one transition
   failure, retain later claims and enter **Stop and Recovery** without rolling back delivery or
   changing a later ticket.
6. After every Ticket Completion and claim removal succeeds, delete the retained workflow-owned
   recovery ref through an expected-old-value check and perform the remaining authorized Git
   cleanup. A mismatch retains the ref and fails cleanup.

Complete only when Batch Delivery, every Ticket Completion, claim removal, and authorized Git
cleanup are proven. A successful `return-for-review`, `keep-for-later`, or `create-pull-request`
outcome returns that exact handoff without Ticket Completion. Report the selected order, immutable
base, target and batch branches, workers, Ticket Commits, whole-batch review and verification,
final history policy, retained and deleted recovery refs, tracker transitions, cleanup, and
exclusions.
