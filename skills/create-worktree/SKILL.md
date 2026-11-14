---
name: create-worktree
description: Use when state-changing repository work needs an isolated linked Git worktree.
---

# Create Worktree

Select or create one linked Git worktree and establish its Agent configuration and environment readiness without disturbing existing work. Return `ready` or `non-ready`. Carry the source's current work by default; inherited changes remain protected under their original ownership rather than automatically becoming the caller's task.

## 1. Select the workspace and starting state

Start from the established need for isolation and the accepted task scope. Use existing choices of source, target, base, and permitted effects. Ask for unresolved required choices or permission, reusing decisions that already cover the operation. Resolve the source checkout, primary project checkout, and physical Git common directory from repository topology; the invoking linked checkout need not be the primary checkout.

Before creating a worktree, check whether an existing task worktree can serve the accepted work. Verify a candidate's physical path, Git registration, branch, `HEAD`, base relationship, and local changes against the task context. Reuse it when they agree, preserving its inherited and task changes. Do not repurpose another task's worktree or copy fresh source changes over a continued one. If a selected worktree's identity or ownership is unclear, return `non-ready`; otherwise skip creation and assess configuration and environment readiness.

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

For **clean**, skip transfer capture, counting, and carry approval. For **carry**, capture staged and unstaged changes separately, including when both affect one path, plus untracked inputs. Preserve contents, additions, deletions, renames, binary files, executable modes, and symlinks. Exclude ignored files, dependency caches, and nested worktrees; route required Agent configuration through configuration preparation below and other necessary omitted inputs through environment preparation. Establish the expected target state before copying, including any agreed cross-base transformation.

### Carry counts and approval

Count added plus deleted lines in staged and unstaged deltas and new untracked text. Count each distinct changed path once across all layers; binary changes count as paths without invented line counts.

Before creation or copying, if **lines >= 300 OR paths >= 10**, show the source, target, counts, and carried state, then obtain an explicit carry decision unless that snapshot and target already have one. Disclose unmeasurable items and obtain a decision covering them; they are not zero. Below both thresholds, proceed with default carry and report the counts.

A material change to the reviewed snapshot or target requires a fresh summary and decision. If carry is declined, obtain an explicit clean `HEAD`/base choice or cancel; silence is not approval.

## 3. Create and verify

Immediately before creation, recheck the source snapshot, selected base and mode, decisions, and absence of the target path, branch, and registration. Use the host's applicable creation interface or Git with conflict-rejecting semantics. Account for material hooks, filters, and subprocess effects within the permitted operation before running it.

Create at the selected commit. For clean mode, copy no source changes during this transfer; configuration and environment preparation follow under their own accepted scope. For carry mode, reproduce the captured index and working state, including untracked inputs. Keep source bytes, index, `HEAD`, and branch unchanged: stash, commit, reset, and moving source files are not transfer methods.

Verify the registered target path, named branch, and `HEAD` at the chosen base. Compare its index and working state to the expected result, including file contents, types, modes, and staged versus unstaged changes. Compare index semantics, not binary index-extension metadata. Confirm that the source stayed unchanged and that container, exclusion, and creation effects match the chosen plan. Drift or an incomplete comparison yields `non-ready`.

### Continue safely after interruption

Inspect what actually exists before retrying after interruption or failure. Retain partial paths, branches, registrations, and copied work with enough context to continue safely; do not replay a copy over later changes. Remove partial artifacts only when they belong solely to this attempt, contain no other work, and removal is authorized. Recheck the applicable choices before resuming.

## 4. Establish Agent configuration readiness

Before discovering target project Skills, establish which project instructions, Rules, Skills, custom Agents, MCP declarations, and host settings the accepted task requires. Check the selected worktree first and preserve its usable configuration on reuse. When no project configuration is required, report configuration `not-needed` and continue.

Git-shared configuration (`local`) arrives through checkout or carry and needs no extra transfer. For `local-only` and `repository`, use the accepted, initialized source checkout and follow [Worktree configuration](references/configuration.md) to prepare missing configuration and handle later edits and cleanup of linked or copied configuration. Resolve corresponding project directories through Git topology; the source need not be a physical parent. Keep code and project operations rooted in the selected worktree.

Treat configuration preparation separately from clean or carry transfer, within the caller's accepted permissions. Preserve usable target configuration. Missing required source content, unresolved scope or conflicts, and incomplete preparation yield `non-ready`; retain the worktree and report the needed resolution.

Make the selected configuration available through the active host's supported loading route. Before environment preparation, verify that required instructions and Skills can be resolved for the target and that settings and capabilities needed for preparation are usable. Reuse still-applicable evidence. Copied files, setup markers, or synchronization receipts alone do not prove activation; a required host reload, trust decision, or unavailable preparation capability yields `non-ready` with its next action. When a task-required capability depends on the project environment being prepared, verify it after preparation, before returning `ready`.

## 5. Assess environment readiness

Preparation applies on a newly created worktree's first use, when evidence shows a missing or stale environment prerequisite for the current task, or when the user explicitly requests preparation. Otherwise report `not-needed` and use the existing environment. A linked-worktree location or invalid cached preparation record alone establishes no preparation need.

When preparation applies, discover the selected target's project `prepare-worktree-environment` Skill. If present, invoke it within accepted preparation permissions, marking inherited modifications as protected, or reuse a still-valid result for this target. Use its `environment-ready` or `environment-non-ready` result. A required Skill that is unavailable, or preparation that fails, is interrupted, or remains ambiguous yields `non-ready`.

If the Skill is absent, report `not-provided` and skip it; a known indispensable missing input or preparation still prevents readiness. If the absent Skill is indispensable, return `non-ready` and identify project setup as the route to provide it.

For a project already using CodeGraph, prepare a local index when the selected tree will support sustained implementation and repeated code-relationship queries. Do so on first use or when current evidence shows a missing or stale index, reusing a current local index. A short review or one-off verification does not need index preparation merely because it uses a worktree.

Use the already-installed CodeGraph CLI within accepted local preparation permissions, checking its version and help for the supported interface. Bind `<target-root>` to the selected physical worktree. Keep its database at `<target-root>/.codegraph/codegraph.db`, rather than copying or linking another tree's index. Initialize only when that local database is absent. For an existing database, inspect status and synchronize pending changes only when it identifies a usable index for this exact tree; preserve and report a mismatched index or one requiring repair or rebuilding:

```text
codegraph init "<target-root>"
codegraph status "<target-root>" --json
codegraph sync "<target-root>"
```

These are conditional operations, not a sequence to run on every visit. Status and sync can resolve a parent index, so require the local database and a matching status `projectPath` before sync. Keep any interactive choice limited to local indexing and manual synchronization; decline hook installation or expansion of the scan scope. Account for tool-owned `.codegraph` metadata updates, including during status checks. Recheck status after indexing and confirm that the reported project and worktree identity match the target and that indexing is complete. Subsequent CodeGraph queries must explicitly identify this tree with `projectPath`. This branch neither installs CodeGraph nor configures or manages its services.

Treat this CodeGraph branch as an aid unless the accepted task requires it. If the tool is unavailable or preparation fails, retain existing and partial index state, report the gap and continue through direct source inspection where sufficient; this alone does not change the project environment result or make the workspace `non-ready`. A genuinely task-required CodeGraph capability follows the required-capability checks below. Include its prepared, reused, skipped or unavailable disposition in the handoff.

After preparation, verify any remaining task-required host settings and MCP capabilities, including that their project operations target this worktree. Report configuration `ready` only when the required configuration is usable; unresolved activation or a required unavailable capability yields `non-ready` with its next action.

Recheck target identity and expected state after the assessments and any preparation, accounting for authorized changes. Return `ready` only when creation or reuse is verified, existing work is preserved, configuration status is `ready` or `not-needed`, environment status is `environment-ready`, `not-needed`, or `not-provided`, and no unresolved choice, unauthorized effect, or indispensable prerequisite remains. Otherwise return `non-ready` and preserve the workspace and partial state for safe continuation.

Give the caller a concise readiness handoff:

- Status, target path, branch, immutable base, and current `HEAD`.
- Whether the worktree was created or reused, its carried/inherited-state summary and any carry decision, configuration source and scope with link/copy provenance and readiness, and environment status.
- For `non-ready`, the blocker, retained partial state, and concrete next action.

Keep supporting observations available; the handoff need not reproduce the full evidence inventory.

Readiness covers the workspace and its preparation, not project health. This Skill runs no project baseline, build, or test checks. The implementation workflow owns those checks and commit decisions; carrying inherited work does not authorize committing it. Before using a returned workspace, recheck its current identity and state and investigate unexpected drift.
