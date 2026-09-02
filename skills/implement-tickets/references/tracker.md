# Tracker Contract

The configured external tracker and its frozen contract own authoritative business status,
blocker, claim, completion, and release meanings and every mutation operation. This reference owns
only `implement-tickets` observation through that interface, Batch eligibility and selection,
dependency closure and order, requested deltas, proof and recovery cursors, drift, and consumption.
Other references pass a canonical ticket identity and requested delta; they neither restate nor
infer tracker behavior.

Freeze the configured tracker owner and route, canonical identity fields, public order, every
authoritative business meaning, Batch-claim representation, mutation operation, exact before/after
predicate, authorization, and observation proof. Consume those meanings and operations as
returned; this reference does not define or reinterpret them. A visible control is not authority.
Drift in the external contract stops the Batch.

## Observe and select

Read every candidate and blocker in the bounded scope through the frozen route. Record canonical
identity, complete contract and acceptance sources, raw status, owner, claim, blockers, public
order, and the external contract's authoritative predicates. Using those predicates, exclude
tickets the tracker identifies as completed, rejected, human-owned, information-blocked, or
externally claimed. Close the selection recursively over eligible same-scope open blockers. An
external blocker is satisfied only by the tracker's authoritative pre-Batch completion proof; a
dependent whose tracker-identified open blocker is neither completed nor eligible for this same
Batch is excluded.

Reject cycles, conflicting identities, and ambiguous edges. Produce a dependency-valid order,
using public order only to break ties between equally ready tickets. Freeze one **Selection
Result** containing the selected tickets and complete sources, graph and order, exclusions and
reasons, external completion proofs, and the observations that make its first ticket ready. A
proven Ticket Commit satisfies its selected ticket for later readiness; no other in-Batch evidence
does. Later decisions re-observe affected tickets and blockers. A changed contract, owner, status,
claim, or edge is selection drift and stops rather than silently changing the Result, with one
exception: the current Batch's exact claim delta may update the current observation after the
frozen tracker operation contract authorizes it and its authoritative after-state proof passes.
That expected delta leaves the frozen Selection Result, dependency graph, and order unchanged. Any
other owner, status, claim, or edge change, including an unbound or unproved claim delta, remains
selection drift.

**Complete when:** one nonempty, acyclic, closed Selection Result and its next-ticket evidence are
authoritative and mutually consistent.

## Request and consume one tracker delta

Every claim, completion, and release request has one recoverable operation cursor:

1. Observe the before-state, then transition the cursor through the Persistence Contract, binding
   the Batch, ticket, delta, unique attempt identity, authority, route, and exact before and after
   predicates.
2. If the after-state is already proven for this attempt, consume it without requesting a
   mutation. Otherwise ask the external tracker owner to invoke its frozen operation once from the
   exact before-state.
3. Re-observe the authoritative after-state through the frozen interface, then transition the raw
   invocation evidence, observation, and cursor through the Persistence Contract before advancing.

An unavailable prerequisite before the request is `stopped`. A returned failure remains that raw
result. An unknown invocation result, conflicting state, or unproved after-state is ambiguous: keep
the operation in flight at its cursor and never request it again until the after-state or proven
effect-free before-state resolves the original attempt.

For a ticket claim, re-observe eligibility and dependency readiness immediately before the attempt.
The claim binds the exact Batch and Ticket Commit proof yet to be produced. Keep every Batch claim
through delivery; no failure before delivery authorizes abandonment or release.

**Complete when:** the requested delta has a proven after-state, or one exact recoverable cursor and
raw result are retained.

## Close after authoritative delivery

Enter only with the unchanged `finish-worktree` result whose authoritative classification is
`authoritative delivery`, including **Already Delivered** only when that is the dependency's own
classification. Bind that raw result, its phase handoff, the selected dependency order, every
Ticket Commit boundary, the retained source history, and the first unproved tracker cursor.

For each ticket in dependency order, request its completion and then its Batch-claim release from
the external tracker owner using the cursor contract above. Never pass the first unproved
operation. A proven existing after-state advances without another request; an ambiguous operation
keeps the suffix untouched. Delivery remains authoritative and is never rolled back.

Transition the completed prefix and next cursor through the Persistence Contract. Recovery
re-proves the same delivery result, source-boundary evidence, tracker contract, completed prefix,
and current before/after state; it does not recreate the worktree, dispatch workers, rerun review,
or invoke another finalizer effect attempt.

After the past-final cursor, return the full closure proof to the frozen
`finish-worktree`/lifecycle cleanup owner. Retain source history and every recovery item until that
owner proves its authorized removal, release, or intentional retention. Missing cleanup proof is
not Batch completion.

**Complete when:** every selected ticket is completed, every Batch claim is released, the entire
operation order is proven, and the lifecycle owner has enough exact proof to close retained state.
