# Worker Boundary

This reference owns one ticket or repair worker attempt.

## Principles

- **Bounded ownership.** The unit owner supplies scope, current state, authority, and success; the
  host runtime owns worker identity, dispatch, observation, interruption, and quiescence. A worker
  receives no Batch-wide or adjacent-unit authority.
- **Serial attribution.** Preserve raw results and keep the original attempt in control until host
  evidence proves quiescence and attributes every inherited change. Only then may a successor or
  reconstructed result proceed.

## Qualify a claim when needed

Enter read-only only when `tracker.md` or `process-one-ticket.md` determines that later dispatch
failure could strand the proposed claim. Establish that the environment-owned runtime and
observation route can supply one serial attempt with the proposed authority. When a Batch Worktree
exists, also establish exclusive control and quiescence of any retained worker; before its creation,
establish that no attributable Batch worker attempt is live and that readiness will be checked
before dispatch. Reuse shared facts across claims while their observable freshness conditions hold,
and evaluate only ticket-specific constraints that can change this result.

This gate allocates or dispatches no worker, reserves no capacity, persists no state, and mutates
neither tracker nor worktree. An unavailable or ambiguous fact stops before the claim.

**Complete when:** the material dispatch risks that could strand the proposed claim are resolved
without an effect, or the exact unresolved risk and owner stop that claim.

## Dispatch or resume one attempt

Immediately before dispatch, establish exclusive Batch Worktree ownership, the exact unit base and
current `HEAD`/tree/local state, one suitable worker identity, scoped write and commit authority,
and that every earlier attempt is quiescent. Reuse a quiescent attributable Batch worker when its
prior unit is closed and its scope and authority can be rebound without ambiguity; otherwise use a
fresh identity. A missing capability or possibly live worker stops before another dispatch.

Give the selected worker only the unit, applicable project rules, existing attributable state,
targeted checks needed to make its mutation safe to hand back, success predicate, and scoped
authority. The worker may create recoverable commits within the unit and returns its identity, raw
status, commits, final `HEAD` and tree, local state, check evidence, residuals, and next action. It
performs no tracker or finalizer effect. Whole-Batch repository verification and independent
Standards and Spec review remain the final barrier rather than work duplicated by each worker.

Preserve the raw return. A returned failure does not become success, even if the worktree looks
complete; the unit owner decides its next safe disposition from both sources of evidence. A fresh
replacement is eligible only after the prior worker is proven quiescent and every observed commit
and local-state item is attributable to the same unit. Supply that recovered state to the new
worker rather than restarting it blindly.

**Complete when:** one bounded attempt has returned and is quiescent, or the exact unavailable or
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
