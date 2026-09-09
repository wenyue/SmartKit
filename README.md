# WenYue SmartKit

English | [简体中文](README.zh-CN.md)

`WenYue SmartKit` is a cross-Harness plugin for Codex, Cursor, GitHub Copilot, and Qoder. It provides
Rules, Skills, Agents, and MCP as peer capabilities, then checks whether recommended tools and
configured MCP prerequisites are available when a session starts.

## Install the plugin

Install `smartkit` once in each host you use.

Codex:

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

You can also use `/plugins` in Codex to install it.

> **Required Codex Hook review:** Installing or enabling SmartKit does not automatically trust its
> bundled Hook. After installation, open a Codex CLI session, run `/hooks`, review and trust the
> SmartKit Hooks, then start a new Codex session or run `/clear`. Until they are trusted,
> Codex skips SmartKit's recommended-tool check and Rule delivery. Review again only when an update changes a
> Hook definition and Codex marks it for review.

Cursor: install it through the Plugin Marketplace or `/add-plugin`; import private versions through
a team marketplace or as a local plugin.

GitHub Copilot CLI:

```sh
copilot plugin marketplace add wenyue/SmartKit
copilot plugin install smartkit@wenyue
```

To update the Copilot plugin, run `copilot plugin marketplace update wenyue`, followed by
`copilot plugin update smartkit`.

Copilot CLI and VS Code discover SmartKit through `.claude-plugin/plugin.json`,
following Superpowers' entry layout. Codex and Cursor retain their native manifests;
Qoder retains its existing native integration. This does not add Claude Code as a
supported SmartKit host. Copilot hooks use `CLAUDE_PLUGIN_ROOT`, including
`$env:CLAUDE_PLUGIN_ROOT` in PowerShell. The entry change does not make Copilot CLI
and VS Code hook events or response protocols identical.

Qoder:

```sh
qoder plugin marketplace add wenyue/SmartKit
qoder plugin install smartkit@wenyue
```

## Plugin Rules, Skills, Agents, and MCP

| Capability | What SmartKit provides |
| --- | --- |
| Rules | Always-on, file-scoped, and Harness-scoped instructions. Strength wins first (`Mandatory` > `Default` > `Advisory`), followed by project ownership and narrower file scope. Harness scope controls activation and shares the always-on precedence tier. |
| Skills | SmartKit workflows plus reviewed, licensed, version-pinned third-party workflows. |
| Agents | `change-set-verifier` on all four hosts. It uses the project's change-set-verification Skill, reports `inconclusive` when setup has not installed that Skill, and inherits the host-selected model. Cursor, Copilot, and Qoder receive it from the plugin; Codex receives it through setup-managed default delivery. |
| MCP | Playwright in isolated headless mode on all four hosts, subject to normal host approval. |

Codex, Copilot CLI, and Qoder receive Rules through Hooks; Cursor uses native plugin Rules. Inspect the
host's Hook diagnostics when an expected Rule is absent. Copilot cloud agents are outside this
plugin-Rule contract.

Codex plugin packages do not load custom Agents. Run `setup-project-agents` in each maintained
project snapshot to install SmartKit's Codex Agent adapter under `.codex/agents/`. The adapter
remains plugin-owned and does not need an `.agents/config.json` Project Agent declaration.

## Harness and platform support

All four hosts support Windows and Linux.

| Host | Rules | Skills | Agents | MCP |
| --- | --- | --- | --- | --- |
| Codex | Session, prompt, and structured-tool Hooks | Plugin Skill catalog | Setup-managed `change-set-verifier` | Playwright |
| Cursor | Native plugin Rules | Plugin Skill catalog | `change-set-verifier` | Playwright |
| GitHub Copilot CLI | Session, transformed-prompt, and structured-tool Hooks | Plugin Skill catalog | `change-set-verifier` | Playwright |
| Qoder | Session, prompt, and structured-tool Hooks | Plugin Skill catalog | `change-set-verifier` | Playwright |

## Set up each project

In the target repository, ask the Agent to use `setup-project-agents` to configure Codex, Cursor,
Copilot, and Qoder. If prompted, complete `setup-matt-pocock-skills` first, then continue setup.

One maintainer runs setup, reviews the changes, and commits them. Teammates receive the configuration
through Git. Every unqualified setup or update is a full setup: it reauthors all current generated
project Rules and Skills, including supporting resources, using current project evidence and the
plugin’s immutable authoring contracts. You can edit generated sources directly; those edits inform
the next full setup even when upstream contracts have not changed.

Explicitly request project-only synchronization to refresh local Rule/Skill discovery and project
Agent/MCP mappings without fetching, generating, or upgrading shared/external assets. This requires
ownership recorded by full setup; external Skill declaration changes require full setup. For changes
limited to the `AGENTS.md` Rule index, request Rule-index synchronization, which also works before
full setup. Both local operations support a read-only check.

| Capability | Where to configure it |
| --- | --- |
| Rules | `.agents/rules/` |
| Skills | `.agents/skills/`; declare external Skills in `.agents/config.json` |
| Agents | `.agents/agents/`; declare them in `.agents/config.json` |
| MCP | `.agents/config.json` |

See the [configuration schema](setup-assets/catalog/project-config.schema.json) for supported fields.

### MCP overrides

Each override has a `when` selector and a `set` object. Omit `when.harnesses` to match every Harness
enabled for the server, or omit `when.operatingSystems` to match every supported operating system
(`windows` and `linux`). When both are present, both must match. Matching rules apply in array order,
and a later rule wins only for fields it declares:

```json
{
  "id": "inspector",
  "command": "python",
  "overrides": [
    {
      "when": {"operatingSystems": ["windows"]},
      "set": {"command": "py"}
    },
    {
      "when": {"harnesses": ["cursor", "copilot"]},
      "set": {"cwd": "tools/inspector"}
    }
  ]
}
```

### Project MCP readiness

Project MCP prerequisite checks are automatic. Use `readiness.harnesses` or
`readiness.operatingSystems` when a check applies only to selected hosts or operating systems:

```json
{
  "id": "inspector",
  "command": "cache/inspector.exe",
  "readiness": {
    "operatingSystems": ["windows"]
  }
}
```

Add `readiness.checks` to replace the automatic checks, or set it to `[]` to disable them. Supported
check kinds are `command-exists`, `runtime-version`, `workspace-path`, and `environment-variable`.

SmartKit manages only the content it generates and preserves the project's existing files and user
configuration whenever possible. Commit `AGENTS.md`, `.agents/`, managed host wrappers and config,
and `docs/agents/`; do not add them to `.gitignore`. Session data, caches, logs, and credentials stay
outside the repository, and generated project files must not contain secrets.

## Hooks, multi-agent, MCP readiness, and tool maintenance

The plugin runs one automatic readiness pipeline per canonical project, active host, and local
calendar day. Its first step is the daily gate; policy changes do not bypass it, while an explicit
`--force` run does. The current checks are:

- recommended-tool installation and version, including CodeGraph and Tokscale;
- required effective values, including Codex multi-agent support;
- MCP prerequisites that apply to the current Harness and operating system.

These checks never install tools, mutate MCP configuration, start an MCP server, probe a network or
application port, trigger OAuth, or require a live debug session. Project HTTP MCP declarations
therefore produce no connectivity check.

When missing or outdated tools are detected, SmartKit first lists the affected items and asks the
user. It runs maintenance actions only after explicit consent. If the user explicitly declines the
listed actions, SmartKit skips them without asking again and the original task continues. Items that
cannot be handled automatically include manual instructions. Cursor blocks affected prompts in
interactive sessions and uses the same ask-and-stop requirement as session context in headless
`--print` sessions.

## Typical workflow

```text
Install or update SmartKit → start a new host session → complete host Hook review (Codex: /hooks)
→ a maintainer runs setup-project-agents → review and commit the generated snapshot → other
developers pull → start working
```

If a check reports that tools need to be installed or upgraded, confirm the tool names and actions
before deciding whether to grant permission.
