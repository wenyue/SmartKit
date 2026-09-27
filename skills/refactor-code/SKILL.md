---
name: refactor-code
description: Refactor one concrete code target while preserving supported caller-visible behavior and external contracts, or route open-ended searches for architectural opportunities.
---

# Refactor Code

Remove an established structural pressure from one concrete code target. Improve where knowledge
lives and how the implementation fits together while keeping supported caller-visible behavior,
invariants, and external contracts unchanged. The pressure gives the change its purpose; the
supported contract gives it its boundary.

## Route before writing

First determine whether the request is a bounded refactor, using authorized repository reads and
non-mutating evidence. Keep adjacent Skills responsible for their own work and reach them through
their existing public Skill interfaces.

| Requested outcome | Route |
| --- | --- |
| Pure symbol or tracked-path rename, including a public name or externally observed path | Return **Redirected** to the model-invoked `rename-code`. It owns the compatibility decision. Carry the confirmed target, preservation boundary, relevant evidence, and required outcome. |
| Open-ended search for architectural opportunities | Return **Redirected** to the user-invoked `improve-codebase-architecture`. Confirm only the search scope and hand off that scope and outcome for the user to invoke; do not start the search here. |
| Non-rename change to caller-visible behavior or an external contract | Return **Out of Scope**, identifying the target, evidence of the observable or contract change, and required outcome. This includes public-interface, persistence, protocol, integration, and user-visible behavior changes. |

A concrete refactor can still contain a genuine design question. Use the model-invoked
`codebase-design` for a material unresolved interface, seam, adapter, or test-surface choice only
when established repository evidence and ordinary in-scope judgment cannot settle it. Reconcile
its result with repository evidence before continuing. A result requiring a non-rename change to
caller-visible behavior or an external contract is **Out of Scope**.

**Redirected**, **Out of Scope**, and pre-write **Blocked** results perform no write. When
classification or a returned design depends on unavailable material, return **Blocked** with the
exact missing evidence.

## Establish the boundary

Before writing, establish the target, the structural pressure, the intended internal result, and
the accepted scope. Trace affected implementation and caller paths far enough to distinguish the
structure that may change from the supported behavior, invariants, and external contracts that
must survive. Use the target's tests, configuration, history, and local patterns where they help
establish those facts.

Choose preservation evidence at each supported seam for the regressions this refactor could
introduce. Suppose callers of a record parser rely on input order being retained and malformed
records producing a particular error. A check that parsing returns a nonempty list does not
establish either guarantee. Observe the promised results through the supported interface.
The useful check distinguishes preservation from regression, rather than merely exercising code.

Gather the least evidence that makes that distinction at every supported seam, together with
every owner-required affected-surface check. Establish applicable project rules, each hand-written
or generated surface's owner, the required check routes, and authority for every needed read,
command, and write. For generated surfaces, establish an authorized operation through their owner
before any writing; direct edits cannot substitute for that route.

Keep discovery and proof bounded by these obligations and the integration context needed to
interpret them. Widen only when evidence exposes another materially affected path or unresolved risk.
Unavailable noncritical evidence narrows the supported conclusion and belongs in the handoff.
If a missing fact, access, authority, material evidence, or check route leaves a safe change or
preservation claim unsupported, return **Blocked** before writing and name the exact gap.

## Restructure the target

Choose the smallest coherent internal structure that removes the accepted pressure and localizes
knowledge. Let the source of the pressure guide the shape: repeated knowledge may belong together;
indirection that scatters one idea may be worth removing. Introduce an abstraction only when a real
seam earns it. Speculative frameworks, extension points, compatibility layers, and test-only APIs
are outside the result.

For example, suppose several parser branches must change together whenever the same escape rule
is corrected. One internal implementation of that rule can remove duplicated knowledge while
preserving parsing behavior. A configurable parsing framework would need additional real variation
to justify it. The aim is to concentrate the existing responsibility, not to prepare a family of
future parsers.

Change only necessary, owner-authorized implementation surfaces and internal callers, keeping
scope anchored to this target and pressure. Authority over one internal does not extend to another.
Change generated surfaces only through their established owners and authorized operations.
Preserve unrelated and user-owned state throughout the work.

Account for every materially reachable reference before retiring an internal. Keep preservation
assertions at supported seams; structure-coupled tests may change only while retaining their
behavioral assertions. A test's dependence on a retired helper is a reason to change how it reaches
the behavior, not a reason to discard the behavior it protected.

## Prove the result

After one coherent internal result:

1. Inspect the final diff and necessary integration context against the established boundary.
   Confirm every edit belongs to the authorized result, affected callers are migrated, and retired
   internals have no materially reachable reference.
2. Run the discriminating preservation evidence and every owner-required affected-surface check.
   Reuse valid evidence for equivalent claims. Add proof only for an uncovered material risk or an
   independently required check; repeated evidence of the same property cannot close a different gap.
3. Correct a finding when the evidence supports an authorized in-scope change that preserves the
   established behavior, invariants, and contracts. Choose among sound methods using ordinary
   engineering judgment, favoring locality and simplicity, then rerun affected checks.

Suppose a refactor groups records and returns them in group order, although callers require input
order. Retaining input positions or changing the traversal could both restore that behavior. If
both fit the established contract and authorized scope, choose the clearer fit for the
implementation. If required behavior or authority is unresolved, or a material effect of the
change is unknown, stop the dependent correction: choosing a method cannot settle those gaps.

## Results and handoff

Return **Complete** only when the structural pressure is removed, supported caller-visible behavior
and external contracts remain preserved, invariants hold, replaced internals are retired, the final
scope matches ownership and authority, and every required check passes.

After writing, return **Failure** when a required check cannot pass or run, preservation evidence
no longer discriminates, no authorized in-scope correction is supported by the available evidence,
or the same finding recurs unchanged. Failure takes precedence over any coincident Blocked,
Redirected, or Out of Scope fact: the handoff must account for the changed state. Preserve useful
state and evidence without inventing rollback authority.

Hand off the pressure and result; preserved behavior, invariants, and contracts; changed internals
and callers; retired code; exact checks and exits; corrections; and unresolved or untested surfaces.
A non-complete result also identifies the stopping fact and preserved state.

This Skill grants no publication, installation, commit, push, worktree, translation, network
access, or remote effect. Target-project governance remains authoritative for reads, writes,
commands, and generated owners.
