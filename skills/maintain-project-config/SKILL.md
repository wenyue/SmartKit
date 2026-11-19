---
name: maintain-project-config
description: Maintain project agent configuration shared with the project, kept only on this machine, or backed up in a separate personal configuration repository.
disable-model-invocation: true
---

# Maintain Project Config

Maintain Agent configuration in the business project. Verify it there before saving selected complete files to a configuration repository.

Resolve this directory from the loaded plugin as `<skill-root>`, the business project as `<target-root>`, and `<skill-root>/scripts/maintain.py` as `<maintain>`. Use the linked sections of [Project Configuration Maintenance](references/maintenance.md) for the operation you select. Report an unavailable command or required resource and leave dependent work pending.

## 1. Establish the operation

```text
python "<maintain>" inspect --target "<target-root>"
```

This inspection reads the maintenance mode, binding, available scope and differences without fetching or writing. Preserve staged, unstaged, untracked and unpublished work in both checkouts. An inspection-only request ends with the findings and any unavailable evidence.

For explicit restoration, follow the [source selection and restoration route](references/maintenance.md#restore-explicitly-or-synchronize-at-startup) and end with its result. Restoring a backup and saving local edits require separate authority.

For an unbound project, present all three [maintenance modes](references/maintenance.md#choose-the-maintenance-mode) and obtain the user's choice before [binding](references/maintenance.md#bind-or-deliberately-change-a-source). Reuse a valid binding for later maintenance. If initializing over existing configuration, compare the actual contents, propose the concrete replacements and obtain the user's decision. An initial repository import belongs after local verification.

## 2. Edit and verify the project

Use the business project's evidence to choose what to change and how to verify it. Work on its actual configuration files. For a Rule or Skill, use those files as the Candidate for [Write Rules and Skills](../write-rules-and-skills/SKILL.md), with qualified project evidence.

When the backup is inaccessible or a synchronization choice is pending, continue authorized local work in known scope that can be done independently. Complete the applicable checks on the actual result, including any [required rendering](references/maintenance.md#render-local-configuration-only-when-required). If a required check or render is blocked, retain the local work and report the missing verification before any backup.

Check [Git treatment](references/maintenance.md#keep-personal-configuration-out-of-business-git) for the local result, even when the backup is deferred. Report tracked configuration and any outstanding exclusions, setup or migration prerequisites. In either local mode, finish with the verified local result.

## 3. Back up the verified selection

For an authorized repository save, follow the [initial import route](references/maintenance.md#import-verified-files-into-a-new-entry) for a new entry or [back up verified changes](references/maintenance.md#back-up-verified-local-changes) for an existing binding, including one just connected to an existing entry. Once agreement is recorded, verify Git treatment for the resulting scope and follow [exact-scope publication](references/maintenance.md#publish-an-exact-verified-scope).

## Report the result

Report the mode, source, accepted and preserved paths, checks performed and configuration files already tracked by business Git. Include the exact commit and verified publication outcome when applicable. If a later step is blocked, preserve completed work and distinguish the local result, saved backup, agreement receipt and any retained commit or pending publication.
