---
name: rule-code-comment
description: Use for work involving code or documentation comments, including coverage decisions and requested assessment.
---

# Code Comments

Use comments to help a reader understand, use, or maintain the code. Unless the target specifies
otherwise, write for someone who knows the language and framework but not this implementation.

## Decide what deserves a comment

Meet explicit coverage requirements. For coverage and information choices, weigh these questions
together:

- What is this code for, and who actually uses or shares it? Give shared and externally consumed
  contracts deliberate attention even when there is only one caller.
- How complex is the contract or behavior, and what would remain unclear? Explain significant
  caller obligations, invariants, lifecycle constraints, and edge cases that names, types,
  signatures, and code do not adequately convey.
- How does the explanation fit comparable local code? Consider comment presence and absence, style,
  detail, and visual coherence as evidence about the reading experience.

These considerations have no fixed priority; local practice does not decide the answer by itself.
Public visibility alone does not require a comment, and straightforward local code may need none.
Adding or omitting a comment need not imply that neighboring choices are wrong.

## Ground the explanation in the code

Use the current implementation and its owning contracts to establish what is true. Expand the
evidence when uncertainty could change the comment or its validation.

If implementation and contract disagree, resolve the conflict within authorized scope or report it
and its owner. Describe actual behavior truthfully; a comment must not present the intended contract
as though it were already implemented.

## Put information where readers need it

Distinguish comments by their purpose, wherever they appear:

- API documentation explains the caller's contract.
- Implementation comments explain local reasons, constraints, and trade-offs alongside the code.
- Broader concepts belong in their owning documentation.

Choose the useful destination, then establish authority to change it. Recommend corrections or moves
that exceed the task's scope. Remove an original explanation only when its meaning is safely
represented at an authorized destination.

## Write and maintain useful prose

Begin with concrete responsibility or behavior, then explain significant constraints on correct use.
Choose obligations and reasoning in proportion to the reader's need. A longer account can earn its
space by clarifying important relationships; a sparse section label can make a coherent part easier
to find even when it supplies no hidden knowledge.

Use natural, precise, ordinary language. Omit generic praise, line-by-line narration, redundant
names, and edit history.

Follow the target's documentation language, syntax, and explicit formatting requirements. Observed
habits inform expression without becoming requirements. Where no convention applies, use an
established native comment mechanism.

Correct or remove stale and redundant prose while preserving still-valid meaning, including meaning
already clear in code or another owning surface. Keep required machine directives, generated
markers, protocol tokens, machine-readable forms, and externally fixed wording intact.

Read the result alongside the code across relevant paths for usefulness, directness, and accuracy.
For contrasting choices about information and voice, consult the optional
[comment judgment examples](references/examples.md). Their stated contexts make the choices
understandable; they supply neither policy, prescribed formats, nor facts about the target.

## Work within the task

Establish the locations, owners, and review or edit authority. Complete authorized comment edits,
keeping related comments aligned with independently authorized code changes. Comment work alone
authorizes no changes to code, names, types, or structure. Assessment-only work leaves files and
structures unchanged.

For managed or generated surfaces, establish the canonical edit route and authority for its effects
and required outputs before editing.

In ordinary work, use the parent task's validation and handoff. Applying this Rule does not add a
separate comment audit, report, or subagent process.

For a requested assessment, cover the requested boundary using the coverage and evidence guidance
above. Report actionable missing, misleading, stale, or redundant comments at precise locations.
Explain their consequential meaning or conflict and the governing evidence; include recommended
moves or structural corrections and their owners where relevant. A no-finding conclusion applies
only to the assessed boundary.

For dedicated comment work, run relevant available owner-supported checks, including every required
check for authorized targets and managed outputs. Add proportionate checks when they materially
improve confidence in the change or a likely regression. Completion requires preserved owned
requirements and passing required checks; a failed or unavailable required check leaves the work
incomplete.

For dedicated work, hand off covered locations, consequential decisions and evidence, actual
validation results, and remaining limitations concisely. Include incomplete coverage, untested
targets or paths, uncertainty, blocked action, ownership conflicts, and out-of-scope recommendations.

If necessary evidence, a required resource, ownership, a target requirement, access, or authority
cannot be established, report the exact gap and pause dependent actions and conclusions. Continue
independent authorized work where the owning workflow permits it.
