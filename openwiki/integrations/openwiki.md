---
type: integration
title: OpenWiki retrieval and generation
description: How SmartKit packages OpenWiki, retrieves sections without generation, and completes a durable page queue with source-backed Claims.
tags: [openwiki, mcp, retrieval, claims, maintenance]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:39:35.516Z
sources:
  - id: openwiki-source-d28827b9695726ae0a7d5a96
    resource: repo://mcp/registry.json
  - id: openwiki-source-9b7c101203d315daa391eb6b
    resource: repo://runtime/project_state/config_backup.py
  - id: openwiki-source-f27335ea429d443b8de638e2
    resource: repo://skills/openwiki/SKILL.md
  - id: openwiki-source-246b33be93974d8f29bf072e
    resource: repo://skills/setup-project-agents/SKILL.md
  - id: openwiki-source-13d428f8e2b1c17d150cb36b
    resource: repo://tests/test_sync_mcp_adapters.py
generated: { by: "smartkit", at: "2026-11-12T04:39:35.516Z" }
---

# OpenWiki retrieval and generation

SmartKit delivers OpenWiki through two surfaces. The Skill is a patched upstream snapshot managed by the [Skill registry](../../skills/registry.json). The [MCP registry](../../mcp/registry.json) pins the OpenWiki CLI and uses `npx` to launch its stdio server with `--host smartkit` for all four harnesses. Readiness checks Node.js and `npx`. The [MCP adapter tests](../../tests/test_sync_mcp_adapters.py) cover the generated invocation.

## Retrieve the evidence needed for a question

Search takes the absolute Git root and returns section references. Optional source paths boost related results. A linked workspace can search several wikis and returns a wiki identity with each result. Ambiguous memberships require an active workspace or a selected workspace ID. The read operation takes the wiki, page, and exact section anchors. Optional provenance identifies recorded evidence versions. Important details are verified against source as needed. Search and read do not start generation or call a model. [OpenWiki Skill](../../skills/openwiki/SKILL.md)

## Setup handoff

Full Setup checks for a completed Wiki at the Git top-level after its configuration work. It checks the actual pages and completion evidence, including the previous update recorded by an active refresh, to decide whether the Wiki can be reused. If the first generation is missing or incomplete, Setup delegates it to the bundled OpenWiki Skill and uses the Git root's maintenance binding. The Setup-owned recovery note in the worktree's Git directory records the scope and progress of first generation and its maintenance handoff. An interrupted first generation still needs reconciliation after its queue closes. [Setup handoff](../../skills/setup-project-agents/SKILL.md#9-complete-openwiki-and-hand-off) · [Project setup](../configuration/project-setup.md)

## Durable generation

SmartKit uses `openwiki_begin` in English update mode for new runs. Update creates a missing Wiki without a scheduled GitHub workflow. An active queue belongs to its worktree and is resumed with the recorded mode and language. The agent submits the page plan, researches and writes one assigned page at a time, and submits sparse Claim decisions. OpenWiki retains issue-free Claims automatically, assigns IDs to new Claims, and persists the queue, evidence versions, sidecars, and indexes. Stale and unresolved Claims require explicit rechecking. Source drift can invalidate the plan and require replanning. The run completes after the queue drains and `openwiki_finish` succeeds. [Generation and Claims contract](../../skills/openwiki/SKILL.md)

The project's maintenance binding also governs the complete Wiki bundle. Project-shared mode leaves it available to business Git. Machine-only mode excludes it locally. Repository mode adopts the completed bundle into the accepted snapshot scope. An active queue is rejected by the backup reader, and the configuration tests exercise complete bundle restoration and explicit adoption into an existing manifest. [Storage and synchronization](../configuration/storage-and-sync.md) · [Backup reader](../../runtime/project_state/config_backup.py) · [Backup integration tests](../../tests/test_project_configuration.py)
