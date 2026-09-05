# Empty Differences and Batch Repairs

Use these branches when a ticket requires no code change, the final batch diff is empty, or final
verification/review requires repair. All other nonempty candidates use public `code-review` as
specified in the main workflow. Its empty-diff rejection is not a review pass.

## Independently accept an empty difference

Freeze the exact implementation state, comparison base and complete accepted requirements with
source provenance. Prove there is no omitted task change in the index or working tree. Supply two
independent read-only reviewing roles, **Standards** and **Spec**, with the relevant existing
implementation, all accepted requirements, applicable standards (including the public review
owner's smell-baseline treatment), and verification evidence. They must be independent of the
implementation Worker and each other and may run in parallel in the same environment.

Require affirmative evidence of fulfillment for every requirement, Standards coverage of the
relevant implementation, and explicit results from both roles bound to that exact state. Absence
of edits, a skipped axis, unsupported assumptions, or earlier Worker claims cannot establish
acceptance. Missing inputs or unavailable independent roles stop. Ordinary findings return to the
implementation owner for repair; a resulting nonempty diff requires public `code-review`.

For **one ticket**, prove its accepted behavior was already satisfied at `ticket_base`. After both
roles pass, the Controller authorizes the Worker to create one normal-hook empty commit with the
canonical ticket reference and sole `SmartKit-Ticket: <canonical-id>` trailer. If repair already
produced an unaccepted candidate for this ticket, amend that same unpublished candidate into the
empty ticket commit instead of appending a second commit. Verify its sole parent is `ticket_base`,
its tree equals that base, relevant evidence/checks still apply, and all
remaining [ticket acceptance predicates](process-one-ticket.md#accept-the-ticket-commit) hold.
Rerun commit/hook-sensitive checks. Hook-created content changes exit this branch: keep the ticket
incomplete, remove the premature completion marker in the supported repair, and use the normal
candidate/check/public-review/marker sequence. The empty commit alone never closes the ticket.

For **the final batch**, apply the same independent requirement-based acceptance to the final
implementation and all selected requirements after whole-batch verification. This covers both
all-no-change tickets and changed tickets whose combined diff is empty. Preserve individual ticket
commits and examine conflicting requirements, interactions and regressions; cancellation of changes
is not fulfillment evidence. The resulting full reports are the final review evidence for
`complete-run.md`, subject to the finalizer's independent authoritative-target delivery proof.

## Repair the whole batch

Retain the failed immutable state, all blocking required-check or review findings, and accepted
ticket commits. Freeze `repair_base` at the current accepted HEAD and dispatch a fresh batch-repair
Worker through [Worker boundary](worker-transaction.md) with the complete batch scope, sources,
findings, prior evidence, and exact repair authority. This Worker owns only the current repair.

After targeted checks, create one separate normal-hook repair candidate with `repair_base` as sole
parent and no ticket completion trailer. Pause writes, verify its entire intended result is
committed and the worktree is clean, then replay required whole-batch verification and both
independent review axes from immutable `batch_base`. Use public `code-review` for a nonempty batch
diff and the empty-diff branch above otherwise. Prior reports provide context, never a substitute
for full coverage of the repaired batch.

Return ordinary findings to this same Worker. It amends only its current unpublished, unaccepted
repair candidate through normal hooks, then pauses for renewed verification and both review axes.
Only a complete passing barrier resolves the findings. The Controller independently verifies the
repair's parent and sole-commit range, scope, unchanged accepted ticket boundaries, absent ticket
trailer, clean state, Worker quiescence, source freshness, and exact evidence binding before
accepting the repaired batch.

Keep all previously accepted ticket and repair commits unchanged. A later repair after batch
acceptance appends a new repair candidate with a fresh Worker and its own acceptance cycle. A
material blocker or no-progress repair pauses through [Pause and resume](resume.md), retaining the
current candidate and partial files; never roll back accepted history or run a later phase to bypass
the failed barrier.
