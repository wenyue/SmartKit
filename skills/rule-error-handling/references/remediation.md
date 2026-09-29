# Remediation

Use this reference when designing, changing, or reviewing a final disposition that relies on human
action, or when cross-role resolution and feedback responsibilities need to be established.

## Assign a Feasible Action to an Authorized Actor

Establish who can perform the action from actual deployment, access, available tools, callers, and
expected use. Keep specialist troubleshooting and complex repair with qualified actors. Use these
defaults to start that investigation:

- For a service operated by developers or operations staff, the operator is the default remediation
  actor for startup or infrastructure failures. A diagnosable failure routed into their supported
  repair or alert process can be an appropriate disposition. The service's business users are not
  thereby responsible for operating it.
- For a client application, the default human audience is an ordinary user with limited ability to
  inspect or modify internal state. The application must resolve the problem within its authority,
  or provide a supported mechanism enabling the user or a qualified actor to resolve it. Displaying
  an exception alone is insufficient when no feasible action follows.

Actual evidence overrides these defaults: a specialist client may expose suitable repair tools,
while a service may lack an operator with the necessary access. A product label establishes neither
an actor's ability to repair the failure nor permission to do so. Keep concrete product facts and
recovery mechanisms in the project's contracts and policy.

Where direct repair is unavailable, offer a feasible supported escalation route when one exists.
If no feasible action by a capable, authorized actor is established, keep remediation unresolved
and pause the dependent design until its ownership and disposition are settled.

A runtime prompt may collect a bounded product choice under an established contract. It cannot
resolve a missing development-time data or recovery contract. Investigate available evidence and
obtain the missing decision from its owner before implementing the dependent behavior.

For example, a deterministic reconstruction failure on unchanged persisted data will recur on
later reads. If an ordinary client user cannot inspect or repair that data, transferring the
exception to that user alone leaves a repeating failure. Select repair, explicit degradation or
isolation, or supported escalation according to the data contract, preserving data whose loss is
unauthorized. An accepted degraded result must keep the failure and its material impact visible;
neither catching the exception nor keeping the bytes establishes a complete disposition. Apply the
entry's persisted-data and recovery branches when their conditions hold. This is a final human-facing
disposition decision; internal layers may still propagate through their accepted contracts.

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
