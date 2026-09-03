# Tracker Boundary

The configured tracker owns authoritative ticket identities, status, blockers, claims, completion,
release, observation, and mutation operations. Consume only the meanings and capabilities its
current project contract actually documents. This reference owns Batch selection and the safe use
of those operations; it does not invent compare-and-set, operation cursors, Batch-specific claims,
release operations, or recovery interfaces.

## Select the Batch

Resolve the configured tracker/triage owner's affirmative agent-executable eligibility predicate,
then read every ticket and blocker in the caller's bounded scope through that owner's route. Retain
each canonical identity, complete ticket/spec sources, authoritative status, claim or owner,
blocking edges, public order, and eligibility result. A missing or ambiguous predicate or result
stops before a Selection Result can establish a Batch.

Select only tickets with authoritative positive eligibility proof. Recursively include a
same-scope open blocker only with the same proof. Record authoritative negative results—such as
completed, rejected, human-owned, information-blocked, or externally claimed tickets—as
exclusions and reasons, never as an alternative eligibility test. An external blocker is satisfied
only when the tracker proves it complete; otherwise exclude its dependent. Reject conflicting
identities, ambiguous edges, and cycles. Order the remaining graph by dependencies, using stable
public order only to break ties between equally ready tickets.

For every selected ticket, resolve the tracker owner's claim requirement, session boundary, legal
timing, and whether a blocked or later-frontier ticket may be claimed initially. The resulting
claim plan must give every ticket one owner-supported route: an initial claim before other Batch
writes, an expressly compatible just-in-time claim after earlier Batch effects, or no claim when
the tracker does not require one. Ordinary per-ticket claim syntax does not by itself authorize an
initial claim for a not-yet-ready ticket. Missing or incompatible timing stops before any write.

Return one frozen Selection Result with the tickets, complete sources, graph, order, exclusions and
reasons, external completion proofs, and the complete claim plan. If no ticket remains eligible,
return `nothing-to-do` with those observations and exclusions. That is a successful no-effect
result: it establishes no Batch and authorizes no mutation.

Re-observe a ticket and its blockers before its claim and before accepting its Ticket Commit. A
proven Ticket Commit satisfies that selected ticket for later in-Batch readiness. Any other
material status, owner, claim, requirement, or edge change stops the frozen Batch instead of
silently changing it. The sole expected claim or owner delta is the exact after-state that this
tracker owner has already proved for this ticket's configured claim operation; exempt only the
fields attributable to that consumed effect.

**Complete when:** either an acyclic, closed, nonempty selection, its first frontier, and its
complete owner-supported claim plan are proven, or an empty eligible selection is proven as
`nothing-to-do`.

## Satisfy the initial claim gate

Enter before the first Batch write with the nonempty Selection Result. For every claim assigned to
this gate, first require [`worker-transaction.md`](worker-transaction.md)'s current non-mutating
feasibility result for that selected ticket. Then request only tracker-authorized initial claims,
in stable dependency order, through the operation boundary below. Re-observe and consume each
exact after-state before the next claim.

Stop at the first unavailable, failed, or in-flight qualification or claim. Preserve the frozen
Selection Result and claim plan; the proven claimed prefix and its raw responses/current tracker
state; the exact current failed or in-flight claim attempt, if one started, including intended
delta, before-state, raw result and observation, and tracker owner/action; and the untouched
suffix. An unresolved current claim belongs to neither prefix nor suffix and is never retried from
current-state inference.

Return that evidence as the claim partition of the Pre-ready selection handoff, including every
frozen JIT/no-claim disposition, with Create state `never-started` and the worktree explicitly
absent. A later public Create result may advance only that independent Create partition. Do not
invoke `create-worktree` or perform another Batch write unless every selected ticket's claim route
remains compatible, every required initial claim is proven, and no claim attempt is unresolved.

**Complete when:** every required initial claim and every deferred or no-claim route is currently
proved under the tracker-owned plan.

## Revalidate the frozen selection

After the complete verification/review barrier and immediately before finalization, re-observe
every selected ticket and relevant blocker through the configured tracker, and re-read every
frozen acceptance source through its authoritative route. Compare those complete sources,
dependency graph, statuses, owners, and claims with the frozen Selection Result. Permit only each
exact claim or owner delta already consumed and authoritatively proved for this Batch under the
operation boundary below.

Any other material change invalidates the verification/review barrier and enters
[`stop.md`](stop.md) before the finalizer effect. Current observations never silently update the
frozen Batch.

**Complete when:** the whole frozen selection remains current except for its exact attributable
claim effects, on the state immediately preceding finalizer invocation.

## Use one documented tracker effect

Perform a claim, completion, or release only when the tracker contract documents that operation,
its success meaning is observable, and the caller supplies authority for the exact effect. Observe
the current state immediately before the request. If the tracker already proves the intended
state, consume it only when its meaning is sufficient for this Batch; otherwise treat it as drift.

Request the operation once, preserve its raw response, then re-observe authoritative state. A
successful return without the documented after-state does not pass. A returned failure remains a
failure. When the response is missing or the observation cannot distinguish success from no
effect, keep that exact tracker effect in flight with its ticket, intended delta, before-state, raw
evidence, owner, and next observation or recovery action. Do not repeat it by inference.

Before implementation, request a claim only when the configured tracker provides one. If it has no
claim operation, continue only when its own contract and the accepted workflow still establish
that the ticket is eligible for this worker; otherwise stop at the unsupported capability. Hold
every acquired claim through authoritative delivery. A distinct release is required only when the
tracker contract defines it as part of closure.

**Complete when:** the intended tracker state is authoritatively observed, or the original raw
failure or in-flight effect is retained with its owner and next action.

## Close after authoritative delivery

Enter only with the unchanged `finish-worktree` result whose own classification is authoritative
delivery, plus the selected order and recoverable Ticket Commit boundaries. In dependency order,
re-observe each ticket, request its documented completion when needed, and perform any separately
documented required claim release. Stop before the first unresolved effect; leave the remaining
suffix untouched. Delivery is retained and never rolled back.

After every ticket is authoritatively complete, give the closure proof to the lifecycle owner named
by the `finish-worktree` handoff. Retain source history, claims, refs, worktrees, and other recovery
state until their owner proves an authorized removed, released, or retained disposition.

**Complete when:** every selected ticket is authoritatively complete, every tracker-required claim
disposition is proven, and the lifecycle owner receives the proof needed to close retained state.
