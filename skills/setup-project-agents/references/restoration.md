# Restore Local Configuration

Read this guide after the Setup entry selects restoration. Reuse its resolved `<skill-root>`, `<maintain>` and `<target-root>`, its Ownership guidance, and the accepted operation scope. This route recovers lost or changed local configuration or applies configuration-repository changes, in new checkouts or already configured projects. Read [Project Configuration Maintenance](../../maintain-project-config/references/maintenance.md) for binding, backup scope, restoration, Git exclusions and failure recovery. Use its supported commands directly without invoking the user-only maintenance Skill. This route needs neither full-session preflight nor Matt context, migrations, custom-Agent reassessment or generated authoring.

1. **Establish which backup to use.** Reuse still-current local findings from operation selection in the Setup entry, or inspect the selected checkout when those findings are unavailable or stale:

   ```text
   python "<maintain>" inspect --target "<target-root>"
   python "<maintain>" bind --help
   ```

   With an established binding and matching successful local receipt, reuse its repository address, branch and entry unless the user requests a change. For any remaining selection or confirmation, including a requested change with a missing new value, use [Choose the configuration repository](choose-configuration-repository.md) and wait.

   Before binding a source not already verified, use authenticated read-only repository evidence to verify the selected repository and branch contain `projects/<entry>/manifest.json` for the intended backup. If the entry is absent or its existence cannot be verified, stop before `bind`. Use the maintenance reference's repository `bind` route only when needed, preserving existing source and target work. A copied binding alone grants neither restoration nor automatic-sync authority.

2. **Show what applying that backup will change.** Update the bound source, then inspect the actual effects:

   ```text
   python "<maintain>" update --target "<target-root>"
   python "<maintain>" inspect --target "<target-root>"
   ```

   Authentication, fetch or update failure stops application. Retain existing state and report the cause. After a successful update, show differences for the selected complete files and directories, including additions, overwrites and deletions.

   When there are differences, use [Confirm configuration changes](confirm-configuration-changes.md) for the whole restoration choice and wait. Keeping local skips snapshot application and preserves the then-current target and any remaining receipt. A separately accepted binding switch and its Git treatment or receipt changes stay in effect. Work requiring convergence remains pending. Applying the backup requires the exact inspection fingerprint through `--accept-existing`. If source and target already agree, no difference-acceptance token is needed.

   Explain that keeping local does not save those files back to the repository. Preserving an intended target edit there requires the maintenance owner's separately accepted adoption route. If either side changes after inspection, show the new differences and obtain a new choice before applying them; the earlier choice covered different contents.

3. **Set the separate startup preference and apply.** Use [Choose startup synchronization](choose-startup-sync.md) when neither an applicable recorded preference nor a clear answer for this checkout settles it, or when a requested change remains unclear. Retain a recorded preference unless the user requests a change.

   Apply with the recorded or newly accepted preference, adding `--accept-existing "<inspect-fingerprint>"` whenever differences were accepted:

   ```text
   python "<maintain>" apply --help
   python "<maintain>" apply --target "<target-root>" --auto-sync off
   python "<maintain>" inspect --target "<target-root>"
   ```

   Use the recorded or newly accepted value for `--auto-sync`. Verify source-target agreement, the target-local synchronization receipt and applicable Git exclusions through the shared reference's read-only Git checks. The result is the restored snapshot's bytes. Copied `setupVersion` or ownership records establish neither successful full setup nor runtime readiness for this checkout.

4. **Check whether this machine can use the restored configuration.** Use the owners' supported read-only checks for local tools, credentials and services. Report missing or unverifiable prerequisites without installing tools, starting services or rewriting the snapshot as part of restoration.

   Report the source, restored/preserved paths, synchronization preference, exclusions, actual prerequisite results and any failure or recovery evidence. Distinguish restored content from local readiness and explicitly state that full setup was not performed. Restoration neither generates configuration, records a new successful setup version, commits nor publishes source changes. A requested initialization or upgrade follows the separate full-setup route.
