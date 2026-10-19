---
name: maintain-project-config
description: Maintain project agent configuration at its selected source, apply accepted changes, and synchronize a bound personal configuration repository.
disable-model-invocation: true
---

# Maintain Project Config

Maintain the project's agent configuration using the business project's evidence. Edit its selected source, verify what the target receives, and finish the publication requested for this operation. This Skill handles inspection, maintenance and synchronization, and explicit adoption of target edits. Setup owns the initial maintenance choice, binding and full upgrades.

Resolve this directory as `<skill-root>`, its containing plugin as `<plugin-root>`, and the business project as `<target-root>`. Read the shared [Project Configuration Maintenance](../../runtime/project_config/maintenance.md) reference before using the commands below. It supplies the source layout, supported entry points, authentication, difference protection and publication recovery. Use `<plugin-root>/skills/setup-project-agents/scripts/workflow.py` as `<workflow>`; resolve resources from the loaded plugin, not from the business project's working directory.

## 1. Establish the requested result

| Request | Work and completion |
| --- | --- |
| Inspect configuration or explain differences | Read available binding, source and target state; report findings and unavailable evidence. Inspection performs no update, edit, apply, commit or push. |
| Maintain and synchronize project configuration | Make accepted source changes, validate and apply them, and normally publish the exact source scope when repository mode is selected. |
| Adopt specified target edits into the source | Compare the last application, current source and target; adopt only accepted files or portable fields, then validate, apply and publish under the same maintenance contract. |

An explicit maintenance-and-sync or adoption request includes the source repository's scoped commit and normal push. That authority belongs to this operation; it does not extend to ordinary project editing, other entries, the business repository or startup behavior. A request limited to inspection stays read-only. If the requested configuration change is unclear, inspect first and resolve that change before editing.

```text
python "<workflow>" project-config inspect --target "<target-root>"
```

Identify the maintenance mode, source entry, current application differences and unfinished work from the result. An unbound project needs setup to choose and record its maintenance source; report that prerequisite and direct the user to `setup-project-agents`. Do not infer repository identity from an unrelated remote or silently establish a binding. Return inspection-only findings here.

## 2. Establish a usable source without losing existing work

Read complete relevant source content, current target configuration and ownership evidence. Preserve staged, unstaged, untracked and unpublished work in both repositories. Record which source edits already exist so the eventual commit can be traced to this request. A shared private repository can hold several projects; the binding selects one entry, and unrelated entry changes remain outside the task.

In repository mode, update the persistent checkout before editing:

```text
python "<workflow>" project-config update --target "<target-root>"
```

Continue only when repository identity, branch state and required access are verified. Follow the shared reference's preservation and recovery route for a dirty checkout, divergence, unfinished operation or failed access. A failed update is not evidence that the working copy is current. Retain unique local work while resolving the cause.

In local mode, the business project's canonical inputs remain the authoring source. Apply the same scope, ownership and validation discipline there; this mode has no configuration-repository commit or push. Changing the maintenance mode is a separate setup choice.

## 3. Author the accepted change or adopt selected target edits

Use business-project evidence to decide what configuration should say. The configuration repository's own layout and conventions are storage facts, not evidence of the target project's architecture or required checks. Keep complete instructions and necessary supporting resources together in the declared source scope.

For authored changes, edit the source paths and portable declarations selected by inspection. When writing or revising a Rule or Skill, use the supported [Write Rules and Skills](../write-rules-and-skills/SKILL.md) workflow with the source files as its Candidate and the business project as qualified evidence. Preserve its author and review responsibilities. Resolve dependencies through their owners; public authorship does not grant access or effects outside this maintenance request.

For explicit adoption, inspect the differences among the last applied content, current source and current target before selecting files or fields. If both source and target changed the same content, explain the overlap and obtain the intended resolution rather than choosing one silently. Use the accepted selections, for example:

```text
python "<workflow>" project-config adopt --target "<target-root>" --file ".agents/rules/example.md" --field settings
```

Read `adopt --help` for the supported selectors. Replace the example with the actual accepted scope; preserve every unselected difference. Adopting existing text still requires the applicable content assessment and validation before it can be published.

Continue when the complete proposed source change matches the request, its ownership is established, and any required public writer handoff is accepted. Record exact repository-relative changed files for later publication, including necessary manifest or portable-config changes.

## 4. Validate and apply through the existing owners

Run the source's applicable checks and inspect the proposed target differences. In repository mode, apply accepted source configuration through the shared route:

```text
python "<workflow>" project-config inspect --target "<target-root>"
python "<workflow>" project-config apply --target "<target-root>"
```

Preserve target edits that have not been adopted. Initial-collision acceptance is only for an accepted first application of the exact inspected state; it is not a way to suppress later target drift. Keep setup's generated `Project rules` section, native adapters, delivered assets and local state with their owners.

When the change requires a full setup or migration, delegate the upgrade to [Setup Project Agents](../setup-project-agents/SKILL.md) as part of this explicitly requested maintenance. Read and execute its complete applicable contract, preserving the binding and editing source first. This is a necessary part of the accepted maintenance operation, not a new invocation at startup or a reason to repeat settled approvals. Missing Matt context and material model or cost choices retain setup's existing prerequisites and decision boundaries.

For changes that fit established local synchronization, use setup's supported local route and honor any full-setup refusal. Local maintenance uses these same target owners after editing its canonical inputs. Configuration convergence establishes the rendered result; also complete any semantic or project checks required for the actual change.

Continue only when source validation, target application and all required checks succeed. If full setup was needed, retain its finish, cleanup and actual `setupVersion` evidence. If application fails after source changes were saved, preserve them and report target recovery separately; do not claim a cross-repository rollback.

## 5. Publish the verified source scope

In repository mode, use the shared reference's publish route after confirming that the applied target agrees with the accepted source. Supply only exact files changed for this request:

```text
python "<workflow>" project-config publish --target "<target-root>" --path "projects/<entry>/files/.agents/rules/example.md" --message "Update project configuration"
```

Repeat `--path` for the complete accepted scope. Preserve unrelated index entries and working changes. If a selected file includes preexisting work whose inclusion is not accepted, resolve that scope before publication. Commit hooks can change source content; revalidate and reapply any such change before publishing, retaining the commit and diagnostic if the command refuses.

For a failed or uncertain push, inspect actual local and remote state before retrying the retained verified commit through `publish --commit`. Preserve the applied target and local commit when the remote advances or diverges. The shared reference defines the protected retry boundary; ordinary maintenance grants no force push or destructive history repair.

Repository-mode maintenance completes only when required target work succeeded and the intended scoped commit is confirmed on the selected remote branch. Local-mode maintenance completes after its source and target checks succeed, with no remote publication step. Neither ordinary maintenance nor a push advances `setupVersion`; only a completed local full setup does.

## Report the actual result

Report the maintenance mode and source, accepted changed and preserved paths, validation and application results, any full setup result and version, and the exact source commit and verified remote result when applicable. For incomplete work, distinguish saved source edits, a retained local commit, target application, cleanup or rollback status, and remote synchronization. A successful local setup followed by a failed push is useful local progress and incomplete repository maintenance.
