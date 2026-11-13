# Retries and Side Effects

Use this reference when retry, compensation, or any other recovery depends on effects that may have happened, may repeat, or may remain after interruption.

## Establish which effects happened

Trace consequential writes, remote mutations, held resources, notifications, and visible state through the failed step and any recovery. Include in-flight work and effects whose outcome is uncertain. Establish what remains after cleanup, compensation, cancellation, or interruption, and who owns that state. Inspect the native failure mechanism when a secondary failure could replace the first error or obscure a retained resource.

## Make the whole replay path safe

Examine the complete replay path, including restoration and compensation, for repeated or irreversible effects.

A reusable checkpoint needs evidence that arguments, current state, resources, and already completed effects still permit the promised result. Establish any idempotency or compensation the full replay path requires. Explain why retry is safe beside the replay logic when code, types, and referenced contracts leave that reasoning unclear.

Suppose an operation promises remote creation followed by a required local refresh. Creation succeeds but refresh fails: remote state has already changed, so a full retry needs protection against duplicate creation. Depending on the accepted contract, the owner could:

- Retry only the refresh.
- Compensate the creation.
- Report an accepted partial result.

If the contract supports none of these options, propagate the failure and remaining remote state to its owner.

## Verify what repeats and what remains

Check the public operation or responsible boundary for the effects it promises to repeat, retain, or compensate. Exercise the stopping bound, failed compensation, and interruption where they can change that outcome.

In the creation example, failed creation must not proceed to refresh. Refresh-only recovery must not create again. Failed compensation must retain both the refresh failure and the remaining remote object. Test a stop after creation or during compensation when supported by the path.
