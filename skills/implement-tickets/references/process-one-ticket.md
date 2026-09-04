# Process One Ticket

Enter with one frozen dependency-ready ticket and exclusive control of the current Batch Worktree.
The only successful result is `completed-in-batch`: one independently proven first-parent Ticket
Commit for this unit. The worker attempts the unit; this reference owns its acceptance.

## Establish and run the unit

Re-observe the ticket, its complete sources, status, claim, and blockers through
[`tracker.md`](tracker.md). Consume a proven initial claim from the frozen claim plan when one
exists. Otherwise, before a tracker-authorized just-in-time claim, require
[`worker-transaction.md`](worker-transaction.md)'s non-mutating qualification only when a later
dispatch failure could strand that claim under the tracker-owned lifecycle, then use the documented
claim operation. A missing, stale, or incompatible claim route stops before mutation. For a
no-claim route, proceed only from its current tracker-owned proof.

Freeze `ticket_base` as the current `HEAD` and tree, or on resume reconstruct it and account for
every later first-parent commit and local-state item as this ticket's recovery state. Mixed or
ambiguous ownership stops.

Give [`worker-transaction.md`](worker-transaction.md) one Ticket Unit containing the canonical
ticket and sources, blocker proof, Batch Worktree and immutable Batch base, `ticket_base`, earlier
Ticket Commits, current owned state, scoped write and commit authority, and repository validation.
Its success predicate requires:

- the complete ticket sources are satisfied and every changed item belongs to this ticket;
- targeted checks sufficient to catch failures that would make the ticket unsafe to commit or
  contaminate later Batch work pass, with any deferred noncritical coverage recorded for the
  whole-Batch barrier;
- the final worktree is clean; and
- the first-parent range after `ticket_base` ends in exactly one Ticket Commit with exactly the
  canonical trailer, while every preceding Checkpoint has no ticket trailer. The Ticket Commit may
  be empty only when independent comparison proves zero ticket-owned net change and the complete
  accepted behavior was already satisfied at `ticket_base`, including through earlier selected
  boundaries. Do not create a Checkpoint to manufacture that case.

**Complete when:** the current ticket, base, owned state, claim disposition, worker authority, and
success predicate are exact.

## Prove the Ticket Commit

Consume the worker transaction's returned or recovered result without rewriting its status.
Independently verify the worker is quiescent, all commits and local state after `ticket_base` belong
to this unit, the targeted checks cover the final `HEAD` and tree, the worktree is clean, the
target/base remains valid, and the sole Ticket Commit and trailer are exact. Re-observe the ticket
and blockers before accepting it. Accept the worker's ticket-source evidence when it is attributable
to that immutable state; investigate only contradictions, gaps material to accepting the Ticket
Commit, or evidence made stale by the final state.

A zero-net-change result additionally requires an unchanged tree from `ticket_base`, sufficient
source evidence that the accepted behavior was already satisfied, the checks material to that
claim, and the normal hook-validated empty Ticket Commit and exact trailer boundary. It cannot
conceal a substantive change or relax any other success predicate.

A mismatch, returned failure, live or ambiguous worker, changed source, or unproved requirement
enters [`stop.md`](stop.md) with the raw worker result and current Git evidence. Otherwise return
the Ticket Commit as `completed-in-batch`. It may unlock later selected tickets, but it is neither
tracker completion nor Batch delivery.

**Complete when:** exactly one independently proven Ticket Commit closes this ticket's unit.
