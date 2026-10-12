---
name: upgrade-smartkit
description: Advance this repository's SmartKit release version and assess whether its changes require project setup migration.
---

# Upgrade SmartKit

Prepare a SmartKit version change with an explicit decision about existing projects. A release number identifies the plugin; it does not by itself require those projects to rerun setup. Maintain necessary migration declarations and their concise project instructions together.

This project-local Skill maintains the SmartKit repository. An assessment request ends with a proposal; an authorized version upgrade proceeds through the steps below. Publication, installation, commit, and push retain their own authorization.

## 1. Establish the release being prepared

Inspect the working tree and index, the root [VERSION](../../../VERSION), and existing version edits. Preserve unrelated work and any already accepted target version. Identify the requested target and resolve any material uncertainty about it before changing release inputs.

Establish the preceding published release from repository release records or a verified release tag, and resolve its commit. Use that release as the comparison baseline, including staged and unstaged changes intended for the new release in the target. The current `HEAD`, a local version edit, or the newest-looking tag alone does not prove which release projects already use. If the baseline cannot be established, report the missing evidence before deciding that no migration is needed.

Continue with a known baseline, target version, and release scope. Retain their identities and the existing changes so later verification can distinguish this task's edits from prior work.

## 2. Decide whether existing project setup must change

Compare the baseline with the complete intended release. Trace relevant changes through [setup ownership](../../../skills/setup-project-agents/references/ownership.md), the catalog, blueprints, project configuration schema, entry templates, and setup behavior. Read related project decisions through this repository's documentation conventions when they explain the intended contract. A changed filename or blueprint fingerprint is a signal to investigate, not a migration decision.

Require migration when a change affects the requirements, generated results, or reading contract of existing project setup. Examine what an already initialized project would retain and why leaving it there would fail the new contract. Relevant changes include substantive blueprint requirements, incompatible configuration formats, required `AGENTS.md` loading changes, and incompatible project-defined Agent configuration.

For example, correcting a blueprint's typo leaves its valid project outputs usable; adding a required loading condition can make those outputs incomplete. A new shared Skill or a newly available model does not itself require project migration. Full setup owns routine assessment of project Agent models and reasoning settings; this release assessment concerns a necessary change to their configuration contract, not whether a newer model might be preferable.

Account for every relevant release change as requiring migration or remaining usable without it, with the concrete project consequence behind the decision. Resolve uncertain compatibility from the owning source or a targeted check; a version mismatch alone supplies no evidence. Finish this step only when the migration decision covers the complete release scope.

## 3. Maintain only necessary migration instructions

Read [the setup migration guide](../../../skills/setup-project-agents/references/migrations.md) and [the migration catalog](../../../setup-assets/catalog/migrations.json) before changing migration records. The guide explains applicability and how to find independent version guides under `skills/setup-project-agents/references/migrations/`; the catalog records the release version and guide file for each necessary migration. Read each applicable version guide before deciding its action.

When migration is necessary, add the target release's declaration and one `skills/setup-project-agents/references/migrations/<version>.md` file as one coherent change. The declaration's `guide` is `references/migrations/<version>.md`; keep the migration instructions in that file without adding a version entry to the overview. Keep the file brief: state the main changes and what the affected project must do. Include a prerequisite, ordering constraint, or manual source change only when it affects a successful upgrade. Make the required action specific enough for setup to execute or identify the missing project decision; a changelog entry alone is insufficient.

Retain necessary migration history so a project skipping releases can satisfy all applicable requirements in one setup. Read earlier applicable entries when writing a new one; explain any dependency or superseded action so projects need not install each intermediate plugin version. Keep published migration identities stable. Before editing an existing target-version entry, establish that it belongs to the same unpublished release; resolve a conflicting published entry as a release decision rather than silently replacing it.

Reconcile an existing entry for the same unpublished release with the current migration decision rather than appending a duplicate. If migration remains necessary, update that entry and its version guide. If the release no longer needs migration, remove its obsolete draft declaration and version guide within the accepted editing scope. Preserve published history and independently owned edits; unresolved ownership or permission blocks that removal and must be reported before proceeding with release preparation.

If no migration is needed and no obsolete draft entry exists, leave the catalog, overview, and version guides unchanged. Report the reason; an unrelated version bump needs no empty migration file.

## 4. Advance the canonical version and synchronize

Once the target and migration decision are settled, update the root version to the accepted target and use the existing synchronizer from the repository root:

```bash
python scripts/sync_plugin_version.py
```

The synchronizer owns which manifests and catalog version fields follow `VERSION`; use its current interface rather than maintaining a second list here. Review its changed paths and preserve all unrelated fields and pre-existing edits. If it fails, inspect the actual partial result and cause before retrying. Reconcile only this task's changes; a failed command is not proof that no files changed.

## 5. Verify and hand off the release inputs

Run the version check without modifying files:

```bash
python scripts/sync_plugin_version.py --check
```

Run the applicable owner checks from [CI](../../../.github/workflows/test.yml), including migration validation and tests when declarations or guides changed. Verify that every declaration resolves to its matching version guide, that migration versions fit the target release, and that earlier necessary entries and files remain available. Follow the project translation workflow for changed first-party Skill references.

Review the complete diff against the established baseline and existing-work record. Check whitespace with `git diff <comparison-point> --check`, including new files, and confirm that source changes, synchronized version fields, and the migration decision agree. Required check failures remain unresolved work, even when the version synchronizer reports success.

Report the baseline and target, changed paths, whether project migration is required and why, the applicable guide entries, and verification results. Completion means coherent, checked repository release inputs; it does not mean a release was published or any project's recorded setup version was advanced.
