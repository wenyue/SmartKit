# Remediation

Use this reference when designing, changing, or reviewing human remedial actions or cross-role
resolution and feedback responsibilities that require capability, authority, or effort decisions.

## Assign a Feasible Action to an Authorized Actor

Establish who can perform the action from actual access, callers, and expected use, rather than a
module or surface name. The actor needs both capability and authority, and the action's complexity
and effort must be reasonable for that audience. Keep specialist troubleshooting and complex repair
with qualified actors.

Where direct repair is unavailable, offer a feasible supported escalation route when one exists.
If no capable, authorized actor is established, keep remediation unresolved and pause the dependent
design until its ownership is settled.

A runtime prompt may collect a bounded product choice under an established contract. It cannot
resolve a missing development-time data or recovery contract. Investigate available evidence and
obtain the missing decision from its owner before implementing the dependent behavior.

## Connect Feedback to the Resulting State

Distinguish what the audience needs to understand or do from the evidence maintainers need to
investigate. Connect feedback about the resulting state to the feasible action or supported
escalation established for that audience.

For a library or component that transfers handling, follow impact, diagnostic, and remediation
information through its return or failure contract to the caller or established feedback owner.
Delegation must preserve the action's state and completion ownership.

For example, suppose only maintainers have both access and authority for storage repair, while users
have a supported sign-in or support route. Maintainers may need a path and diagnostic evidence to
repair storage; users need the affected capability and their feasible next action. The difference
follows from their responsibilities and access, without prescribing universal channels or audience
roles.

Feedback must accurately reflect the resulting state. Acknowledgement or delegation does not
establish that recovery is complete.

## Own the Action Through Completion

Trace each action from the failed state through successful completion, failure, and any mid-path
stop. Establish the acting owner, final reporter, and feedback owner from evidence. Determine what
state remains, who receives the result, and how feedback changes as the action succeeds or fails.

Use channels appropriate to the audience and environment. An initiated action or displayed prompt
alone does not establish an observable outcome.

Verify meaningful paths through the responsible public boundary, including secondary failures,
cancellation or interruption where applicable. Keep completion, failure, and retained state
observable after ownership transfers.
