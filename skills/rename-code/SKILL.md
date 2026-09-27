---
name: rename-code
description: Rename one established code symbol or tracked repository path, including public names.
---

# Rename Code

Rename one established code symbol or tracked repository path from `old` to `new`. Follow the
identity through its real uses; shared spelling alone does not make another symbol part of the
rename. Preserve behavior and keep adjacent refactoring, cleanup, and unrelated renames out of scope.

The accepted request and target-project governance own all reads, writes, and commands. This Skill
covers the rename and its necessary same-identity reference, generated, test, and documentation
changes. It grants no authority to discard, stash, reset, or overwrite user work; edit canonical
generated output directly; commit, push, publish, release, deploy, create a worktree, use the network,
or perform remote actions.

## Establish the Identity and Compatibility Decision

Record one old name, one new name, the target identity, intended scope, and exact authority for
every required effect. Locate the declaration or tracked path that establishes the identity.
Distinguish it from unrelated homonyms and overloaded, shadowed, inherited, or generated identities.
Rule out a collision with a different symbol or path at the destination.

An externally observable name is a contract. For a public API or a name observed through callers,
persisted data, configuration, protocols, or published interfaces, establish the approved breaking
rename, staged migration, alias, adapter, or no-change decision before writing. Do not invent
compatibility policy.

Keep serialization keys, protocol fields, database columns, persisted names, and configuration keys
unchanged unless the approved rename explicitly includes them. A code symbol's new spelling does
not by itself authorize a change to those contracts.

## Trace References and Establish the Write Route

Begin with identity-bearing surfaces and their necessary integration context. Choose discovery
methods according to what can establish the binding:

- For symbols, prefer semantic references when they cover the relevant language and build context.
  Otherwise combine lexical search with inspection of imports, call sites, type use, inheritance,
  registration, reflection, and other identity-bearing structures.
- Inspect dynamic strings, generated code, cross-language use, scripts, tests, documentation, and
  build or configuration files when evidence connects them to the target.
- For paths, inspect the repository tree and index together with imports, manifests, links, and
  case-sensitive references. Text search alone cannot establish complete path coverage.

Follow every confirmed use. Widen discovery when unresolved references, repository structure,
build metadata, generated ownership, or check failures indicate that the identity may reach farther.
Shared spelling alone does not justify inventorying unrelated repository surfaces.

Before any writing, identify the canonical owner and usable supported generator for affected
generated surfaces. Establish a safe version-control move for a path rename and the applicable
owner-required checks with their executable routes.

Stop before writing if identity, scope, authority, or an observed name's compatibility decision is
unresolved; the destination collides; a needed generated owner, supported generator, safe move, or
required check route is unavailable; or the compatibility decision requires no change. Report the
actual blocking fact or decision and its owner. A settled no-change decision means the rename will
not proceed, not that a decision is missing.

## Apply the Rename Through Its Owners

Rename the declaration or tracked path and every confirmed in-scope reference. Use a semantic rename
when its coverage is trustworthy; otherwise make the evidence-backed edits explicitly.

Apply each affected surface's ownership constraints:

- Change generated surfaces through their canonical source and supported generator.
- Move tracked paths with the repository's version-control mechanism. For a case-only rename on a
  case-insensitive filesystem, use a unique temporary name before moving to the destination.
- Apply only the approved compatibility measure through its owning interface or module.
- Update tests, comments, documentation, examples, user-visible text, and identity-bound filenames
  only when they refer to the renamed identity.

Order actions where safety or repository tooling requires it, such as updating a generator before
regeneration or establishing the temporary path before a case-only destination. Choose ordinary
editing details within those constraints.

## Verify Coverage and Correct Supported Misses

A new spelling does not establish a complete rename. Repeat the relevant identity-aware discovery
after editing, searching affected surfaces and necessary integration context for the old name.
Widen only when evidence indicates incomplete coverage. For paths, recheck the tree, index, and
path references.

Classify every remaining occurrence that could plausibly denote the target as:

- an intentional preserved contract;
- an unrelated identity;
- a missed in-scope reference; or
- unresolved.

Group unrelated homonyms when common evidence supports the classification. A per-occurrence
inventory of low-signal matches does not prove correctness.

Run every applicable owner-required check for the changed surfaces and material rename risks,
including formatting, static analysis, builds, generated-output verification, and tests where
required. Add broader checks only when repository governance or current evidence makes them relevant.
When compatibility preserves both names, verify the supported behavior of each.

Correct a miss when current evidence ties it unambiguously to the approved identity and supports an
authorized in-scope correction that preserves behavior and the compatibility decision. Choose among
sound methods using ordinary engineering judgment, then repeat affected discovery and checks.

For example, suppose the new name of an imported function is shadowed at a known caller. If the
established scope permits that caller's reference repair, and module qualification and an unambiguous
import alias both preserve the approved binding and behavior, either may be a sound repair. The
choice between those methods is different from uncertainty about which function the caller uses.
An unresolved overload or dynamic binding still needs identity evidence.

Stop correcting when evidence no longer improves, no supported safe in-scope correction remains,
or continuing requires broader scope, another compatibility decision, or another owner's action.
Choosing a method cannot resolve missing identity, authority, or material behavior evidence.

An unavailable or failing required check prevents completion. When unavailable non-required
evidence leaves no material identity or compatibility risk unresolved, narrow the completion claim
and report the exact untested surface.

## Report the Outcome and Remaining State

- `COMPLETE`: The target uses the approved name, every confirmed reference uses it or is preserved
  by approved compatibility, no plausible target occurrence remains unresolved, and every applicable
  required check passes. Record any noncritical untested surface that narrows this result.
- `BLOCKED`: Before writing, a requirement for a safe authorized rename cannot be established, or
  the approved compatibility decision requires no change. State the actual reason; a settled
  no-change decision is not a request for missing input.
- `FAILED`: After any write, the rename cannot be completed or verified safely. This includes a
  failing or unavailable required check, an unresolved occurrence, exhausted correction, or newly
  required scope or owner action. After a write, `FAILED` takes precedence over a condition that
  would otherwise be `BLOCKED`. Preserve useful partial state and evidence without inventing
  rollback authority.

Report the mapping and identity; compatibility decision; discovery methods and coverage; changed,
generated, moved, and preserved surfaces; remaining old-name classifications and unrelated same-name
identities; checks and exits; corrections; outcome; and unresolved or untested surfaces. Group
homogeneous resolved occurrences when common evidence supports them, but locate every unresolved,
mixed, or materially exceptional occurrence. For a non-complete result, include the exact partial
state, stopping evidence, and next owner or decision, if one is needed.
