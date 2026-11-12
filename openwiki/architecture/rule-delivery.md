---
type: architecture
title: Rule delivery across harnesses
description: How the plugin loads complete core Rules, advertises indexed Rules, and restores context after compaction.
tags: [rules, hooks, harnesses, compaction]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-f87a842422c19220bd65fd16
    resource: repo://runtime/rules/contract.py
  - id: openwiki-source-e9abd5798bc2da26acf7d34e
    resource: repo://runtime/rules/dispatch.py
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Rule delivery across harnesses

SmartKit's Rule registry identifies each policy by ID, Markdown filename, and discovery description. The loader checks source existence, unique IDs, valid delivery values, and that inline Instruction Governance comes first. The dispatcher renders core Rules as individually wrapped Markdown bodies by default. It gives indexed Rules as descriptions with absolute source paths from the active plugin root. The same output declares installed resource locations for workflows such as local artifact hosting. [Registry](../../rules/registry.json) · [Registry validation](../../runtime/rules/contract.py) · [Context rendering](../../runtime/rules/dispatch.py)

The ordering constraint ensures that the precedence policy is delivered. The policy resolves conflicts by authority source, artifact type within the same source, then specificity. The delivery mechanism and the instruction hierarchy are independent. Project-specific Rule registration belongs to project configuration, and language or domain Rule Skills use Skill discovery. [Instruction Governance](../../rules/core-instruction-governance.md) · [Project setup](../configuration/project-setup.md)

## Session events and recovery

| Harness | Delivery path |
| --- | --- |
| Codex and Qoder | Native SessionStart hooks deliver the Rule context as `hookSpecificOutput.additionalContext`. Codex also wires its compaction matcher through SessionStart. |
| Cursor | SessionStart returns `additional_context`. After compaction, the first applicable pre-tool or completed-stop hook carries the restored context in the host response. |
| Copilot | Session start returns `additionalContext`. After compaction, the next prompt can be prefixed with the restored context. A pre-tool or stop hook can also deliver it. |

For Cursor and Copilot, a compaction event increments a generation in session-scoped state. Restoration is pending while the recorded restored generation is behind. The dispatcher assembles the context and any event-specific recovery message before it advances the restored generation. Subsequent ordinary events return an empty response until another compaction. Tests cover one-time restoration, pending state after a failed restoration, and the completed-stop guard in Cursor. [Dispatch](../../runtime/rules/dispatch.py) · [Rule tests](../../tests/test_plugin_rules.py)
