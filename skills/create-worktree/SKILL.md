---
name: create-worktree
description: Use when state-changing repository work needs an isolated linked Git worktree.
---

# Create Worktree

Select or create one linked Git worktree and establish its environment readiness without disturbing existing work. Return `ready` or `non-ready`. Carry the source's current work by default; inherited changes remain protected under their original ownership rather than automatically becoming the caller's task.

## 1. Select the workspace and starting state

Use the accepted task scope and existing choices of source, target, base, and permitted effects. Resolve the source checkout, primary project checkout, and physical Git common directory from repository topology; the invoking linked checkout need not be the primary checkout.

If continuing a selected worktree, check its physical path, Git registration, branch, `HEAD`, base relationship, and local changes against the task context. Reuse it when they agree, preserving its inherited and task changes. Do not copy fresh source changes over it. If its identity or ownership is unclear, return `non-ready`; otherwise skip creation and assess environment readiness.

For a new worktree, resolve the base to an immutable commit and choose the starting state:

| Mode | Starting state and decision |
| --- | --- |
| **Carry** | Default: source `HEAD` plus staged, unstaged, and untracked nonignored changes, preserving the distinction between layers. |
| **Clean** | Explicit choice required: selected base without source changes. |

A different base requires an explicit clean choice or agreed compatible carry semantics. Establish how carried changes apply to that base before proceeding; a base choice alone does not authorize copying changes from another base. A caller that requires only task-owned state may reject inherited work, but that does not authorize dropping it or changing the carry default.

## 2. Settle location and carry decisions

### Location

Honor an explicit target path. Otherwise prefer `<primary-project-root>/.worktrees/<task>` and use an existing valid `.worktrees` container. An invalid entry, unsafe physical alias, or tracked-content conflict requires resolution rather than fallback to another location.

When the container is absent and placement is undecided, ask the user to choose between exactly two locations, showing both concrete target paths:

1. `<primary-project-root>/.worktrees/<task>` with local Git exclusion.
2. The plugin's persistent `data/worktrees/<project-id>/<task>` location.

Resolve the plugin data root from authoritative host or configuration inputs. On Codex, SmartKit's convention is `<resolved-codex-configuration-root>/plugins/data/smartkit/worktrees/<project-id>/<task>`. Use `<project-name>-<short-hash-of-canonical-git-common-dir>` for the project ID, so linked worktrees share a location and same-name clones remain distinct. This is SmartKit's convention, not an official host capability. On another host without a known persistent root, obtain that location before offering the second path. Keep worktrees outside versioned plugin caches and Skill installs.

Choose a unique task path and named branch. Verify that the path, branch, and worktree registration are absent; resolve physical paths to avoid aliases and recursive nesting beneath the invoking worktree. Preserve an existing branch rather than repurposing it.

For project placement, verify effective Git exclusion. If necessary, resolve the local `info/exclude` through Git and narrowly add `/.worktrees/`, preserving other bytes and shared `.gitignore`. The placement choice authorizes this local exclusion within the caller's effect constraints. Wait until both placement and carry decisions are settled before changing the container or exclusion.

### Source preservation and carry

For either mode, capture the source's `HEAD`, branch, index, working contents, and untracked nonignored state sufficiently to check that creation leaves them unchanged. An unresolved index conflict, in-progress operation, or unsupported file/index semantics stops creation unless the chosen mechanism can faithfully preserve that state.

For **clean**, skip transfer capture, counting, and carry approval. For **carry**, capture staged and unstaged changes separately, including when both affect one path, plus untracked inputs. Preserve contents, additions, deletions, renames, binary files, executable modes, and symlinks. Exclude ignored files, dependency caches, and nested worktrees; route necessary omitted inputs to environment preparation. Establish the expected target state before copying, including any agreed cross-base transformation.

### Carry counts and approval

Count added plus deleted lines in staged and unstaged deltas and new untracked text. Count each distinct changed path once across all layers; binary changes count as paths without invented line counts.

Before creation or copying, if **lines >= 300 OR paths >= 10**, show the source, target, counts, and carried state, then obtain an explicit carry decision unless that snapshot and target already have one. Disclose unmeasurable items and obtain a decision covering them; they are not zero. Below both thresholds, proceed with default carry and report the counts.

A material change to the reviewed snapshot or target requires a fresh summary and decision. If carry is declined, obtain an explicit clean `HEAD`/base choice or cancel; silence is not approval.

## 3. Create and verify

Immediately before creation, recheck the source snapshot, selected base and mode, decisions, and absence of the target path, branch, and registration. Use the host's applicable creation interface or Git with conflict-rejecting semantics. Account for material hooks, filters, and subprocess effects within the permitted operation before running it.

Create at the selected commit. For clean mode, copy no source changes. For carry mode, reproduce the captured index and working state, including untracked inputs. Keep source bytes, index, `HEAD`, and branch unchanged: stash, commit, reset, and moving source files are not transfer methods.

Verify the registered target path, named branch, and `HEAD` at the chosen base. Compare its index and working state to the expected result, including file contents, types, modes, and staged versus unstaged changes. Compare index semantics, not binary index-extension metadata. Confirm that the source stayed unchanged and that container, exclusion, and creation effects match the chosen plan. Drift or an incomplete comparison yields `non-ready`.

### Continue safely after interruption

Inspect what actually exists before retrying after interruption or failure. Retain partial paths, branches, registrations, and copied work with enough context to continue safely; do not replay a copy over later changes. Remove partial artifacts only when they belong solely to this attempt, contain no other work, and removal is authorized. Recheck the applicable choices before resuming.

## 4. Assess environment readiness

Preparation applies on a newly created worktree's first use, when evidence shows a missing or stale environment prerequisite for the current task, or when the user explicitly requests preparation. Otherwise report `not-needed` and use the existing environment. A linked-worktree location or invalid cached preparation record alone establishes no preparation need.

When preparation applies, discover the selected target's project `prepare-worktree-environment` Skill. If present, invoke it within accepted preparation permissions, marking inherited modifications as protected, or reuse a still-valid result for this target. Use its `environment-ready` or `environment-non-ready` result. A required Skill that is unavailable, or preparation that fails, is interrupted, or remains ambiguous yields `non-ready`. If the Skill is absent, report `not-provided` and skip it; a known indispensable missing input or preparation still prevents readiness.

Recheck target identity and expected state after the assessment and any preparation, accounting for authorized changes. Return `ready` only when creation or reuse is verified, existing work is preserved, environment status is `environment-ready`, `not-needed`, or `not-provided`, and no unresolved choice, unauthorized effect, or indispensable prerequisite remains. Otherwise return `non-ready` and preserve the workspace and partial state for safe continuation.

Give the caller a concise readiness handoff:

- Status, target path, branch, immutable base, and current `HEAD`.
- Whether the worktree was created or reused, its carried/inherited-state summary and any carry decision, and environment status.
- For `non-ready`, the blocker, retained partial state, and concrete next action.

Keep supporting observations available; the handoff need not reproduce the full evidence inventory.

Readiness covers the workspace and its preparation, not project health. This Skill runs no project baseline, build, or test checks. The implementation workflow owns those checks and commit decisions; carrying inherited work does not authorize committing it. Before using a returned workspace, recheck its current identity and state and investigate unexpected drift.
