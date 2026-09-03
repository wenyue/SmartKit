# Recover a Missing Finalizer Response

This reference routes one absent, interrupted, or unattributable `finish-worktree` response. It
owns no finalizer effect or classification. Enter with the original invocation identity when the
host exposes one, exact frozen input, expected pre-state, reviewed base/`HEAD`/tree, dependency
contract, retained handoffs, and all observed effects.

Use the original host/session and the recovery route supplied by `finish-worktree` to determine
whether that same invocation is live and whether it produced an attributable response. Preserve
its worktree, branches, refs, target state, publication evidence, recovery objects, and unrelated
state while resolving it. Current target contents or tracker state may help observation, but cannot
by itself establish delivery, **Already Delivered**, failure, or permission to retry.

If the original invocation may still run or its effects remain ambiguous, return it as `in-flight`
with the exact missing evidence and next finalizer-owner observation or recovery action. If the
original owner recovers a causally attributable raw response, pass that complete response unchanged
to [`complete-run.md`](complete-run.md)'s sole finalizer-result route. This reference never
authorizes another finalizer invocation or invents a recovery or classification interface.

**Complete when:** the original owner supplies one attributable raw result, or the exact in-flight
attempt and its next owner/action are retained without a second effect by inference.
