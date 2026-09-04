---
name: write-code-comment
description: Use when deciding whether code needs a comment, or when adding, editing, or reviewing code comments or documentation comments, so they follow the target project's conventions and explain non-obvious intent, constraints, or behavior.
---

# Write Code Comment

Decide whether a code or documentation comment is necessary, then review or edit the authorized
surface. A useful comment preserves consequential meaning that the owning code, name, type,
structure, or documentation cannot express clearly enough.

## Principles

- **Meaning over narration.** Preserve non-obvious rationale, invariants, trade-offs, behavior, and
  constraints. Omit prose that merely restates the code, repeats names, or records edit history.
- **Semantic ownership.** Put each fact where it belongs: caller-visible contracts in the required
  API-documentation surface, broader concepts in their owning documentation, and local rationale or
  constraints beside the implementation.
- **Grounded judgment.** Judge comments against the current implementation, contracts, project
  conventions, and owner-supported language or toolchain mechanisms. Nearby comments are evidence
  only when their ownership and applicability are credible.
- **Exact authority.** Distinguish review-only work, comment edits, and independently authorized
  changes to code, names, types, or structure. The need for a comment grants no structural
  authority.
- **Durable truth.** Keep comments aligned with owned behavior and preserve required directives,
  generated markers, protocol tokens, machine-readable forms, and externally defined wording.

## Establish the decision

Inspect the implementation, contracts, project conventions, owner documentation, and native
comment mechanisms needed for the requested surface. Expand the evidence only when a remaining
uncertainty could change the comment's need, owner, form, routing, validation, or truth. If the
project has no applicable comment convention, use a reliably established native mechanism; that
absence alone is not a blocker. State any evidence boundary that limits the resulting claim.

Confirm the authorized mode and target owner before acting. For a generated or otherwise managed
surface, follow its canonical edit and generation route only when those effects are authorized. If
the selected action requires ownership, a mandatory convention, or write authority that cannot be
established, stop and report the exact missing fact or access.

## Judge and act

A comment earns its place when an applicable convention requires it or a future maintainer or
caller would otherwise miss consequential rationale, an invariant, a trade-off, caller-visible
behavior, or a lifecycle, failure, ordering, concurrency, security, compatibility, or protocol
constraint.

Prefer an independently authorized name, type, signature, or structural correction when it makes
the fact enforceable or self-evident. Without that authority, preserve the structure and hand off
the exact correction and owner rather than explaining around the defect.

Stale, misleading, redundant, or purely narrative prose does not earn its place; still-valid
non-obvious facts and protected forms do.

### Review only

Leave files and structures unchanged. Cover the requested locations and the implementation or
contract paths materially needed to judge them. Report each actionable missing, misleading, stale,
or redundant comment at a precise location, with the consequential meaning or conflict and its
governing evidence.

When the available evidence cannot support exhaustive coverage, state the covered boundary and
untested remainder; make no broader no-finding claim. If nothing is actionable within that boundary,
say so.

### Authorized edits

Change only the selected comment surface or independently authorized code, name, type, or structure,
plus required owner-managed outputs within scope. Remove or update prose that does not earn its
place while preserving its still-valid meaning and protected forms. Express missing meaning at its
narrowest truthful scope in the target's established terminology and form. Keep related in-scope
comments aligned with any code change.

When the implementation or owning contract appears wrong but lies outside scope, preserve it and
hand off the exact conflict and owner rather than making the comment present intended behavior as
fact.

## Validate and hand off

Run every owner-required check for the authorized targets and their required owner-managed outputs.
Add the least burdensome owner-supported checks that materially increase confidence in changed
behavior or a likely regression. Report each check, covered target, and result. Mark a selected
target untested when no relevant check exists; if a required check is unavailable or fails, report
the blocker or failure without claiming completion.

Complete the requested review or edits only after owned requirements are preserved and required
validation succeeds. Hand off the changed or reviewed locations, consequential no-comment
decisions, non-obvious meaning preserved, governing evidence, validation status, and every remaining
uncertainty, ownership conflict, blocked action, or out-of-scope correction.
