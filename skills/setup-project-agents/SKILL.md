---
name: setup-project-agents
description: Use when initializing or reconciling a repository's Rules, Skills, Agents, or MCP across Codex, Cursor, and Copilot.
---

# Setup Project Agents

Reconcile one repository against the SmartKit setup snapshot and its project-owned Agent inputs.
SmartKit owns the setup catalog, generated targets, host adapters, ownership manifest, rendering,
validation, and transaction. The target repository owns its local Rules, Skills, Agent sources,
configuration, unrelated state, and secrets. Change target-owned intent only with accepted project
authority; a rendered target never becomes plugin authority.

## Supported state

The shipped catalog always enables Codex, Cursor, and Copilot, installs its declared shared Rules,
Skills, and Codex Plugin Agent defaults, and requests the five catalog-declared project blueprints.
Project configuration may add external Skills, project Agents, and MCP servers:

- `.agents/config.json` follows the shipped schema. `skills` names GitHub sources and included Skill
  directories; `agents` maps `.agents/agents/<id>.md` sources to host adapters; and `mcp` declares
  exactly one of `url` or `command`, with optional ordered host/OS overrides and readiness.
- Setup discovers additional project-owned Rules and Skills under `.agents/rules/` and
  `.agents/skills/`, preserves them, and keeps every project Agent source project-owned.
- Setup owns only files and structured fields recorded in `.agents/smartkit.lock.json`. It stops on
  an ownership or digest conflict and preserves undeclared files, fields, directories, and secret
  values. Environment-variable names may be rendered; secret values may not enter generated
  content or the ownership manifest.

Native Cursor and Copilot Plugin Agents and plugin Rules, Skills, and MCP remain outside this
workflow. Catalog-declared Codex Plugin Agent defaults are fallbacks, not project Agent declarations.
Matt repository context is also separate project-owned state: setup neither generates nor owns
`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/domain.md`, or the
`## Agent skills` entry block that points to them.

## Preflight and effects

Establish accepted project intent through the supported inputs above. Require the three Matt
context files and a matching `## Agent skills` block in `AGENTS.md` or `CLAUDE.md`. If absent, end
this invocation and ask the user to invoke `setup-matt-pocock-skills` in the target; after that
workflow completes, begin a fresh `setup-project-agents` invocation.

Before `start`, obtain authority for its private system-temporary session, one read-only canonical
Git fetch of SmartKit `master`, and the Git fetches declared by configured external Skills. These
fetches may contact their declared repositories and create then remove private temporary checkouts;
they do not authorize credential prompts, dependency installation, target writes, publication, or
Git-history changes. If canonical fetch is unavailable, `start` may use the validated installed
plugin root and reports `source_commit: null`; configured external sources still require their own
network access. Stop before an unauthorized effect.

## Start one frozen session

From the target repository root, identify this loaded Skill directory as
`SETUP_PROJECT_AGENTS_ROOT`, then start one private session:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" start --target "$PWD"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" start `
  --target (Get-Location).Path
```

Stop on a nonzero result. Record `session` as `SESSION`, `generated` as `GENERATED`, and the returned
`request`, `source_root`, `source_commit`, and `source_fingerprint`. The request freezes setup
inputs, external snapshots, the five generation requests, and source and target fingerprints.
Confirm it matches accepted intent before authoring. A canonical run is pinned to its commit and
fingerprint; an installed fallback is identified by its root, null commit, and fingerprint.

Keep exactly this private session until one `finish` or `cancel`. Treat the request and source as
immutable. Any target change after `start`—including a downstream authoring Acceptance effect—ends
this session: cancel it and restart from the resulting accepted target state. This keeps authoring
effects under their own grant instead of silently incorporating them into setup.

## Fulfil generation requests

For every request, resolve its immutable Setup Authoring Contract from `source_root` and invoke
`write-rules-and-skills` in the target-repository context with that contract as accepted task/spec
input. The authoring workflow independently owns its Candidate, evidence, proof, Acceptance effects,
and result; setup supplies no target-effect authority. Continue only from its ready handoff and copy
each exact returned Candidate path beneath `GENERATED`. Preserve complete project-owned content
unless accepted reconfiguration says otherwise.

After all five requests are ready, create `GENERATED/.setup-generation.json` with this exact shape:

```json
{
  "version": 1,
  "requests": [
    {"id": "<generation request id>", "outputs": ["<exact target-relative path>"]}
  ]
}
```

Include every request and returned Candidate path exactly once. Each request's primary `target` is
mandatory. A Rule request declares only its primary target. A Skill request may also declare exact
supporting paths returned under that Skill directory by its Authoring Contract; a directory, glob,
inferred path, or resource from a non-ready handoff is not a declaration. The manifest is private
session control data and is not installed.

Before finish, confirm that generated files equal the manifest exactly; each output satisfies its
authoring contract and qualified target evidence; Matt context remains complete; project Agent
sources are complete; no generated content contains a credential or secret; and the request,
source, and target fingerprint remain unchanged.

## Finish atomically

Run `finish` exactly once:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" finish --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" finish --session "$SESSION"
```

Finish revalidates the request, target fingerprint, external snapshots, exact generated manifest,
ownership, rendered state, and plan before mutation. It applies the plan and its clean postcondition
within one rollback boundary. Success requires zero exit plus JSON with `phase: finish` and
`check: clean`; only then is the session removed as a completed transaction.

## Stops and recovery

If work must stop after `start` and before any `finish` attempt, cancel the session:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" cancel --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" cancel --session "$SESSION"
```

Before finish, unresolved declarations, ownership or digest conflicts, target drift, or generated
path mismatches require cancellation and a fresh session after correction. A cancel failure is
terminal and is reported unchanged.

After any finish failure, preserve its exact error. The transaction restores the pre-finish setup
state when it can do so without overwriting a concurrent third-party change; a reported rollback
failure identifies residual state for human inspection. Finish removes its private session on
success or failure, so never cancel or retry it. Resolve the cause, inspect residual paths, and
start a fresh session.

## Handoff

Report the source mode, source root, source fingerprint, and commit when present; enabled hosts;
changed paths; external Skill sources and commits from the ownership result; preserved
project-owned paths; rollback or
residual-state evidence when applicable; and clean-check status. Ask the maintainer to review and
commit the project snapshot. This Skill grants no commit, push, publication, dependency
installation, target-external installation, or release.
