---
name: create-worktree
description: Use when state-changing repository work requires an isolated linked Git worktree for parallel execution, workflow isolation, or protection of the current checkout.
---

# Create Worktree

Select, establish, and prepare exactly one linked Git worktree, then return its current `ready` or
`non-ready` result. The caller owns the implementation scope and the authority requiring isolation;
this Skill owns target selection, creation, validation, and readiness.

Keep the accepted scope and its `scope_owner` explicit. For a creation attempt, also name the actor
accountable for the attempt and authorized recovery as `creation_owner`. These roles record
accountability; each effect still requires an explicit grant from its owner. Implementation,
commits, completed-change verification, integration, tracking, lifecycle cleanup, publication, and
remote action remain with their established owners.

## Principles

- **One exact target.** A result covers one linked worktree with a proved repository identity,
  physical location, registration, branch/ref, base, and owned local state.
- **Preservation by default.** Protect all pre-existing, unrelated, and user-owned state. Prefer a
  non-destructive target whenever an action would overwrite, stash, reset, clean, or discard it.
- **Effects require authority.** Bound and authorize filesystem, Git-common, subprocess, credential,
  network, service, and other persistent effects before they occur.
- **Uncertainty remains visible.** Retain partial or ambiguous state until current evidence and an
  exact recovery grant make cleanup safe.
- **Readiness is fresh.** `ready` describes the recorded observation boundary, not a durable claim.

## 1. Establish the safety boundary

Resolve the accepted scope, `scope_owner`, isolation requirement, immutable base commit and tree,
and any required base lineage. Establish repository identity, source checkout, physical Git common
directory, registered worktrees, current path and branch conventions, caller constraints, ownership
of existing target state, and authority for creation, preparation, baseline checks, recovery, and
every external or persistent effect. A branch tip, convention, existing worktree, or owner identity
is evidence rather than authority. Material ambiguity yields `non-ready` before the affected action.

Before mutation, freeze the exact paths, refs, registrations, and Git administration state that an
operation can write, overwrite, or delete, or that recovery must restore. For committed and staged
content in this write-and-recovery set, record commit object IDs and affected index entries. For
every non-index item—including tracked unstaged, untracked, and ignored content—record file type,
mode, symlink target, size, and content hash. Preserve raw bytes only for an existing at-risk path
that authorized recovery may need to restore.

For all other checkout state, prove non-reachability from the operation's semantics, resolved
physical boundaries, and bounded repository identity and status evidence. Expand observation only
when a concrete alias, configuration, hook, filter, or subprocess creates a plausible path to that
state, and record every applicable subprocess, external, or persistent target. Continue only when
the scope and base are exact, the full potential effect boundary is observable, and every possible
mutation has an owner and grant.

## 2. Select Reuse or Create

Choose **Reuse** only when one existing linked worktree is uniquely safe for the scope. Prove its
lexical and physical path, Git common directory, registration, named branch/ref, `HEAD`, tree, index
identity, base lineage, and current ownership. Every commit in the target-specific comparison range
defined by the immutable base and required lineage, and every local-state item Reuse would consume,
must be attributable to this scope. Base-reachable history before the immutable base is outside that
test. Protect state beyond Reuse's consumed, write, and recovery paths through the safety boundary.
Ambiguous or unrelated state is never adopted, repaired, reset, cleaned, or repurposed.

Otherwise choose **Create**. Follow applicable target- or host-owned path and branch conventions;
when none applies and selection is authorized, derive a valid unique path and named branch from the
scope. Validate both through current filesystem and Git interfaces, including physical aliases,
symlinks, junctions or reparse points, registrations, and ref conflicts. A path nested under another
checkout is eligible only when already excluded from that checkout's tracked and untracked surface
and creation cannot alter surrounding state; ignore rules remain unchanged. An external or sibling
path requires proved repository identity and authority.

Freeze the mode, lexical and physical path, branch/ref, base, and expected consumed or affected
local state. Reuse permits no registration or branch creation. Create requires absent path, branch,
and registration and a conflict-rejecting mechanism; force, reset, replacement, and branch reuse
remain outside this contract. If materially different choices remain and evidence cannot select one,
return `non-ready` with the decision owner and choices. Continue only with one conflict-free target
whose consumed or affected existing state has proved scope ownership.

## 3. Establish the selected worktree

For **Reuse**, make no establishment mutation. Immediately before preparation, recheck its frozen
identity and every local-state item it will consume or can affect. Drift or ownership ambiguity is
`non-ready`.

For **Create**:

1. Resolve the actual creation mechanism and its effects from current semantics and configuration.
   Include checkout population, branch/ref and Git-common administration, and applicable hooks,
   filters, or subprocesses; follow those integrations far enough to identify material filesystem,
   credential, network, service, and persistent effects. Require authority for the path, ref, and
   each effect. An unresolved or unobservable material boundary is `non-ready`.
2. Immediately before the attempt, recheck the immutable base, source preservation boundary, path
   and branch absence, registrations, mechanism, and grants. Invoke the applicable host-native or
   Git worktree interface only with conflict-rejecting semantics.
3. After success, failure, or interruption, re-observe the frozen effect boundary before deciding
   what occurred. Success requires exactly one registration at the selected physical path, its named
   branch and ref, `HEAD` and tree at the immutable base, and only authorized effects.
4. After an unsuccessful or uncertain attempt, retain every artifact unless current evidence proves
   it came solely from that attempt, contains no user or unrelated work, and an exact recovery grant
   authorizes removal. Retry only when the mechanism owner supports repetition from the observed
   state, recovery restores the complete pre-attempt boundary, and every creation gate passes again.
   An unchanged failure is not retried. Unexpected, unauthorized, ambiguous, or unobservable effects
   end `non-ready` with artifacts and recovery evidence retained.

## 4. Prepare the environment and check the baseline

When current target evidence declares `worktree-environment-setup` applicable, invoke that
target-owned Skill with the exact selected root and accepted setup-effect authority. It owns command
selection, effect accounting, recovery, and Git preservation; consume only `environment-ready` or
`environment-non-ready` without reproducing its procedure. Record `not-required` only when current
target evidence establishes that preparation is unnecessary. A missing or unavailable applicable
capability, or an ambiguous, failed, interrupted, or `environment-non-ready` result, ends
`non-ready` before baseline checks.

After either supported `not-required` or `environment-ready`, select the least burdensome
repository-owned baseline check or set that covers every accepted material worktree and environment
risk. Use a mandatory canonical baseline when repository evidence requires it; otherwise choose the
narrowest supported coverage and report only noncritical gaps. Freeze each invocation, target
binding, success condition, and effect set; require exact authority for every mutation or external
effect. Never invent a baseline or substitute completed-change verification.

A pass is compatible with readiness. An exact observed failure requires the user's explicit
acceptance. A proved absence or uncovered material readiness risk requires explicit acceptance from
the user or owning workflow. After every preparation or baseline attempt, re-observe its effect set,
investigate unexpected change, and recheck target identity. Branch/ref, `HEAD`, tree, and index must
remain exact; local additions must be expected, authorized, and owned by the scope. An unauthorized,
unexplained, out-of-boundary, or incompletely observed effect or result is `non-ready`, with partial
and uncertain state preserved.

## 5. Return a fresh readiness result

Return `ready` only when target identity is current; unrelated state is preserved; every effect is
owned, authorized, and fully observed; environment setup is `environment-ready` or supported
`not-required`; the baseline passed or has the exact required acceptance; and the final readiness
snapshot is complete. Every other result is `non-ready`. Except for the authorized attempt recovery
above, retain the selected worktree and residual state for its current owner.

Return a compact handoff containing the status and terminal reason; accepted scope, `scope_owner`,
mode, and rationale; repository and Git-common identity; immutable base and lineage; lexical and
physical root, registration, named branch/ref, `HEAD`, tree, index, and scope-owned local state;
`creation_owner` and recovery disposition when applicable; preservation verdict; authorized and
actual effects; retained state; exact environment and baseline evidence, including any accepted
failure or absence; and the observation boundary. For `non-ready`, also identify the failed boundary,
partial effect, next owner, and exact next action.

Use observations rather than inferred values. Before its first mutation, the caller rechecks the
physical identity, registration, branch/ref, `HEAD`, tree, index, and scoped local-state snapshot.
Any drift requires a fresh `create-worktree` evaluation, which again selects Reuse or Create from
current evidence. Later workflows and finalizers establish their own current contracts; all effects
remain under their originating grants.
