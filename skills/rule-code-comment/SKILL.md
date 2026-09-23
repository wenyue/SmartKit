---
name: rule-code-comment
description: Use for work involving code or documentation comments, including coverage decisions and requested assessment.
---

# Code Comments

Strength: `Default`

Scope: Code and documentation comments affected by development or review across languages, and
requested assessment or maintenance of those comments.

## Select useful information

Meet explicit coverage requirements; otherwise judge coverage from purpose, actual use and sharing
boundaries, contract and behavioral complexity, what names, types, signatures, and code already
explain, and comparable local comment presence, absence, style, detail, and visual coherence.
Weigh these together without a fixed priority or a presumption that local practice decides the
answer.

Explain significant caller obligations, invariants, lifecycle constraints, and edge cases that
would otherwise remain unclear. Give shared and externally consumed contracts deliberate attention
even with one caller. Public visibility alone does not require a comment, and straightforward local
code may need none. Adding or omitting one need not establish that neighboring choices are wrong.

## Establish meaning and destination

Ground each judgment in the current implementation and its owning contracts. Expand the evidence
when uncertainty could change the comment or its validation. If implementation and contract
conflict, resolve the conflict within authorized scope or report it and its owner; describe actual
behavior truthfully rather than presenting the intended contract as implemented.

Distinguish API documentation from implementation comments by purpose, wherever they appear. API
documentation explains the caller's contract. Place local reasons, constraints, and tradeoffs with
the implementation, and broader concepts in their owning documentation. Choose the useful
destination, then establish authority to change it. Recommend out-of-scope corrections or moves;
remove an original explanation only when its meaning is safely represented at an authorized
destination.

## Write for an experienced colleague

Unless the target specifies otherwise, assume a reader who knows the language and framework but
not this implementation. Begin with concrete responsibility or behavior, then explain significant
constraints on correct use. Select the relevant obligations and reasoning in proportion to the
reader's need. A longer account can clarify important relationships; sparse section labels can
make coherent parts easier to find without supplying hidden knowledge.

Use natural, precise, ordinary language. Omit generic praise, line-by-line narration, redundant
names, and edit history. Follow the target's documentation language, syntax, and explicit formatting
requirements. Observed habits inform expression without becoming requirements; where no convention
applies, use an established native comment mechanism.

Correct or remove stale and redundant prose while preserving still-valid meaning, including meaning
already clear in code or another owning surface. Keep required machine directives, generated
markers, protocol tokens, machine-readable forms, and externally fixed wording intact. Read the
result alongside the code across relevant paths for usefulness, directness, and accuracy. Optional
[contrasting examples](references/examples.md) illustrate information selection and voice; they
supply neither policy, prescribed formats, nor facts about the target.

## Apply and finish within the task

Establish the task's locations, owners, and review or edit authority. Complete authorized comment
edits, keeping related comments aligned with independently authorized code changes. Comment work
alone authorizes no changes to code, names, types, or structure; assessment-only work leaves files
and structures unchanged. For managed or generated surfaces, establish the canonical edit route
and authority for its effects and required outputs before editing.

Ordinary work uses the parent task's validation and handoff without a separate comment audit,
report, or subagent process. For requested assessments, cover the requested boundary under the
coverage and evidence policy above. Report actionable missing, misleading, stale, or redundant
comments at precise locations, with their consequential meaning or conflict and governing evidence.
Include relevant recommended moves or structural corrections and their owners. A no-finding
conclusion applies only to the assessed boundary.

For dedicated work, run relevant available owner-supported checks, including all required checks
for authorized targets and managed outputs. Add proportionate checks when they materially improve
confidence in the change or a likely regression. Finish with owned requirements preserved; failed
or unavailable required checks leave the work incomplete. Hand off covered locations, consequential
decisions and evidence, actual validation results, and any incomplete coverage, untested targets or
paths, uncertainty, blocked action, ownership conflict, or out-of-scope recommendation concisely.

If necessary evidence, a required resource, ownership, a target requirement, access, or authority
cannot be established, report the exact gap and pause dependent actions and conclusions. Continue
independent authorized work where the owning workflow permits it.
