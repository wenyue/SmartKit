# Derive Qoder CN's Conventional Plugin Layout at Install Time

Status: Accepted

Date: 2026-09-07

## Context

Qoder CN 0.1.4 (`product: qodercn`) loads a plugin payload from fixed conventional locations and
ignores the paths that plugin's manifest declares. Its bundled `qoder-context@qoderapp-bundler`
plugin carries a four-field `.qoder-plugin/plugin.json` (name, displayName, version, description),
a root `mcp.json`, and `hooks/hooks.json`. SmartKit instead declares `agents: ./agents/qoder/`,
`skills: ./skills/`, `hooks: ./hooks/qoder.json`, and `mcpServers: ./mcp/qoder.json`, and
`tests/test_plugin_manifests.py` enforces those declarations for all four Harnesses. A faithful
archive of this repository is consequently rejected by Qoder CN as an incompatible package format.

The same build exposes no headless plugin CLI: `qoder` is absent and `qoder-cn` is the desktop
application, so the `qoder plugin install smartkit@wenyue` route documented in `README.md` reaches
only the international CLI. Qoder CN installations therefore need both a different payload layout
and a different registration mechanism, neither of which is visible from this repository.

## Decision

Keep the declared-path layout canonical here and derive Qoder CN's conventional layout as an
untracked install-time artifact. The derivation copies `mcp/qoder.json` to a root `mcp.json`, copies
`hooks/qoder.json` to `hooks/hooks.json`, and trims `.qoder-plugin/plugin.json` to its four metadata
fields; `skills/<name>/SKILL.md` already matches and needs no change. Installation places the
resulting payload under `~/.qoder-cn/plugins/cache/wenyue/smartkit`, adds a `smartkit@wenyue` entry
to `plugins/installed_plugins_v2.json` carrying `userVisible: true`, and enables that same key in
`settings.json`. The derived package stays outside version control because it contradicts the
manifest contract by construction.

Qoder CN scans `agents/**` recursively and registers each Markdown Agent as
`smartkit:<subdirectory>:<name>`, so the existing per-Harness adapters load with no `agents`
declaration and no flattened copy at the `agents/` root. Non-Markdown adapters such as
`agents/codex/change-set-verifier.toml` are skipped.

This was verified end to end on Qoder CN 0.1.4: all 34 Skills, the Playwright MCP server, the
SessionStart / UserPromptSubmit / PreToolUse Hooks, and the four Markdown Agent adapters load from
the derived payload, and the hand-written registry entry survives an application restart unchanged.

## Considered Options

Declaring the conventional locations in this repository was rejected. It would break
`tests/test_plugin_manifests.py` and diverge from the parallel Codex, Cursor, and Copilot manifests
to accommodate one undocumented host behavior, and `qoder-context` is a first-party bundler plugin
that may not be subject to public import validation at all. Committing the derived package was
rejected for the same contract reason. Shipping no Qoder CN installation route was rejected because
the documented CLI route does not exist on that build.

## Consequences

The conventional layout is inferred from a single first-party sample rather than documented, so a
Qoder upgrade can invalidate it silently and no test here covers it. Both the derivation and the
manual registry edit are out-of-band steps owned by no generator in `scripts/`, unlike every other
delivered surface, so reproducing an installation means re-deriving them from
`docs/research/2026-09-06-minimal-cross-harness-plugin-formats.md` and this ADR. `README.md`'s Qoder
instructions remain correct only for the international CLI.
