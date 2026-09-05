---
name: setup-project-agents
description: Use when initializing or reconciling a repository's Rules, Skills, Agents, or MCP across Codex, Cursor, Copilot, and Qoder.
---

# Setup Project Agents

Reconcile one repository against a trusted SmartKit snapshot and the repository's own Agent inputs.

## Principles

- **One repository, one transaction.** Discover the complete setup-relevant state, freeze it in one
  private session, and either finish that session once or cancel it.
- **Ownership is explicit.** SmartKit owns the catalog, rendered targets, host adapters, ownership
  records, validation, and transaction. The repository retains its local Rules, Skills, Agent
  sources, configuration, unrelated content, and secrets.
- **Project intent remains authoritative.** Change project-owned input only with accepted authority.
  Rendered files are consequences of that input, never a new source of truth.
- **Effects require their own grant.** Network access, temporary storage, generated authoring, and
  target mutation are distinct effects. Permission for one does not imply permission for another.
- **Evidence is frozen.** A session binds the source, external snapshots, generation requests, and
  the target state setup actually consumes. Drift on that surface requires a fresh session.
- **Finish must converge or recover.** Apply the complete plan within one rollback boundary,
  preserve unrelated state, and call the result complete only when the postcondition is clean.

## Inputs and ownership

The shipped catalog always enables Codex, Cursor, Copilot, and Qoder. It installs its declared shared Rules
and Skills, the Codex Plugin Agent defaults, and every catalog-declared project blueprint. Optional
project configuration can add external Skills, project Agents, and MCP servers.

If `.agents/config.json` exists, or accepted intent requires any non-default input, resolve the
[shipped schema](../../setup-assets/catalog/project-config.schema.json) from this loaded Skill
directory and use it to reconcile or create that target-owned file before `start`. Its absence means
shipped defaults. In the schema, `skills` identifies GitHub sources and included Skill directories;
`agents` maps project-owned `.agents/agents/<id>.md` sources to host adapters; and `mcp` declares
exactly one of `url` or `command`, with optional ordered host/OS overrides and readiness metadata.

Setup discovers and preserves additional project-owned Rules and Skills under `.agents/rules/` and
`.agents/skills/`. Project Agent sources also remain project-owned. Catalog-declared Codex Plugin
Agent defaults are fallbacks, not project Agent declarations. Native Cursor, Copilot, and Qoder Plugin
Agents, and native plugin Rules, Skills, and MCP, are outside this workflow.

SmartKit owns only the files and structured fields recorded in `.agents/smartkit.lock.json`, plus one
authenticated `AGENTS.md` unit bounded by its ownership markers and containing `## Project rules`.
It appends the unit when no such section exists, and may adopt an unmarked legacy section only when
the whole section exactly equals the current generated content. A conflicting section, malformed or
duplicate markers, ambiguous ownership, or any other ownership or digest conflict stops setup before
replacement. Preserve every byte outside the marked unit and every undeclared file, field,
directory, and secret value.

MCP environment fields name environment variables; URL, command, argument, and override literals
remain project input. Do not infer that an arbitrary string is sensitive. If qualified repository
evidence identifies a real sensitive literal, stop before rendering and ask the project owner to
replace it with supported indirection.

MCP readiness belongs to a separate automatic daily project check. Setup validates, freezes, and
preserves readiness declarations but does not execute them. The check selects the current Harness
and OS, infers checks when `checks` is absent, honors explicit checks and `checks: []`, and owns its
findings. It installs nothing and does not start a server, contact an endpoint, or authenticate.
Setup success and `check: clean` therefore prove configuration convergence, not MCP readiness.

## Preflight

Resolve only material choices that affect shipped defaults, project-owned inputs, or authorized
effects. Prefer qualified repository evidence and ask only about genuinely unresolved choices.

First require `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and
`docs/agents/domain.md`, together with a real `## Agent skills` section in `AGENTS.md` or `CLAUDE.md`
that references all three. This Matt context is project-owned: setup neither creates nor owns those
files or the entry block. If it is incomplete, end this invocation and ask the user to invoke
`setup-matt-pocock-skills` in the target. Begin a fresh `setup-project-agents` invocation only after
that workflow finishes.

Before `start`, obtain accepted project intent and separate authority for the private
system-temporary session, one read-only Git fetch of canonical SmartKit `master`, and every fetch
declared by configured external Skills. Downstream generated-authoring effects and the exact target
mutations applied by `finish` remain separate grants; obtain each before that action begins.

The fetches may contact only their declared repositories and may create, then remove, private
temporary checkouts. They run non-interactively without ambient Git configuration, credential
helpers, proxies, SSH, or askpass state. None authorizes dependency installation, publication,
Git-history changes, or any other target write. Stop before an unauthorized effect. If the canonical
fetch is unavailable, `start` may use the validated installed plugin root and reports
`source_commit: null`; configured external sources still require their own network authority.

For each configured external source, `source` must identify its GitHub `owner/repository`; `ref` may
be an existing safe branch, tag, or full commit, and omission selects the remote default branch.
The repository root must contain one unambiguous full recognized MIT, Apache-2.0, BSD-2-Clause,
BSD-3-Clause, MPL-2.0, or ISC license. Every included path must be a safe regular tree whose UTF-8
`SKILL.md` has one exact marker-bounded frontmatter `name` equal to its destination basename; links,
malformed or duplicate frontmatter, contradictory license text, non-regular entries,
destination collisions, and shared-Skill name collisions are rejected. A previously recorded tag
may not resolve to a different commit. Any rejection stops `start` before target mutation and
removes its private checkout. Correct the declaration or source, then begin a fresh invocation.

## Start a frozen session

From the target repository root, identify this loaded Skill directory as
`SETUP_PROJECT_AGENTS_ROOT`, then start one private session:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" start --target "$PWD"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" start `
  --target (Get-Location).Path
```

Both launchers check only `python3`, then `python`, require Python 3.10 or newer, and execute with
the first compatible command. If neither command qualifies, the launcher names the requirement and
checked order, then exits 2. Do not search for another interpreter or bypass the launcher.

Stop on a nonzero result. Record `session` as `SESSION`, `generated` as `GENERATED`, and the returned
`request`, `source_root`, `source_commit`, and `source_fingerprint`. The request freezes setup
inputs, external snapshots, the generation requests, and source and setup-relevant target
fingerprints. The target fingerprint covers only evidence setup consumes: project setup config,
ownership and managed assets, generated destinations, project Rule metadata, project Agent sources,
and touched native host configuration. Git history and index state, caches, logs, and other
project-owned work remain outside it.
Confirm it matches accepted intent before authoring. A canonical run is pinned to its commit and
fingerprint; an installed fallback is identified by its root, null commit, and fingerprint.

Keep exactly this private session until one `finish` or `cancel`. Treat the request and source as
immutable. `finish` and `cancel` each claim the session atomically; an existing claim means another
terminal operation started, so preserve the session and stop. Any target change after
`start` within the frozen setup-relevant surface—including a downstream authoring Acceptance effect
on that surface—ends this session: cancel it and restart from the resulting accepted target state.
Changes outside that surface do not restart generation; preserve them as unrelated state. This
keeps authoring effects under their own grant instead of silently incorporating them into setup.

## Fulfil generation requests

For every request, resolve its immutable Setup Authoring Contract from `source_root`, then load and
invoke the public workflow at `source_root/skills/write-rules-and-skills/SKILL.md`, including the
same-source references and `writing-for-agents` dependency it requires. Run that workflow in the
target-repository context with the Setup Authoring Contract as accepted task/spec input and
`GENERATED` as its request root. An ambient or target-checkout writer is not this session's
authority. The authoring workflow independently owns its Candidate, proportionate evidence and
proof, Acceptance effects, and result; setup supplies no target-effect authority. Continue only
from its ready handoff, whose exact Candidate paths must already be beneath `GENERATED`. Preserve
complete project-owned content unless accepted reconfiguration says otherwise.

After every frozen request is ready, create `GENERATED/.setup-generation.json` with this exact shape:

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

## Finish once

Run `finish` exactly once:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" finish --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" finish --session "$SESSION"
```

Finish revalidates the request, setup-relevant target fingerprint, source and external snapshots,
exact generated manifest, ownership, rendered state, and plan before mutation. It applies the plan
and its clean postcondition within one rollback boundary. Give `finish` exclusive access to every
planned target path until it returns. Before each mutation it rechecks the observed pre-finish
content, mode, and identity, but supported host filesystems do not provide a portable atomic
compare-and-swap replacement or deletion by prior identity. An uncooperative writer in the narrow
interval between that check and the filesystem mutation can therefore be overwritten. Success
requires zero exit plus JSON with `phase: finish` and `check: clean`; only then is the session removed
as a completed transaction.

## Stop and recover

If work must stop after `start` and before any `finish` attempt, cancel the session:

```sh
sh "$SETUP_PROJECT_AGENTS_ROOT/scripts/setup_project_agents.sh" cancel --session "$SESSION"
```

```powershell
& "$SETUP_PROJECT_AGENTS_ROOT\scripts\setup_project_agents.ps1" cancel --session "$SESSION"
```

Before finish, unresolved declarations, ownership or digest conflicts, setup-relevant target drift,
or generated path mismatches require cancellation and a fresh session after correction. A cancel
failure is terminal and is reported unchanged.

After a pinned finish or transaction failure, preserve its exact error. The transaction attempts to
restore the pre-finish setup state and refuses a rollback mutation when its checks detect a
concurrent third-party change; a reported rollback failure identifies residual target state for
human inspection. The same filesystem limitation applies between a rollback check and its mutation,
so keep exclusive access through failure handling. Finish then attempts to remove its private session
and must report the exact session path if cleanup fails.

A cleanup failure can occur after the target already reached clean desired state or after a failed
transaction, so neither a zero-exit success nor rollback may be inferred. Never reuse, finish, or
cancel that residual session. Treat any remaining claim or partial session contents as
terminal-operation evidence. Inspect the reported target and session, remove only the verified
workflow-owned residue, resolve the original cause when present, and start a fresh session if setup
is still required.

## Handoff

Report the source mode, source root, source fingerprint, and commit when present; enabled hosts;
changed paths; external Skill sources and commits from the ownership result; preserved
project-owned paths; rollback or
residual-state evidence when applicable; and clean-check status. Ask the maintainer to review and
commit the project snapshot. This Skill grants no commit, push, publication, dependency
installation, target-external installation, or release.
