---
name: upgrade-smartkit
description: Advance this repository's SmartKit release version and assess whether its changes require project setup migration.
---

# Upgrade SmartKit

Prepare a version change and an explicit decision about existing projects. A release number identifies the plugin; it does not by itself require setup to run again. Keep necessary migration declarations and concise project instructions together.

This project-local Skill maintains the SmartKit repository. An assessment ends with a proposal; an authorized upgrade follows the sequence below. Publication, installation, commit, and push retain their own authorization.

## 1. Establish the baseline, target, and release scope

Inspect the working tree, index, root [VERSION](../../../VERSION), and existing version edits. Preserve unrelated work and an already accepted target. Resolve material uncertainty about the requested version before changing release inputs.

Establish the preceding published release from repository release records or a verified release tag, and resolve its commit. Compare that release with the complete intended new release, including its staged and unstaged changes. Current `HEAD`, a local version edit, or the newest-looking tag alone does not establish what projects already use. If the baseline is unknown, report the missing evidence before deciding that migration is unnecessary.

Retain the known baseline and target identities, complete release scope, and existing-work record so later checks can distinguish this task's changes.

## 2. Decide what existing projects need

Trace the complete release delta through [setup ownership](../../../skills/setup-project-agents/references/ownership.md), catalogs, blueprints, project configuration schema, entry templates, and setup behavior. Discover related project decisions through the repository's documentation conventions when they explain the contract. A changed filename or blueprint fingerprint is a reason to investigate, not a migration decision.

Require migration when a change affects existing setup's requirements, generated results, or reading contract. Identify what an initialized project would retain and why that state would fail the new contract.

| Change | How to assess it |
| --- | --- |
| Substantive blueprint requirement, incompatible configuration format, required `AGENTS.md` loading, or incompatible project-defined Agent configuration | Determine the required change to existing project state. |
| Blueprint typo | Valid existing outputs can remain usable; a textual delta alone does not require migration. |
| New shared Skill or newly available model | Neither alone requires migration. Full setup owns routine assessment of Agent models and reasoning settings; this decision concerns necessary configuration-contract changes. |

Account for every relevant release change as requiring migration or remaining usable without it, with its concrete project consequence. Resolve uncertain compatibility through the owning source or a targeted check. Complete this decision only when it covers the whole release; a version mismatch is not enough evidence.

## 3. Maintain necessary migration instructions

Before editing records, read [the migration guide](../../../skills/setup-project-agents/references/migrations.md) and [catalog](../../../setup-assets/catalog/migrations.json). Read applicable version guides before deciding their actions. The overview owns applicability and discovery; the catalog associates each necessary migration version with its independent guide.

When migration is necessary, add or reconcile the target release's declaration and `skills/setup-project-agents/references/migrations/<version>.md` together. Set the declaration's `guide` to `references/migrations/<version>.md`; keep instructions in that file without adding a version entry to the overview.

Write for the Agent upgrading an affected project: which project state is affected, what must change, and how to recognize completion. Include prerequisites, ordering constraints, or manual source changes only when they matter to successful upgrade. Refer to owning instructions for execution details already supplied by setup or an invoked writer. Exclude internal-only changes and changes needing no attention from that Agent. A changelog alone cannot make the required action executable or expose the missing project decision.

### Preserve history while reconciling an unpublished release

Retain necessary published migration identities and history so projects can skip releases and satisfy all applicable requirements in one setup. Read earlier applicable entries; explain dependencies and superseded actions without requiring installation of every intermediate plugin version.

Before editing an existing target-version entry, establish that it belongs to the same unpublished release. A conflicting published entry requires a release decision, not silent replacement.

Reconcile that unpublished entry with the current decision. Update its declaration and guide if migration remains necessary; remove an obsolete draft declaration and guide within accepted scope if it does not. Preserve published history and independently owned edits. Unresolved ownership or permission blocks removal and must be reported before release preparation continues.

When no migration is necessary and no obsolete draft exists, leave the catalog, overview, and guides unchanged and report why. An unrelated version bump needs no empty guide.

## 4. Synchronize from the canonical version

Once the target and migration decision are settled, update root `VERSION` and run the owning synchronizer from the repository root:

```bash
python scripts/sync_plugin_version.py
```

Use its current interface and output to identify synchronized manifests and catalog fields instead of maintaining a second list. Review changed paths while preserving unrelated fields and existing edits. On failure, inspect the actual partial result and cause before retrying; reconcile only this task's changes. Failure is not proof that no files changed.

## 5. Verify and hand off

Check version agreement without changing files:

```bash
python scripts/sync_plugin_version.py --check
```

Run applicable owner checks from [CI](../../../.github/workflows/test.yml), including migration validation and tests when declarations or guides changed. Confirm that declarations resolve to matching guides, migration versions fit the release, and earlier necessary entries and files remain available. Follow project translation policy for changed first-party Skill references.

Review the complete diff against the published baseline and existing-work record. Run `git diff <comparison-point> --check`, covering new files too. Source changes, synchronized fields, and the migration decision must agree; a passing synchronizer does not close other required check failures.

Report baseline and target, changed paths, whether migration is required and why, applicable guide entries, and verification results. Completion establishes coherent, checked repository release inputs. It does not establish publication or advancement of any project's recorded setup version.
