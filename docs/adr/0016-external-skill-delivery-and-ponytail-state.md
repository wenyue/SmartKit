# Deliver External Skills Through Their Owners and Isolate Ponytail State

Status: Accepted

Date: 2026-09-24

External Skills need reproducible upstream provenance and maintainable SmartKit adaptations.
Ponytail also needs conversation-local behavior without coupling an active conversation to future
default changes or to another Agent's mode changes. We keep external snapshots under the owning
updater and separate Ponytail's saved defaults from explicitly identified conversation state.

This records the delivery and state boundaries alongside
[ADR 0015](0015-patch-external-skill-snapshots.md), which owns the decision to apply versioned
patches. Coding-specific simplification remains with Ponytail under the general core principles.

## Snapshot Delivery

The external Skill updater owns the distributed snapshots. The registry selects each upstream
repository, revision, license, and Skill; each Skill may list ordered, repository-relative
`patches`. A patch uses paths relative to that upstream Skill's root, such as `a/SKILL.md` and
`b/SKILL.md`. Keep the patch narrowly scoped to accepted SmartKit differences.

Run `python scripts/update_external_skills.py --update` to derive all selected snapshots, or add
`--source <owner/repository>` to update one source. Run the same command with `--check` instead
of `--update` to verify the derived contents and lock. These operations resolve upstream sources
and may require network access; `--check` is not an offline-only lock check.

The updater validates upstream content, applies patches in staging, validates the result, and
records final file hashes together with patch paths and hashes. Installation preserves the
existing transaction boundary across Skills, licenses, and lock. A patch conflict leaves the
previous installation intact. Unrecorded edits in managed output stop an update: first preserve
and express the intended change in the owning patch, then restore the corresponding generated
output to its recorded state before updating. Never discard another person's changes to make an
update pass.

Review an upgrade against the old upstream revision, the new revision, and the existing local
patches. An authorized upgrade can repair patch context while preserving accepted behavior;
changed behavior requires a new decision. Preserve upstream wording outside those changes and
retain license and copyright notices. The registry, lock, and patches are the provenance and
delta records; no separate Markdown diff ledger is maintained.

## Ponytail Modes

Ponytail is delivered through four independent Skills: `ponytail`, `ponytail-review`,
`ponytail-audit`, and `ponytail-debt`. [rule-code](../../skills/rule-code/SKILL.md#ponytail-loading)
owns required per-task loading for coding work; [Ponytail](../../skills/ponytail/SKILL.md) owns its
simplification, modes, and state. The review, audit, and debt Skills remain task-selected and do
not switch modes. Hooks deliver conversation state alongside the existing SmartKit context,
not Ponytail's instructional body.

Cross-task principles remain with [Reasoning Workflow](../../rules/core-reasoning-workflow.md) and
[Agent Personality](../../rules/core-personality.md). These general principles continue to apply
when Ponytail's continuous coding simplification is off.

`/ponytail off|lite|full|ultra` changes only the current conversation. `/ponytail default <mode>`
changes the saved default for future conversations. A new conversation resolves
`PONYTAIL_DEFAULT_MODE`, then the saved `defaultMode`, then `full`. Existing conversations retain
their selected mode across reload, resume, and compaction. An environment override remains
effective after changing the saved default; the mode helper reports both values.

The JSON preferences file is `%APPDATA%/smartkit/ponytail.json` on Windows. Elsewhere it is
`smartkit/ponytail.json` below `XDG_CONFIG_HOME` when set, or below `~/.config`. It retains the upstream `defaultMode`
field and preserves unrelated saved fields when updating it. Invalid or unreadable data is
reported instead of being silently overwritten.

Runtime state is separate from preferences. Each native Harness conversation ID gets its own
opaque handle; Skill commands explicitly pass that handle to the mode helper. State resides
under `smartkit/ponytail` in `XDG_STATE_HOME`, Windows local application data, or `~/.local/state`.
It remains available for conversation restoration; ending a process does not delete it.

The state Hook independently directs every delegation, including non-coding work and off mode,
to load the `ponytail` Skill's inheritance protocol. Ordinary noncoding tasks need no per-task
Ponytail load. Before delegating, the Skill creates an independent child handle with the parent's
current mode and passes it in the child task. That delegated handle takes precedence over a host handle
in the child's context. Preserve it when resuming or handing off the same task. Subsequent
parent, child, and sibling switches are independent. This route does not assume that all hosts
expose interchangeable parent and child IDs through their subagent Hooks.

A missing native ID is reported as unavailable; a working directory, process ID, or shared
`.ponytail-active` file is not an isolation fallback. Resolve missing handles or failed state
operations before claiming a mode change succeeded. Independent specialized Skills remain
available without changing persistent mode state.

## Verification

Exercise the updater's update/check boundary and Ponytail's command and native Hook boundaries.
Use temporary upstream sources and isolated configuration/state directories. Check final output
and failure effects, including patch conflicts, unrecorded changes, conversation isolation,
restoration, and parent/child independence. Run applicable manifest, Rule delivery, translation,
and repository checks after regenerating snapshots.

Patch files themselves must pass Git whitespace checks as well as applying successfully. Empty
context lines may omit the context prefix; shorten a trailing empty context with the corresponding
hunk counts instead of disabling whitespace checks. Review the complete applied Skill, since a
mechanically applicable patch does not establish coherent instructions or correct loading.
