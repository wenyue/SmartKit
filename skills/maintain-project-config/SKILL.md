---
name: maintain-project-config
description: Maintain project Agent configuration. Use to inspect or change its maintenance binding, edit and verify local configuration, save or restore a backup, run enabled startup synchronization, or handle configuration work requested by Setup or OpenWiki.
---

# Maintain Project Config

Maintain the business project's Agent configuration within the scope granted by the user or calling workflow. An inspection ends with findings. A verified edit can end in the project or continue to an authorized backup. A restoration ends with the accepted files in place. Full Setup chooses the configuration operations and their order, including its own source-authoring route.

Resolve `<maintain>` to `skills/maintain-project-config/scripts/maintain.py` in the loaded plugin and `<target-root>` to the business project. Use `python "<maintain>" --help` for command options and the same plugin's `setup-assets/catalog/project-config.schema.json` for declarations. Hold exclusive access to source and target during writes. Report a missing resource and leave dependent work incomplete. Discovery grants no edit, restore, or publication authority.

Start at the requested operation:

- [Inspect or choose a binding](#inspect-or-choose-a-binding) or [edit, render, or check local configuration](#edit-and-verify-in-the-project).
- [Save already verified configuration](#save-verified-configuration) or [publish an accepted scope or retry a verified commit](#publish-or-retry-the-verified-scope).
- [Restore an explicitly chosen backup](#restore-an-explicitly-chosen-backup) or [synchronize on enabled startup](#synchronize-on-enabled-startup).
- [Prepare or save the Git-root OpenWiki](#prepare-and-save-the-git-root-openwiki).

## Inspect or choose a binding

Inspect the project using local, read-only evidence. Inspection does not fetch. Reuse a valid binding. When an unbound project needs a mode choice, present all three modes together in the user's language. Before initializing over existing configuration, obtain the user's decision about replacement.

```text
python "<maintain>" inspect --target "<target-root>"
```

| Mode | Stored value | Where configuration stays |
| --- | --- | --- |
| Project shared | `local` | In the project for sharing through business Git. |
| This machine only | `local-only` | In the project with local Git exclusions. |
| Separate configuration repository | `repository` | In the project with local exclusions, backed up in a personal private GitHub repository. |

Bind the chosen mode. A repository binding identifies one personal private repository, branch, and project entry. Confirm all three. Use Git and `gh` authenticated as the personal owner on the matching GitHub or GitHub Enterprise host. Specify `owner/repository` for github.com or a credential-free HTTPS URL for the selected host. Creating the named repository requires explicit permission for `--create-repository`. The `bind` and `publish` commands check ownership and privacy. A successful `update` verifies checkout and fetch; verify ownership or privacy separately if still uncertain.

```text
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<repository>" --branch "<branch>" --entry "<entry>"
```

Distinguish connecting to an existing entry from importing into a new one *before* running `bind`. For a connection, verify `projects/<entry>/manifest.json` in the state the command will use after refresh. On a fresh clone, check the selected remote branch. With an existing persistent source checkout, verify the entry there, including accepted unpublished work. If the entry is missing or unverified, stop the connection: the same command could import local files. For an intended new import, use the [initial import](#initial-import) procedure below. Use `--replace-binding` only for an accepted switch after resolving outstanding differences, including any Git-root Wiki owned by a nested project. Preserve existing work and entries.

### Complete contents and Git treatment

An entry's `manifest.json` selects target-relative `files` and recursive `directories` stored under `files/`. Review the entire selected contents, including credentials and machine paths. Keep secrets in credential facilities and synchronization receipts outside the backup. Native settings, MCP files, and `.agents/config.json` are copied in full when selected. Neither a lockfile nor the `ruleEntry` setting selects the backup scope. A copied setup marker proves neither setup nor local readiness. Preserve and report unreadable or unsupported state, including versioned manifests and receipts.

Personal modes protect configuration through the project's scoped Git `info/exclude`. A switch to project shared retires only the managed block. Preserve shared ignore files and tracked configuration. Check relevant paths even if synchronization is deferred, and report tracked files or missing exclusions. Binding, application, and rendering manage exclusions. Read-only inspection and `--check` leave them as found.

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

## Edit and verify in the project

If initialization would replace existing configuration, obtain the [user's replacement decision](#inspect-or-choose-a-binding) before editing. Use the project's actual files and evidence. For a Rule or Skill revision, use those files as the Candidate for [Write Rules and Skills](../write-rules-and-skills/SKILL.md). Run applicable checks and render only when required. A conflicting or unavailable backup need not stop independent authorized local work.

Use `sync-project` for established local configuration or `sync-project-rules` for only the generated Project rules section. The `ruleEntry` setting selects `AGENTS.md` or `AGENTS.local.md`. Both use existing inputs and ownership checks. For authorized rendering, use the applicable command below.

```text
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>"
```

Use `--check` for a read-only check of either scope.

```text
python "<maintain>" sync-project --target "<target-root>" --check
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

In repository mode both commands require a readable matching backup, including when run with `--check`. If an edit makes required generation or verification unavailable, use a supported local check only when it suffices. Otherwise retain the edits and defer backup. Verify rendered outputs selected for saving. Report missing setup or migration prerequisites separately.

When the task includes saving, follow [Save verified configuration](#save-verified-configuration) for the applicable finish and report. For an edit or check alone, report the changed files, actual checks, and any unmet prerequisites.

## Save verified configuration

Saving requires the applicable verification. Report changed local files, actual checks and unmet prerequisites, and any backup, receipt, and publication outcomes. If checking, access, refresh, or adoption fails, or the save is deferred, preserve local work and report where it stopped, including stages never reached or still uncertain.

For a direct save or a save after editing, reuse the project's valid binding. For an unbound project, [establish the selected binding](#inspect-or-choose-a-binding), asking the user to choose a mode if none was supplied. In either local mode, check the [applicable Git treatment](#complete-contents-and-git-treatment) and finish in the project.

For a repository backup, keep the persistent source checkout, binding, and evidence together through refresh, save, agreement, and publication. An authorized repository save includes a scoped commit and normal push unless the user requests a local result. Keep provenance for accepted source work already produced in the operation.

### Initial import

For ordinary maintenance, review and verify complete selected files before the first bind that imports them. Choose target-relative files or directories with repeated `--file`, or review the actual defaults. A selected `.agents/config.json` includes the resulting binding in the backup. Verify the bound result. Retain the exact imported paths and manifest for publication with `--path`, then record agreement when the files match. A failed bind can leave work in the source checkout; report that separately from the business project's state.

### Existing entry

Establish the [repository access requirements](#inspect-or-choose-a-binding) for this binding before refreshing or adopting, reusing valid evidence and checking ownership or privacy if uncertain. Reuse current refresh and reconciliation evidence for this binding or run the commands below. Stop the backup if refresh fails. Read-only `reconcile` compares the two sides with their last agreement. Compare the entry's `source_fingerprint` and `scope` with any reliable earlier observation. When `local_updates_only` is true and that earlier evidence does not contradict it, save the verified files already authorized by the task. If the entry changed upstream or direction remains unknown, [review the current differences and obtain a choice](#choose-between-differing-copies) before saving.

```text
python "<maintain>" update --target "<target-root>"
python "<maintain>" reconcile --target "<target-root>"
```

Guard exact selected differing files with the current inspection `fingerprint`. Verify that their complete contents still match the reviewed version. Inspect staged, unstaged, untracked, and outgoing changes affecting the backup paths and manifest. Defer a save that would overwrite pending work outside the task. Obtain acceptance for actual scope changes, including deletions that remove manifest declarations. Adoption may rewrite the manifest without changing its selection. A path outside the inspection requires accepted expansion and a stable, reviewed local file and source destination before exact-path adoption without the guard.

Use `adopt` to save the selected files and retain its result for publication. If the requested files and scope are already backed up, skip adoption.

```text
python "<maintain>" adopt --target "<target-root>" --accept-existing "<inspect-fingerprint>" --file ".agents/rules/project.md" > "<adoption-result.json>"
```

When authorized to adopt **all** proven local-only changes, the caller can instead review and execute the full selection through a fingerprinted plan. An explicit `adopt --all` refreshes the entire declared scope and removes missing file declarations. Use it only with authority for that whole refresh.

```text
python "<maintain>" reconcile --target "<target-root>" --adopt-local
python "<maintain>" reconcile --target "<target-root>" --adopt-local --accept-plan "<plan-fingerprint>"
```

### Record agreement

Once the files match, `apply` without a difference token records agreement in the local `.agents/project-config-sync.json` receipt. It accepts no outstanding differences. If differences remain, preserve both sides and resolve them before publication. A backup write, a matching receipt, and a published commit are separate results.

```text
python "<maintain>" apply --target "<target-root>"
```

### Publish or retry the verified scope

When required checks, agreement, and repository access are established, use the accepted adoption JSON with `--plan` or name each accepted repository-relative path with `--path`. Include owned imports, manifest changes, and deletions. Leave unrelated Git work out of the request. A save can have nothing new to publish. The command checks plan digests, exact scope, convergence, and the remote result.

```text
python "<maintain>" publish --target "<target-root>" --plan "<adoption-result.json>" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

If publication fails, inspect the reported state and preserve any retained commit. Revalidate hook-altered content. Retry the verified commit when source, target, and remote evidence support it; retain `--plan` with `--commit` when there is accepted plan evidence. Use `wiki publish` for Wiki scope. Report the actual local work, checks, backup, receipt, and push results, including any incomplete or unknown effect.

## Restore an explicitly chosen backup

Reuse a binding for explicit restoration only with a matching successful local receipt. Otherwise obtain the chosen repository, branch, and existing entry and verify it before binding. With repository access established, run `update` and inspect the exact additions, overwrites, and deletions. For an accepted differing restoration use the inspection fingerprint with `apply`. Check the restored files, Git treatment, and local prerequisites. Restore-only work ends with the accepted bytes in place. Rendering, full Setup, and saving local changes each require their own operation.

### Choose between differing copies

Show the exact differences, including binary differences. Offer to apply the reviewed backup when restoration is within scope, and offer to save the reviewed local changes only when saving is within scope and the route supports it. Keeping both copies and the receipt in place is always an option. If the effects change, show the new differences and obtain a fresh choice. Pending choices hold affected synchronization while independent authorized work can continue.

For an accepted project save, complete the guarded save and publication path above. For an accepted project restoration, apply the reviewed inspection fingerprint. For Wiki choices, use the [Git-root maintenance route](#prepare-and-save-the-git-root-openwiki).

```text
python "<maintain>" apply --target "<target-root>" --accept-existing "<inspect-fingerprint>"
```

After application, agreement is recorded in the local receipt. If Git exclusions fail, check actual files, receipt, and exclusions separately. To deliberately set this checkout's startup preference, use `--auto-sync on` or `--auto-sync off` with `apply`, supplying the difference token when applying accepted differences.

## Synchronize on enabled startup

Startup synchronization is off by default. For an enabled checkout with a valid binding and matching receipt, run `update` and then read-only `reconcile`. Use the result to select the next action.

| Evidence after refresh | Action |
| --- | --- |
| `in-sync` | Run `apply` without a token to record agreement. |
| `source-updated` with proven repository-only changes | Apply the reviewed differences with the exact inspection fingerprint. A legacy receipt lacking the earlier manifest cannot prove this direction. |
| `needs-choice` with `local_updates_only` | Ask whether to save or defer. Follow an accepted save through exact backup and publication for the reviewed selection. |
| Other `needs-choice` | [Review the differences and obtain a choice](#choose-between-differing-copies). |

Report invalid enabled state. If refresh fails or synchronization is deferred, preserve the files and receipt, report where it stopped, and continue independent authorized work.

## Prepare and save the Git-root OpenWiki

Use the bound project as `--target` and establish authority for writes at its Git root. If the Git root has an independent binding, Wiki commands from a nested target refuse. Preserve the nested project's binding, files, and backup state. Identify the Git-root project as the owner and stop the nested attempt. Maintenance at the root requires authority for that project. Any active Wiki run stays with its current owner and must finish in its worktree before dependent preparation or saving.

In either local mode, `wiki prepare` establishes the applicable Git treatment and completes maintenance. In repository mode, meet the [repository access requirements](#inspect-or-choose-a-binding) and reuse current verified refresh evidence or run `update` before preparing a new run or planning a save. If refresh fails, preserve both copies and report where maintenance stopped.

A project at its Git root uses its ordinary project snapshot. A nested project uses `projects/<entry>/wiki/` and the Git root's separate `.agents/openwiki-config-sync.json` receipt. Before offering a nested save or saving a finished nested Wiki, establish the backup baseline and require a successful `wiki save` preview for the exact selection. For an existing snapshot, verify the receipt for the selected binding and source so the preview can check that the refreshed backup still matches the last agreement. `source_changed_since_sync` can be false when that receipt is absent. For a first save, verify that the nested snapshot is absent in the refreshed source.

If `wiki prepare` reports `needs-choice`, [review the exact differences](#choose-between-differing-copies). Restore-only work offers apply or keep. For other work, offer the choices supported by the observed direction and the operation's authority.

- If the bound project is the Git root, run or reuse ordinary `reconcile` for that snapshot. For `source-updated`, offer apply or keep. For `needs-choice` with `local_updates_only`, offer save or keep. If both sides changed or the direction is unknown, offer the supported writes within scope and the option to keep the current state. Use [ordinary guarded adoption](#existing-entry) for an accepted save.
- For a nested project, offer apply or keep. Add a save option only when the backup baseline and preview checks above pass.

Apply an accepted backup with `wiki prepare --accept-existing` and the reviewed inspection fingerprint. Keeping the current state leaves preparation pending. After a save chosen during preparation, confirm agreement and rerun `wiki prepare`.

To save a finished Wiki in repository mode, verify it and review the save plan for `openwiki/`, `.openwikiignore`, and any explicitly selected Git-root `AGENTS.md` or `CLAUDE.md`. Save with the same selections and the reviewed plan fingerprint. Publish only this operation's verified scope.

```text
python "<maintain>" wiki prepare --target "<target-root>"
python "<maintain>" wiki prepare --target "<target-root>" --accept-existing "<inspect-fingerprint>"
python "<maintain>" wiki save --target "<target-root>" > "<wiki-plan.json>"
python "<maintain>" wiki save --target "<target-root>" --accept-plan "<plan-fingerprint>"
python "<maintain>" wiki publish --target "<target-root>" --plan "<wiki-plan.json>" --message "Back up OpenWiki"
```

Keep the Wiki and backup work when direction is unresolved or the save is refused. After interruption, compare saved contents with the plan and use `wiki prepare` to record agreement when needed. Report the actual Wiki save and publication results.
