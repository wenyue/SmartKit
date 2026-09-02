---
name: refactor-code
description: Use when moving, combining, splitting, extracting, or simplifying one code target while preserving supported caller-visible behavior and external contracts; route pure renames, open-ended architecture searches, material unresolved interface or seam design decisions, and observable contract changes before writing.
---

# Refactor Code

Remove one concrete target's structural pressure while preserving what supported callers and
external consumers observe.

## Route Before Writing

Classify the requested outcome using authorized repository reads and non-mutating evidence. Use
adjacent Skills only through their current public distribution interfaces:

- A pure symbol or path rename is **Redirected** to `rename-code`.
- An open-ended search for architectural opportunities is **Redirected** to the user-invoked
  `improve-codebase-architecture` Skill; confirm only the search scope.
- A material unresolved choice about an interface, seam, adapter relationship, or test surface
  invokes `codebase-design` only when established repository evidence and ordinary in-scope
  refactoring judgment cannot settle it. Reconcile its result with repository evidence: return
  **Redirected** without writing through the user-invoked `implement` route when the result
  requires caller-visible behavior or contract change; otherwise continue here.
- A public-interface, persistence, protocol, integration, or user-visible behavior change is
  **Redirected** to the user-invoked `implement` Skill.

A Redirected result performs no write. An architecture-search handoff carries only the confirmed
search scope and required outcome. Rename and implementation handoffs carry the confirmed target,
accepted preservation boundary, relevant evidence, and required outcome. If routing or a returned
design depends on unavailable material, return **Blocked** without writing and name it.

## Establish the Refactoring Contract

Before any write, establish from the target repository:

- the exact target, structural pressure, intended internal result, and accepted scope;
- applicable project rules and owners, including generated-surface ownership;
- the supported caller seam and the observable behavior, invariants, and external contracts it
  must preserve;
- the target, callers, tests, configuration, history, and local patterns needed to judge the
  change;
- focused green evidence that can discriminate preservation from regression, plus every
  owner-required affected-surface check; and
- authority for every required read, command, and write.

Return **Blocked** without writing when any required fact, access, authority, evidence, or supported
check route is missing, naming the exact gap.

## Refactor

Choose the smallest coherent internal structure that removes the pressure and localizes knowledge.
Every abstraction earns a real seam; the result contains only required structure, not speculative
frameworks, extension points, compatibility layers, or test-only interfaces.

Change only necessary owner-authorized implementation surfaces and internal callers while
preserving unrelated and user-owned state. Preserve the supported seam, behavior, invariants, and
contracts. Account for every real reference before retiring an internal. Keep preservation
assertions at supported seams; change structure-coupled tests only while retaining their behavioral
assertions.

## Verify and Return

After one coherent internal result:

1. Compare the exact final scope, ownership, and structure with the refactoring contract. Prove
   every edit necessary, callers migrated, and retired internals free of real references.
2. Run the discriminating preservation evidence and every owner-required affected-surface check.
3. Apply only uniquely evidence-determined in-scope corrections, then rerun affected checks. Stop
   when evidence no longer determines progress.

Return **Failure** after writing when a required check cannot pass or run, preservation evidence
ceases to discriminate, no supported in-scope correction exists, or the same finding recurs
unchanged.
Preserve useful state and evidence without inventing rollback authority. After-write Failure
governs any coincident Blocked or Redirected fact.

Return **Complete** only when the pressure is removed, caller-visible behavior and external
contracts remain supported, replaced internals are retired, final scope matches ownership, and all
required checks pass.

Hand off the pressure and result; preserved behavior, invariants, and contracts; changed internals
and callers; retired code; exact checks and exits; corrections; and unresolved or untested
surfaces. A non-complete result also identifies the stopping fact and preserved state.

This Skill grants no publication, installation, commit, push, worktree, translation, or remote
effect. Target-project governance remains authoritative for reads, writes, commands, and generated
owners.
