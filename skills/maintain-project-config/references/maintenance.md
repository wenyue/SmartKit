# Project Configuration Maintenance

This reference and its commands serve maintenance, setup, startup synchronization and OpenWiki. Resolve `<maintain>` to `skills/maintain-project-config/scripts/maintain.py` in the loaded plugin and `<target-root>` to the business project. Use `python "<maintain>" --help` for command options and `setup-assets/catalog/project-config.schema.json` from that plugin for project declarations. Report unavailable resources and leave dependent work incomplete.

## Choose the maintenance mode

```text
python "<maintain>" inspect --target "<target-root>"
```

Inspection is read-only and works with locally available evidence. For an unbound project, present the three modes together in the user's language. Reuse a valid binding, and obtain the user's decision before replacing existing configuration during initialization.

| Mode | Stored value | Where configuration stays |
| --- | --- | --- |
| Project shared | `local` | In the project for sharing through business Git. |
| This machine only | `local-only` | In the project with local Git exclusions. |
| Separate configuration repository | `repository` | In the project with local exclusions, backed up in a personal private GitHub repository. |

## Bind or deliberately change a source

```text
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<repository>" --branch "<branch>" --entry "<entry>"
```

Repository operations use Git and `gh` authenticated as the owning personal account on the matching GitHub or GitHub Enterprise host. Confirm the repository, branch and entry. Use `owner/repository` for github.com or a credential-free HTTPS URL for the selected host. Use `--create-repository` only with explicit permission to create the named repository. `bind` and `publish` verify ownership and privacy. A successful `update` verifies the checkout and fetch, so check ownership or privacy separately if uncertain.

Before connecting an existing entry, verify its `projects/<entry>/manifest.json` in the state `bind` will use after refresh. Check the selected remote branch for a fresh clone, or the preserved entry in the existing checkout, which may contain accepted unpublished work. A missing or unverified entry blocks connection because `bind` can import local files into a new entry. Use `--replace-binding` only for an accepted switch. Resolve outstanding differences first, including a nested project's owned Git-root Wiki, and preserve existing work and entries.

## Back up complete files and directories

Each entry's `manifest.json` selects target-relative `files` and recursive `directories` under `files/`. Review complete contents, including credentials and machine paths. Keep secrets in credential facilities and synchronization receipts out of the backup. Selected native settings, MCP files and `.agents/config.json` are copied in full. The configuration lock does not choose the scope, and `ruleEntry` alone does not add files to it. A copied setup marker does not prove local setup or readiness. Preserve and report unreadable or unsupported state, including versioned manifests and receipts.

### Import verified files into a new entry

For ordinary maintenance, verify the [complete selected contents](#back-up-complete-files-and-directories) before the initial [`bind`](#bind-or-deliberately-change-a-source). Select exact files or directories with repeated `--file`, or review the actual default selections. Where selected, `.agents/config.json` in the backup includes the resulting binding. Verify the bound result and retain the exact imported files and manifest for [publication](#publish-an-exact-verified-scope) with `--path`. Use `apply` without a difference token to record agreement once the files match. A binding failure can leave saved source work. Report it separately from the business project's result.

## Back up verified local changes

With the [repository access prerequisites](#bind-or-deliberately-change-a-source) met, refresh the configuration repository and check which side changed. Stop the backup if refresh fails. Full setup follows its own source-authoring route. Keep provenance for accepted source work already produced in the operation.

```text
python "<maintain>" update --target "<target-root>"
python "<maintain>" reconcile --target "<target-root>"
```

`reconcile` compares both sides to the last agreement. Compare the entry's `source_fingerprint` and `scope` with any reliable earlier observation. When `local_updates_only` is true and no earlier evidence contradicts it, save the verified files already authorized by the task. If the entry changed upstream or the direction is unknown, review both sides and obtain the [synchronization choice](#apply-the-users-whole-synchronization-choice).

Use the current inspection `fingerprint` to guard the exact selected differing files. Check that the [complete contents](#back-up-complete-files-and-directories) still match what was verified. Check staged, unstaged, untracked and outgoing changes on affected backup paths and the manifest. Defer any save that would overwrite pending work outside the task. Accept any actual scope change, including deletions that remove manifest declarations. Adoption can rewrite the manifest without changing its selection. A path outside the inspection needs an accepted expansion, with stable, reviewed local contents and source destination before exact-path adoption without the guard.

```text
python "<maintain>" adopt --target "<target-root>" --accept-existing "<inspect-fingerprint>" --file ".agents/rules/project.md" > "<adoption-result.json>"
python "<maintain>" apply --target "<target-root>"
```

The first command saves selected files to the backup. The second records agreement without accepting any differences. Keep the adoption result and use [exact-scope publication](#publish-an-exact-verified-scope). If the requested files and scope are already backed up, skip adoption and record agreement when needed. If differences remain, keep both sides and resolve them before publishing.

When a caller is authorized to save **all** proven local-only changes, it can use the reviewed plan route. Review its full file selection before applying the plan. An explicit `adopt --all` refreshes the entire declared scope and removes missing file declarations. Use it only when that whole refresh is authorized.

```text
python "<maintain>" reconcile --target "<target-root>" --adopt-local
python "<maintain>" reconcile --target "<target-root>" --adopt-local --accept-plan "<plan-fingerprint>"
```

## Restore explicitly or synchronize at startup

For explicit restoration, reuse the binding only with a matching successful local receipt. Otherwise obtain the chosen repository, branch and existing entry, and verify it before [binding](#bind-or-deliberately-change-a-source). Meet the [repository access prerequisites](#bind-or-deliberately-change-a-source), run `update`, then inspect concrete additions, overwrites and deletions before an accepted application. Check the restored files, [Git treatment](#keep-personal-configuration-out-of-business-git) and local prerequisites. Restore-only work copies the accepted bytes and ends there. Rendering, full setup and saving local changes are separate operations.

Startup synchronization is off by default. An enabled checkout with a valid binding and matching receipt can refresh and run read-only `reconcile`. Apply `source-updated` without a fresh choice only when it proves repository-only changes, using the exact inspection fingerprint. A legacy receipt without the earlier manifest cannot prove that direction. For `in-sync`, apply when agreement needs recording. For local-only differences, ask whether to save or defer. Report invalid enabled state, and defer application when refresh fails or a choice is pending.

### Apply the user's whole-synchronization choice

Show the exact differences, including binary differences. Offer to save reviewed local changes, apply the reviewed backup, or leave files and receipt in place. A routine local save uses the [verified local change route](#back-up-verified-local-changes). Applying a differing backup uses the exact inspection fingerprint. If the reviewed effects change, show the new differences and obtain a fresh choice. A pending choice holds the affected synchronization while independent work can continue.

```text
python "<maintain>" apply --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

### Record verified agreement and the startup preference

`apply` records the local receipt in `.agents/project-config-sync.json` once source and target agree. If Git exclusions fail after application, check the actual files, receipt and exclusions separately. To deliberately set the checkout's startup preference, use `--auto-sync on` or `--auto-sync off`, with the difference token when a differing application was accepted.

## Render local configuration only when required

Use the narrow command when only the generated `Project rules` section needs updating. `ruleEntry` selects `AGENTS.md` or `AGENTS.local.md`. Local rendering uses existing inputs and ownership checks. It does not run full setup.

```text
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>"
```

Both commands, including read-only `--check`, require a readable, matching backup in repository mode. If a local edit makes required generation or verification unavailable, use a supported local check only when sufficient. Otherwise keep the edits and defer backup. If rendering changes selected files, verify those outputs before saving them. Report unmet setup or migration prerequisites separately.

## Keep personal configuration out of business Git

Personal modes use the target's scoped Git `info/exclude`. Switching to project shared retires only its managed block. Preserve shared ignore files and existing tracked configuration. Check relevant paths even when synchronization is deferred. Report any tracked files or missing exclusions. Binding, application and rendering manage exclusions. An inspection or `--check` does not repair them.

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

## Maintain OpenWiki with the project binding

Use the bound project as `--target`. The commands locate its Git root and honor an independent binding there. A nested project's repository backup uses `projects/<entry>/wiki/` and a separate Git-root receipt. Establish authority for Git-root writes before preparation. Resume active Wiki work before preparing or saving its backup.

Refresh repository mode before preparing a new run. Resolve `needs-choice` as for configuration, then pass the exact token for an accepted differing restoration. In repository mode, verify the finished Wiki and review the save plan for `openwiki/`, `.openwikiignore` and any explicitly selected Git-root `AGENTS.md` or `CLAUDE.md`. Save with the same selections and the reviewed plan fingerprint. If interrupted, verify saved contents against that plan and use `wiki prepare` to record agreement when needed. Publish only the current operation's verified scope.

```text
python "<maintain>" wiki prepare --target "<target-root>"
python "<maintain>" wiki prepare --target "<target-root>" --accept-existing "<inspect-fingerprint>"
python "<maintain>" wiki save --target "<target-root>" > "<wiki-plan.json>"
python "<maintain>" wiki save --target "<target-root>" --accept-plan "<plan-fingerprint>"
python "<maintain>" wiki publish --target "<target-root>" --plan "<wiki-plan.json>" --message "Back up OpenWiki"
```

## Publish an exact verified scope

An authorized repository save includes its scoped commit and normal push unless the user requests a local result. When required checks, agreement and [repository access](#bind-or-deliberately-change-a-source) are established, pass the accepted adoption JSON with `--plan` or name each accepted repository-relative path with `--path`. Include owned imports, manifest changes and deletions when applicable. A save may have nothing new to publish. Keep unrelated Git work out of the request. The command verifies plan digests, exact scope, convergence and the remote result. Revalidate any hook-altered content before retrying.

```text
python "<maintain>" publish --target "<target-root>" --plan "<adoption-result.json>" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

If publication fails, inspect the reported state and preserve any retained commit. Retry that verified commit once source, target and remote evidence support it, retaining `--plan` when there is accepted plan evidence. Use `wiki publish` for Wiki scope. Report whether local work, backup, receipt and publication actually completed.
