# External Operations

## Establish the outcome before replay

Identify known and uncertain effects, including in-flight work, held resources, and visible state, before choosing recovery. Establish what remains and who owns it after cleanup, compensation, or interruption. Check native cleanup semantics when they could hide the original failure or a retained resource.

| Evidence | Consequence for handling |
| --- | --- |
| The request was not dispatched. | This attempt caused no remote effect; local preparation may need cleanup. |
| An authoritative response refused the request. | Follow the refusal contract, including effects it permits; keep unrelated infrastructure failures distinct. |
| The request was accepted or an effect confirmed. | Determine whether the promise is complete or still needs acknowledgement or follow-up. |
| The response was lost, timed out, or leaves completion unknown. | Preserve uncertainty; a missing response does not prove that a mutation failed. |

Reconcile uncertainty through a supported status or operation identity when available; otherwise transfer the unresolved outcome before unsafe replay. Prefer retrying only the unfinished step. Use existing idempotency or deduplication guarantees where needed; a fresh attempt identifier may defeat them.

For optional-file access, skip or default only when the caller accepts the native query's possible lookup failure or type mismatch. Let required access expose the actual operation's failures. An existence check supplies neither exclusive creation nor atomic replacement; use an operation with the required guarantee.

## Make the whole replay path safe

Check the full replay path, including restoration and compensation, for repeated or irreversible effects. Arguments, current state, resources, and completed effects must still permit the promised result at the retry point. Establish required idempotency or compensation, and explain replay safety beside the logic when it is otherwise unclear.

If remote creation succeeds but a required refresh fails, a full retry risks duplicate creation. Retry only refresh, compensate creation, or report a partial result when the contract supports it; otherwise propagate the failure and remaining remote state. Failed creation must skip refresh, and refresh-only recovery must not create again.

Compensation has its own completion and failure outcome; attempting it proves no rollback. In the example, failed compensation must preserve both the refresh failure and remaining remote object. Verify stops after creation or during compensation when they can change the outcome.
