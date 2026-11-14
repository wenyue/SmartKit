The valid local receipt for target {target} authorizes startup synchronization. Read the maintenance contract at <plugin-root>/skills/maintain-project-config/references/maintenance.md from this Hook's plugin installation.

Run `update`, then `reconcile` without `--adopt-local`. Use the result to choose the next action:

| Result | Action |
| --- | --- |
| `source-updated` | Restore automatically with `apply --accept-existing` and the exact inspection fingerprint. |
| `in-sync` | Use `apply` to record agreement. |
| `needs-choice` with `local_updates_only` | Show changed paths and content differences; ask whether to save local changes to the configuration repository or defer. |
| Other `needs-choice` | Show changed paths and content differences; ask whether to save local, use the configuration repository or defer. |
| Update failure | Preserve both sides and report the failure; do not proceed to application. |

An accepted save authorizes its exact scope and normal commit/push without a second confirmation. Follow the maintenance contract's guarded save and publication route.

Deferral preserves local files and the prior receipt; report it and continue independent original work. Report any independent setup prerequisite and partial results under their owning contracts.
