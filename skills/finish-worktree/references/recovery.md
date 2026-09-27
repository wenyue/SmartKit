# Effect Recovery

Read this before the first state-changing effect or when resuming an unresolved attempt. Recovery
starts by determining what the original attempt did. Repeating the requested command is unsafe
when the first attempt may already have published, transferred or removed state.

For bounded observations using the bundled helper, read [Read-only evidence](transfer-mechanism.md#read-only-evidence).
Before using file-transfer helpers or recovering a partial transfer, read the complete relevant
sections of [Transfer Mechanism](transfer-mechanism.md).

## Operation receipt

Persist the receipt outside every affected worktree so it survives their removal. Record the job
and route, exact source/target identities, authority, pre-state, intended effect and attempt
identity. Append observed effects, residual locations, recovery owner and release conditions.
Use exact OIDs and physical or host paths; retain readable backups when hashes alone cannot support
recovery.

Group effects by the decision needed to retry them. A prepared file batch or history helper can be
one attempt. Push, PR creation and individual removals need separate effect records because one can
succeed independently of the next. Within an attempt, distinguish children known completed, known
absent, in flight or ambiguous. Update the receipt before a dependent effect proceeds.

## Resolve the original attempt

Observe current authoritative state before deciding to retry. Keep the proven prefix and resume
only the original incomplete suffix whose authority and preconditions still hold. Prove an effect
absent before attempting it again. If observation is unavailable, retain the uncertainty and its
owner instead of treating a missing response as absence.

For example, a proven push followed by failed PR creation needs PR recovery; it does not need
another push. Proven delivery followed by failed cleanup needs cleanup recovery; it does not need
another integration. File-transfer recovery has stricter attribution and restoration guards in its
mechanism contract.

Report whether the original phase was rejected without effects, partly effected or still ambiguous,
using [Public Results](results.md). Preserve the original cause, any proven publication or other
positive result, and the recovery observations even when recovery succeeds or later work completes.
