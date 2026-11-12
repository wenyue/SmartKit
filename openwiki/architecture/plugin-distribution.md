---
type: architecture
title: Plugin distribution and source ownership
description: How SmartKit turns canonical sources into native harness payloads, maintains vendored Skills, and checks its distribution.
tags: [distribution, manifests, adapters, vendoring, testing]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-e3d4d4361f2dca61da7e1822
    resource: repo://.codex-plugin/plugin.json
  - id: openwiki-source-4f2678f93d3fd3835f9f2909
    resource: repo://.github/workflows/test.yml
  - id: openwiki-source-c5cd32676adc8a6981e3d4d1
    resource: repo://scripts/sync_agent_adapters.py
  - id: openwiki-source-8613012c38743ee731f48312
    resource: repo://scripts/sync_mcp_adapters.py
  - id: openwiki-source-ad5cb756513dd9c61b41f0a0
    resource: repo://scripts/update_external_skills.py
  - id: openwiki-source-72fcb1c478a27b5803dfdf61
    resource: repo://tests/test_plugin_manifests.py
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Plugin distribution and source ownership

SmartKit uses one repository root for its plugin payload. Harness manifests connect each host to the native surfaces it understands. The Codex manifest points to the shared Skills directory, a Codex hook file, and a generated MCP adapter. Cursor, Copilot, and Qoder have their own manifest or marketplace entry and native hook wiring. Python runtime features live behind those hooks and dispatchers, while Skills carry workflow instructions and their own supported helpers. [Codex manifest](../../.codex-plugin/plugin.json) · [Manifest contract tests](../../tests/test_plugin_manifests.py)

## Canonical inputs and delivered files

| Surface | Source and owner |
| --- | --- |
| Plugin Agents | [Agent registry](../../agents/registry.json) and `agents/source/` feed [the Agent synchronizer](../../scripts/sync_agent_adapters.py), which renders and reconciles the declared harness directories. |
| Plugin MCP | [MCP registry](../../mcp/registry.json) feeds [the MCP synchronizer](../../scripts/sync_mcp_adapters.py). The renderer filters by harness and emits its native transport fields. Readiness data stays in the registry. |
| Version | [VERSION](../../VERSION) feeds [the version synchronizer](../../scripts/sync_plugin_version.py), which aligns native plugin and marketplace manifests and the setup asset catalog. |
| External Skills | [Skill registry](../../skills/registry.json), source revisions, and [patch series](../../vendor/patches/) feed [the external Skill updater](../../scripts/update_external_skills.py). The updater produces the selected Skill trees, licenses, and [lock record](../../vendor/external-skills.lock.json). |

The external updater resolves a source checkout, assembles and validates the selected snapshot, and records the revision and content hashes. A tag already recorded at a different commit is rejected. Replacement starts with a drift check against the previous lock, checks collisions with local Skills, and stages the new trees and license files. This keeps local customizations visible as patch inputs and protects installed snapshots with unrecorded changes. [External updater](../../scripts/update_external_skills.py) · [Updater tests](../../tests/test_update_external_skills.py)

## Distribution checks

The adapter scripts provide read-only `--check` modes that detect missing, different, and, for the Agent directories, extra files. The CI workflow checks the version, runs the Python unittest suite on Linux and Windows with Python 3.8, and checks the Git diff for whitespace errors. The manifest tests exercise the root layout and the wiring exposed to each harness. Qoder CN's separately derived conventional installation layout is documented in its ADR. [CI workflow](../../.github/workflows/test.yml) · [Qoder CN layout decision](../../docs/adr/0014-derive-qoder-cn-conventional-plugin-layout.md)
