# Failure Paths

Read this reference when caller behavior leaves the failure channel or owner unclear, or when
partial effects or remediation actions make recovery non-obvious.

## Read Callers As Evidence

Compare the callee's promise with the decisions its callers actually make:

- If an empty optional value means the record is absent, returning it after a failed read converts
  failure into absence. Determine whether recovery really established the promised absent state or
  whether the caller still needs the failed outcome.
- If callers make different valid decisions for two failures, locate the stable distinction at
  their shared boundary. For a closed business vocabulary, inspect coverage of every contracted
  case. For an open protocol, follow an unfamiliar failure through the unknown-outcome path and
  check that it retains failure and useful cause rather than becoming ordinary business refusal.
  Where every caller aborts identically, investigate whether added distinctions serve any contract.
- For a returned-error library, follow both ordinary results and failed returns into callers before
  proposing local reporting. The library's responsibility may end with faithful contract transfer;
  identify where the independently initiated operation then owns the final outcome.
- For a handler that reports and propagates, follow the failure to the final reporter. Determine
  whether the earlier output supplies complementary context or duplicates the incident. Conversely,
  when a handler consumes a failure, inspect how it completes the handling responsibility: a global
  observer will no longer receive that failure.
- A launched asynchronous operation can let its initiator report success before required work
  finishes. Determine whether the promise includes its completion, then inspect the completion
  chain or the detached operation's lifecycle and final failure owner. Follow cancellation and
  interruption through the same state and ownership transitions.
- If work fails while holding a resource and releasing it also fails, inspect the language or
  lifecycle mechanism's actual behavior. Determine whether the final owner can distinguish the
  primary failure, the cleanup failure, and the remaining resource state. A cleanup failure that
  replaces the original cause can conceal the decision the caller still needs to make.

These are reasoning patterns, not conclusions based on syntax. Confirm each meaning from the
current contract, including which production checks enforce it and which diagnostics survive the
target's native failure mechanism.

## Reason From Partial Effects

Identify effects that change recovery: durable writes, remote mutations, held resources, emitted
events, or visible state. Inspect the entire replay path, including restoration and compensation,
before deciding that a retry is safe. A reusable checkpoint needs evidence that its arguments,
state, resources, and already completed effects still permit the promised outcome.

For example, a remote create can succeed before a required local refresh fails. Retrying the whole
operation may duplicate the remote object. An established idempotency key could make replay safe;
otherwise the owner may retry only the refresh, compensate the create, or report a supported partial
outcome. Determine which choice the observed effects and accepted contracts support. If none is
supported, carry the failure and remaining remote state to the final owner.

Verify this scenario through the public operation. Create plus the required refresh should complete
the promise; failed create should not refresh; successful create followed by failed refresh should
retain the created state without claiming full success. For refresh-only recovery, establish that
it issues no second create and stops at the selected bound. For compensation, check both successful
removal and failed removal, retaining the refresh failure and remaining remote object. Include a
stop after create or during compensation when cancellation or interruption can occur there. These
checks follow from the operation's promise and effects, not from a requirement to test unrelated
failures.

## Follow Feedback To Completion

Locate the boundary responsible for feedback and inspect what its audience can understand and
change. For a library or component that transfers handling, follow useful diagnostic, impact, and
remediation details through its return or failure contract to the caller or established feedback
owner. Establish capability and authority from actual access, callers, and expected use, rather than
a module or surface name. For each proposed action, identify a feasible action or supported
escalation route and the impact the audience needs to understand. If no capable, authorized actor is
established, keep remediation unresolved and return the missing decision to the readiness step.

A maintainer may need a path and diagnostic evidence to repair storage; an ordinary user may need
the unavailable capability explained and a supported sign-in or support route. Where the operation
has product feedback, compare it with the resulting state, including material loss or unavailability
even when that user cannot fix it. Keep specialist repair design with the capable owner; a runtime
prompt for a bounded product choice cannot settle a missing development-time data contract.

Trace a reporter call back to the failed state and forward to each remediation action. For a reset
action, inspect who owns completion, what feedback changes on success, and how failure or a mid-path
stop remains observable through the environment's supported channel. Delegating feedback must leave
the action's state and completion owned. Check diagnostics separately: useful operation context,
impact, disposition, and available causes should reach the final reporter without credentials or
needless private data. Complementary traces and audience feedback can coexist with one incident
report; successful recovery may still warrant investigation under the project's severity policy.
