# Soft-Isolated Role Adapter

Soft isolation is a prompt-enforced behavioral access contract for shared authoring. It is not a
hard filesystem or security boundary.

## Probe mechanics

This Adapter requires an executable launch and access Probe.

Use the same fresh, no-inherited-turn launcher selected for shared roles for one disposable launch
and access Probe. Prompt it to
follow a unique control, report supplied context and available tools, and avoid file and network
access and delegation.

Before every Probe, Author, Reviewer, or Runner invocation—initial launch or later resume—freeze a
versioned expected-operation manifest for that exact invocation. It contains the complete
Controller-supplied prompt and context for the invocation, including any Repair Scope, Context
Supplement, access update, or Runner evidence, plus every prompt-authorized tool, file, and access
grant. Bind the manifest version to the invocation and its output. Require the invocation's
self-report to separately identify physically available tools and acknowledge the authorized subset
and boundaries. A physically available superset is not by itself a mismatch.

Before consuming any Probe, Author, Reviewer, or Runner output, compare the self-report and any
available launcher or host evidence against the manifest version bound to that exact invocation and
make a per-invocation behavioral audit decision. PASS only when Controller authority, supplied
prompt and context, and prompt-authorized grants agree with that manifest and the evidence
sufficiently supports the boundary. Available abnormal or no-report launcher or host evidence may
substitute for the self-report only when sufficient. An unexplained mismatch, missing manifest
binding, or insufficient evidence terminally invalidates the Adapter, and the output is not
consumed. Retain the comparison as transient Role Boundary Audit evidence. Host evidence is optional
corroboration; no host hook is required. This is behavioral evidence, not proof of physical
visibility or isolation.

Before any role launches, qualification must also establish that the selected launcher can end
every fresh Runner and establish quiescence after normal, failed, abnormal, or non-returning
execution. Fail when this capability is not proven, parent-turn content is reported, the control is
not followed, the instruction-authoritative Controller channel or bounded updates cannot be
preserved, Candidate or evidence payload can override that channel, or the Probe contradicts any
statically established persistence, access, or capacity capability. Qualification reaches a
bounded pre-launch outcome: it passes only when all conditions hold; otherwise it fails without
launching roles. The Controller runs it after static PASS; qualification and later Acceptance
evidence remain transient and are not written into the Candidate.

## Build role contracts

Apply the loaded public Role Launch Interface and role contracts. Limit each shared role to its
complete prompt, required declared semantic context, and minimum prompt-authorized repository use:
candidate and owned resources for the Author, candidate and declared dependencies for Reviewers,
and those declared shared inputs plus the frozen case and fixture for a Runner.

Beyond each role's allowlist, that role does not read source-project Rules, Skills, context
documents, unrelated files, or parent conversation. It does not use the network or delegate.

This Adapter never grants network access or authority for external effects. A required Acceptance
case that needs either stops as `EXECUTION_UNAVAILABLE` under the public Acceptance contract.

For Acceptance, apply the loaded public attempt lifecycle unchanged with the case's exact file,
tool, and machine-check grants prompt-authorized.

Apply the public preauthorized update envelope. An otherwise eligible Context Supplement or access
expansion must also preserve shared source-context exclusion and declared dependency closure.
Refuse one that reveals source-project private content, an unrelated path, or an undeclared
dependency.

## Adapter invalidation

Any observed out-of-contract read, write, create, delete, tool call, network action, or delegation
invalidates the Adapter and is a terminal audit violation. Prompt compliance is evidence for
authoring independence, not a security claim.
