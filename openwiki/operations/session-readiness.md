---
type: operations
title: Session readiness and diagnosis
description: How startup combines daily tool checks with per-session project observations, and where SmartKit gets evidence for diagnosing an agent session.
tags: [readiness, hooks, codegraph, mcp, diagnostics]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-bc8d4997fab16b9f2486e768
    resource: repo://runtime/recommended-tools/check_recommended_tools.py
  - id: openwiki-source-1a7111951f3b3bddf697af10
    resource: repo://runtime/recommended-tools/codegraph_runtime.py
  - id: openwiki-source-8eb1b8dc3b25c353b7eaa069
    resource: repo://skills/diagnose-agent-session/SKILL.md
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Session readiness and diagnosis

SmartKit runs independent hook features for Rule delivery, local web startup, and tool readiness. The readiness dispatcher uses per-harness policy and a daily gate keyed by the resolved project and harness. Behind that gate it checks tool and configuration requirements, plugin and project MCP prerequisites, setup migrations, plugin version, and login startup. The implementation runs those independent checks concurrently and validates any required prompt resources before recording notification. It also reconciles duplicate user-level MCP names owned by the plugin. [Codex hooks](../../hooks/codex.json) · [Readiness dispatcher](../../runtime/recommended-tools/check_recommended_tools.py) · [Readiness tests](../../tests/test_recommended_tools.py)

## Project observations on each session

Initialized projects receive a fresh CodeGraph check independently of the daily gate. The check verifies the CLI, the worktree's local index, and live MCP health through a bounded probe. A responding daemon can still report incomplete or disabled synchronization. The startup check reports the condition. Full setup owns preparation that installs or starts the required runtime. [CodeGraph runtime](../../runtime/recommended-tools/codegraph_runtime.py) · [Project setup](../configuration/project-setup.md)

The configuration startup check reads an existing local receipt and matching repository binding. It emits the synchronization prompt only when automatic synchronization is enabled. The prompt hands off to the maintenance workflow, which owns updates, inspection, and application of accepted differences. The startup check itself performs no fetch or restoration. [Configuration startup tests](../../tests/test_config_backup_hook.py) · [Storage and synchronization](../configuration/storage-and-sync.md)

## Evidence for an individual agent session

The [diagnosis Skill](../../skills/diagnose-agent-session/SKILL.md) uses `timing.py diagnose` for an exact client and session identity. Codex turn and behavior evidence comes from an immutable copy of its local log. Whole-session usage, model and cost evidence comes from supported Tokscale rows. Cursor and Copilot CLI have the whole-session provider path only. Codex token totals can remain available when the provider fails, with model or cost coverage reported separately. Each observation carries its own time interval and source. The tests cover exact provider attribution, schema errors, and partial evidence. [Diagnosis implementation](../../skills/diagnose-agent-session/scripts/timing.py) · [Diagnosis tests](../../tests/test_diagnose_agent_session.py)
