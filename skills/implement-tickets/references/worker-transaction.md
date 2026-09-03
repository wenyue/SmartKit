# Worker Boundary

This reference owns one ticket or repair worker attempt. The unit owner supplies scope, current
state, authorities, and a success predicate; the host runtime owns worker identity, dispatch,
observation, interruption, and quiescence. Use those capabilities as exposed rather than requiring
a separate worker-state store or protocol.

## Qualify before a claim

Enter read-only with one selected ticket, its intended unit and Batch boundary, the current
worktree evidence when one exists, and the proposed write and commit authority. Prove the
environment-owned worker runtime and observation route, capacity for one fresh serial attempt,
the exact authority the unit can receive, and, when the Batch Worktree exists, the controller's
exclusive control and quiescence of every earlier worker. Account for any attributable retained
attempt and state. Before New-Batch worktree creation, prove instead that no Batch Worktree or
attributable Batch worker attempt exists, that an exclusive-control route is available, and that
exact readiness will be re-established before dispatch.

This gate allocates or dispatches no worker, reserves no capacity, persists no state, and mutates
neither tracker nor worktree. An unavailable or ambiguous fact stops before the claim.

**Complete when:** every currently knowable worker prerequisite that could strand the proposed
claim is proven without an effect.

## Dispatch or resume one attempt

Immediately before dispatch, prove exclusive Batch Worktree ownership, the exact unit base and
current `HEAD`/tree/local state, one available fresh worker identity, scoped write and commit
authority, and that every earlier attempt is quiescent. A missing capability or possibly live
worker stops before another dispatch.

Give the fresh worker only the unit, applicable project rules, existing attributable state,
validation, success predicate, and scoped authority. The worker may create recoverable commits
within the unit, validates and self-reviews its complete result, and returns its identity, raw
status, commits, final `HEAD` and tree, local state, validation, self-review, residuals, and next
action. It performs no tracker or finalizer effect.

Preserve the raw return. A returned failure does not become success, even if the worktree looks
complete; the unit owner decides its next safe disposition from both sources of evidence. A fresh
replacement is eligible only after the prior worker is proven quiescent and every observed commit
and local-state item is attributable to the same unit. Supply that recovered state to the new
worker rather than restarting it blindly.

**Complete when:** one fresh attempt has returned and is quiescent, or the exact unavailable or
in-flight worker boundary is retained.

## Recover a missing response

A missing response proves neither failure nor quiescence. Inspect the original host identity and
control route. While the worker may still run, preserve its ownership of the worktree and permit no
replacement or overlapping write.

After quiescence is proven, inspect the unit's first-parent history and complete local state. An
attributable complete result may be reconstructed and handed to the unit owner for independent
proof. Fully attributable incomplete state may be handed to a fresh replacement under the dispatch
gate above. Mixed ownership, uncertain quiescence, or an unexplained effect remains in flight with
the original worker identity and the next host observation or recovery action.

**Complete when:** the original attempt is quiescent and its complete or incomplete state is fully
attributable, or its exact in-flight ownership and next action are preserved.
