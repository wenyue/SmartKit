---
name: maintain-project-config
description: Maintain project agent configuration shared with the project, kept only on this machine, or synchronized through a separate personal configuration repository.
disable-model-invocation: true
---

# Maintain Project Config

Maintain the project's agent configuration using the business project's evidence. Edit its selected source, verify what the target receives, and complete the operation under the shared publication contract. This Skill owns configuration binding, inspection, application, explicit adoption of target edits, local synchronization and source publication.

Resolve this directory as `<skill-root>`, its containing plugin as `<plugin-root>`, and the business project as `<target-root>`. Read [Project Configuration Maintenance](references/maintenance.md) before using the commands below. It supplies the source layout, supported entry points, authentication, difference protection and publication recovery. Use `<skill-root>/scripts/maintain.py` as `<maintain>`; resolve resources from the loaded plugin, not from the business project's working directory. Other plugin workflows may consume this reference and command interface without invoking this user-only Skill.

## 1. Establish the requested result

| Request | Work and completion |
| --- | --- |
| Inspect configuration or explain differences | Read available binding, source and target state; report findings and unavailable evidence. Inspection performs no update, edit, apply, commit or push. |
| Maintain and synchronize project configuration | Make accepted source changes, validate and apply them, and normally publish the exact source scope in repository mode unless the user requests a local result. |
| Adopt specified target edits into the source | Compare the last application, current source and target; adopt only accepted files or portable fields, then validate, apply and publish under the same maintenance contract. |

The shared reference owns the operation's publication default and explicit local-result exception. A request limited to inspection stays read-only. If the requested configuration change is unclear, inspect first and resolve that change before editing.

```text
python "<maintain>" inspect --target "<target-root>"
```

Identify the maintenance mode, source entry, current application differences and unfinished work from the result. Return inspection-only findings here. For an unbound project, present the reference's three user-facing modes as one choice: project shared, this machine only, or a separate configuration repository. Resolve the intended mode and any required source before dependent work; use the reference's binding route only after that choice is explicit. Do not infer repository identity from an unrelated remote or silently establish a binding.

## 2. Establish a usable source without losing existing work

Read complete relevant source content, current target configuration and ownership evidence. Preserve staged, unstaged, untracked and unpublished work in both repositories. Record which source edits already exist so the eventual commit can be traced to this request. A shared private repository can hold several projects; the binding selects one entry, and unrelated entry changes remain outside the task.

In repository mode, update the persistent checkout before editing:

```text
python "<maintain>" update --target "<target-root>"
```

Continue only when repository identity, branch state and required access are verified. Follow the shared reference's preservation and recovery route for a dirty checkout, divergence, unfinished operation or failed access. A failed update is not evidence that the working copy is current. Retain unique local work while resolving the cause.

In both project-shared (`local`) and machine-only (`local-only`) modes, the business project's canonical inputs remain the authoring source, without opening a configuration repository. Apply the same scope, ownership and validation discipline there; neither mode has a configuration-repository commit or push. The reference owns their different Git treatment and the safeguards for a deliberate mode or source switch.

## 3. Author the accepted change or adopt selected target edits

Use business-project evidence to decide what configuration should say. The configuration repository's own layout and conventions are storage facts, not evidence of the target project's architecture or required checks. Keep complete instructions and necessary supporting resources together in the declared source scope.

For authored changes, edit the source paths and portable declarations selected by inspection. When writing or revising a Rule or Skill, use the supported [Write Rules and Skills](../write-rules-and-skills/SKILL.md) workflow with the source files as its Candidate and the business project as qualified evidence. Preserve its author and review responsibilities. Resolve dependencies through their owners; public authorship does not grant access or effects outside this maintenance request.

For explicit adoption in repository mode, inspect the differences among the last applied content, current source and current target before selecting files or fields. If both source and target changed the same content, explain the overlap and obtain the intended resolution rather than choosing one silently. Use the accepted selections, for example:

```text
python "<maintain>" adopt --target "<target-root>" --file ".agents/rules/example.md" --field settings
```

Read `adopt --help` for the supported selectors. Replace the example with the actual accepted scope; preserve every unselected difference. Adopting existing text still requires the applicable content assessment and validation before it can be published.

Continue when the complete proposed source change matches the request, its ownership is established, and any required public writer handoff is accepted. Record exact repository-relative changed files for later publication, including necessary manifest or portable-config changes.

## 4. Validate, apply and synchronize the target

Run the source's applicable checks and inspect the proposed target differences. In repository mode, apply accepted source configuration through the shared route:

```text
python "<maintain>" inspect --target "<target-root>"
python "<maintain>" apply --target "<target-root>"
```

Preserve target edits that have not been adopted. Initial-collision acceptance is only for an accepted first application of the exact inspected state; it is not a way to suppress later target drift. Keep generated sections and native adapters under the synchronization commands' ownership checks, and preserve delivered assets and local state.

Synchronize native outputs through the maintenance command after applying repository sources, or after editing canonical inputs in either local mode:

```text
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

Use the reference's narrower `sync-project-rules` route when only the generated `Project rules` section needs synchronization. Verify the selected mode's Git treatment, including any reported paths that remain tracked. Configuration convergence establishes the rendered result; also complete any semantic or project checks required for the actual change.

If a command reports that full setup or migration is required, preserve saved source edits and target progress, report the unmet prerequisite and leave maintenance incomplete. Full setup requires the user to explicitly invoke its owning Skill; this workflow neither invokes it nor delegates it through a callback. Resume dependent maintenance only after its prerequisite is satisfied and current source and target evidence has been rechecked.

Continue only when source validation, target application and all required checks succeed. If application fails after source changes were saved, preserve them and report target recovery separately; do not claim a cross-repository rollback.

## 5. Publish the verified source scope

In repository mode, follow the shared reference's publication decision after the required local checks succeed. An explicit local-result instruction defers publication. When the operation has neither accepted pending source changes nor a retained verified commit of its own, finish without publication. For accepted pending source changes, use the publish route with only the operation's exact accepted source files:

```text
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.agents/rules/example.md" --message "Update project configuration"
```

Repeat `--path` for the complete accepted scope, including accepted initial imports and retained work whose provenance belongs to this operation. Follow the shared reference's scope protection and commit-hook recovery; preserve unrelated index entries and working changes.

For a retained verified commit, including after a failed or uncertain push, inspect actual local and remote state before retrying through `publish --commit`. Preserve the applied target and local commit when the remote advances or diverges. The shared reference defines the protected retry boundary; ordinary maintenance grants no force push or destructive history repair.

Repository-mode maintenance completes after required target work succeeds and the shared reference's publication outcome is established: verified remote publication, an explicitly requested local result, or no publication needed for this operation. Both local modes complete after their source, target and applicable Git-exclusion checks succeed, with no remote publication step. Neither ordinary maintenance nor a push advances `setupVersion`; only a completed local full setup does.

## Report the actual result

Report the user-facing maintenance mode and source, accepted changed and preserved paths, validation, application and local synchronization results, Git-exclusion status and any configuration paths that remain tracked, and the exact source commit and verified remote result when applicable. Identify an explicitly requested local result or the absence of owned source changes when publication is unnecessary. For incomplete work, distinguish saved source edits, a retained local commit, target application, cleanup or rollback status, unmet prerequisites and remote synchronization. Successful target work followed by a failed push is useful local progress and incomplete repository maintenance.
