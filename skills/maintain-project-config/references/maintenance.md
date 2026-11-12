# Project Configuration Maintenance

This reference owns the shared maintenance contract and command interface for callers that manage project configuration. Resolve `<plugin-root>` from the loaded Skill installation, `<target-root>` as the business project, and `<plugin-root>/skills/maintain-project-config/scripts/maintain.py` as `<maintain>`. Resources must come from the same supported plugin distribution; an unavailable command or required resource leaves dependent work incomplete. Reading this reference and using its supported commands does not invoke the user-only maintenance Skill.

```text
python "<maintain>" --help
```

Command help owns arguments and output details. The project schema at `<plugin-root>/setup-assets/catalog/project-config.schema.json` owns supported project declarations. The caller establishes its requested operation and prerequisites. Maintenance owns bindings, snapshots, application, deliberate local synchronization and configuration-repository publication. A restored snapshot does not establish successful setup of a fresh checkout.

## Choose the maintenance mode

The target's `.agents/config.json` records its mode and, in repository mode, the repository, branch and project entry. Present these three choices together in the user's language:

| User-facing mode | Stored mode | Configuration and Git treatment |
| --- | --- | --- |
| Project shared | `local` | Canonical inputs stay in the business project for sharing through its Git repository. SmartKit adds no personal configuration exclusions. |
| This machine only | `local-only` | Canonical inputs stay in the business project and configuration paths are excluded from business Git locally. No configuration-repository access is required. |
| Separate configuration repository | `repository` | A personal private GitHub repository stores the selected complete configuration backup; target configuration paths are excluded from business Git locally. |

Existing `local` bindings retain project-shared meaning. A missing choice is readable legacy state and requires the user's selection before binding. Both local modes retain existing authoring and rendering behavior; selecting project-shared mode does not stage, commit or push business-project files. A binding contains no machine-specific checkout path.

```text
python "<maintain>" inspect --target "<target-root>"
```

Inspection reads available binding, source, target and synchronization state without fetching, repairing exclusions or writing configuration. Report unavailable evidence instead of assuming a complete backup. Repository mode uses a persistent user-owned checkout and the entry `projects/<entry>/`; this checkout may contain the only copy of unpublished work and is not a disposable cache. Entries have independent scope.

## Back up complete files and directories

An entry has `manifest.json` and `files/`. Its manifest declares exact target-relative files in `files` and recursive directory roots in `directories`:

```json
{
  "files": [".agents/config.json", ".cursor/mcp.json", ".codex/config.toml"],
  "directories": [".agents/rules", ".agents/skills"]
}
```

Only `files` and `directories` are supported manifest fields. Versioned manifests are unsupported; report the format error and preserve the source rather than converting it.

The snapshot under `files/` preserves selected files byte for byte and selected directories recursively. Selecting `AGENTS.local.md` through `ruleEntry` does not by itself add that local file to an existing manifest; explicitly select it through the accepted backup-scope route when it needs restoration. Native MCP and settings files, project instructions and selected generated files can be backed up in full. Backup neither splits fields nor uses `smartkit.lock.json` to decide which bytes to copy. The lock and existing setup mechanisms retain their separate behavior; restoring a full-file snapshot requires no MCP regeneration. An explicit scope may include the lock as an ordinary complete file; defaults omit it and runtime state.

### Accept the complete selected content

Select the paths needed to restore the user's configuration. Review their full content before accepting the scope: selected files can contain credentials and machine paths, and backup performs no secret filtering. Keep credential values in their existing credential facilities and target-local synchronization state outside the backup.

When selected, `.agents/config.json` is copied in full, including binding and `setupVersion`. A copied setup marker does not prove that this checkout completed setup. Its repository binding must match the selected source; resolve a mismatch rather than silently rewriting snapshot bytes.

Snapshots support regular files and directories. Symlinks and paths rejected by command validation require resolution before proceeding. Report unavailable source content rather than treating it as an empty backup.

Repeated `--file` arguments to binding and adoption accept files or directories. When creating an entry without explicit selections, the command selects existing default project configuration paths and directories; inspect that actual scope and the complete selected content before publication. The command help and inspection report provide the current selection. Defaults include project entry files, `.agents/config.json`, native MCP/settings files and project Rule, Skill and Agent directories; a default list is a starting scope, not evidence that every project-specific configuration is covered.

## Bind or deliberately change a source

Before repository binding or update, require Git and the GitHub CLI (`gh`), authenticated as the repository's owning personal account on its github.com or GitHub Enterprise hostname. The private repository must be accessible to that account. These operations verify the repository and use authenticated Git access; missing tools or access stops repository-dependent work while preserving existing state. Credentials remain in the user's credential facilities, outside the binding.

```text
python "<maintain>" bind --help
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<repository>" --branch "<branch>" --entry "<entry>"
```

Local modes accept no repository arguments or import selections. For repository mode, establish the user's personal private repository, branch and project entry; a remote default branch is a possible choice, not a value to assume. Creating a repository requires the user's specified identity and name and explicit `--create-repository`. Use `owner/repository` for github.com or a credential-free HTTPS GitHub Enterprise URL such as `https://github.example/owner/repository.git`. The hostname selects authentication and separates persistent checkouts of same-named repositories on different hosts.

For a new entry, inspect existing target content and accept its backup scope before binding. A successful binding records the selected maintenance choice in the target, and an initial full-file backup of `.agents/config.json` includes the resulting bound document. If binding fails after saving source content, preserve and report that source work separately from the target outcome. For example, select complete MCP configuration and project Rules with `--file ".cursor/mcp.json" --file ".agents/rules"`. Import selections apply only to new entries; use adoption to refresh an existing entry after update and inspection.

Use `--replace-binding` only for a deliberate mode or source switch. Inspect the old source, target and proposed source, preserve unpublished work, and establish the intended content before retrying a refused switch. A routine upgrade retains the binding. Switching neither deletes the old source nor authorizes discarding pending work; the binding command owns retirement of obsolete local synchronization state.

For a nested project that owns the Git-root Wiki, a deliberate switch verifies agreement with the old Wiki backup before retiring its matching receipt. It preserves Wiki files and both source entries. A switch to project-shared mode clears the project's own root Wiki exclusions. Subsequent Wiki maintenance uses the new binding.

## Restore explicitly or synchronize at startup

For an explicit restoration, reuse an existing repository binding only when a matching local receipt records successful restoration in this checkout. Otherwise ask the user for the configuration-repository Git address, branch and existing project entry before binding the selected source. A copied binding without a successful local receipt requires this selection too. Infer no source from business remotes, known repositories or other local checkouts. Inspect concrete target differences and obtain the user's choice before every differing application through the route below.

Restore-only operations use binding, update, inspection and application to restore the selected backup's exact bytes, then check local prerequisites and Git treatment. They author no source, generate no configuration, invoke no full setup and publish no source changes. Report missing local tools, credentials or services separately from restored content; their absence does not authorize rewriting the snapshot.

Automatic startup synchronization is an explicit local preference, defaulting to off. The session-start hook supplies synchronization guidance only for a bound repository checkout with a matching successful receipt and automatic synchronization enabled. Update the backup, run `reconcile` without `--adopt-local`, and follow the [reconciliation outcomes](#adopt-accepted-target-changes). Startup may restore a proven repository-only update without another question. Saving local changes requires the user's acceptance of that upload; automatic synchronization alone grants no upload authority. An unbound or disabled checkout stays silent. Report invalid enabled bindings or receipts. Explicit manual restoration remains available while automatic synchronization is off. Other readiness findings retain their own consent and setup requirements.

## Update before authoring or restoring

```text
python "<maintain>" update --target "<target-root>"
```

The repository support verifies the personal private repository and persistent checkout identity, then fetches and safely fast-forwards supported states. Preserve existing staged, unstaged, untracked and unpublished work before updating. Dirty, divergent or unfinished states may be refused; resolve the reported condition without reset, automatic stash, force push or history rewrite. If authentication, fetching or update fails, preserve existing state and stop before application; a stale checkout cannot stand in for a successful update.

After a successful update, edit or adopt the accepted source scope. Initial import, authoring or deliberate local generation can leave accepted source changes in the same operation; retain their provenance through validation, application and publication without requiring another clean-checkout update between those steps.

## Apply the authoritative backup

```text
python "<maintain>" apply --help
python "<maintain>" inspect --target "<target-root>"
python "<maintain>" apply --target "<target-root>"
```

In repository mode, validate the accepted source and inspect its target effects. A differing application requires the user's whole-synchronization choice, except for a proven repository-only update during enabled startup synchronization. Show the changed paths and content differences, including additions, deletions, and binary differences, before asking for a choice. For authorized setup or maintenance that keeps newer local configuration, [resolve and adopt](#adopt-accepted-target-changes) accepted local updates before application. While a choice remains pending, preserve the whole target.

### Apply the user's whole-synchronization choice

**Save local to the configuration repository** accepts the reviewed local content and backup scope, including any overwrites or deletions of source files. Follow the adoption route below, validate the accepted result, apply to record agreement, and publish only that operation's exact verified scope. Acceptance includes the scoped commit and normal push; no second publication confirmation is needed unless the user requests a local result or forbids publication.

**Keep local for now** skips this synchronization, preserving target contents and the prior synchronization receipt. Report the skipped synchronization and remaining differences. Independent work may continue; work requiring source/target convergence stays pending. This choice neither adopts local content nor publishes it to the configuration repository. Later synchronization still checks the differences.

**Use the configuration repository** applies the complete reviewed restoration, passing `--accept-existing <inspect-fingerprint>` for the exact inspected state. If either side changes after inspection, inspect again, show the new differences, and obtain a new choice; a stale token is refused. No saved per-file history or three-way conflict resolution is involved. When source and target already agree, application needs no difference-acceptance token.

### Record verified agreement and the startup preference

Repository mode records successful agreement in the target-local `.agents/project-config-sync.json` with `binding`, `source`, `sourceFingerprint`, `sourceManifest`, `appliedPaths` and `automatic`, without a format version. The source fingerprint covers the selected entry's scope and actual snapshot contents, including accepted unpublished edits, rather than the entire repository commit. `sourceManifest` records that scope so reconciliation can verify the complete local baseline after the repository changes. Existing receipts without it remain readable, but cannot prove that only the repository changed; the next successful application records the scope. Changes to another project do not invalidate this receipt. Versioned receipts are unsupported; report the format error and preserve the state rather than migrating it.

The command may skip content writes only when the saved source fingerprint matches and the local selected contents also agree. `appliedPaths` supports proposing deletion of formerly applied files that the backup has removed. Record the new fingerprint, scope and applied paths after successful application. Preserve the prior receipt on refusal or failure.

Set the checkout's subsequent startup preference explicitly through the supported application route, obtaining difference acceptance as above when needed:

```text
python "<maintain>" apply --target "<target-root>" --auto-sync on
python "<maintain>" apply --target "<target-root>" --auto-sync off
```

Restoration copies the selected snapshot and verifies agreement; it does not render native outputs or establish full setup success. Keep separately required initialization or migration visible, and wait for the user to explicitly invoke its owning Skill. Preserve saved progress and report source, target and receipt outcomes separately when an operation fails.

## Adopt accepted target changes

After updating, use `reconcile` to classify differences against the last successful local receipt. A repository-only update requires the complete local contents to match the recorded baseline scope, with no differing local content overwritten by newly selected source paths. A changed repository fingerprint alone does not establish that the local configuration is behind. Local-only changes mean the repository snapshot still matches the receipt; additions, edits and deletions all count. When both sides changed or the baseline cannot establish the direction, obtain the user's choice even if the repository appears to contain the local changes.

For local-only changes at startup, show the differences and ask whether to save them to the configuration repository or keep local for now. Once the user accepts the save, or an existing configuration-writing task already covers it, pass `--adopt-local` to plan it. Review the plan's scope and complete selected content under the backup-scope contract. Retain the accepted `planned` JSON in private task state, then execute with its `plan_fingerprint` through `--accept-plan`.

```text
python "<maintain>" reconcile --target "<target-root>"
python "<maintain>" reconcile --target "<target-root>" --adopt-local
python "<maintain>" reconcile --target "<target-root>" --adopt-local --accept-plan "<plan-fingerprint>"
```

| Result | Next action |
| --- | --- |
| `in-sync` | Apply the agreed snapshot when this operation needs to record agreement. |
| `source-updated` | At enabled startup, apply with the exact inspection fingerprint without another question. An explicit manual restoration still requires the user's difference choice. |
| `adopted` | Apply to record agreement. Retain `source_changes` for authorized publication. |
| `planned` | Review the exact save and retain its JSON before executing it. |
| `needs-choice` | When `local_updates_only` is true, ask whether to save local changes or keep local for now. Otherwise show the differences and offer the whole-synchronization choices: save local, use the repository, or keep local for now. |

For a proven repository-only update at enabled startup, the recorded preference accepts the direction; bind application to the exact inspected contents:

```text
python "<maintain>" apply --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

If the plan changes or its local-only evidence no longer holds, inspect the new state and reestablish the decision. The `source_changes` keys are exact repository-relative paths. Each value is the intended content digest, or `null` for a deletion.

When both sides changed or the direction is unknown, an explicit choice to save local content permits guarded `adopt` for the exact differing files covered by that choice. Review source overwrites and deletions before obtaining it. If the guard refuses a changed fingerprint, inspect again and reestablish the decision. Apply to record agreement, then carry `source_changes` into publication.

```text
python "<maintain>" adopt --target "<target-root>" --accept-existing "<inspect-fingerprint>" --file ".agents/rules/project.md"
```

For other deliberate adoption, inspect current source and target and resolve the intended result before saving the accepted scope:

```text
python "<maintain>" adopt --help
python "<maintain>" adopt --target "<target-root>" --file ".cursor/mcp.json" --file ".agents/rules"
python "<maintain>" adopt --target "<target-root>" --all
```

Use repeated exact `--file` selections, or `--all` to refresh the files and directories already declared in the manifest. With `--all`, missing declared files are removed from the backup and manifest, and directory declarations remain. Preserve unselected content and unrelated source work. Validate, apply and verify the accepted result before publication.

## Render local configuration only when required

Existing local synchronization remains available for deliberate changes to canonical inputs. It is separate from full-file backup restoration and retains original ownership and collision protections:

```text
python "<maintain>" sync-project --help
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

This route renders established discovery and native Agent, MCP and settings mappings without fetching, blueprint authoring or full migration. Check mode writes nothing: exit 0 means clean, exit 1 means drift, and exit 2 means failure. If rendering intentionally changes selected backed-up files, adopt those accepted results and reconfirm source-target agreement before publication. In either local mode, use this route directly after editing the project's canonical inputs.

The schema's `ruleEntry` selects `AGENTS.md` (the default) or `AGENTS.local.md` for the generated `Project rules` section. Both local synchronization routes manage that section in the selected file, preserving its other bytes and the unselected entry. Changing the selection does not move or remove an existing section or delete the former entry.

When only that generated section needs updating, use the narrower route, which does not require full setup ownership:

```text
python "<maintain>" sync-project-rules --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

Honor prerequisite and ownership failures. Maintenance neither invokes full setup automatically nor reaches it through another workflow or callback. Preserve saved source and target work, report the unmet prerequisite, and recheck current state after the user completes the owning setup workflow.

## Keep personal configuration out of business Git

Machine-only and repository modes maintain target-local Git exclusions for their configuration scope, local synchronization state and known generated outputs. Machine-only mode includes the selected Rule entry in those exclusions. The maintenance commands manage exclusions after binding, application and deliberate local synchronization. Exclusions belong in the target worktree's Git `info/exclude`, resolved by Git and anchored correctly within the business repository, including nested monorepo targets. Preserve shared `.gitignore` files and unrelated exclusion rules.

Exclusions affect untracked paths only. Preserve and report configuration already tracked by business Git; choosing a personal mode grants no automatic untracking or history rewrite. Without a Git worktree, report exclusions as not applicable. Switching to project-shared mode retires only the verified SmartKit-managed block for this target; retain and report other matching exclusions. A failed exclusion update leaves mode enforcement incomplete even if configuration was saved.

Check relevant target-relative paths rather than inferring exclusions from an empty tracked-path report:

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

The first command reports tracked paths; the second identifies the matching ignore rule for an untracked path, with exit 1 meaning no match. Inspection and `--check` do not repair Git state.

## Maintain OpenWiki with the project binding

OpenWiki inherits the selected project's established binding. Supply that project as `--target` so the commands derive the Git top-level for Wiki files. An independently bound Git root owns its Wiki. Resolve an ownership conflict under that binding. In repository mode, a nested project's Wiki backup lives under `projects/<entry>/wiki/` with its receipt at the Git root in `.agents/openwiki-config-sync.json`. When the project is the Git root, prepare uses the ordinary project snapshot.

Before a new run, establish authority for the Git-root writes. In repository mode, use current refresh evidence for this binding or run the ordinary `update` command. Then prepare the Wiki. `ready` establishes the inherited Git treatment and reports any applied backup changes and tracked paths. For `needs-choice`, use the [whole-synchronization choice](#apply-the-users-whole-synchronization-choice) and pass its exact fingerprint if the user accepts restoration. Resume an active Wiki run in its own worktree before preparing or saving its backup.

```text
python "<maintain>" wiki prepare --target "<target-root>"
python "<maintain>" wiki prepare --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

The Wiki owner verifies the completed result in every mode. In repository mode, `wiki save` plans a backup of the complete `openwiki/` directory and any `.openwikiignore`. Add `--file` for each changed Git-root `AGENTS.md` or existing `CLAUDE.md` accepted for complete-file backup. Review the exact selection and content, retain the plan JSON, then execute the same selection with `--accept-plan`. Save verifies agreement and records the receipt.

```text
python "<maintain>" wiki save --target "<target-root>" > "<wiki-save-plan.json>"
python "<maintain>" wiki save --target "<target-root>" --accept-plan "<plan-fingerprint>"
```

If saving stops after writing the backup, verify the saved source against the retained plan. Use `wiki prepare` to record agreement when needed and resume publication with the original accepted scope. An empty new plan leaves any previously owned source changes or retained commit pending. Use the [publication contract](#publish-an-exact-verified-scope) for the established scope.

```text
python "<maintain>" wiki publish --target "<target-root>" --plan "<wiki-save-plan.json>" --message "Back up OpenWiki"
```

## Publish an exact verified scope

In repository mode, an authorized configuration-writing operation includes one exact-scope commit and normal push after required local work succeeds. Proceed without a separate publication confirmation unless the user requests a local result or forbids publication. This default grants no publication for inspection, ordinary business-project editing, other entries or any restore-only operation, whether manual or automatic, and grants no release, force push or history rewrite. Neither local mode publishes to a configuration repository.

Establish the operation's accepted source changes and outgoing commits before publication, including accepted initial imports and retained current-operation work with verified provenance. An unborn branch can have new source files to publish. Collect exact repository-relative files, including changed manifests and deletions; whole directories, unrelated index entries and unaccepted preexisting content are outside the commit scope. If the operation owns neither pending source changes nor a retained verified commit, finish without an empty commit or publication of earlier work.

When an accepted adoption result covers the complete publication scope, use its JSON with `--plan`. The command verifies every path and content digest. For a separately assembled scope, pass one `--path` per accepted file. These routes apply to both `publish` and `wiki publish`.

Publish after source validation, accepted application, any required deliberate local rendering and all applicable checks succeed. Confirm source-target agreement. The caller establishes completion of any additional prerequisites before using this publication route. A full-file restoration has no automatic renderer prerequisite. An explicit local-result instruction leaves the accepted source work available and reports intentional publication deferral.

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --plan "<adoption-result.json>" --message "Update project configuration"
```

Commit hooks run normally. Revalidate hook-altered content, restore it and repeat relevant checks before publication. Preserve the retained commit and diagnostic when publishing is refused. Resolve ambiguous selected paths, unverified outgoing scope or additional outgoing commits within the current accepted scope.

### Recover a failed or uncertain publication

A failed or uncertain push may leave a valid local commit and applied target. Inspect the actual local and remote outcome before retrying a retained verified commit:

```text
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

Confirm that source and applied evidence still agree. Use the corresponding `publish` or `wiki publish` route and reuse `--plan` when the operation has accepted plan evidence. Preserve local commits when the remote advances or diverges and resolve branch state before a protected retry. Verify that the intended commit is reachable on the selected remote branch.

### Report the established result

Report source edits and validation, target application, any deliberate rendering, exclusions and tracked configuration, unmet prerequisites and remote publication separately. Repository-mode completion requires successful local work and verified publication of the intended scope, except for an explicitly requested local result or no owned source changes or commit to publish. A failed push preserves saved source, retained commits, applied target and completed local work. Report local success and incomplete remote synchronization. The caller owns any broader completion result.
