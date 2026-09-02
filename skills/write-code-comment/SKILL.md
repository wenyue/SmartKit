---
name: write-code-comment
description: Use when deciding whether code needs a comment, or when adding, editing, or reviewing code comments or documentation comments, so they follow the target project's conventions and explain non-obvious intent, constraints, or behavior.
---

# Write Code Comment

Decide whether a code or documentation comment is necessary, then review or edit it within the
request's authority. A useful comment preserves consequential information that its owning code,
name, type, structure, or documentation cannot express clearly enough.

## Establish the comment's authority

Inspect the relevant implementation and contract together with the target project's current rules,
language conventions, owner documentation, configuration, and applicable maintained comments.
Treat nearby comments as evidence only when their ownership and applicability are credible. Resolve
from those live sources the required language, terminology, form, placement, documentation tags,
directives, markers, and validation; do not substitute remembered syntax or tool lists.

Confirm whether the request authorizes review only, comment edits, or an independently requested
code, name, type, or structural correction, and whether the target is the owned source. Comment
need alone grants no structural mutation. When a structural correction lacks independent request
authority, report the exact correction and owner. For generated or otherwise managed surfaces,
follow the canonical owner's edit and generation route only when those effects are authorized. If
ownership, a necessary convention, or write authority cannot be established, stop and report the
exact missing fact or access rather than changing the surface.

Place each fact with its semantic owner. Caller-visible behavior and public contracts belong in the
project's required API-documentation surface; broader concepts belong in their owning documentation.
Use an implementation comment for local rationale or constraints. Preserve required directives,
generated markers, and protocol tokens exactly unless their owner authorizes a change.

## Decide whether prose earns its place

A comment is warranted when an applicable convention requires it or a future maintainer or caller
would otherwise miss consequential rationale, an invariant, a trade-off, caller-visible behavior,
or a lifecycle, failure, ordering, concurrency, security, compatibility, or protocol constraint.
Subject to the established authority, prefer a name, type, signature, or structural correction
when it can make the fact enforceable or self-evident; otherwise report it instead of explaining
around the defect.

Omit narration, repeated names, edit history, and facts already clear from the immediate code or
owned documentation. Compare every retained comment with the current behavior and contract: update
or remove stale, misleading, or redundant prose, while preserving still-valid non-obvious meaning.

## Review or edit

For review-only work, leave all files and structures unchanged. Report each missing, misleading,
stale, or redundant comment at an actionable location, explain the consequential information or
conflict, and identify the governing evidence. If none is actionable, say so.

For an authorized edit, change only the selected target—comment surface or independently authorized
code, name, type, or structure—and required owner-managed outputs within scope. Express any comment's
missing meaning at its narrowest truthful scope, in the target's established terminology and form.
Keep causal rationale and constraints rather than implementation narration, and preserve required
machine-readable forms and externally defined wording.

When related code changes within scope, keep its comments aligned with the resulting behavior. When
the code or owning contract appears wrong but is outside scope, preserve it and hand off the exact
conflict and owner rather than making the comment assert intended behavior as fact.

## Validate and hand off

Use checks declared by the live owner for every selected authorized target—comment, code, name,
type, or structural change—and required owner-managed output, within the authorized effects.
Report each target's checks and results. If no relevant check exists for a selected target, mark
that target untested. If a required check is unavailable or fails, report the blocker or failure
and do not claim completion.

Completion requires the requested review or authorized edits, preservation of owned requirements,
and successful required validation. Hand off changed or reviewed locations, consequential
no-comment decisions for requested or reviewed locations, the non-obvious meaning preserved,
governing evidence, validation status, and every remaining uncertainty, ownership conflict,
blocked action, or out-of-scope correction.
