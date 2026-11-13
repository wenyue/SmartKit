# User Recovery

Use this reference when users or other human actors receive failure feedback, retry, repair state, or take over unresolved work.

## Leave a practical way to proceed

Preserve input, drafts, completed work, and still-valid visible state as the operation's contract requires. A failed refresh need not erase useful prior content; a rejected save need not close the editor. Make stale or unsaved status clear when it matters. Restore interaction after failure or refusal when retry or another supported action remains available, using the existing UI state and lifecycle rather than a second recovery state machine.

Offer the simplest supported action that can help, such as waiting, retrying a safe unfinished step, signing in, choosing a valid location, or contacting the responsible operator. Explain the relevant cause, impact, resulting state, and action in terms the audience can use. Include technical detail, such as an affected path, when it helps them understand or act.

## Assign human repair to someone who can perform it

Rely on human remediation only when the actor has the access, authority, tools, and ability to act with reasonable effort. Identify that actor from the actual deployment and audience. Operators normally own infrastructure repair for a staffed service. Client applications normally handle failures within their authority or provide a supported action for ordinary users or a qualified actor.

When direct repair is unavailable, offer a feasible supported escalation route if one exists. If disposition depends on human action and no capable, authorized actor can act, settle ownership and disposition before implementing it. A runtime prompt may collect a bounded choice under an established product contract; missing recovery or data-loss decisions belong with their owner before dependent behavior is implemented.

Carry impact and audience-safe evidence to the receiving actor and establish who owns completion and final feedback. Reporting the failure or displaying a contact instruction alone does not complete that handoff.

## Make remedial completion observable

Keep the remedial action's success, failure, and material interruption visible to those who need to act. Re-enable controls or retain an actionable failure state when the action fails; preserve the original incident and any new failure through their diagnostic owners. Feedback delivery can itself fail: use a feasible established fallback without recursive notifications or replacing the original operation's outcome.

Choose feedback persistence according to the action needed. A transient notification is insufficient when unresolved conditions require later attention and would otherwise become invisible. Verify retained input, usable interaction, supported retry or escalation, and failed remediation at the responsible user boundary.
