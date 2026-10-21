# WenYue SmartKit

English | [简体中文](README.zh-CN.md)

WenYue SmartKit is a plugin for Codex, Cursor, GitHub Copilot, and Qoder. It provides reusable AI coding workflows and shared project guidelines to help teams set up and maintain their coding assistants. It supports Windows and Linux.

## Skills at a glance

Includes SmartKit workflows, Matt Pocock's skills, the ponytail series, and Diagram Design. Each group is organized by purpose to help you find the Skill for your current task.

### Requires manual invocation

Ask for these skills by name; the assistant does not select them automatically.

| Skill | Source | What it does and when to use it |
| --- | --- | --- |
| `implement` | [Matt Pocock](https://github.com/mattpocock/skills) | Implements a piece of work from a spec or tickets. |
| `implement-spec` | [Matt Pocock](https://github.com/mattpocock/skills) | Implements a spec’s dependency graph with parallel agents and a shared integration branch. |
| `grill-me` | [Matt Pocock](https://github.com/mattpocock/skills) | Sharpens a plan or design through an in-depth interview and identifies unresolved decisions. |
| `what-if` | [SmartKit](https://github.com/wenyue/SmartKit) | Judges whether an idea you are unsure about beats current practice and alternatives, giving an independent verdict with pros and cons without making changes. |
| `to-spec` | [Matt Pocock](https://github.com/mattpocock/skills) | Synthesizes the discussion into a spec and publishes it to the project's tracker. |
| `to-tickets` | [Matt Pocock](https://github.com/mattpocock/skills) | Breaks a plan or spec into incrementally deliverable tickets with declared dependencies. |
| `review-for-humans` | [SmartKit](https://github.com/wenyue/SmartKit) | Explains supplied changes by file with simple examples and reasoned judgments, displaying groups for a human reviewer to read and continue. |
| `collect-todos` | [SmartKit](https://github.com/wenyue/SmartKit) | Saves deferred tasks in the project's configured tracker and reports what was collected; use to record side tasks and continue the current main task. |
| `handoff` | [Matt Pocock](https://github.com/mattpocock/skills) | Compacts the conversation into a handoff document for another agent or a later session. |
| `retro` | [Matt Pocock](https://github.com/mattpocock/skills) | Reviews a coding session and suggests improvements to the agent’s working environment. |
| `ask-matt` | [Matt Pocock](https://github.com/mattpocock/skills) | Recommends a skill or flow for your situation; use when unsure which one to choose. |
| `wait-what` | [Matt Pocock](https://github.com/mattpocock/skills) | Asks the assistant to explain its last answer again when it was hard to follow. |
| `teach` | [Matt Pocock](https://github.com/mattpocock/skills) | Teaches a skill or concept in the context of the current workspace. |
| `triage` | [Matt Pocock](https://github.com/mattpocock/skills) | Categorizes and verifies issues and external PRs, turning them into actionable briefs for agents. |
| `grill-with-docs` | [Matt Pocock](https://github.com/mattpocock/skills) | Sharpens a design through an interview while recording architectural decisions and domain terminology. |
| `improve-codebase-architecture` | [Matt Pocock](https://github.com/mattpocock/skills) | Scans for structural improvements, presents a visual report, and explores the target you select. |
| `to-questionnaire` | [Matt Pocock](https://github.com/mattpocock/skills) | Turns an unresolved decision into a questionnaire for someone else to supply missing information. |
| `wayfinder` | [Matt Pocock](https://github.com/mattpocock/skills) | Maps large work spanning multiple sessions into decision tickets and resolves the path to implementation. |
| `setup-project-agents` | [SmartKit](https://github.com/wenyue/SmartKit) | Initializes or upgrades project agent configuration, or restores an existing configuration-repository backup. |
| `maintain-project-config` | [SmartKit](https://github.com/wenyue/SmartKit) | Maintains project Agent configuration shared with the project, kept on this machine, or synchronized through a separate configuration repository. |
| `setup-matt-pocock-skills` | [Matt Pocock](https://github.com/mattpocock/skills) | Configures the issue tracker, triage labels, and domain docs; run before first using Matt Pocock's engineering skills. |

### User-invokable task Skills

Use these Skills for a specific task. Ask for them by name, or let the assistant select them when the task fits. They are ordered by purpose: scope review, research and validation, development and improvement, audit and delivery, then setup and session diagnosis.

| Skill | Source | What it does and when to use it |
| --- | --- | --- |
| `what-changes` | [SmartKit](https://github.com/wenyue/SmartKit) | When you ask to execute many accumulated edits or broad changes, reviews the intended scope and asks whether to begin implementation; you can also invoke it by name. |
| `research` | [Matt Pocock](https://github.com/mattpocock/skills) | Investigates a question against trusted primary sources and saves the findings as a Markdown document in the repo. |
| `diagram-design` | [Diagram Design](https://github.com/cathrynlavery/diagram-design) | Creates architecture diagrams, flowcharts, and other HTML/SVG figures, with PNG export and diagram imports; uses the default style immediately unless a brand is configured or requested. |
| `prototype` | [Matt Pocock](https://github.com/mattpocock/skills) | Builds a throwaway prototype to check a design, state model, or interface. |
| `diagnosing-bugs` | [Matt Pocock](https://github.com/mattpocock/skills) | Diagnoses bugs or performance regressions, finds the cause, and verifies the fix. |
| `tdd` | [Matt Pocock](https://github.com/mattpocock/skills) | Builds features or fixes bugs by writing a failing test, implementing, then refactoring. |
| `refactor-code` | [SmartKit](https://github.com/wenyue/SmartKit) | Improves the structure of one concrete code target while preserving behavior; use when that target has a specific structural problem. |
| `ponytail-audit` | [ponytail](https://github.com/DietrichGebert/ponytail) | Audits the codebase for bugs, security and load risks, missing tests, performance, and complexity; ranks findings without applying fixes. |
| `ponytail-debt` | [ponytail](https://github.com/DietrichGebert/ponytail) | Collects `shortcut:` and older `ponytail:` comments into a debt ledger with limits, revisit triggers, and upgrade paths; saves a file only when authorized. |
| `pr` | [Matt Pocock](https://github.com/mattpocock/skills) | Writes a concise PR body with a visual summary, verification evidence, and merge risks. |
| `write-rules-and-skills` | [SmartKit](https://github.com/wenyue/SmartKit) | Authors or revises one agent Rule or Skill; use when creating or changing reusable agent instructions. |
| `wizard` | [Matt Pocock](https://github.com/mattpocock/skills) | Generates an interactive Bash guide for steps only a human can perform, such as credentials, CI secrets, or migration cutovers. |
| `diagnose-agent-session` | [SmartKit](https://github.com/wenyue/SmartKit) | Investigates one agent session's token cost, tool activity, waits, or incomplete calls; use when session behavior looks abnormal. |

### Generally invoked automatically by the Agent

The Agent usually selects these supporting Skills as part of its work. You can also ask for them by name; they are listed here without separate usage sections.

| Skill | Source | What it does and when to use it |
| --- | --- | --- |
| `ponytail` | [ponytail](https://github.com/DietrichGebert/ponytail) | Favors the simplest solution that meets coding requirements, cutting unnecessary abstractions, dependencies, and code. |
| `ponytail-review` | [ponytail](https://github.com/DietrichGebert/ponytail) | Reviews changes for correctness, security, load, tests, performance, and complexity; use `code-review` for project-standard and spec compliance. |
| `code-review` | [Matt Pocock](https://github.com/mattpocock/skills) | Reviews changes since a commit, branch, or tag against both project standards and the originating spec. |
| `grilling` | [Matt Pocock](https://github.com/mattpocock/skills) | Stress-tests a plan, decision, or idea through probing questions. |
| `rename-code` | [SmartKit](https://github.com/wenyue/SmartKit) | Renames one symbol or tracked path and its real references; use for a precise rename across a repository. |
| `create-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | Prepares an isolated Git worktree; use when parallel work or existing checkout changes need protection. |
| `finish-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | Completes an isolated worktree through a handoff, pull request, local merge, retention, or explicit discard; use when an isolated worktree needs a chosen outcome. |
| `codebase-design` | [Matt Pocock](https://github.com/mattpocock/skills) | Clarifies module interfaces and responsibilities to improve encapsulation, testability, and code navigation. |
| `domain-modeling` | [Matt Pocock](https://github.com/mattpocock/skills) | Defines domain terminology, maintains glossaries, and records architectural decisions. |
| `writing-for-agents` | [Matt Pocock](https://github.com/mattpocock/skills) | Writes or edits agent-facing documents with clear instructions, boundaries, and conditions for action. |

## Use SmartKit Skills

The sections below cover SmartKit Skills from the first two groups, in their overview order. Ask for a Skill by name in your message, as in the examples below. Manual-only Skills require that explicit request; user-invokable task Skills can also be selected automatically when the task fits.

### `what-if`

Manually invoke this Skill when you want an independent judgment of an idea before acting. It compares the proposal with current practice and useful alternatives, explains the trade-offs, and keeps the evaluation read-only. Implementation needs a later, separate instruction.

Example: “Use `what-if` to judge whether we should combine these two configuration files.”

### `review-for-humans`

Manually invoke this Skill to understand changes file by file, with explanations and separate judgments of reasonableness and elegance. Specify a PR, branch, or selected files. PR reviews default to skipping files the current GitHub viewer has marked viewed; local reviews, including requests without a scope, cover only unstaged changes relative to the index. You can explicitly include viewed PR files or staged local changes. It skips test files and displays complete files in groups; ask to continue for the next group, or select numbered findings to fix or suggestions to optimize.

Example: “Use `review-for-humans` to explain my unstaged changes.” Then: “Fix item 2 and continue.”

### `collect-todos`

Manually invoke this Skill to save selected deferred tasks in the project's declared tracker, then return to the main task. It checks for existing records and reports verified links. Configure the project's tracker first; the Skill does not choose a replacement destination when one is missing.

Example: “Use `collect-todos` to record the cache cleanup we discussed for later, then continue the login fix.”

### `setup-project-agents`

Manually invoke this Skill to choose between initializing/upgrading project agent configuration and restoring an existing configuration-repository backup. Full setup checks project Rules, Skills, custom Agents, and MCP mappings while preserving valid project decisions. On first setup, choose configuration shared through the project, kept only on this machine, or backed up in a separate private repository; existing choices are retained on upgrade. When tracker, triage-label, or domain context is missing, full setup guides you through the shared Matt initialization workflow and then continues in the same invocation. Existing choices are retained, and new edits are shown before writing. State an explicit limit when you only want local synchronization or a Rule-index update.

For a new checkout, invoke setup yourself and choose restoration to recover saved configuration without regeneration or publication. Restoration checks local prerequisites and reports gaps; it does not complete full setup. Automatic startup synchronization is optional and defaults to off. Session startup does not discover missing configuration or ask to restore it.

Examples: “Use `setup-project-agents` to update this repository's agent configuration.” Or: “Use `setup-project-agents` to restore my configuration backup on this machine.”

### `maintain-project-config`

Manually invoke this Skill to check configuration, maintain and synchronize it, or explicitly adopt selected project edits into its source. First use `setup-project-agents` to choose Project shared, This machine only, or Separate configuration repository. The latter uses a private personal GitHub repository that can serve multiple projects; maintenance verifies the applied configuration and saves only the accepted changes to GitHub.

Example: “Use `maintain-project-config` to update this project’s Rules and synchronize the accepted changes.”

### `what-changes`

Use this Skill to reconcile accumulated edits before implementation. You can ask for it by name; the Agent may also select it when you ask to execute many accumulated edits. It reports the current goals, exclusions, unresolved choices, and intended file changes without editing anything. After unresolved choices are settled, it asks whether to begin implementation.

Example: “Use `what-changes` to review the accumulated changes from this conversation; do not implement them yet.”

### `refactor-code`

Use this Skill for one concrete code target with a known structural problem. Name the target and the problem to remove; it improves internal structure while preserving supported behavior and external contracts. An open-ended search for architecture improvements is a different task.

Example: “Use `refactor-code` to remove duplicated escape handling in `parse_record`, preserving its input order and error behavior.”

### `write-rules-and-skills`

Use this Skill to author or revise one reusable Agent Rule or Skill. You can ask for it by name or let the Agent select it when the task fits. Describe the intended job, readers, and constraints. It produces one coherent artifact with required checks and quality, change, and correctness reviews; publication and installation are separate actions.

Example: “Use `write-rules-and-skills` to write a project Rule requiring verification of exported records before replacing an existing export.”

### `diagnose-agent-session`

Use this Skill to investigate abnormal token usage, tool activity, waits, or incomplete calls in one agent session. Name the client and session for another session; the current Codex session can be inferred when both are omitted. Codex supports turn and session evidence; Cursor and Copilot CLI support whole-session usage evidence. The report distinguishes observations from missing evidence and labels cost as an estimate; whole-session acquisition requires authorization for the provider's record scanning, network, and cache access.

Example: “Use `diagnose-agent-session` to investigate tool activity and waits in the current Codex turn.”

## Third-party Skills and tools

### Included Skills

SmartKit includes selected Skills from the following projects, with SmartKit-specific adaptations. They are installed with the plugin. The overview above lists the individual Skills and their sources.

| Source | Focus | License |
| --- | --- | --- |
| [Matt Pocock Skills](https://github.com/mattpocock/skills) | Planning, specifications, implementation, research, and review workflows. | [MIT](licenses/mattpocock-skills-LICENSE.txt) |
| [ponytail](https://github.com/DietrichGebert/ponytail) | Simple coding solutions, change reviews, codebase audits, and technical debt tracking. | [MIT](licenses/DietrichGebert-ponytail-LICENSE.txt) |
| [Diagram Design](https://github.com/cathrynlavery/diagram-design) | Branded diagrams, diagram imports, and HTML/SVG/PNG output. | [MIT](licenses/cathrynlavery-diagram-design-LICENSE.txt) |

### Tools

SmartKit configures or recommends the following tools. Full project setup prepares CodeGraph on the current machine: it installs the tool when missing, initializes or synchronizes the project's index, and verifies the running service. Setup requires authorization for those effects. Every session in an initialized SmartKit project checks CodeGraph again and reminds you when it needs attention. Tokscale is installed separately. The plugin owns the MCP configuration for CodeGraph and Playwright: at session start, SmartKit removes same-named entries from your user-level MCP configuration.

| Tool | Purpose | Installation and use |
| --- | --- | --- |
| [CodeGraph](https://github.com/colbymchenry/codegraph) | Navigates indexed code through symbols and call relationships. | Required for projects initialized by SmartKit. Full setup prepares the local installation, index and service; the plugin includes MCP configuration. Index databases remain local to each working tree. |
| [Tokscale](https://github.com/junhoyeo/tokscale) | Supplies token usage and estimated cost evidence for `diagnose-agent-session`. | Make `tokscale` available on PATH; available diagnostic data depends on the client and its recorded usage. |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Provides browser automation. | The plugin includes MCP configuration; the client uses `npx` to obtain and launch `@playwright/mcp`. Requires Node.js 18 or newer and `npx` on PATH. |

Hook launchers warn on stderr when execution exceeds 0.2 seconds. Timing includes the Python preflight and handler; it preserves the original output and exit status and never blocks a task because of elapsed time.

## Install the plugin

Install your preferred coding assistant and Python 3.8 or newer first, with `python` available on PATH for SmartKit Hooks and project setup. To use Playwright MCP, also install Node.js 18 or newer with `npx` on PATH. Then follow your assistant's instructions below.

### Codex

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

After installation, open a Codex CLI session and run `/hooks` to review and trust SmartKit's Hooks. Then start a new session or run `/clear`. You can also install from the added marketplace through `/plugins`. See the [Codex plugin guide](https://learn.chatgpt.com/docs/plugins).

### Cursor

Clone the plugin into Cursor's local plugin directory:

```sh
git clone https://github.com/wenyue/SmartKit.git "$HOME/.cursor/plugins/local/smartkit"
```

Restart Cursor or run `Developer: Reload Window`, then open Customize to confirm the plugin is loaded. Your organization must allow local plugin imports. For team marketplace installation, see the [Cursor plugin guide](https://cursor.com/docs/plugins).

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

These commands require plugin marketplace support to be enabled in Qoder. See the [Qoder plugin guide](https://docs.qoder.com/cli/plugins).
