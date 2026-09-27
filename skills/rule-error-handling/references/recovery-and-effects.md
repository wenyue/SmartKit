# Recovery and Effects

Use this reference when choosing, changing, or reviewing a recovery, retry, compensation, or
accepted partial-completion strategy whose safety depends on effects, replay, or resulting state.

## Establish What Remains After Failure

Compare the promised outcome with the state the operation has actually reached. Trace consequential
effects such as durable writes, remote mutations, held resources, emitted events, and visible state
from their origin through handling transfers to the final owner. Include required asynchronous
completion, cancellation, interruption, and secondary failures. Establish what each owner learns
about the outcome and remaining state; reporting a failure alone does not settle its effects.

Recovery must establish a valid state through feasible, bounded action with authority for its
effects. Establish the accepted loss, its authority, and the outcome if recovery fails.

Distinguish recovery that completes this operation from recovery that only restores future
usability. Compare the proposed disposition with the promise and the decisions callers need to
make. An accepted partial or degraded outcome must disclose its remaining effects; otherwise
retain the failed outcome and state for its owner. Explain recovery rationale, especially loss
authority and retry safety, where code, types, and referenced contracts leave it unclear.

## Make Replay Safe Across the Whole Path

A retry needs a reason the cause can be overcome and a stopping bound. Examine the complete replay
path, including restoration and compensation, for repeated or irreversible effects.

A reusable checkpoint needs evidence that arguments, current state, resources, and already
completed effects still permit the promised result. Establish any necessary idempotency or
compensation rather than assuming that catching a failure makes another attempt safe.

For example, suppose an operation promises remote creation followed by a required local refresh.
Creation succeeds, then refresh fails: remote state has already changed. A full retry requires
protection against duplicate creation. Depending on the accepted contract, the owner could retry
only the refresh, compensate the creation, or report an accepted partial result. If none is
supported, propagate the failure and remaining remote state while the disposition is resolved.
The effect pattern illustrates the decision; it prescribes no single recovery strategy.

Keep cleanup and compensation outcomes distinct from the primary failure. Inspect the native
mechanism when a secondary failure could replace the first error or hide a retained resource.
Preserve useful originating evidence, secondary causes, and remaining state for the final owner.

Follow cancellation and interruption during recovery through the same ownership and state
transitions. A mid-path stop must leave an owned outcome rather than an assumed rollback.

## Verify the Chosen Disposition

Check the strategy through the public operation or responsible boundary. Cover the meaningful
success, initial failure, partial effects, unsupported recovery, recovery success and failure,
stopping bound, and cancellation or interruption paths that exist. Confirm the promised result
and remaining state, including which effects are repeated, retained, or compensated.

In the creation example, failed creation must not proceed to refresh; refresh-only recovery must
not create again. Failed compensation must retain both the refresh failure and the remaining
remote object. Test a stop after creation or during compensation when supported by the path.
Choose checks for the actual effects and contract rather than extending this example to unrelated
failure cases.
