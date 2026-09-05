# Pause and Resume

Read this reference at a material blocker, interrupted control, missing evidence, possible prior
attempt, or retained handoff. Pause the whole batch at the first unproved boundary. Keep the
worktree, partial files, current candidate, accepted ticket/repair commits, claims, and recovery
state; later tickets remain untouched. Ordinary supported repairs may continue while they make
progress. Otherwise report the exact blocker and next owner/action.

Use `stopped` for an unproved prerequisite before its effect, retain an owner's returned `failed`
result after an attempted effect, and use `in-flight` while the original attempt may run or its
effect is unresolved. Preserve the owner's more specific result vocabulary and strongest proven
facts. No automatic revert, reset, clean, discard, claim abandonment or queue change follows a stop.

## Retain a useful handoff

Keep no batch journal. Recover from Git history, the frozen selection and accepted source revisions,
current tracker observations, retained check/review reports and public dependency handoffs, and
observable live Agent state. Retain the identities and causal boundaries needed to distinguish
completed, pending and ambiguous work. The finalizer still owns its own external effect receipts.

A handoff identifies the scope and exclusions; dependency order and claim plan; exact worktree,
branch, immutable batch/ticket or repair bases, HEAD/tree and complete owned local state; accepted
commit prefix and current candidate; check/review provenance and acceptance bindings; raw tracker,
Worker, Create and finalizer results; observed effects and residuals; and one exact next owner/action.
Include only applicable evidence, but account for every item material to attribution, safety,
acceptance or effect recovery. Before any effect has occurred, report that proof and the missing
prerequisite without claiming a batch exists.

## Establish the original phase

Identify the original scope and attempts from whichever retained evidence exists: selection and
claim results may precede worktree creation, while finalizer receipts may outlive removal. Ambiguous
scope, ownership, base, liveness or external-effect state stops before another mutation. Choose the
furthest attributable phase; once a finalizer attempt exists or cannot be excluded, never resume an
earlier implementation phase until that owner's recovery hands it back:

- **Before readiness:** recover the frozen selection and independent claim/Create states below.
- **Before finalization:** recover an accepted commit prefix and at most one current ticket or
  repair candidate plus its complete owned local tail. Revalidate tracker/source facts and recover
  Worker control before returning to the current ticket or whole-batch barrier.
- **Raw finalizer result retained:** pass it once to [Consume the result](complete-run.md#consume-the-result),
  including delivery with incomplete tracker closure.
- **Finalizer response missing or possibly live:** recover the original attempt as described below.
- **Terminal result already consumed:** resume only the named tracker, lifecycle, classification or
  other dependency-owner action. Preserve the existing result; do not consume it or finalize again.

Where a worktree exists, recheck its physical path, registration, Git common identity, branch,
immutable base relationship, HEAD/tree, index and staged/unstaged/untracked state against the
identified phase. Account for ignored state where it affects ownership, pending writes,
verification, finalization or cleanup; retain bounded noncritical residuals with their owner.
If the phase needs an existing worktree but its identity or presence is unproved, stop with that
boundary's owner. A proven pre-creation phase needs no worktree to resume its claim/Create gates.

After a gap in control at an implementation frontier, ask public `create-worktree` to re-evaluate
that exact existing worktree with retained state protected. Consume a fresh `ready` result only for
the same candidate; this is readiness re-evaluation, not another creation. A non-ready or unresolved
result remains with its owner. Under continuous attributable control, current identity/state checks
suffice unless drift invalidates readiness.

## Recover claims and creation independently

Retain the frozen claim plan, proven initial-claim prefix with raw responses and current proof,
optional failed/in-flight current claim with before-state and intended delta, untouched suffix,
and every deferred/no-claim route. The unresolved current claim belongs to neither prefix nor suffix.
Recover it through the tracker owner's original operation; Create cannot follow an unresolved claim.

Retain Create separately as `never-started` with proof of no attempt/worktree,
`non-ready-or-in-flight` with its original effects, artifacts and owner/action, or attributable
`ready` with its recorded snapshot. Only `never-started`, after all required initial claims pass,
may start initial clean creation. A partial or interrupted Create returns to its owner; an existing
candidate needing refreshed readiness is reused, never silently replaced. Consume claims and
readiness only from current attributable proof, without repeating successful effects.

## Recover a Worker and its candidate

A missing response is neither failure nor quiescence. Observe the original Agent through the host
control interface. While it may write, preserve its exclusive ownership and permit no replacement,
review of a mutable candidate, or overlapping implementation. Prove it stopped before resuming it
or assigning a replacement. A replacement receives the exact attributable inherited candidate and
local tail under the original unit scope; it never restarts the ticket blindly.

After quiescence, compare Git history and complete local state with the accepted boundaries. An
accepted ticket requires its Controller acceptance evidence, not just a commit or completion
trailer. Recover immutable checks/review reports and their original input bindings when available;
otherwise repeat missing checks and both independent judgments against the attributable candidate.
A marker written just before interruption remains unaccepted until every acceptance predicate is
re-established. Preserve proven earlier boundaries. Mixed or unexplained changes remain blocked
rather than being attributed to the current ticket by position alone.

An attributable incomplete candidate returns to its Worker for the normal repair/acceptance loop.
A recovered complete result may enter Controller acceptance only after all required proofs hold;
preserve the original attempt's raw failure or interruption alongside its supported recovery.

## Recover the finalizer's original effect

Retain the original invocation identity when exposed, frozen input, expected pre-state, accepted
base/HEAD/tree, raw handoffs and observed effects. Use the original host/session and public
`finish-worktree` recovery route to establish liveness and recover its attributable result. Preserve
source and target state, publication, branches/refs, receipts and other recovery objects meanwhile.
Current target contents or tracker status cannot independently classify delivery or authorize retry.

If the invocation may still run or its effects remain ambiguous, return that same `in-flight`
attempt with the missing fact and next owner observation/recovery action. If the owner recovers a
raw response, pass it unchanged to `complete-run.md`. Never repeat a possibly completed tracker or
finalizer effect just to obtain a new receipt.
