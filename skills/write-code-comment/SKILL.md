---
name: write-code-comment
description: Use when writing or materially revising code comments during development, or for dedicated code-comment or documentation-comment assessment, review, completion, cleanup, or migration. Explicit invocation remains available.
---

# Write Code Comment

Use this Skill once ordinary development needs comment writing or material revision, or for a
dedicated comment task. Select the branch from the requested scope, including explicit invocation:

- **Ordinary development:** apply the writing guidance and safeguards within the authorized code
  task, using that task's validation and handoff. This does not start a separate comment audit,
  report, or subagent process.
- **Dedicated comment work:** apply the writing guidance and safeguards, then follow the dedicated
  workflow below.

## Writing guidance

Write like a maintainer explaining the implementation to an experienced colleague. Unless the target
specifies otherwise, assume the reader knows the language and framework but not this implementation.
Ground the account in the code and owning contracts; expand the evidence when uncertainty could
change the wording or its validation. Express actual behavior and caller obligations truthfully.

**Information and organization.** Explain concrete responsibilities or behavior first, then the
significant constraints on correct use. Select the relevant invariants, lifecycle obligations,
external requirements, or edge cases without inventorying every possible concern.

API documentation explains the caller's contract; internal comments explain the implementation.
Distinguish them by purpose, wherever they appear. Put local reasons, constraints, and tradeoffs with
the implementation and broader concepts in their owning documentation. Choose the useful
destination before determining whether the task authorizes changing it. Sparse section labels can
improve reading and visual organization without revealing hidden knowledge.

**Expression and form.** Use concrete, ordinary words and begin with the substance, rather than a
generic evaluation such as “a robust and flexible helper.” Let sentences and length fit the
explanation, including a longer account when the reader needs the relationships or reasoning.
Omit line-by-line narration, redundant names, and edit history.

Use the target's documentation language, syntax, and explicit formatting requirements. Observed
habits inform expression but are not requirements; where no convention applies, use an established
native comment mechanism. Preserve still-valid meaning when revising or removing prose, including
meaning already clear in code or another owning surface. Keep required machine directives,
generated markers, protocol tokens, machine-readable forms, and externally defined wording intact.

For optional calibration while writing or performing a requested assessment, consult the relevant
[contrasting examples](references/examples.md). They illustrate information selection and voice,
not coverage policy, prescribed formats, or facts about the target.

**Final read-through.** Read the comments alongside the code as the intended colleague. Check that
the selected information is useful, the wording is direct, and the account remains accurate across
the relevant paths. Keep still-useful explanations and remove stale or redundant prose.

## Scope and edit safeguards

Work within the authorized locations and effects. Comment work alone does not authorize changes to
code, names, types, or structure; recommend necessary corrections outside that scope. Review-only
requests leave files and structures unchanged.

For generated or otherwise managed surfaces, establish the canonical edit route and the authority
for its required effects before editing; include required outputs only within that authority. If
material ownership, an applicable target requirement, a necessary resource, access, or authorization
cannot be established, stop the dependent action and report exactly what is missing. Continue
independent authorized work, keeping claims within the available evidence.

For relocation, remove the original only once its meaning is safely represented at the authorized
destination. Recommend out-of-scope moves while retaining information that cannot yet be safely
relocated. When implementation and the owning contract conflict, resolve the conflict only within
authorized scope; otherwise report it and its owner without presenting intended behavior as
implemented.

## Dedicated comment workflow

Establish whether the request authorizes review only or edits, and identify the target locations and
owners. Judge the requested coverage against independently applicable documentation requirements
and the current implementation and contract evidence.

### Review only

Cover the requested locations. Report actionable missing, misleading, stale, or redundant comments
at precise locations, with their consequential meaning or conflict and governing evidence. Include
recommended moves or structural corrections with their owners when relevant.

If nothing is actionable, say so within the reviewed boundary. Identify incomplete coverage and
untested paths rather than extending a no-finding claim beyond the evidence.

### Authorized edits

Add, revise, remove, or relocate comments to complete the scoped outcome, applying the writing
guidance and scope safeguards. Keep related in-scope comments aligned with independently authorized
code changes, then perform the final read-through.

### Validate and hand off

Run relevant available owner-supported checks, including every required check for authorized targets
and required managed outputs. Add proportionate checks only when they materially improve confidence
in the change or a likely regression. Record what was checked and the result; identify untested
targets when no relevant check exists. If a required check is unavailable or fails, report the
blocker or failure and keep the work incomplete.

Complete the authorized review or edits with owned requirements preserved and required validation
successful. Give a concise handoff of reviewed or changed locations, consequential decisions and
supporting evidence, validation status, and any incomplete coverage, uncertainty, blocked action,
ownership conflict, or recommended out-of-scope correction.
