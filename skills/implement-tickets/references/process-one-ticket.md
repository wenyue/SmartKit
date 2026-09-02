# Process One Ticket

Enter with one frozen dependency-ready ticket, the Batch Worktree exclusively controlled for this
unit, and either no worker attempt or its durable handoff. The only success result is
`completed-in-batch`.

## Qualify, claim, and define the unit

Read [`tracker.md`](tracker.md) if its frozen contract is not already loaded. Re-observe the ticket,
claim, full contract, acceptance sources, and blockers.

Before the claim effect, read [`worker-transaction.md`](worker-transaction.md) and have it pass its
read-only qualification gate for this ticket: the frozen runtime identity and route, fresh-attempt
capacity, authorities, and any required quiescence and retained handoff must be proven. This gate
allocates or dispatches no worker and persists no attempt. Only after it passes may the tracker
owner execute or accept the claim delta through its operation contract. Keep that claim until
authoritative delivery and tracker closure.

Freeze `ticket_base` as the current `HEAD` and tree for a new ticket. On recovery,
reconstruct the original base and account for every later commit and staged, unstaged, and
untracked item as this ticket's state; mixed or ambiguous ownership stops.

Give the transaction one **Ticket Unit** containing the canonical ticket and complete sources,
blocker proof, Batch/worktree identity, immutable base, `ticket_base`, earlier Ticket Commits,
owned recovery state, scoped write and commit authority, and project-required validation. Its
success predicate is:

- only this ticket is implemented and every owned item is accounted for;
- focused and complete required validation pass and the whole unit is self-reviewed against all
  ticket sources;
- the worktree is clean; and
- the first-parent unit range ends in exactly one Ticket Commit with exactly the canonical trailer,
  while every preceding Checkpoint has no ticket trailer. If Checkpoints already contain the net
  change, the Ticket Commit may be empty.

**Complete when:** the claim, unit boundary, success predicate, owned recovery state, and worker
authority are exact.

## Obtain and prove the result

Let `worker-transaction.md` exclusively decide whether an existing attempt is complete,
incomplete, ambiguous, or dispatchable. Use one fresh worker for every authorized attempt. A
reconstructed or returned complete result proceeds directly to independent proof; only a proven
quiescent incomplete result may receive a fresh replacement. Every other result stops at the
transaction's handoff.

Independently rederive and prove the complete Ticket Unit result: worker identity and quiescence,
first-parent ancestry from `ticket_base`, ownership of every commit and local item, validation and
self-review, clean final `HEAD` and tree, unchanged authoritative target, and the exact sole Ticket
Commit/trailer boundary. Re-observe the ticket and blockers before acceptance.

Any mismatch, residual, changed source, or unproved requirement returns the exact worker or unit
handoff through `stop.md`. Otherwise transition the Batch Handoff through the Persistence Contract
to record the Ticket Commit as this ticket's durable dependency boundary, then return
`completed-in-batch`. This is neither tracker completion nor Batch Delivery.

**Complete when:** one independently proven Ticket Commit boundary is recorded for the ticket.
