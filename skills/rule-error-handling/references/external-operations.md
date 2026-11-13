# External Operations

Use this reference when filesystem, network, subprocess, or other external effects determine recovery, replay, or completion. Base handling on what the operation actually did and what its contract acknowledges.

## Establish the outcome before replay

Trace consequential writes, remote mutations, held resources, notifications, and visible state through the failed step and recovery. Include in-flight work and effects whose outcome is uncertain. Establish what remains after cleanup, compensation, cancellation, or interruption, and who owns that state. Inspect the native failure mechanism when a secondary failure could replace the first error or obscure a retained resource.

| Evidence | Consequence for handling |
| --- | --- |
| The request was not dispatched. | No remote effect occurred through that attempt; local preparation may still need cleanup. |
| An authoritative response refused the request. | Follow the refusal contract, including any effects it permits; preserve unrelated infrastructure failures separately. |
| The request was accepted or an effect was confirmed. | Establish whether the promised operation is complete or still needs acknowledgement, follow-up, or reconciliation. |
| The response was lost, timed out, or otherwise leaves completion unknown. | Preserve uncertainty. Reconcile through a supported status or identity when available, or transfer the unresolved outcome to its owner before unsafe replay. |

A timeout or broken connection after dispatch does not prove that a mutation failed. Prefer a status check or retry of only the unfinished step when it can establish the promised result. Use an existing idempotency or deduplication contract where needed; a fresh attempt identifier may defeat that protection.

For ordinary optional-file access, select a skip or default only when the caller accepts the native query's possible lookup failure or type mismatch. Required access and failures the caller must observe belong to the actual operation. A preliminary existence check supplies neither exclusive creation nor atomic replacement; use the protocol that supplies the required guarantee.

## Make the whole replay path safe

Examine the complete replay path, including restoration and compensation, for repeated or irreversible effects. A reusable checkpoint needs evidence that arguments, current state, resources, and already completed effects still permit the promised result. Establish any idempotency or compensation the full path requires. Explain why retry is safe beside replay logic when code, types, and referenced contracts leave that reasoning unclear.

Suppose an operation promises remote creation followed by a required local refresh. Creation succeeds but refresh fails: remote state has changed, so a full retry needs protection against duplicate creation. Depending on the accepted contract, the owner can retry only refresh, compensate creation, or report an accepted partial result. If none is supported, propagate the failure and remaining remote state to its owner.

Compensation has its own completion and failure outcome; attempting it does not establish rollback. Avoid building a compensation system when direct propagation with known remaining effects or a safe manual retry meets the accepted contract.

## Verify what repeats and what remains

Check the public operation or responsible boundary for the effects it promises to repeat, retain, or compensate. Exercise the stopping bound, failed compensation, and interruption where they can change that outcome.

In the creation example, failed creation must not proceed to refresh. Refresh-only recovery must not create again. Failed compensation must retain both the refresh failure and remaining remote object. Test a stop after creation or during compensation when supported by the path.
