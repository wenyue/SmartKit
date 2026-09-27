---
name: create-worktree
description: Use when state-changing repository work needs an isolated linked Git worktree.
---

# Create Worktree

Select or create one linked Git worktree, prepare its environment, and return `ready` or `non-ready`
with evidence the caller can use. New creation carries the source's current work by default;
isolation does not erase that work's original ownership.

The caller owns the accepted scope and isolation requirement. Honor its target, base, path,
ownership, and effect constraints, including choices already made in the session. This Skill owns
workspace selection and immediate readiness. Implementation, commits, project verification,
finalization, cleanup, and remote actions retain their existing owners.

## Select One Attributable Workspace

Identify the accepted scope and `scope_owner`, the source and primary project checkouts, and the
physical Git common directory. Use proportionate repository and filesystem evidence to establish
those identities; investigate aliases or other boundaries further when a concrete risk could change
preservation or authority.

When continuing an exact attributable linked worktree, compare its physical root, registration,
branch/ref, `HEAD`, base relationship, and local state with retained task context. Reuse it when they
agree. Preserve inherited and task state already there; do not apply fresh source changes over it.
There is no need to search unrelated candidates exhaustively or migrate the selected path.
Ambiguous identity or ownership returns `non-ready`.

For reuse, recheck that target's identity and preserved local state before environment preparation,
then continue there without creation or transfer. For a new worktree, establish the choices and
source evidence below before mutation.

## Plan New Creation

### Choose the base and state to carry

Freeze the immutable base and creation mode:

- **Carry** defaults to the source's frozen current `HEAD` plus its staged, unstaged, and untracked
  nonignored state.
- **Clean** creates the selected base without source changes.

An explicit different base requires an explicit clean choice or agreed compatible carry semantics;
it does not implicitly authorize applying dirty state from another base. A caller requiring all
state to belong to its task may reject inherited unrelated work, without changing the carry default
or authorizing that work's loss.

### Resolve the physical location

Use an explicit target path when supplied. Otherwise prefer
`<primary-project-root>/.worktrees/<task>`, even when invoked from another linked checkout. Resolve
the primary root from repository topology rather than assuming the invoking checkout is primary.
Use an existing valid `.worktrees` container directly. An invalid existing entry, unsafe physical
alias, or tracked-content conflict is a conflict to report, not an absent-container fallback.

When that container is absent and no prior choice resolves placement, ask the user to choose
between exactly two locations, displaying both concrete proposed target paths:

1. Create `<primary-project-root>/.worktrees/<task>` with local Git exclusion.
2. Use the plugin's persistent `data/worktrees/<project-id>/<task>` location.

Resolve the actual plugin data root from authoritative host or configuration inputs. For Codex,
SmartKit proposes `<resolved-codex-configuration-root>/plugins/data/smartkit/worktrees/<project-id>/<task>`;
this is a SmartKit storage convention, not an official host capability. Use
`<project-name>-<short-hash-of-canonical-git-common-dir>` as the project ID: same-name clones remain
distinct, while linked worktrees share one project location. Do not put worktrees inside a versioned
plugin cache or installed Skill directory. On another host, missing persistent-root information
requires an explicit location before offering the concrete second path; do not invent a host path.

Choose safe, unique task paths and named branches from current filesystem and Git evidence. New
creation requires the target path, branch, and registration to be absent, with conflict-rejecting
semantics. Do not overwrite or repurpose a branch. Resolve physical paths to prevent aliases and
recursive container nesting beneath whichever linked checkout invoked the Skill.

For project placement, verify effective exclusion before creation. If needed, resolve the actual
local Git `info/exclude` path through Git and narrowly add `/.worktrees/`, preserving every other
byte and leaving shared `.gitignore` unchanged. Selecting project placement authorizes this local
exclusion subject to the caller's effect constraints. Defer container and exclusion edits until
both the location decision and any carry decision below are complete.

## Freeze Source State and Resolve the Carry Gate

For either creation mode, record a stable source snapshot sufficient to prove preservation: physical
source identity, `HEAD` and branch/ref, index entries and staged contents, working contents and file
types/modes, and untracked nonignored paths. A conflicted index or ambiguous in-progress operation
stops before mutation unless the selected mechanism explicitly supports preserving that state.

This preservation evidence is separate from the transfer payload. For **clean**, the expected target
is the selected base with a clean index and working tree; skip carry capture, counting, and approval.

For **carry**, capture staged and unstaged layers separately, including when one path has both.
Preserve additions, deletions, renames, binary contents, executable modes, and symlinks where
supported. Establish the expected target index and working state from the selected base and agreed
carry semantics. Same-base carry reproduces the source state; explicit compatible cross-base carry
preserves its changes over the selected base. An unresolved transformation or conflict that prevents
establishing the expected result stops before mutation.

Exclude ignored files, dependency caches, and nested worktree contents from carry by default. Route
known required omitted inputs to environment preparation or a missing-prerequisite result. Stop
before mutation if unsupported file or index semantics prevent faithful transfer.

For carry, count added plus deleted lines across the snapshot's staged and unstaged deltas, including
new untracked text lines. Count each distinct changed path once across those layers and untracked files.
Binary changes count as paths; do not invent line counts for them.

Before any creation or state copy, if **lines >= 300 OR paths >= 10**, show the source, target,
both counts, and what will be carried, and obtain the user's explicit carry decision. An unmeasurable
item must not count as zero: disclose the uncertainty and obtain a decision covering it. Below both
thresholds, proceed with default carry and report the counts.

Approval covers the reviewed snapshot and target. A material change requires a fresh summary and
decision. No reply is not approval. If carry is declined, obtain an explicit clean `HEAD`/base choice
or cancel; do not silently omit source changes.

## Establish and Verify the New Target

Name the `creation_owner` accountable for the attempt and recovery. Establish the expected local
filesystem, branch/ref, and Git administration effects and authority for each. Use the applicable
host-owned creation interface or Git with conflict-rejecting semantics. Inspect configuration-driven
hooks, filters, or subprocess effects where material. Unresolved authority for credentials, network,
services, or another persistent effect stops that effect.

Immediately before mutation, confirm that the frozen source snapshot, immutable base, mode, and
required decisions remain valid, and that the target path, branch, and registration remain absent.
Create from that base. For **clean**, perform no source-state transfer. For **carry**, reproduce the
agreed index and working state from captured changes, including in-scope untracked inputs.

Leave source bytes, index, `HEAD`, and branch/ref unchanged. Stash, commit, reset, and moving source
files are not transfer methods.

Verify the target's registered physical root, named branch, and `HEAD` at the selected base. Compare
its index and working tree with the expected clean or carry state, including contents, file
types/modes, and staged versus unstaged semantics. Compare index content and semantics rather than
requiring binary-identical index extension metadata. In both modes, prove that the source remained
unchanged through capture and establishment, and account for authorized container, exclusion, and
creation effects. Source drift or an incomplete comparison returns `non-ready`.

### Retain attributable state after failure

After a failed or interrupted attempt, observe actual effects and retain partial paths, refs,
registrations, copied state, and evidence with their recovery owner. Remove an artifact only when
it is proven solely attributable to this attempt, contains no user or unrelated work, and exact
recovery authority permits removal.

Retry only from an observed state supported by the mechanism owner, with selection and carry gates
satisfied again. A partial copy is evidence for recovery, not permission to overwrite later work or
assume the whole attempt must be repeated.

## Prepare the Selected Environment

Resolve the selected target's `worktree-environment-setup` through its project Skill discovery.
When present, invoke it for that exact target with accepted setup-effect authority and inherited
modifications marked as protected. Consume its `environment-ready` or `environment-non-ready`
result, reusing valid attributable dependency evidence without duplicating its internal checks.
A present but unavailable, failed, interrupted, or ambiguous dependency yields `non-ready`; it is
not an absent Skill.

When the target Skill is absent, record `not-provided` and skip it. A known indispensable missing
preparation or input still prevents readiness.

This Skill runs no project baseline, build, test, or project-health check. Repository-required
verification belongs to implementation and finalization owners. Environment readiness makes no
claim that project tests pass.

## Return Readiness and Ownership

Finish with a small current target identity/state check against creation or reuse evidence and the
attributable environment result. Account for authorized preparation effects when determining the
expected state. Investigate concrete drift or unexpected effects.

Return `ready` only when the selected workspace and inherited state are correct, preservation holds,
expected effects are authorized, present environment preparation succeeded, and no known
indispensable prerequisite is missing. Otherwise return `non-ready`, retaining the selected workspace
and any partial state for their owner. Unresolved material choices and unsupported effects cannot
become readiness.

Give the caller a compact handoff containing:

- Status and reason; scope, `scope_owner`, reuse/create choice, and `creation_owner` where applicable.
- Source and target roots, physical repository/Git-common identity, registration, branch, immutable
  base, current `HEAD`/tree, and the observation boundary for those facts.
- Source snapshot and inherited-state attribution; staged, unstaged, and untracked evidence; carry
  counts and decision, or the explicit clean-base choice.
- Environment status and attributable evidence; expected local state; expected and actual effects;
  preservation verdict; and retained partial or uncertain state.
- For `non-ready`, the blocker, next owner, and exact next action.

Inherited work retains its original ownership and protection. Carrying it does not authorize
committing it; the caller accounts for inherited work under its own scope and commit policy.
Consuming a fresh result requires only the necessary current target identity/state check, with
concrete drift investigated before mutation. Later workflows and `finish-worktree` establish their
own current contracts.
