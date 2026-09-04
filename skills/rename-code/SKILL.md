---
name: rename-code
description: Rename exactly one established code symbol or tracked repository path, including a public name, and update every real in-scope reference without changing unrelated identities or behavior.
---

# Rename Code

Rename one established code symbol or tracked repository path from `old` to `new`. Identity, not
shared spelling, defines the change.

## Principles

- **Identity first.** Resolve the declaration or tracked path before searching for references.
  Distinguish it from unrelated homonyms and overloaded, shadowed, inherited, or generated
  identities.
- **Compatibility first.** An externally observable name is a contract. Before editing, require an
  approved breaking rename, staged migration, alias, adapter, or no-change decision.
- **Proportional completeness.** Follow every confirmed use of the identity, while widening discovery
  only when repository evidence shows that relevant surfaces may remain.
- **One-purpose change.** Preserve behavior and keep adjacent refactoring, cleanup, and unrelated
  renames outside the change.
- **Evidence-based finish.** A new spelling is not proof of a completed rename. Close the work through
  renewed identity-aware discovery and every required owner check.

## 1. Establish the rename

Record one old name, one new name, the target identity, intended scope, and exact authority for every
required effect. Locate the identity-bearing declaration or tracked path; rule out a collision with
a different symbol or path; identify any generated owner and supported generator; and establish the
owner-required checks and their executable routes.

For a public API or any name observed through callers, persisted data, configuration, protocols, or
published interfaces, establish the approved compatibility decision before writing. Keep
serialization keys, protocol fields, database columns, persisted names, and configuration keys
unchanged unless the approved rename explicitly includes them. Do not invent compatibility policy.

Discover references in proportion to the target:

- For symbols, prefer semantic references when they cover the relevant language and build context.
  Otherwise combine lexical search with inspection of imports, call sites, type use, inheritance,
  registration, reflection, and other identity-bearing structures.
- Inspect dynamic strings, generated code, cross-language use, scripts, tests, documentation, and
  build or configuration files when evidence connects them to the target.
- For paths, inspect the repository tree and index together with imports, manifests, links, and
  case-sensitive references. Text search alone does not establish complete path coverage.

Begin with identity-bearing surfaces and the necessary integration context. Widen only when
unresolved references, repository structure, build metadata, generated ownership, or check failures
indicate that the identity may reach farther. Shared spelling alone does not justify inventorying
unrelated repository surfaces.

Stop before writing if the target, scope, or authority is unresolved; an observed name lacks an
approved compatibility decision; the destination collides; generated surfaces lack an established
canonical owner or usable supported generator; a safe move or required check route cannot be
established; or the compatibility decision requires no change. Report the blocking fact or decision
and its owner.

## 2. Rename the identity

Rename the declaration or tracked path and every confirmed in-scope reference to that identity. Use
a semantic rename when its coverage is trustworthy; otherwise make the evidence-backed edits
explicitly.

Where applicable:

- change generated surfaces only through their canonical source and supported generator;
- move tracked paths with the repository's version-control mechanism, using a unique temporary name
  for a case-only rename on a case-insensitive filesystem;
- apply only the approved compatibility measure through its owning interface or module; and
- update tests, comments, documentation, examples, user-visible text, and identity-bound filenames
  only when they refer to the renamed identity.

Order actions only where safety or repository tooling requires it, such as updating a generator
before regeneration or establishing the temporary path before a case-only destination.

The target project's governance and the accepted request own all reads, writes, and commands. This
Skill authorizes only the rename and its necessary same-identity reference, generated, test, and
documentation changes. It does not authorize discarding, stashing, resetting, or overwriting user
work; editing canonical generated output directly; committing, pushing, publishing, releasing,
deploying, creating a worktree, using the network, or performing remote actions.

## 3. Verify the result

Repeat the relevant identity-aware discovery after editing. Search the affected surfaces and
necessary integration context for the old name, widening only when evidence indicates incomplete
coverage. For paths, inspect the tree, index, and path references again. Classify every remaining
occurrence that could plausibly denote the target as:

- an intentional preserved contract;
- an unrelated identity;
- a missed in-scope reference; or
- unresolved.

Group unrelated homonyms when common evidence supports the classification; a per-occurrence inventory
of low-signal matches does not prove correctness. Correct a missed reference only when current
evidence uniquely determines an in-scope edit, then repeat the affected discovery and checks. Stop
correcting when the evidence no longer improves, no longer determines a unique repair, or requires
broader scope, another compatibility decision, or another owner.

Run every applicable owner-required check for the changed surfaces and material rename risks,
including formatting, static analysis, builds, generated-output verification, and tests where
required. Add broader checks only when repository governance or current evidence makes them relevant.
An unavailable or failing required check prevents completion. If unavailable non-required evidence
leaves no material identity or compatibility risk unresolved, narrow the completion claim and report
the exact untested surface. When compatibility preserves both names, verify the supported behavior of
each.

## Outcomes and handoff

- `COMPLETE` when the target uses the approved name, every confirmed reference uses it or is preserved
  by approved compatibility, no plausible target occurrence remains unresolved, and every applicable
  required check passes. Record any noncritical untested surface that narrows this result.
- `BLOCKED` only before writing, when an establishment requirement is missing.
- `FAILED` after any write when the rename cannot be completed or verified safely, including a failing
  or unavailable required check, unresolved occurrence, exhausted correction, or newly required scope
  or owner action. After a write, `FAILED` takes precedence over a condition that would otherwise be
  `BLOCKED`; preserve the useful partial state and evidence without inventing rollback authority.

Report the mapping and identity; compatibility decision; discovery methods and coverage; changed,
generated, moved, and preserved surfaces; classifications of remaining old-name occurrences and a
summary of unrelated same-name identities; checks and exits; corrections; outcome; and unresolved or
untested surfaces. Group homogeneous resolved occurrences when common evidence supports them, but
locate every unresolved, mixed, or materially exceptional occurrence. For a non-complete result,
also report the exact partial state, stopping evidence, and next owner or decision.
