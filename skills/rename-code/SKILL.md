---
name: rename-code
description: Rename exactly one established code symbol or tracked repository path, including a public name, and update every real in-scope reference without changing unrelated identities or behavior.
---

# Rename Code

Perform one `old -> new` rename within an approved compatibility boundary. Identity—not spelling—is
the unit of change.

## Principles

- Identify the target before matching its spelling. Separate unrelated homonyms and overloaded,
  shadowed, inherited, or generated identities.
- Treat a rename as a contract change when external callers, persisted data, configuration,
  protocols, or published APIs can observe the name.
- Prefer the repository's semantic rename, version-control move, generator, and verification tools.
  Tool choice is a matter of informed judgment, not a prescribed sequence.
- Keep the change about the rename. Do not fold in adjacent refactoring or cleanup.
- Preserve behavior unless the approved scope explicitly says otherwise.

## Establish the rename

State exactly one target, its old and new names, intended scope, and authority for every required
effect. Locate the declaration or tracked path that establishes its identity. Check that the
destination does not collide with a different symbol or path. Establish the owner-required affected
checks and their executable routes.

Discover references in proportion to the target:

- Use semantic references for symbols when they cover the relevant language and build context.
  Otherwise combine lexical search with inspection of imports, call sites, type use, inheritance,
  registration, reflection, and other identity-bearing structures.
- Inspect dynamic strings, generated code, cross-language use, scripts, tests, documentation, and
  build or configuration files when evidence connects them to the target.
- For paths, inspect the repository tree and index as well as imports, manifests, links, and
  case-sensitive references. A text search alone is not proof that path discovery is complete.

For a public API or other externally observed name, determine the compatibility decision before
editing: breaking rename, staged migration, alias, adapter, or no change. Do not invent compatibility
policy. Keep serialization keys, protocol fields, database columns, persisted names, and
configuration keys unchanged unless they are explicitly part of the approved rename.

Stop before editing when the target, scope, authority, compatibility decision, canonical generated
owner, or supported generator cannot be established or used; when a safe move or required
verification route cannot be established; when
the destination collides until the mapping changes or its owner resolves it; or when the approved
compatibility decision does not permit the rename. Report the blocking fact or decision and its
owner.

## Make the change

Rename the declaration or tracked path and update every confirmed reference to the same identity.
Use a semantic rename when its coverage is trustworthy; otherwise make the evidence-backed edits
explicitly.

Additional practices apply where relevant:

- Change every generated surface only through its canonical source and supported generator.
- Move tracked paths with the repository's version-control mechanism. For a case-only rename on a
  case-insensitive filesystem, use a unique temporary name so both move steps are recorded safely.
- Apply only the approved compatibility measure, through the owning interface or module.
- Update tests, comments, documentation, examples, and user-visible text only when they refer to the
  renamed identity. A filename tied to that identity may move with it after the same path checks.

Order these actions only where safety or repository tooling requires it—for example, update a
generator before regenerating output, or establish a temporary path before a case-only destination.

Target-project governance and the accepted request own all reads, writes, and commands. This Skill
grants only the rename and necessary same-identity reference, generated, test, and documentation
changes. It grants no authority to discard, stash, reset, or overwrite user work; edit canonical
generated outputs directly; commit, push, publish, release, deploy, create a worktree, use the
network, or perform remote actions.

## Verify the result

Repeat the relevant semantic and textual discovery after editing. For paths, also inspect the tree,
index, and path references. Classify every remaining old-name occurrence as:

- an intentional preserved contract;
- an unrelated identity;
- a missed in-scope reference; or
- unresolved.

Correct a miss only when current evidence uniquely determines an in-scope correction, then repeat
the affected discovery and checks. Stop when the same finding recurs, evidence no longer determines
a correction, or progress requires broader scope, a different compatibility decision, or another
owner. Run every owner-required affected formatter, static check, build, generated-output check,
and test. When compatibility retains both names, verify the supported old and new behavior.

## Finish

- **Complete** when the target uses the approved name, every confirmed reference uses it or is
  intentionally preserved by approved compatibility, remaining occurrences are understood, and
  the affected checks pass.
- **Blocked** only before writing, when an establishment requirement above is missing.
- **Failed** after any write when the rename cannot be completed or verified safely, including an
  unavailable or red required check, unresolved occurrence, exhausted correction, or newly required
  scope or owner action. It governs any coincident Blocked fact. Preserve the exact useful partial
  state and evidence without inventing rollback authority.

Report the mapping and target identity; compatibility decision; discovery methods and coverage;
changed, generated, moved, and preserved surfaces; every remaining target occurrence with location
and classification; unrelated same-name identities in summary; exact checks and exits; corrections;
outcome; and unresolved or untested surfaces. For a non-complete result, also report the exact
partial state, stopping evidence, and next owner or decision.
