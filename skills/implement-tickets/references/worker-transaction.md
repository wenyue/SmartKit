# Worker Transaction

This reference is the sole authority for a ticket or repair worker attempt, response, handoff,
quiescence, reconstruction, and replacement. Unit owners supply their scope and success predicate
and consume its result; they do not define another worker-state protocol.

Freeze the environment-owned worker runtime identity, controller and worker actors, dispatch and
observation routes, scoped write/commit authority, quiescence proof, replacement authority, and
unavailable/failed-use outcomes. Consume the Persistence Contract's existing Worker Handoff record
identity, actors, capabilities, authorities, and lifecycle. A **Worker Handoff** binds those facts,
the unit and base, unique attempt and worker identities, dispatch/response evidence, owned commits
and local state, current `HEAD` and tree, validation/self-review evidence, raw result, residuals,
and next owner/action. Missing or changed capability stops before dispatch.

## Qualify the unit boundary

Enter read-only immediately before the ticket unit owner requests its tracker claim. Re-observe
and prove the frozen worker runtime identity and observation route, capacity for one fresh attempt,
scoped authorities, and any required quiescence and retained Worker Handoff ownership and state.
Return only the exact pass or missing/mismatched boundary to the unit owner.

This gate allocates or dispatches no worker, reserves no capacity, mutates no worktree, and performs
no persistence transition. A missing or mismatched proof blocks the claim request.

**Complete when:** every fact required to permit one later fresh attempt is proven immediately
before the claim request without any state change.

## Dispatch one fresh worker

Enter only with no prior attempt or a proven quiescent incomplete attempt. Reprove the exact unit,
current owned state, runtime identity, authority, capacity, and quiescence. Transition the Worker
Handoff through the Persistence Contract, binding the unique attempt, fresh worker identity,
complete handoff, and authorized effects, then dispatch once.

Give the worker only its unit, applicable project rules, recovered owned state, validation, and
unit-scoped write/commit authority. The worker accounts for its whole range, validates and
self-reviews it, and returns the evidence required by the unit's success predicate.

After a response, preserve its raw status and evidence, collect the current host and worktree
observations, and enter **Classify one observed attempt** below. Do not translate a raw failure into
success.

**Complete when:** the response and current evidence are ready for the common classifier, or the
exact unresolved attempt is retained.

## Recover a missing response

A missing response proves nothing. Freeze all observations and first prove through the frozen host
route that the original worker and dispatch are quiescent. Until then, retain its ownership; no
replacement or worktree write is permitted.

After quiescence, reconstruct the attempt from the durable Worker Handoff, unit base, Ticket Commit
boundary, first-parent history, and complete local state. For a repair unit, use the corresponding
review-finding scope and repair range instead of inventing a ticket boundary. Then enter the same
classifier used for returned responses; this branch adds no classification rule.

## Classify one observed attempt

Apply these predicates once to either a returned response or the reconstructed evidence from a
missing response:

- **complete:** the attempt and worker identities are exact, quiescence is proven, every observed
  state and effect is fully accounted for and attributable to the unit, and the complete frozen
  success predicate is proven. A returned raw failure is not success evidence.
- **incomplete:** identity and quiescence are exact and every state and effect is fully accounted
  for and attributable to the unit, but the success predicate is not fully satisfied or the raw
  returned status is failure.
- **ambiguous:** identity, quiescence, ownership, range, local state, or effects are unresolved,
  mixed, or conflicting.

Transition the raw evidence and classification through the Persistence Contract. Complete proceeds
to the unit owner's independent verification without another worker. Only proven incomplete
permits a fresh replacement, after quiescence is reproven and all recovered state is supplied.
Ambiguous retains the original in-flight ownership and exact next observation/proof action; it
neither becomes failed/stopped by inference nor authorizes replacement or worktree writes.

**Complete when:** one evidence-backed classification is durable and its only permitted next action
is explicit.
