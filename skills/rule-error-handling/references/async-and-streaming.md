# Async Work and Streaming

## Keep required work in the completion chain

Return, await, or otherwise observe required work, including every started sibling's failure after another sibling fails. Stop dependent work when its prerequisite fails; settle admitted work and required cleanup before declaring the completion that depends on them.

Detached work needs a completion, failure, recovery, and lifetime owner with enough state and diagnostic context to finish after the initiator is disposed. A detached marker or callback alone establishes none of these responsibilities.

## Separate stopping observation from stopping effects

Establish what cancellation, timeout, shutdown, and disposal actually stop: cancelling a subscription or timing out a wait may leave work in flight. Stop new admission when required, request supported cancellation, and drain or transfer admitted work under its contract to an owner that will remain available.

Use existing lifecycle or operation identity to reject obsolete state publication; recheck mutable preconditions after asynchronous gaps when changes could invalidate the action. A token check cannot undo dispatched writes. Account for them during reset or replacement through ordering, draining, or an established mechanism; add coordination only for a reachable conflict with the accepted outcome.

## Distinguish partial output from completion

A stream may deliver useful output and then fail. Follow its contract for retaining accepted partial output, exposing an unfinished draft, or discarding it. Preserve terminal failure or cancellation and consequential effects; an item, empty result, or closed transport alone does not prove promised completion.

Observe terminal stream errors and cancellation completion. Preserve required backpressure and bounded in-flight work during pause or cancellation, and attempt remaining safe cleanup if an earlier cleanup fails. Preserve primary and secondary failures under the entry's evidence policy.
