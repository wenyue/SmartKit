# Async Work and Streaming

Use this reference when concurrent or deferred work, cancellation, timeouts, late results, or streamed output affect the operation's promise.

## Keep required work in the completion chain

Return, await, or otherwise observe work required for the operation to complete. Observe every started sibling, including failures after another sibling fails. Stop dependent work when its prerequisite fails; settle admitted work and required cleanup before declaring the completion that depends on them.

Detached work needs its own completion, failure, recovery, and lifetime owner. Marking a call detached or installing a callback does not establish these responsibilities. When work intentionally outlives its initiator, give its owner the state and diagnostic context needed to finish without relying on a disposed caller.

## Separate stopping observation from stopping effects

Establish what cancellation, timeout, shutdown, and disposal actually stop. Cancelling a subscription or timing out a wait may leave work in flight. Stop new admission when required, request supported cancellation, and drain or transfer admitted work according to its contract. Keep remaining effects and cleanup failures observable through an owner that still exists.

Use the existing lifecycle or operation identity to reject late results from superseded work before they publish into current state. After an asynchronous gap, recheck mutable conditions this boundary owns when they can invalidate the action. A token check cannot undo a write already dispatched; resets and replacements must account for those writes through ordering, draining, or another established protocol. Add coordination only for a reachable conflict that affects the accepted outcome.

## Distinguish partial output from completion

A stream may deliver useful output and then fail. Establish whether the contract retains that output as an accepted partial result, exposes it as an unfinished draft, or discards it. Preserve the terminal failure or cancellation and consequential effects; receiving an item, an empty result, or a closed transport alone does not establish the promised complete result.

Give terminal stream errors and cancellation completion an observer. Preserve required backpressure and bounded in-flight work when pausing or cancelling. Complete required resource cleanup on success, failure, cancellation, and interruption, attempting remaining safe cleanup when an earlier cleanup fails. Apply the entry's primary and secondary failure policy rather than allowing a cleanup failure to silently replace the incident.

Verify the affected completion boundary with failed siblings, cancellation or timeout, late results, partial output, and cleanup failure where they change its promise. An immediate reset of visible state and a successful cancellation request are separate observations from durable reset or fully settled work.
