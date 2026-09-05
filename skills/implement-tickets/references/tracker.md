# Tracker Boundary

Use the target project's configured tracker and triage contracts for authoritative identity,
agent-executable eligibility, blockers, ordering, claims, completion and release. Resolve them from
`docs/agents/issue-tracker.md` and its owner pointers. Missing configuration or unsupported operations
stop with that owner; never invent claim, compare-and-set, release, cursor or recovery interfaces.

## Select and freeze

Observe the complete candidate set in the caller's bounded scope and every dependency edge needed
for closure. Retain each candidate's identity, sources, status, owner/claim, ordering evidence and
positive eligibility proof or exclusion reason. Missing eligibility meaning, uncertain membership,
conflicting identities or ambiguous edges prevent selection.

Recursively include same-scope open blockers only with affirmative eligibility proof. Record
completed, rejected, human-owned, information-blocked, externally claimed or other authoritative
negative results as exclusions. An external blocker is satisfied only when the tracker proves it
complete; otherwise exclude its dependent. Propagate unsatisfied dependencies so every selected
ticket has a closed readiness proof. Reject cycles. Use dependency order and the owner's stable
public order only to break ties between equally ready tickets.

Resolve claim requirements, session boundaries and legal timing for each represented policy. Every
ticket needs an owner-supported route: an initial claim before other batch writes, an expressly
compatible just-in-time claim after earlier batch effects, or no claim when the owner requires none.
Per-ticket claim syntax alone does not authorize claiming a not-yet-ready ticket. Incompatible or
uncertain claim timing stops before writes.

Freeze the selection with membership, dependency graph/order, complete accepted requirements and
source revisions, external completion proofs, exclusions/reasons and every claim route. An empty
eligible selection returns `nothing-to-do` with observations and exclusions, creates no batch, and
makes no mutation. Report a nonempty selection before acting so excluded input is not mistaken for
work the batch will complete.

## Claim and revalidate

Before an initial or just-in-time claim, use [Worker boundary](worker-transaction.md)'s read-only
qualification only if dispatch failure could strand it under the tracker lifecycle. Complete all
required initial claims in stable dependency order before `create-worktree` or another batch write.
Prove each after-state before the next claim. Defer just-in-time claims to their ticket frontier;
consume proven initial claims without repeating them, and re-establish current no-claim eligibility.

At each claim, ticket acceptance, and finalization boundary, re-observe the relevant tickets and
blockers and revalidate accepted requirements through authoritative revisions, digests or change
signals. Reread content when no stable signal exists or a source changed. Ticket acceptance checks
its full accepted sources; finalization checks every selected ticket and the complete graph.
A `completed-in-batch` commit with retained acceptance proof satisfies that selected dependency for
later in-batch readiness.

Compare with the frozen selection. Exempt only exact claim/owner deltas already proved for this
batch's consumed tracker operations. Any other material requirement, status, owner, claim or edge
change pauses the whole batch for reconciliation. Preserve membership and requirements; current
observations never silently revise them. Refresh checks and review whose inputs changed before
accepting the reconciled result.

## Perform one documented effect

A claim, completion or release requires its owner's documented operation and observable success
meaning plus exact effect authority. Observe the before-state, request it once, retain the raw
response, and observe the authoritative after-state. If the intended state already exists, consume
it only when its provenance and meaning suffice for this batch; otherwise treat it as drift.
A successful response without the required after-state does not pass. Preserve returned failures.

For a missing response or ambiguous outcome, retain the original attempt, ticket, intended delta,
before-state, raw evidence, current observation and next owner/action. Resume through that owner's
observation/recovery route; never repeat a possibly completed effect to obtain a response.
Stop the dependent work at the first unresolved operation. Hold acquired claims through authoritative
delivery; a distinct release is required only where the tracker defines it as part of closure.

## Close after authoritative delivery

Enter only with public `finish-worktree`'s attributable `authoritative delivery` classification and
recoverable accepted ticket boundaries. Re-observe each ticket in dependency order, perform its
required documented completion and any separately required claim release, and prove each after-state.
Consume a proven completed prefix and continue only its unresolved suffix. The first failed or
ambiguous effect stops closure; preserve delivery and leave later tickets untouched.

PRs, retained worktrees, review transfers, history preparation and explicit discard do not permit
tracker completion. A cancellation requiring claim disposition stays with the tracker owner under
separate exact authority. When closure is proven, give that proof to the lifecycle owner named by
the finalizer. Retain source history and recovery items until their owners establish authorized
retention, release or removal.
