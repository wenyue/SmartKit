---
type: workflow
title: Project setup, generation, and migration
description: How SmartKit assesses a target, freezes a setup session, reconciles generated and native configuration, and completes the initial OpenWiki handoff.
tags: [setup, migrations, blueprints, ownership, configuration]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:39:35.516Z
sources:
  - id: openwiki-source-c5d0dd215161bb72f6e7f773
    resource: repo://skills/setup-project-agents/references/ownership.md
  - id: openwiki-source-e98d6ec98e52e2c023fbd305
    resource: repo://skills/setup-project-agents/scripts/setup_project_agents.py
  - id: openwiki-source-b44cfa643981f91f92496491
    resource: repo://skills/setup-project-agents/scripts/workflow.py
  - id: openwiki-source-246b33be93974d8f29bf072e
    resource: repo://skills/setup-project-agents/SKILL.md
generated: { by: "smartkit", at: "2026-11-12T04:39:35.516Z" }
---

# Project setup, generation, and migration

The [Setup Project Agents Skill](../../skills/setup-project-agents/SKILL.md) selects among full initialization or migration, backup restoration, and limited local synchronization. The read-only workflow inspection checks whether the configuration session can be skipped and surfaces prerequisites for sessions that are needed. A project may have usable managed files in a fresh checkout. A restored snapshot or copied version can describe earlier work and still leave this machine's prerequisites unverified. [Storage and synchronization](storage-and-sync.md)

## Inputs and rendered ownership

The [asset catalog](../../setup-assets/catalog/assets.json) declares shipped assets and blueprints. The [configuration schema](../../setup-assets/catalog/project-config.schema.json) governs project inputs such as external Skill sources, custom Agents, MCP declarations, and structured host settings. When configuration work is required, Setup assesses existing custom Agents, current project evidence, and all declared blueprints. `.agents/smartkit.lock.json` tracks managed file and structured-field ownership and records the exact output paths for each blueprint. Project-owned generated sources can be revised between sessions. A temporary registration seal guards the accepted writer outputs while a session is in progress. [Setup ownership](../../skills/setup-project-agents/references/ownership.md)

The Rule entry selected by `ruleEntry` has one managed `Project rules` section. Discovery includes direct Rule files in `.agents/rules/`. Conditional policy uses discoverable `rule-<domain>` Skills. The renderer preserves the surrounding entry text and unowned files and fields. Retiring a blueprint removes its recorded outputs within the ownership contract. Unrecorded neighboring files remain project inputs. [Rule entry renderer](../../skills/maintain-project-config/scripts/project_config/project_rules.py)

## Configuration session and full Setup completion

The public workflow coordinates CodeGraph preparation, source selection and pinning, a frozen setup request, writer inputs, output registration, and finish. The pinned implementation builds a plan against captured target evidence and applies it with postcondition checks. The transaction and workflow tests exercise rollback, target drift, failed registration, and preservation of unrelated edits. [Session protocol](../../skills/setup-project-agents/references/session-protocol.md) · [Transaction tests](../../tests/test_setup_transaction.py)

At finish, the public workflow rechecks CodeGraph, runs pinned configuration finish, reconciles Git exclusions, and verifies the config bytes returned by the pinned stage. It prepares the version update against those bytes, removes the private session, then applies the `setupVersion` write. A failure at that last write can leave configuration applied with the old version, which the workflow reports as incomplete. [Workflow implementation](../../skills/setup-project-agents/scripts/workflow.py) · [Workflow tests](../../tests/test_setup_workflow.py)

The recorded `setupVersion` identifies the successful local configuration finish. After the configuration result and any required publication, full Setup also verifies a completed repository OpenWiki or completes initial generation and the applicable maintenance handoff. When the migration gate skips configuration changes, Setup can continue the pending Wiki work without opening another configuration session. [Setup handoff](../../skills/setup-project-agents/SKILL.md#9-complete-openwiki-and-hand-off) · [OpenWiki integration](../integrations/openwiki.md)
