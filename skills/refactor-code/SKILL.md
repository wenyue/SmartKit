---
name: refactor-code
description: Refactor one concrete code target while preserving supported caller-visible behavior and external contracts; also route pure renames, open-ended architecture searches, material interface or seam choices, and non-rename observable changes before writing.
---

# Refactor Code

Restructure one concrete target to remove established structural pressure while preserving what
supported callers and external consumers observe.

## Principles

- **Behavior is the boundary.** Internal structure may change; supported caller-visible behavior,
  invariants, and external contracts remain unchanged.
- **One pressure, one target.** Keep scope anchored to the concrete target and structural problem
  accepted for this run.
- **Minimum coherent structure.** Localize knowledge and introduce only abstractions earned by a
  real seam. Speculative frameworks, extension points, compatibility layers, and test-only APIs are
  outside the result.
- **Owned change.** Follow target-project governance and each generated or hand-written surface's
  owner. Authority for one internal does not authorize another.
- **Proportionate proof.** Gather the least evidence that can distinguish preservation from
  regression at every supported seam, plus every owner-required affected-surface check.

## Route before writing

Classify the requested outcome using authorized repository reads and non-mutating evidence. Use
adjacent Skills only through their existing public distribution interfaces; never reproduce their
workflows here.

- **Redirected — rename.** A pure symbol or tracked-path rename belongs to `rename-code`, including
  a public name or externally observed path. `rename-code` owns its compatibility decision.
- **Redirected — architecture search.** An open-ended search for architectural opportunities
  belongs to the user-invoked `improve-codebase-architecture` Skill. Confirm only its search scope.
- **Design dependency.** Use `codebase-design` for a material unresolved interface, seam, adapter,
  or test-surface choice only when established repository evidence and ordinary in-scope judgment
  cannot settle it. Reconcile the result with repository evidence. If it requires a non-rename
  caller-visible behavior or external-contract change, return **Out of Scope**; otherwise continue.
- **Out of Scope.** Any requested non-rename change to caller-visible behavior or an external
  contract belongs elsewhere, including public-interface, persistence, protocol, integration, and
  user-visible behavior changes.

**Redirected**, **Out of Scope**, and pre-write **Blocked** results perform no write. A rename
handoff carries the confirmed target, preservation boundary, relevant evidence, and required
outcome. An architecture-search handoff carries only its confirmed scope and outcome. An Out of
Scope report carries the target, evidence of the observable or contract change, and required
outcome. When classification or a returned design depends on unavailable material, return
**Blocked** with the exact missing evidence.

## Establish the boundary

Before writing, establish from the target repository:

- the target, structural pressure, intended internal result, and accepted scope;
- applicable project rules and owners, including each generated surface's established owner;
- supported caller seams and the behavior, invariants, and external contracts they expose;
- affected implementation and caller paths, plus only the tests, configuration, history, and local
  patterns needed to judge the change;
- preservation evidence for each supported seam and every owner-required affected-surface check;
  and
- authority for every required read, command, and write.

Bound discovery and proof to these obligations and the integration context needed to interpret
them. Widen only when evidence exposes another materially affected path or unresolved risk.
Unavailable noncritical evidence narrows the supported conclusion and enters the handoff. Return
**Blocked** without writing when a missing fact, access, authority, material evidence, or check
route leaves the safe change or a preservation claim unsupported; name the exact gap.

## Restructure the target

Choose the smallest coherent internal structure that removes the pressure and localizes knowledge.
Change only necessary, owner-authorized implementation surfaces and internal callers. Change a
generated surface only through its established owner and only when the required operation is
authorized; otherwise return **Blocked** before writing.

Preserve unrelated and user-owned state along with every supported seam, behavior, invariant, and
contract. Account for every materially reachable reference before retiring an internal. Keep
preservation assertions at supported seams; change structure-coupled tests only while retaining
their behavioral assertions.

## Prove the result

After one coherent internal result:

1. Inspect the final diff and necessary integration context against the established boundary.
   Confirm every edit belongs to the authorized result, affected callers are migrated, and retired
   internals have no materially reachable reference.
2. Run the discriminating preservation evidence and every owner-required affected-surface check.
   Reuse valid evidence for equivalent claims; add proof only for an uncovered material risk or an
   independently required check.
3. Apply only uniquely evidence-determined in-scope corrections, then rerun affected checks. Stop
   when evidence no longer determines progress.

## Results and handoff

Return **Failure** after writing when a required check cannot pass or run, preservation evidence no
longer discriminates, no supported in-scope correction exists, or the same finding recurs unchanged.
Preserve useful state and evidence without inventing rollback authority. After-write Failure takes
precedence over any coincident Blocked, Redirected, or Out of Scope fact.

Return **Complete** only when the structural pressure is removed, supported caller-visible behavior
and external contracts remain preserved, replaced internals are retired, the final scope matches
ownership and authority, and every required check passes.

Hand off the pressure and result; preserved behavior, invariants, and contracts; changed internals
and callers; retired code; exact checks and exits; corrections; and unresolved or untested surfaces.
A non-complete result also identifies the stopping fact and preserved state.

This Skill grants no publication, installation, commit, push, worktree, translation, network
access, or remote effect. Target-project governance remains authoritative for reads, writes,
commands, and generated owners.
