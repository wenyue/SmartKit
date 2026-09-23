# WenYue SmartKit

English | [简体中文](README.zh-CN.md)

WenYue SmartKit is a plugin for Codex, Cursor, GitHub Copilot, and Qoder. It provides reusable
AI coding workflows and shared project guidelines to help teams set up and maintain their coding
assistants. It supports Windows and Linux.

## Skills beyond Matt Pocock's set

### Requires manual invocation

Ask for these skills by name; the assistant does not select them automatically.

| Skill | What it does and when to use it |
| --- | --- |
| `setup-project-agents` | Sets up or updates a repository's coding assistants; use when adopting SmartKit or refreshing project agent setup. |
| `implement-tickets` | Implements and reviews a batch of eligible tracker tickets in dependency order; use when several ready tickets belong in one batch. |

### Can be invoked automatically

The assistant can select these skills when a task fits. You can also ask for them by name.

| Skill | What it does and when to use it |
| --- | --- |
| `what-changes` | When you ask to execute many accumulated edits or broad changes, reviews the intended scope and asks whether to begin implementation; you can also invoke it by name. |
| `refactor-code` | Improves the structure of one concrete code target while preserving behavior; use when that target has a specific structural problem. |
| `rename-code` | Renames one symbol or tracked path and its real references; use for a precise rename across a repository. |
| `create-worktree` | Prepares an isolated Git worktree; use when parallel work or existing checkout changes need protection. |
| `finish-worktree` | Completes an isolated worktree through a handoff, pull request, local merge, retention, or explicit discard; use when an isolated worktree needs a chosen outcome. |
| `diagnose-agent-session` | Investigates one agent session's token cost, tool activity, waits, or incomplete calls; use when session behavior looks abnormal. |
| `write-rules-and-skills` | Authors or revises one agent Rule or Skill; use when creating or changing reusable agent instructions. |

## Install the plugin

Install your preferred coding assistant first, then follow its instructions below.

### Codex

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

After installation, open a Codex CLI session and run `/hooks` to review and trust SmartKit's
Hooks. Then start a new session or run `/clear`. You can also install from the added marketplace
through `/plugins`. See the [Codex plugin guide](https://learn.chatgpt.com/docs/plugins).

### Cursor

Clone the plugin into Cursor's local plugin directory:

```sh
git clone https://github.com/wenyue/SmartKit.git "$HOME/.cursor/plugins/local/smartkit"
```

Restart Cursor or run `Developer: Reload Window`, then open Customize to confirm the plugin is
loaded. Your organization must allow local plugin imports. For team marketplace installation,
see the [Cursor plugin guide](https://cursor.com/docs/plugins).

### GitHub Copilot CLI

```sh
copilot plugin marketplace add wenyue/SmartKit
copilot plugin install smartkit@wenyue
```

See the [Copilot plugin installation guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing).

### Qoder

```sh
qoder plugin marketplace add wenyue/SmartKit
qoder plugin install smartkit@wenyue
```

These commands require plugin marketplace support to be enabled in Qoder. See the
[Qoder plugin guide](https://docs.qoder.com/cli/plugins).
