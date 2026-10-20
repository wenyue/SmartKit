# Project Configuration Maintenance

This reference owns the shared maintenance contract and command interface used by setup, explicit maintenance and approved startup restoration. Resolve `<plugin-root>` from the loaded Skill installation, `<target-root>` as the business project, and `<plugin-root>/skills/maintain-project-config/scripts/maintain.py` as `<maintain>`. Resources must come from the same supported plugin distribution; an unavailable command or required resource leaves dependent work incomplete. Reading this reference and using its supported commands does not invoke the user-only maintenance Skill.

```text
python "<maintain>" --help
```

Command help owns arguments and output details. The project schema at `<plugin-root>/setup-assets/catalog/project-config.schema.json` owns supported project declarations. Full setup retains initialization, delivery, migrations and successful local setup completion; maintenance owns bindings, snapshots, application, deliberate local synchronization and configuration-repository publication. A restored snapshot does not establish successful setup of a fresh checkout.

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

A new entry has `manifest.json` and `files/`. Its version-2 manifest declares exact target-relative files in `files` and recursive directory roots in `directories`:

```json
{
  "version": 2,
  "files": [".agents/config.json", ".cursor/mcp.json", ".codex/config.toml"],
  "directories": [".agents/rules", ".agents/skills"]
}
```

The snapshot under `files/` preserves selected files byte for byte and selected directories recursively. Native MCP and settings files, project instructions and selected generated files can be backed up in full. Backup neither splits fields nor uses `smartkit.lock.json` to decide which bytes to copy. The lock and existing setup mechanisms retain their separate behavior; restoring a full-file snapshot requires no MCP regeneration. An explicit scope may include the lock as an ordinary complete file; defaults omit it and runtime state.

Select the paths needed to restore the user's configuration. Review their full content before accepting the scope: the backup copies credentials and machine paths if those appear in selected files, and performs no secret filtering. Keep credential values in their existing credential facilities. The target-local `.agents/project-config-sync.json` and legacy `.agents/project-config-state.json` receipts stay outside the backup. When selected, `.agents/config.json` is also copied in full, including binding and `setupVersion`; a copied setup marker is not evidence that this checkout completed setup. Its repository binding must match the selected source; resolve a mismatch rather than silently rewriting snapshot bytes. Snapshots support regular files and directories; symlinks and paths rejected by command validation require resolution before proceeding. Report unavailable source content rather than treating it as an empty backup.

Repeated `--file` arguments to binding and adoption accept files or directories. When creating an entry without explicit selections, the command selects existing default project configuration paths and directories; inspect that actual scope and the complete selected content before publication. The command help and inspection report provide the current selection. Defaults include project entry files, `.agents/config.json`, native MCP/settings files and project Rule, Skill and Agent directories; a default list is a starting scope, not evidence that every project-specific configuration is covered.

Legacy version-1 entries containing individual `files` plus a separate portable `config.json` remain readable with their portable-field projection and generated `AGENTS.md` section handling. `adopt --all` refreshes the complete selected/default snapshot and upgrades a legacy entry to full-file backup. Review that replacement before publication. The old `--field` selector remains only for legacy portable fields; new snapshots use complete files and directories.

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

## Restore a new checkout through startup guidance

The session-start hook checks configuration restoration each session, independently of the daily readiness cache. The hook inspects and supplies guidance; the Agent executes only the restoration the user has approved or already enabled for that checkout. It never publishes source changes or invokes full setup.

When a new checkout has no local synchronization record and needs restoration, ask the user for the configuration-repository Git address each time, then establish the branch, entry and accepted target. Do not discover a source by scanning known repositories or matching the business Git remote. Offer restoration with subsequent automatic synchronization, restoration once, or deferral. For existing target configuration, inspect the concrete differences and present the proposed treatment before accepting replacement. Deferral continues the original task and leaves restoration unresolved.

A valid local binding and receipt let later maintenance reuse the source without asking for its address again. Automatic synchronization is an explicit local preference, defaulting to off. A permitted startup restoration updates the repository before applying. If fetching, authentication or update fails, report the failure and preserve existing state; do not apply a stale checkout as if the update succeeded. Without automatic authorization, request approval for the needed restoration and continue only the accepted actions. Other readiness findings retain their own consent and setup requirements.

## Update before authoring or restoring

```text
python "<maintain>" update --target "<target-root>"
```

The repository support verifies the personal private repository and persistent checkout identity, then fetches and safely fast-forwards supported states. Preserve existing staged, unstaged, untracked and unpublished work before updating. Dirty, divergent or unfinished states may be refused; resolve the reported condition without reset, automatic stash, force push or history rewrite. A failed update supplies no evidence that the checkout is current.

After a successful update, edit or adopt the accepted source scope. Initial import, authoring or deliberate local generation can leave accepted source changes in the same operation; retain their provenance through validation, application and publication without requiring another clean-checkout update between those steps.

## Apply the authoritative backup

```text
python "<maintain>" apply --help
python "<maintain>" inspect --target "<target-root>"
python "<maintain>" apply --target "<target-root>"
```

In repository mode, validate the accepted source and inspect its target effects. A first application over differing existing target files requires case-specific analysis and the user's accepted plan. Then pass `--accept-existing <inspect-fingerprint>` for the exact inspected state; a stale token is refused. Subsequent restoration directly overwrites local differences within the declared scope. To preserve an intended target edit in the backup, explicitly adopt it before applying; no saved per-file history or three-way conflict resolution is involved.

Repository mode records successful restoration in the target-local `.agents/project-config-sync.json`: format version, binding, local source entry, `sourceFingerprint`, `appliedPaths` and the automatic synchronization preference. The source fingerprint covers the selected entry's scope and actual snapshot contents, including accepted unpublished edits, rather than the entire repository commit. Changes to another project do not invalidate this receipt.

The command may skip content writes only when the saved source fingerprint matches and the local selected contents also agree. A changed or missing local file still requires alignment even when the source is unchanged; deciding whether the remote changed still requires updating the repository. `appliedPaths` supports deleting formerly applied files that the backup has removed, without authorizing unrelated target deletion. Record the new fingerprint and applied paths only after successful application; preserve the prior receipt on failure. The legacy receipt is readable for migration and is removed only after successful application of its replacement.

Set the checkout's subsequent startup preference explicitly through the supported application route:

```text
python "<maintain>" apply --target "<target-root>" --auto-sync on
python "<maintain>" apply --target "<target-root>" --auto-sync off
```

Restoration copies the selected snapshot and verifies agreement; it does not render native outputs or establish full setup success. Keep separately required initialization or migration visible, and wait for the user to explicitly invoke its owning Skill. Preserve saved progress and report source, target and receipt outcomes separately when an operation fails.

## Adopt accepted target changes

```text
python "<maintain>" adopt --help
python "<maintain>" adopt --target "<target-root>" --file ".cursor/mcp.json" --file ".agents/rules"
python "<maintain>" adopt --target "<target-root>" --all
```

Adoption is a repository-mode operation that deliberately replaces selected backup content with accepted target content. Inspect current source and target, resolve the intended result and update before adoption. Use repeated exact `--file` selections or `--all` for the complete selected/default scope. Preserve unselected content and unrelated source work. Validate, apply and verify the accepted result before publication; successful adoption alone establishes none of those outcomes.

## Render local configuration only when required

Existing local synchronization remains available for deliberate changes to canonical inputs. It is separate from full-file backup restoration and retains original ownership and collision protections:

```text
python "<maintain>" sync-project --help
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

This route renders established discovery and native Agent, MCP and settings mappings without fetching, blueprint authoring or full migration. Check mode writes nothing: exit 0 means clean, exit 1 means drift, and exit 2 means failure. If rendering intentionally changes selected backed-up files, adopt those accepted results and reconfirm source-target agreement before publication. In either local mode, use this route directly after editing the project's canonical inputs.

When only the generated `Project rules` section in `AGENTS.md` needs updating, use the narrower route, which does not require full setup ownership:

```text
python "<maintain>" sync-project-rules --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

Honor prerequisite and ownership failures. Maintenance neither invokes full setup automatically nor reaches it through another workflow or callback. Preserve saved source and target work, report the unmet prerequisite, and recheck current state after the user completes the owning setup workflow.

## Keep personal configuration out of business Git

Machine-only and repository modes maintain target-local Git exclusions for their configuration scope, local synchronization state and known generated outputs. The maintenance commands manage exclusions after binding, application and deliberate local synchronization; full setup retains its own completion route. Exclusions belong in the target worktree's Git `info/exclude`, resolved by Git and anchored correctly within the business repository, including nested monorepo targets. Preserve shared `.gitignore` files and unrelated exclusion rules.

Exclusions affect untracked paths only. Preserve and report configuration already tracked by business Git; choosing a personal mode grants no automatic untracking or history rewrite. Without a Git worktree, report exclusions as not applicable. Switching to project-shared mode retires only the verified SmartKit-managed block for this target; retain and report other matching exclusions. A failed exclusion update leaves mode enforcement incomplete even if configuration was saved.

Check relevant target-relative paths rather than inferring exclusions from an empty tracked-path report:

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

The first command reports tracked paths; the second identifies the matching ignore rule for an untracked path, with exit 1 meaning no match. Inspection and `--check` do not repair Git state.

## Publish an exact verified scope

In repository mode, an authorized configuration-writing operation, including full setup, maintenance or accepted adoption, includes one exact-scope commit and normal push after required local work succeeds. Proceed without a separate publication confirmation unless the user requests a local result or forbids publication. This default grants no publication for inspection, ordinary business-project editing, other entries or startup restoration, and grants no release, force push or history rewrite. Neither local mode publishes to a configuration repository.

Establish the operation's accepted source changes and outgoing commits before publication, including accepted initial imports and retained current-operation work with verified provenance. An unborn branch can have new source files to publish. Collect exact repository-relative files, including changed manifests and deletions; whole directories, unrelated index entries and unaccepted preexisting content are outside the commit scope. If the operation owns neither pending source changes nor a retained verified commit, finish without an empty commit or publication of earlier work.

Publish after source validation, accepted application, any required deliberate local rendering and all applicable checks succeed. Confirm source-target agreement; full setup must first reach its own successful local finish. A full-file restoration has no automatic renderer prerequisite. An explicit local-result instruction leaves the accepted source work available and reports intentional publication deferral.

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
```

Repeat `--path` for the complete accepted scope. Commit hooks run normally; revalidate hook-altered content, restore it and repeat relevant checks before publication. Preserve the retained commit and diagnostic when publishing is refused. Ambiguous selected paths, unverified outgoing scope or additional outgoing commits require resolution rather than broadening this operation's scope; an older scope receipt does not authorize publication of earlier work.

A failed or uncertain push may leave a valid local commit and applied target. Inspect the actual local and remote outcome before retrying a retained verified commit:

```text
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

Confirm that source and applied evidence still agree. Preserve local commits when the remote advances or diverges and resolve branch state before a protected retry. Verify that the intended commit is reachable on the selected remote branch; a successful-looking push message alone is insufficient.

Report source edits and validation, target application, any deliberate rendering, exclusions and tracked configuration, unmet prerequisites and remote publication separately. Repository-mode completion requires successful local work and verified publication of the intended scope, except for an explicitly requested local result or no owned source changes or commit to publish. A failed push preserves saved source, retained commits, applied target and any successful local full-setup result; report local success and incomplete remote synchronization. Maintenance and publication do not establish new setup success.
