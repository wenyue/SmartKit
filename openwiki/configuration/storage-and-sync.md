---
type: configuration
title: Project configuration storage and synchronization
description: How SmartKit binds project storage, restores complete snapshots, detects conflicts, and publishes an explicitly adopted scope.
tags: [configuration, backup, synchronization, git, maintenance]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-9b7c101203d315daa391eb6b
    resource: repo://runtime/project_state/config_backup.py
  - id: openwiki-source-1650105e4952360eabb26d78
    resource: repo://skills/maintain-project-config/scripts/project_config/project_configuration.py
  - id: openwiki-source-d66b47e6968c43da117b24ff
    resource: repo://skills/maintain-project-config/scripts/project_config/repository.py
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Project configuration storage and synchronization

The binding in `.agents/config.json` identifies which copies are canonical. The [maintenance reference](../../skills/maintain-project-config/references/maintenance.md) owns the commands and the lifecycle.

| Mode | Canonical files and Git behavior |
| --- | --- |
| `local` | Files live in the business project and can be shared through its Git repository. |
| `local-only` | Files live in the business project. SmartKit maintains local Git exclusions for personal configuration. |
| `repository` | Selected complete files live in a persistent checkout of a private GitHub repository, in `projects/<entry>/`. The target copies have local Git exclusions. |

The exclusion manager uses the target's Git `info/exclude` and reports already tracked paths. Local exclusions affect only untracked files. The maintenance engine is also the owner of deliberate local rendering and Rule-index synchronization. Those routes use project declaration and ownership records. Backup restores the selected bytes and records agreement. [Maintenance CLI](../../skills/maintain-project-config/scripts/project_config/project_configuration_cli.py) · [Project setup](project-setup.md)

## Snapshot and application

An entry contains `manifest.json` and `files/`. The manifest lists exact files and recursive directory roots. Runtime validation rejects overlapping or case-colliding paths, symlinks in a selected tree, the target-local receipt, and an active OpenWiki queue. The snapshot fingerprint includes both scope and each selected file's hash. [Backup reader](../../runtime/project_state/config_backup.py)

`update` fetches the bound branch and allows a supported fast-forward. `inspect` reports local source and target differences without fetching or applying. Any differing restoration requires the inspection fingerprint covering both sides. `apply` checks it, plans additions, replacements and applicable deletions, verifies the precondition again, and checks source-target agreement after the transaction. The target receipt binds the source fingerprint, applied paths, and automatic startup preference. Startup opt-in allows update and inspection of an established binding, with difference acceptance still required for application. [Configuration engine](../../skills/maintain-project-config/scripts/project_config/project_configuration.py) · [Startup tests](../../tests/test_config_backup_hook.py)

## Saving target edits

Adoption explicitly selects complete target paths to copy back. `--all` refreshes existing manifest scope. New paths need an explicit selection. The publication route requires a verified scope receipt for the requested commit, checks that it is the sole outgoing commit if a push is needed, and verifies reachability on the remote after pushing. A rejected or uncertain push leaves the local commit available for verification and retry. [Repository operations](../../skills/maintain-project-config/scripts/project_config/repository.py) · [Repository tests](../../tests/test_project_config_repository.py)
