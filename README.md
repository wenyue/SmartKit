# WenYue SmartKit

English | [简体中文](README.zh-CN.md)

WenYue SmartKit is a plugin for Codex, Cursor, GitHub Copilot, and Qoder. It provides reusable
AI coding workflows and shared project guidelines to help teams set up and maintain their coding
assistants. It supports Windows and Linux.

## Skills at a glance

Includes SmartKit workflows, Matt Pocock's skills, and the ponytail series. Each group is ordered
from more to less frequently needed in everyday development, to make common tools easier to find;
this is an estimated order, not usage statistics.

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
| `setup-project-agents` | [SmartKit](https://github.com/wenyue/SmartKit) | Sets up or updates a repository's coding assistants; use when adopting SmartKit or refreshing project agent setup. |
| `setup-matt-pocock-skills` | [Matt Pocock](https://github.com/mattpocock/skills) | Configures the issue tracker, triage labels, and domain docs; run before first using Matt Pocock's engineering skills. |

### Can be invoked automatically

The assistant can select these skills when a task fits. You can also ask for them by name.

| Skill | Source | What it does and when to use it |
| --- | --- | --- |
| `ponytail` | [ponytail](https://github.com/DietrichGebert/ponytail) | Favors the simplest solution that meets coding requirements, cutting unnecessary abstractions, dependencies, and code. |
| `diagnosing-bugs` | [Matt Pocock](https://github.com/mattpocock/skills) | Diagnoses bugs or performance regressions, finds the cause, and verifies the fix. |
| `code-review` | [Matt Pocock](https://github.com/mattpocock/skills) | Reviews changes since a commit, branch, or tag against both project standards and the originating spec. |
| `pr` | [Matt Pocock](https://github.com/mattpocock/skills) | Writes a concise PR body with a visual summary, verification evidence, and merge risks. |
| `tdd` | [Matt Pocock](https://github.com/mattpocock/skills) | Builds features or fixes bugs by writing a failing test, implementing, then refactoring. |
| `ponytail-review` | [ponytail](https://github.com/DietrichGebert/ponytail) | Reviews changes for correctness, security, load, tests, performance, and complexity; use `code-review` for project-standard and spec compliance. |
| `refactor-code` | [SmartKit](https://github.com/wenyue/SmartKit) | Improves the structure of one concrete code target while preserving behavior; use when that target has a specific structural problem. |
| `rename-code` | [SmartKit](https://github.com/wenyue/SmartKit) | Renames one symbol or tracked path and its real references; use for a precise rename across a repository. |
| `what-changes` | [SmartKit](https://github.com/wenyue/SmartKit) | When you ask to execute many accumulated edits or broad changes, reviews the intended scope and asks whether to begin implementation; you can also invoke it by name. |
| `research` | [Matt Pocock](https://github.com/mattpocock/skills) | Investigates a question against trusted primary sources and saves the findings as a Markdown document in the repo. |
| `prototype` | [Matt Pocock](https://github.com/mattpocock/skills) | Builds a throwaway prototype to check a design, state model, or interface. |
| `grilling` | [Matt Pocock](https://github.com/mattpocock/skills) | Stress-tests a plan, decision, or idea through probing questions. |
| `create-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | Prepares an isolated Git worktree; use when parallel work or existing checkout changes need protection. |
| `finish-worktree` | [SmartKit](https://github.com/wenyue/SmartKit) | Completes an isolated worktree through a handoff, pull request, local merge, retention, or explicit discard; use when an isolated worktree needs a chosen outcome. |
| `codebase-design` | [Matt Pocock](https://github.com/mattpocock/skills) | Clarifies module interfaces and responsibilities to improve encapsulation, testability, and code navigation. |
| `domain-modeling` | [Matt Pocock](https://github.com/mattpocock/skills) | Defines domain terminology, maintains glossaries, and records architectural decisions. |
| `ponytail-audit` | [ponytail](https://github.com/DietrichGebert/ponytail) | Audits the codebase for bugs, security and load risks, missing tests, performance, and complexity; ranks findings without applying fixes. |
| `ponytail-debt` | [ponytail](https://github.com/DietrichGebert/ponytail) | Collects `shortcut:` and older `ponytail:` comments into a debt ledger with limits, revisit triggers, and upgrade paths; saves a file only when authorized. |
| `diagnose-agent-session` | [SmartKit](https://github.com/wenyue/SmartKit) | Investigates one agent session's token cost, tool activity, waits, or incomplete calls; use when session behavior looks abnormal. |
| `write-rules-and-skills` | [SmartKit](https://github.com/wenyue/SmartKit) | Authors or revises one agent Rule or Skill; use when creating or changing reusable agent instructions. |
| `writing-for-agents` | [Matt Pocock](https://github.com/mattpocock/skills) | Writes or edits agent-facing documents with clear instructions, boundaries, and conditions for action. |
| `wizard` | [Matt Pocock](https://github.com/mattpocock/skills) | Generates an interactive Bash guide for steps only a human can perform, such as credentials, CI secrets, or migration cutovers. |

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
