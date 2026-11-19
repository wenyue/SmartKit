---
name: maintain-project-config
description: Maintain project agent configuration shared with the project, kept only on this machine, or backed up in a separate personal configuration repository.
disable-model-invocation: true
---

# Maintain Project Config

Edit and verify the configuration in the business project. In repository mode, back up the verified files and push them to the selected configuration repository.

Resolve `<target-root>` to the business project and `<maintain>` to `skills/maintain-project-config/scripts/maintain.py` in the loaded plugin. Use the linked parts of [Project Configuration Maintenance](references/maintenance.md) for the operation at hand.

1. **Work locally.** If initializing over existing configuration, obtain the [replacement decision](references/maintenance.md#choose-the-maintenance-mode) before editing. Use the project's own evidence and checks. For a Rule or Skill, use the actual project files as the Candidate for [Write Rules and Skills](../write-rules-and-skills/SKILL.md). Run [local rendering](references/maintenance.md#render-local-configuration-only-when-required) when needed. If a backup or conflict blocks synchronization, continue any independent local work already in scope.
2. **Save in the selected mode.** Reuse the project's binding or present all three [maintenance modes](references/maintenance.md#choose-the-maintenance-mode) before binding. In either local mode, finish in the project. In repository mode, [save and push the verified changes](references/maintenance.md#back-up-verified-local-changes) or [import a new entry](references/maintenance.md#import-verified-files-into-a-new-entry). If a required check or the save fails, keep the local work and report where it stopped.

Check [Git treatment](references/maintenance.md#keep-personal-configuration-out-of-business-git) even when a save is deferred. Report the changed files, validation, outstanding prerequisites and actual backup or push result.

For an inspection-only request, stop after [inspection](references/maintenance.md#choose-the-maintenance-mode). For explicit restoration, use the [restore route](references/maintenance.md#restore-explicitly-or-synchronize-at-startup).
