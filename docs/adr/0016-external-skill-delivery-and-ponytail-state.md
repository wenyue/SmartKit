# Deliver External Skills Through Their Owners and Use Fixed Full Ponytail

Status: Accepted

Date: 2026-09-24

External Skills need reproducible upstream provenance and maintainable SmartKit adaptations.
We keep external snapshots under the owning updater and use fixed full Ponytail behavior.

This records the delivery boundaries alongside
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

Every successful update or check reports patch extent by comparing resolved pristine upstream
with the final patched Skill tree. Split text into whitespace-delimited words and report additions
and deletions separately; report non-text file changes outside word counts. Modification percentage
is added words / original words × 100; deleted words do not increase it. Report an unavailable
percentage when the original word count is zero.

## Fixed Full Ponytail

Ponytail is delivered through four independent Skills: `ponytail`, `ponytail-review`,
`ponytail-audit`, and `ponytail-debt`. [rule-code](../../skills/rule-code/SKILL.md#ponytail-loading)
owns required per-task loading for coding work; [Ponytail](../../skills/ponytail/SKILL.md) owns its
fixed full simplification behavior. The review, audit, and debt Skills remain task-selected.
Ponytail has no configurable modes, saved preferences, conversation state, or state Hooks.

Cross-task principles remain with [Reasoning Workflow](../../rules/core-reasoning-workflow.md) and
[Agent Personality](../../rules/core-personality.md).

## Verification

Exercise the updater's update/check boundary with temporary upstream sources. Check final output
and failure effects, including patch conflicts, unrecorded changes, and patch statistics. Run
applicable manifest, Rule delivery, translation, and repository checks after regenerating snapshots.

Patch files themselves must pass Git whitespace checks as well as applying successfully. Empty
context lines may omit the context prefix; shorten a trailing empty context with the corresponding
hunk counts instead of disabling whitespace checks. Review the complete applied Skill, since a
mechanically applicable patch does not establish coherent instructions or correct loading.
