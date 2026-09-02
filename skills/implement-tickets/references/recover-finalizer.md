# Recover a Lost Finalizer Response

This reference routes an in-flight finalizer attempt to its original effect/recovery owner when the
response is absent, interrupted, or not durably attributable. It owns no finalizer effect,
recovery, classification, tracker transition, or cleanup. Enter with the durable attempt identity,
expected prior state, authorization, frozen `finish-worktree` contract and exact input, reviewed
base/`HEAD`/tree, and all retained observations. Preserve the original logical effect attempt and
its evidence unchanged.

## Reconcile the same attempt

Through routes permitted by the frozen dependency contract, prove the original controller and
finalizer quiescent before any recovery mutation. Observe the authoritative target and branch,
source worktree and branch, relevant refs and recovery objects, publication/dependency state,
complete effect envelopes, unrelated-state preservation, and any durable dependency output. Bind
an observation causally only when the frozen attempt proves that attribution; current target
contents alone never establish delivery or **Already Delivered**.

Hand the exact in-flight attempt—identity, pre-state, frozen input and contract, parent and child
effect evidence, observations, residuals, and uncertainty—unchanged to the original
`finish-worktree` effect/recovery owner named by that contract. Only that owner may continue or
reconcile its logical attempt and return an authoritative raw result. This route invokes no second
finalizer effect and assumes no separately named recovery/classification interface.

When a causally attributable raw result returns from that owner, transition the exact response and
`result-awaiting-consumption` marker through the Persistence Contract without inspecting its
classification. An unavailable or ambiguous persistence transition enters [`stop.md`](stop.md)'s
unresolved-persistence entry and remains with its frozen persistence recovery owner. After the
exact after-state is proved, transfer the response unchanged to
[`complete-run.md`](complete-run.md)'s Returned-response entry, the sole public result route,
regardless of classification usability. This reference does not interpret or enumerate
classifications.

If quiescence, causal ownership, effect reconciliation, or response attribution or return remains
ambiguous, keep the original attempt in flight with every observed effect, exact missing proof, and
next finalizer recovery owner/action. It is neither `stopped` nor `failed` by inference, and it
permits no retry, tracker transition, cleanup, worktree mutation, or release.

**Complete when:** the original effect/recovery owner supplies one attributable authoritative raw
result, or the exact in-flight handoff and that owner's next action are retained without a second
effect attempt.
