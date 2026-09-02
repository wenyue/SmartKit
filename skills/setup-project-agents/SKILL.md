---
name: setup-project-agents
description: Use when initializing or reconciling a repository's Rules, Skills, Agents, or MCP across Codex, Cursor, and Copilot.
---

# Setup Project Agents

Reconcile one target repository's Rules, Skills, Agents, and MCP. The accepted project intent owns
what should exist; the shipped setup workflow owns deterministic discovery, rendering, validation,
transaction, and cleanup. Treat the four capability families as peers and change canonical input
only when the user requests that change.

## Authority and ownership

| Capability | Canonical project input | Setup responsibility |
| --- | --- | --- |
| Rules | Project-owned sources under `.agents/rules/` and requested generated Rule targets | Preserve project Rules and deliver setup-managed Rules to each host. |
| Skills | Project-owned directories under `.agents/skills/`, requested generated Skill targets, and `.agents/config.json` `skills` declarations | Preserve project Skills and install requested generated or external Skills. |
| Agents | Project-owned sources under `.agents/agents/` and `.agents/config.json` `agents` declarations | Preserve Agent sources, render the declared host adapters, and install catalog-declared Codex Plugin Agent defaults. |
| MCP | `.agents/config.json` `mcp` declarations | Render declared host-native MCP entries without storing secret values. |

Use the shipped `.agents/config.json` schema. Each configured Agent has a matching
`.agents/agents/<id>.md` source. Each MCP entry declares exactly one of `url` or `command`; ordered
`when`/`set` overrides may select Harnesses and Platforms, and optional readiness may scope or
replace inferred MCP checks.

Project-owned canonical inputs remain editable project content. Files and structured fields
produced by setup are setup-owned and protected by its ownership manifest and digests. Stop rather
than overwrite an ownership conflict. Plugin Rules, Skills, MCP, and native Cursor and Copilot
Plugin Agents stay outside this workflow. Setup manages only catalog-declared Codex Plugin Agent
defaults, which never become Project Agent declarations.

Matt repository context is a separate project-owned prerequisite. This workflow neither generates
nor owns `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`,
`docs/agents/domain.md`, or the `## Agent skills` block that points to them.

## Preconditions

Before `start`, establish the accepted intent for all four capability families and verify that Matt
repository setup is complete: the three context files above exist and either `AGENTS.md` or
`CLAUDE.md` contains their matching `## Agent skills` block. If the prerequisite is incomplete or
unavailable, terminate this `setup-project-agents` invocation before `start` and tell the user to
invoke `setup-matt-pocock-skills` explicitly in the target repository. Do not reproduce its
questions or choose an issue tracker for it. After Matt setup reports completion, enter this Skill
only through a fresh `setup-project-agents` invocation; never resume or proceed in the terminated
run.

## One-session transaction

From the target repository root, identify this loaded Skill directory as
`SETUP_PROJECT_AGENTS_ROOT`, then start one private session:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" start --target "$PWD"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" start `
  --target (Get-Location).Path
```

Stop on a nonzero result. Record the returned `session` as `SESSION`, `generated` as `GENERATED`,
and the `request` and `source_root` paths. Continue only while exactly that private session exists
and the target remains unchanged. The captured request is immutable: verify it expresses the
accepted Rules, Skills, Agents, and MCP intent; if it does not, cancel, correct canonical input,
and restart.

Fulfil every `generation_requests` entry at its exact `GENERATED/<target>` path. Resolve its Setup
Authoring Contract from `source_root`, keep that contract immutable, and invoke
`$write-rules-and-skills` in the target-repository context for the requested Rule or Skill. Use
current repository evidence and preserve complete project-owned content unless reconfiguration was
accepted. Matt context is never a generation request.

Before finish, `GENERATED` must contain exactly the complete declared target paths, including the
empty set when no generation was requested. Also confirm that:

- all four capability families match accepted intent;
- Matt context remains project-owned and the prerequisite remains complete;
- every configured Agent has a complete matching project-owned source;
- every generated Rule and Skill satisfies its resolved contract and current repository evidence;
- the request and target have not drifted, every requested path exists, and no undeclared path
  exists; and
- generated project content contains no credential or secret.

After those conditions pass, finish the same session exactly once:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" finish --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" finish --session "$SESSION"
```

Success requires a zero exit and JSON containing `phase: finish` and `check: clean`.

## Stops and recovery

If work must stop after `start` and before any `finish` attempt, cancel the session:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" cancel --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" cancel --session "$SESSION"
```

Use only `start`, `finish`, and `cancel`; their implementation owns selection, rendering, deletion,
validation, transaction checking, and cleanup. Report the exact error from any failed operation.
Unresolved declarations, ownership or digest conflicts, request or target drift, and generated-path
mismatches stop before finish and require cancellation and a fresh session after correction.

Never cancel or retry finish for a session after a `finish` attempt: finish owns cleanup on both
success and failure. After a finish failure, discard the session and restart only after resolving
the cause. A cancel failure is terminal for the run and must be surfaced unchanged.

## Result

Report the finish result: pinned source commit, enabled hosts, changed paths, external Skills,
preserved project-owned paths, and clean-check status. Ask the maintainer to review and commit the
reported project snapshot; other developers receive it through clone or pull.
