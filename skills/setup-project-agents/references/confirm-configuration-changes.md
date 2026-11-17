# Confirm configuration changes

Ask when the maintenance contract requires a source/target decision, a backup-scope choice, or acceptance of a save plan. Show the direction and the paths and content that would be added, replaced, or removed, including binary differences where relevant. Identify the selected backup as the repository, branch, and project entry. Use a concise summary with the actual changes available for review. If the inspected contents change, show the new differences and obtain a choice for that version.

## Choose the direction

Choose the prompt for the observed state and operation. Every option applies to the whole reviewed scope. Keeping local skips synchronization, preserves the then-current target and any remaining receipt, and leaves work requiring convergence pending. Any separately accepted binding or Git exclusion changes stay in effect. Retain the chosen direction and exact inspection fingerprint for guarded application or adoption.

In each save prompt, state the effect that applies to this operation. For a publishing result, say that the reviewed changes will be committed and pushed after validation. For a local result, say that the changes will be saved in the local configuration checkout and publication deferred.

### Apply the backup or keep local

Use this for a differing restore-only operation or for differing full-setup application after `source-updated`. The startup exception for repository-only updates does not apply to these operations.

> Applying the backup from `<repository>` (`<branch>`, `<entry>`) would make these changes in `<project>`.
>
> <Reviewed changes by path>
>
> - **A. Keep the local files.** Skip applying the backup.
> - **B. Apply the backup.** Make the changes shown above.
>
> You can reply **A** or **B**.

### Save local changes or keep local

Use this for project reconciliation returning `needs-choice` with proven local-only changes in full setup. Show which complete source files the save affects.

> Only the local configuration changed since the last sync.
>
> <Reviewed changes by path>
>
> - **A. Save the local changes.** <Save effect for this operation>
> - **B. Keep them here for now.** Leave synchronization pending.
>
> You can reply **A** or **B**.

### Choose a direction when the changes cannot be reconciled automatically

Use this for project reconciliation returning `needs-choice` in full setup when both sides changed or the direction is unknown. Explain the concrete effects of each direction, including source or target overwrites and removals.

> <What changed or why the direction is uncertain>
>
> <Reviewed changes in each direction>
>
> - **A. Save the local configuration to the backup.** <Save effect for this operation>
> - **B. Apply the backup to this project.** Apply the reviewed changes locally.
> - **C. Keep the local files for now.** Skip this synchronization.
>
> You can reply **A**, **B**, or **C**.

### Prepare the OpenWiki backup

`wiki prepare` reports `needs-choice` for any differing backup. When the project is the Git root, run ordinary project `reconcile` on that shared snapshot and use the matching prompt above. When the user chooses to save and both sides changed or the direction is unknown, use the reviewed files and inspection fingerprint for guarded `adopt --accept-existing`. For a plan-based save, use the accepted plan's fingerprint. Record agreement and rerun `wiki prepare` after a save.

For a nested Wiki, use the apply/keep prompt with the exact Git-root paths and the `source_updates_only` evidence from `wiki prepare`. Offer a save only when the source has not changed since the last sync and a `wiki save` plan for the nested scope passes the maintenance contract's checks. In either case, if the user accepts applying the backup, run `wiki prepare --accept-existing` with the exact reviewed inspection fingerprint. If the user keeps local, leave preparation pending and retain the recovery evidence.

## Backup scope

For an initial import or scope addition, show the exact files and directory roots and review their complete contents under the maintenance contract. Reuse an existing acceptance covering the same scope and contents.

> I can include these paths in the backup for `<project>`. This will save the full files and everything under any listed directory.
>
> <Proposed paths and effects>
>
> Reply **include these** or tell me which paths to change.

## Save plan

If acceptance of the exact save plan is still needed, show the complete source changes and retain the accepted plan and fingerprint before executing it.

> Saving the local configuration would make these changes in the backup at `<repository>` (`<branch>`, `<entry>`).
>
> <Reviewed source changes by path>
>
> <Save effect for this operation>
>
> Reply **save these changes** to accept this plan, or **keep local** to defer it.
