---
name: create-worktree
description: Use when state-changing repository work requires an isolated linked Git worktree for parallel execution, workflow isolation, or protection of the current checkout.
---

# Create Worktree

Select, establish, and prepare exactly one safe linked Git worktree, then return an evidence-bound
`ready` or `non-ready` mechanical handoff. This Skill owns worktree selection, creation,
validation, readiness, and handoff. The caller owns the accepted implementation scope and the
authority requiring isolation; it need not choose Create versus Reuse, a path, or a branch.

Keep `scope_owner`, the actor responsible for any creation and attempt recovery
(`creation_owner`), and the later `integration_owner` and `cleanup_owner` explicit. Those
identities do not grant effects. This Skill owns no implementation, commit, completed-change
verification, integration, tracking, cleanup, publication, or remote action.

## Establish the boundary

Resolve from the owning workflow and current authoritative repository evidence:

- the accepted scope, `scope_owner`, isolation requirement, exact immutable base commit and tree,
  and any required base-lineage relationship;
- repository identity, the source checkout, resolved Git common directory, every registered
  worktree, and current path and branch conventions;
- lifecycle ownership and any caller-owned constraints on the selected path or branch; and
- the authority available for creation, target preparation, baseline verification, recovery, and
  every external or persistent effect.

A current branch tip, visible convention, existing worktree, or owner identity is evidence, not
authority. Materially ambiguous scope, base, ownership, or permission yields `non-ready` before
the affected action.

Before mutation, capture enough current state to attribute every possible effect: the identity and
local state of each checkout an operation can reach; affected refs and Git-common administration;
the proposed target; and every declared filesystem, subprocess, external, or persistent effect
target. Preserve all pre-existing staged, unstaged, untracked, and unrelated state. The source
checkout's branch, `HEAD`, tree, index, and local content remain exact; outside an authorized target
or effect envelope, every observed item remains exact. Use a non-destructive alternative whenever
an action would overwrite, stash, reset, clean, or discard existing state.

**Complete when:** the scope and base are exact, the potential effect boundary is observable, and
each possible mutation has an applicable owner and grant.

## Select one target

Inspect current registrations, branches, paths, handoffs, and scope ownership, then choose Reuse
when one existing linked worktree is uniquely safe for the accepted scope. Prove its physical path
and Git common directory, registration, named branch/ref, `HEAD`, tree, index, complete local
state, base lineage, and lifecycle disposition. Every commit in the target-specific comparison
range defined by the accepted immutable base and required lineage, and every local-state item that
Reuse would consume, must be attributable to this scope; base-reachable history before the
immutable base is outside this attribution test. Current identity and ownership are sufficient;
historical creator identity is not required. Never adopt, repair, reset, clean, or repurpose
ambiguous or unrelated state.

Otherwise choose Create. Follow current target- or host-owned path and branch conventions when they
apply. When none applies and the grant permits selection, derive a valid, unique path and named
branch from the scope. Validate both with the current filesystem and Git interfaces, including
physical-path aliases, symlinks, junctions or reparse points, registrations, and ref conflicts. A
target nested under another checkout is eligible only when it is already excluded from that
checkout's tracked and untracked surface and creation cannot alter surrounding state; do not edit
ignore rules to make it eligible. An external or sibling target is valid when repository identity
and authority are proved.

Freeze the selected mode, lexical and physical path, branch/ref, base, and expected local state.
Reuse permits no registration or branch creation. Create requires the path, branch, and registration
to be absent and uses a non-clobbering mechanism; force, reset, replacement, or branch reuse is
outside this contract. When multiple choices remain materially different and evidence cannot select
one safely, return `non-ready` with the decision owner and choices.

**Complete when:** exactly one target has a frozen, conflict-free identity and every existing item
that will be retained or consumed has proved scope and lifecycle ownership.

## Establish a new worktree

For Create, resolve the actual worktree-creation mechanism at use. Before invoking it, close its
complete effect envelope, including target checkout population, branch/ref and Git-common
administration, configured hooks, filters and subprocesses, and any credential, network, service, or
other external or persistent effect they can cause. Require authority for the exact path, ref, and
each applicable effect. An unavailable or unresolved effect boundary is `non-ready`; a generic
request to create a worktree does not silently authorize unrelated effects.

Immediately before the attempt, recheck the immutable base, source preservation boundary, target
path and branch absence, registration set, mechanism, and grants. Use the applicable host-native or
Git worktree interface only with conflict-rejecting semantics. After every success, failure, or
interruption, inspect the complete attempted envelope and Git state before deciding what happened.
A successful attempt must prove one registration at the selected physical path, its named branch
and ref, and `HEAD` and tree exactly at the immutable base, with only authorized creation effects.

On an unsuccessful or uncertain attempt, retain every artifact unless current evidence proves it
was created solely by that attempt, contains no user or unrelated work, and an exact recovery grant
authorizes its removal. Retry only after the mechanism owner supports repetition from the observed
state, recovery restores the complete pre-attempt boundary, and every creation gate passes again.
Do not repeat an unchanged failure. Unexpected, out-of-envelope, ambiguous, or unobservable effects
end `non-ready` with the artifact and recovery evidence retained.

For Reuse, make no establishment mutation. Recheck its frozen identity and local state immediately
before preparation; drift or ownership ambiguity is `non-ready`.

## Prepare and prove readiness

Invoke a target-owned `worktree-environment-setup` when current target evidence declares it
applicable. Supply the exact selected root and accepted setup-effect authority; that dependency owns
its command selection, effect accounting, recovery, and Git preservation proof. Do not reproduce
its internal procedure. Consume only its exact `environment-ready` or
`environment-non-ready` result. A supported absence is `not-required`; any other unavailable,
ambiguous, failed, interrupted, or non-ready outcome stops before the baseline.

Then resolve and run the current repository-owned baseline in the selected physical root. Freeze
its invocation, target binding, success condition, and complete effect envelope before execution;
require exact authority for every mutation or external effect. Do not invent a baseline or
substitute completed-change verification. A pass is ready-compatible. An exact observed failure is
ready-compatible only with the user's explicit acceptance; a proved absence requires explicit
acceptance from the user or owning workflow.

After each preparation or baseline attempt, recheck its effect envelope, all potentially affected
pre-existing state, and target identity. The selected branch/ref, `HEAD`, tree, and index must
remain exact; local additions must be scope-owned, expected, and authorized. Preserve partial or
uncertain state and return `non-ready` when an effect, result, or preservation proof is
unauthorized, unexplained, out of envelope, or incomplete.

Return `ready` only when selection or creation identity is current; all unrelated state is
preserved; every actual effect is owned and authorized; setup is `environment-ready` or
`not-required`; the baseline passed or has the exact required acceptance; lifecycle owners are
known; and the final readiness snapshot is complete. Every other exit is `non-ready`. Apart from
explicit attempt recovery above, retain the selected worktree and residual state for its owner.

## Handoff

Return a compact mechanical handoff containing:

- status, exact terminal reason, accepted scope, `scope_owner`, mode and selection rationale;
- repository and Git-common identity; immutable base and lineage; selected lexical and physical
  root, registration, named branch/ref, `HEAD`, tree, index, and scope-owned local state;
- `creation_owner` when creation was attempted, `integration_owner`, and `cleanup_owner`;
- the final preservation verdict, authorized and actual effects, and retained or residual state;
- the exact environment result and its evidence, plus the baseline invocation, result, effects, and
  any accepted failure or absence; and
- the readiness snapshot's observation boundary and, for `non-ready`, the failed boundary,
  unresolved or partial effect, next owner, and exact next action.

Use exact observations rather than inferred values. A consumer may use a `ready` target only after
rechecking its physical identity, registration, branch/ref, `HEAD`, tree, index, and local-state
snapshot immediately before the first mutation. Drift invalidates consumption and requires a fresh
Reuse evaluation; later authorized work does not retroactively change this run's result. The
handoff records authority already supplied but grants none.
