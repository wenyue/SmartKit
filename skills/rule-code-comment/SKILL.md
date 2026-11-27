---
name: rule-code-comment
description: Use when writing or reviewing code and documentation comments, assessing their coverage, or editing, moving, or removing comments during a refactor. Also use when a user specifies or confirms code behavior, when recording or reviewing such decisions, or when a fix depends on a constraint a maintainer could easily overlook.
---

# Code Comments

Write for the person who will call or change the code. Unless the project identifies another audience, assume the reader knows the language and framework and is meeting this implementation for the first time.

## Decide what the reader needs

Consider what a reasonable reader might do after reading the names, types, implementation, and existing documentation. Could they retry an operation unsafely, remove an apparently unnecessary check, or open a repair task for a deliberately accepted limitation? Explain the missing fact where it would change that decision. An existing explanation that gives the reader what they need is sufficient.

Honor explicit documentation requirements. Elsewhere, judge coverage by the code's purpose and users, the difficulty of its contract, and the reading experience in comparable code. A storage interface with a single caller can have retry obligations that deserve careful documentation. A public getter can be clear from its name and body. Nearby comments help establish useful style and detail without setting a quota or implying that neighboring code needs editing.

Consider the need for a comment in the course of implementation, fixes, and review. When the user specifies or confirms behavior, check what a later reader could infer without that conversation. When a fix or review correction turns on a subtle invariant, framework guarantee, or design choice that someone could readily undo, explain the verified basis beside the affected code. An adequate existing note, including one explaining a temporary shortcut, can serve that purpose.

## Establish what is true

Read the relevant paths and the contract that owns the behavior. Follow up on uncertainty that could change the explanation or its verification. If the code disagrees with its contract, describe the discrepancy accurately. Resolve it within the authorized task or report it to the owner. A comment promising the intended behavior would hide the discrepancy.

Ground a surprising trade-off in the implementation and its owning contract. Explain the behavior, the verified reason for retaining it, where it applies, and any material risk that remains. If the reason is unknown, say so. When describing or relying on a choice as explicitly accepted, consult relevant comments and referenced decisions and verify that claim against the decision itself. An accepted defect still carries its consequences, and a lasting choice needs no invented deadline for replacement.

Use those same bounds in review. An explicitly accepted consequence that still matches the decision needs no fresh repair item. New evidence, changed conditions, or effects outside the accepted scope deserve assessment on their own merits.

## Put the explanation at its owner

Document caller obligations and observable behavior at the API. Distinguish outcomes callers may encounter from guarantees they can rely on. Include significant invariants, lifecycle obligations, and edge cases a caller needs to act on. For a failure that affects a caller's choice, explain when it occurs, any stable way the contract provides to recognize it, and what state or partial result remains. This applies to returned errors, exceptions, and failures intentionally propagated from another layer. Promise an error type, category, or identity only as far as the contract supports it.

Keep implementation reasons, constraints, and trade-offs beside the code a maintainer might otherwise change. Put broader concepts in the documentation that owns them. A decision can affect both callers and maintainers. Give each audience the part it needs, reusing an adequate account at its owner.

Establish which locations the task authorizes you to edit. Complete authorized comment edits and keep them aligned with related code changes. In a comment-only task, every code change requires separate authorization, including edits that preserve behavior. For managed or generated content, establish the canonical edit route and authorization for its effects and required outputs. Recommend a move or correction that exceeds your authority, identifying the appropriate owner.

## Write and revise the whole comment

Use plain Google-style explanatory prose by default. Lead with the responsibility or behavior, then explain what matters for correct use or maintenance. Use the project's documentation language, syntax, and required formatting, or the language's native comment convention where no project convention applies. Use an established marker when it does a job, such as a `TODO` for a specific follow-up.

Choose detail to suit the reader. A brief section label can help someone find a coherent operation in a long function. A recovery algorithm may need several sentences to explain how an ordering decision prevents data loss. Omit generic praise, restatements of names, line-by-line narration, and edit history. State the necessary facts directly. Omit links and references to the project's own issues and pull requests, including their numbers. A repository decision document, external standard, or third-party issue can supply background if the comment stands on its own.

When touching a comment, read the whole affected block against the current code. Integrate the change, combine related points, and correct or remove stale or redundant prose. Before removing an explanation, make sure its still-valid meaning is clear in the code or documentation that owns it. Keep required directives, generated markers, protocol tokens, machine-readable forms, and externally fixed wording intact.

When a refactor changes where an explanation belongs or which parts still apply, preserve each trade-off that remains in effect and its rationale in the code or documentation that now owns it. Moving code can change where readers need the explanation even when the original comment stays in place.

After any comment edit, read the result alongside the relevant code paths for accuracy and usefulness. For examples of how much to say and where, consult the optional [comment judgment examples](references/examples.md).

## Verify within the task

Use the parent task's checks and handoff for everyday code changes. Applying this rule adds no separate audit, report, or delegation step.

For a requested assessment, keep the work read-only and cover the requested boundary. Locate actionable omissions and misleading, stale, or redundant comments precisely. Explain the consequence and supporting evidence, including the owner of any recommended move or structural correction. Limit a no-finding conclusion to the area actually assessed.

For dedicated comment edits, run relevant owner-supported checks, including every required check for the authorized sources and managed outputs. Add a check when it materially improves confidence in the change or catches a likely regression. Report the locations covered, consequential decisions and evidence, actual check results, and any remaining uncertainty, untested paths, or work outside the authorized scope. Completion requires preserved target requirements and passing required checks.

When evidence, ownership, authority, target requirements, access, or a required resource or check is missing, identify the specific gap. Pause the actions and conclusions that depend on it and continue independent authorized work. Report a failed or unavailable required check as incomplete verification.
