---
name: write-code-comment
description: Use for dedicated code-comment or documentation-comment assessment, review, completion, cleanup, or migration. Incidental commenting during feature work does not trigger this Skill; explicit invocation remains available.
---

# Write Code Comment

Complete a dedicated comment assessment, review, completion, cleanup, or migration within the
requested scope. Use this workflow when comment work is the task or the user explicitly invokes it;
ordinary incidental commenting during feature work stays within that work's workflow.

## Principles

- **Evidence-based judgment.** Ground decisions in the implementation, contracts, applicable target
  requirements, and comparable local evidence. Distinguish explicit requirements from observed
  habits, which inform judgment without binding it.
- **Information ownership.** Route caller contracts to API documentation, local reasons to the
  implementation, and broader concepts to their owning documentation. Routing identifies the right
  destination; it grants no authority to change it.
- **Proportionate changes.** Make the coherent changes needed for the authorized outcome. Comment
  work alone does not authorize changes to code, names, types, or structure; recommend those
  corrections when they fall outside scope.

## Establish the decision

Establish whether the request authorizes review only or edits, and identify the target locations and
owners. Inspect the implementation, contracts, applicable documentation requirements, comparable
nearby code and comments, and native comment mechanisms needed to decide the comment's need, form,
content, and destination. Expand the evidence when a remaining uncertainty could change the action
or its validation. If no applicable convention exists, use a reliably established native mechanism;
that absence alone is not a blocker.

For generated or otherwise managed surfaces, establish the canonical edit route and the authority
for its required effects before editing. If material ownership, a required convention, or necessary
access or authorization cannot be established, stop the dependent action and report exactly what
is missing. Continue independent authorized work, keeping claims within the available evidence.

## Review or edit

### Review only

Leave files and structures unchanged. Cover the requested locations and the implementation or
contract paths materially needed to judge them. Report actionable missing, misleading, stale, or
redundant comments at precise locations, with their consequential meaning or conflict and governing
evidence. Include recommended moves or structural corrections with their owners when relevant.

If nothing is actionable, say so within the reviewed boundary. Identify incomplete coverage and
untested paths rather than extending a no-finding claim beyond the evidence.

### Authorized edits

Apply the target's documentation requirements and the established evidence to add, revise, remove,
or relocate comments within scope. Express meaning truthfully in the target's terminology and form.
Preserve still-valid meaning during cleanup or migration, including when removing prose whose
meaning is already clear in code or another owning surface. For relocation, remove the original
content only once it is safely represented at the authorized destination. Recommend out-of-scope
moves while retaining information that cannot yet be safely relocated.

Preserve required machine directives, generated markers, protocol tokens, machine-readable forms,
and externally defined wording. Follow the authorized canonical route for managed surfaces and
include required outputs only within that authority. Keep related in-scope comments aligned with
independently authorized code changes.

When implementation and the owning contract conflict, resolve the conflict only within authorized
scope. Otherwise, report the conflict and owner without presenting intended behavior as implemented.

## Validate and hand off

Run relevant available owner-supported checks, including every required check for authorized targets
and required managed outputs. Add proportionate checks only when they materially improve confidence
in the change or a likely regression. Record what was checked and the result; identify untested
targets when no relevant check exists. If a required check is unavailable or fails, report the
blocker or failure and keep the work incomplete.

Complete the authorized review or edits with owned requirements preserved and required validation
successful. Give a concise handoff of reviewed or changed locations, consequential decisions and
supporting evidence, validation status, and any incomplete coverage, uncertainty, blocked action,
ownership conflict, or recommended out-of-scope correction.
