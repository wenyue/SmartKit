---
name: create-worktree
description: Use when state-changing repository work requires an isolated linked Git worktree for parallel execution, workflow isolation, or protection of the current checkout.
---

# Create Worktree

Select or create one linked Git worktree, carry the source's current work when creating by default,
prepare its environment, and return `ready` or `non-ready`. The caller owns the accepted scope and
isolation requirement; this Skill owns workspace selection and immediate readiness. Implementation,
commits, project verification, finalization, cleanup, and remote actions retain their existing owners.

## Principles

- **Explicit choices govern.** Honor the user or caller's target, base, path, ownership, and effect
  constraints, including prior session choices.
- **Preserve the starting work.** Carrying state copies it without changing the source's files,
  index, `HEAD`, or branch/ref. Inherited work retains its original attribution and protection.
- **Proportionate evidence.** Use proportionate evidence for repository, workspace, state, and effect
  judgments. Investigate aliases, hooks, filters, subprocesses, or other boundaries further when a
  concrete risk could change preservation or authority.
- **Visible uncertainty.** Stop before unresolved material choices or unsupported effects. Retain
  attributable partial work and evidence after failure; uncertainty cannot become readiness.

## 1. Select the workspace

Identify the accepted scope and its `scope_owner`, the source and primary project checkouts, and
the physical Git common directory.

When continuing an exact attributable linked worktree, check its physical root, registration,
branch/ref, `HEAD`, base relationship, and local state against the retained task context. Reuse that
target when they agree; no exhaustive search of unrelated candidates or path migration is needed.
Preserve its existing inherited and task state without applying fresh source changes over it.
Ambiguous ownership or identity returns `non-ready`.

For a new worktree, freeze the immutable base and creation mode. Default to **carry**: the source's
current frozen `HEAD` plus its staged, unstaged, and untracked nonignored state. **Clean** creates
the selected base without source changes. An explicit different base requires an explicit clean
choice or compatible carry semantics; it does not implicitly authorize applying dirty state from
another base. A caller requiring all state to belong to its task may reject inherited unrelated
work without changing this default or authorizing its loss.

Use an explicit target path when supplied. Otherwise prefer
`<primary-project-root>/.worktrees/<task>`, even when invoked from another linked checkout. Use an
existing valid `.worktrees` container directly. An existing invalid entry, unsafe physical alias,
or tracked-content conflict is a conflict to report, not an absent-container fallback.

When the container is absent and no prior choice resolves placement, ask the user to choose one of
exactly two locations, displaying the concrete proposed target paths:

1. Create `<primary-project-root>/.worktrees/<task>` and ensure local Git exclusion.
2. Use the plugin's persistent `data/worktrees/<project-id>/<task>` location.

Resolve the actual plugin data root from authoritative host/configuration inputs. For Codex, the
SmartKit proposal is `~/.codex/plugins/data/smartkit/worktrees/<project-id>/<task>` under the resolved
Codex configuration root. This is a SmartKit storage convention, not an official host capability.
Use `<project-name>-<short-hash-of-canonical-git-common-dir>` as the project ID so same-name clones
remain distinct and linked worktrees share one project location. Never store worktrees inside a
versioned plugin cache or installed Skill directory. On another host, missing persistent-root
information requires an explicit location before a concrete second path can be offered; do not
invent a host path.

Choose safe, unique task paths and named branches through current filesystem and Git checks. New
creation requires absent target path, branch, and registration, with conflict-rejecting semantics;
no overwriting or branch repurposing. Resolve physical paths to prevent aliases or recursively
nesting containers beneath whichever linked checkout invoked the Skill.

For project placement, verify effective exclusion before worktree creation. If needed, resolve the
actual local Git `info/exclude` path through Git and narrowly add `/.worktrees/`, preserving all
other bytes and leaving shared `.gitignore` unchanged. Selecting project placement authorizes this
local exclusion subject to the caller's effect constraints. Make the container and exclusion edits
only after the location decision and any carry gate below are complete.

## 2. Capture the source and approve any carry

For either creation mode, record a stable source snapshot sufficient to verify preservation:
physical source identity, `HEAD` and branch/ref, index entries and staged contents, working contents
and file types/modes, and untracked nonignored paths. A conflicted index or ambiguous in-progress
operation stops before mutation unless the selected mechanism explicitly supports preserving that
state.

For **clean**, the expected target is the selected base with a clean index and working tree; skip
carry capture, counting, and approval. For **carry**, capture staged and unstaged layers separately,
including when one path has both. Preserve additions, deletions, renames, binary contents,
executable modes, and symlinks where supported. Derive the expected target index and working state
from the selected base and agreed carry semantics: same-base carry reproduces the source state;
explicit compatible cross-base carry preserves its changes over the selected base. Stop if that
expected result cannot be established without an unresolved transformation or conflict.

Exclude ignored files, dependency caches, and nested worktree contents from carry by default. Route
known required omitted inputs to environment preparation or a missing-prerequisite result.
Unsupported file or index semantics that prevent faithful transfer also stop before mutation.

For carry, count added plus deleted lines across the snapshot's staged and unstaged deltas,
including new untracked text lines. Count distinct changed paths once across those layers and
untracked files; binary changes count as paths, without invented line counts.
Before any worktree creation or state copy, if **lines >= 300 OR paths >= 10**, show the source,
target, both counts, and what will be carried, and obtain the user's explicit carry decision. Do
not count an unmeasurable item as zero: disclose the uncertainty and obtain a decision covering it
before proceeding. Below both thresholds, proceed with the default carry and report the counts.

Approval is bound to the reviewed source snapshot and target. Material change requires a fresh
summary and decision. No reply is not approval, and declining carry requires an explicit clean
`HEAD`/base choice or cancellation; never silently omit changes.

## 3. Establish and verify the target

For reuse, recheck the selected target's identity and preserved local state before preparation;
there is no creation or transfer step.

For creation, name the `creation_owner` accountable for the attempt and recovery. Establish the
expected local filesystem, branch/ref, and Git administration effects and the authority for them.
Follow applicable host-owned creation interfaces or Git with conflict-rejecting semantics. Inspect
configuration-driven hooks, filters, or subprocess effects where material; unresolved authority
for a credential, network, service, or other persistent effect stops that effect.

Immediately before mutation, confirm the frozen source snapshot, selected base and creation mode,
target and branch absence, and required decisions remain valid. Create from the selected immutable
base. For **clean**, perform no source-state transfer. For **carry**, reproduce the agreed target
index and working state from the captured changes, including untracked inputs within the selected
boundary. Use a method that leaves the source bytes, index, and `HEAD`/ref unchanged; stash, commit,
reset, and moving source files are not transfer methods.

Verify the registered physical target, named branch, and `HEAD` at the selected base. Compare its
index and working tree with the expected clean or carry state, including contents, file types/modes,
and staged versus unstaged semantics. Index verification compares content and semantics, not
binary-identical index extension metadata. For both modes, verify that the source remained unchanged
through capture and establishment, and account for authorized container, exclusion, and creation
effects. Source drift or an incomplete comparison returns `non-ready`.

After a failed or interrupted attempt, inspect the actual effects and retain partial paths, refs,
registrations, copied state, and evidence with their recovery owner. Remove an artifact only when
it is proven solely attributable to the attempt, contains no user or unrelated work, and exact
recovery authority permits removal. Retry only from an observed state supported by the mechanism
owner with the selection and carry gates satisfied again.

## 4. Prepare the environment

Check the selected target for its `worktree-environment-setup` Skill. When it exists, invoke it for
that exact target with the accepted setup-effect authority and the inherited modifications marked
as protected. Consume its `environment-ready` or `environment-non-ready` result, reusing valid
attributable dependency evidence without duplicating the Skill's internal checks. A present but
unavailable, failed, interrupted, or ambiguous dependency is `non-ready`, not absent.

When the target Skill is absent, record `not-provided` and skip it. A known indispensable missing
preparation or input still prevents readiness. This Skill runs no project baseline, build, test,
or project-health check. Repository-required verification remains with implementation and
finalization owners; environment readiness makes no test-passing claim.

## 5. Return readiness

Finish with a small check of current target identity and expected state against the creation/reuse
and environment results. Investigate specific drift or unexpected effects. Return `ready` only
when the selected workspace and inherited state are correct, preservation holds, expected effects
are authorized, present environment preparation succeeded, and no known indispensable prerequisite
is missing. Every other outcome is `non-ready`, with the selected workspace and partial state
retained for their owner.

Return a compact handoff with:

- status and reason; scope, `scope_owner`, reuse/create choice, and `creation_owner` when applicable;
- source and target roots, physical repository/Git-common identity, registration, branch, immutable
  base, current `HEAD`/tree, and the observation boundary;
- source snapshot and inherited-state attribution, staged/unstaged/untracked evidence, carry counts
  and decision, or the explicit clean-base choice;
- environment status and attributable evidence, expected local state, expected/actual effects,
  preservation verdict, and retained partial or uncertain state; and
- for `non-ready`, the blocker, next owner, and exact next action.

Inherited source work does not become new task ownership or commit authority through this result.
The caller accounts for it independently under its scope and commit policy. Consuming a fresh
result requires only the necessary current target identity/state check; investigate concrete drift
before mutation. Later workflows and `finish-worktree` establish their own current contracts.
