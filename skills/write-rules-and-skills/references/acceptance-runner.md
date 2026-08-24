# Acceptance Runner

This reference owns the common isolation and execution protocol for Ordinary Artifact Acceptance.
The parent Skill owns when Acceptance starts and who may serve as Runner. The selected lifecycle and
semantic-type references own representative cases and scope-specific pass conditions.

## Give one Context Packet

Give the Runner the frozen candidate as runtime would expose it, one triggered task or policy
application, one selected case input, and the complete required context. Keep the expected result,
semantic ledger, diff, author reasoning, findings, Reviewer instructions, and prior case output
outside the packet.

Start every case with a new Soft-isolated Runner and its declared frozen input. Do not let one case's
result become another case's input. When Readiness required a Behavior Control, compare its raw
result with the matching candidate run only after both complete; expose neither result to the other
Runner.

## Apply the artifact

Default to a tool-free Runner. Applying a Rule or a writing or judgment Skill in the returned
response is real Acceptance when that response is the artifact's observable result; writing the
same content to a file adds no evidence.

Provide tools only when the candidate's observable contract requires their real effects. First pass
the matching tool-policy Probe from `soft-isolation.md`, then name every allowed tool, input, path,
and effect in the packet. Candidate-owned tests or fixtures supply any disposable filesystem state;
the authoring workflow creates no general Acceptance workspace.

Use the real public job entry or policy-application seam when available. Run owned deterministic
resources through their public entries. Report supported execution that the environment cannot run
as untested. A controlled walkthrough may explain that surface but cannot replace required real
effects or establish machine PASS.

Run each case once. Repeat an inconclusive or unstable case at most once with a new Soft-isolated
Runner; divergent outcomes fail. Return the observable result and tested or untested surfaces to the
Reviewer without deciding against the undisclosed expected result. Persist no Runner output or case
report.
