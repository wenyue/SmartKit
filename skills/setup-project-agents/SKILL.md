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

If `.agents/config.json` exists or accepted intent requires non-default inputs, use the
[shipped schema](../../setup-assets/catalog/project-config.schema.json) to reconcile or create this
project-owned file before `start`. Its absence means shipped defaults. Resolve external Skill sources,
project Agent mappings, and MCP declarations through that schema.

The contents of project-local Rules and Skills under `.agents/rules/` and `.agents/skills/`, including
blueprint-generated sources and their supporting files, are project-owned and editable between
sessions. Setup discovers and preserves additional project-owned Rules and Skills. Project Agent sources also remain project-owned.
Catalog-declared Codex Plugin Agent defaults are fallbacks, not project Agent declarations. Native
Cursor, Copilot, and Qoder Plugin Agents, and native plugin Rules, Skills, and MCP, are outside this
workflow.

For each generated project Rule or Skill, SmartKit records the contract fingerprint and exact output
paths, including supporting files, in `.agents/smartkit.lock.json`; it stores no persistent digests of
those files' contents. An unchanged contract with all recorded outputs present preserves project edits
without regeneration. A new or changed contract, or any missing recorded output, selects a generation
request. Removing a contract deletes its recorded outputs; renaming its catalog target retires the old
recorded paths and generates the current destination. Current project content remains input when
regeneration is selected.

Managed rendered, shared, and external assets retain digest protection. Frozen-session target drift
checks still apply to the setup-relevant surface described below.

SmartKit owns the managed files and structured fields recorded in `.agents/smartkit.lock.json` and
the authenticated, marker-bounded `AGENTS.md` unit containing `## Project rules`. Scripts enforce
adoption, marker, ownership, and digest checks before replacement and preserve content outside that
unit and every undeclared file, field, directory, and secret value.

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

`start` checks the project-owned Matt context. If it reports incomplete setup, end this invocation
and ask the user to invoke `setup-matt-pocock-skills` in the target; begin a fresh invocation after
that workflow finishes. Setup neither creates nor owns that context.

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

Scripts validate configured external sources, licenses, Skill trees, names, destination collisions,
and recorded tag stability before target mutation. If `start` rejects a declaration or source,
correct the reported cause and begin a fresh invocation.

## Start a frozen session

Identify this loaded Skill directory as `<skill-root>` and the target repository root as
`<target-root>`. Start one private session through the public `scripts/workflow.py` entry:

```text
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

`workflow.py` is the public entry for `start`, `register`, `finish`, and `cancel`.

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
immutable. If another operation holds the session claim, preserve the session and stop. Any target change after
`start` within the frozen setup-relevant surface—including a separately authorized authoring effect
on that surface—ends this session: cancel it and restart from the resulting accepted target state.
Changes outside that surface do not restart generation; preserve them as unrelated state. This
keeps authoring effects under their own grant instead of silently incorporating them into setup.

## Fulfil generation requests

With no generation requests, go directly to `finish`. Otherwise, complete the following workflow
before registering any request.

### Plan the resulting set

Resolve every requested immutable Setup Authoring Contract from `source_root`. Load the public
writer at `source_root/skills/write-rules-and-skills/SKILL.md`, including its same-source references
and `writing-for-agents` dependency. An ambient or target-checkout writer is not this session's
authority. Apply that writer's **Allocate responsibility** criteria to establish one common plan
before any Rule authoring begins.

Plan the whole resulting project Rule set, including retained Rules outside the generation
requests. Derive its membership from the frozen requests, catalog, contracts, and complete current
project inputs; assume no fixed count. For each Rule, identify its responsibility, main content,
boundaries with neighboring owners, and necessary references. Include Skills wherever their
responsibilities affect this allocation. Supply applicable always-loaded project Rules and
SmartKit global Rules, plus evidence of conditional Rules that can load together in supported
usage. Establish this context through supported discovery and loading routes, not merely the
instructions visible in the current session.

The plan records ownership and loading evidence and unresolved owner dependencies. Setup owns
this batch plan and session coordination; the public writer owns each Rule or Skill's allocation
and single-definition judgment. The catalog, schema, contracts, and scripts retain their facts and
bounds. A plan cannot add a generation request, override a contract, or authorize another owner.

### Author and reconcile before registration

Invoke the pinned public writer in the target-repository context for each request, using its
Setup Authoring Contract as accepted task/spec input and `GENERATED` as the request root. Supply
the common plan, ownership and loading evidence, owner dependency state, and complete current
project content to every job, including Skill jobs. Each invocation owns exactly one Candidate
and its own frozen scope, evidence, validation, review, and result. Jobs may run sequentially.

Accept only a public-writer `COMPLETE` handoff whose exact Candidate paths already lie beneath
`GENERATED` and satisfy the request's contract. Preserve any contract-required evidence in that
handoff; a contract's readiness terminology does not replace the public writer's result. Setup
supplies no authority for downstream effects: obtain a separate grant before any such effect,
and apply the frozen-target drift rule if it changes setup-relevant target state.

Use discoveries from authoring to update the common plan. Before registration, review all
generated outputs together with the retained Rules and relevant Skill and global Rule context
against the plan and accepted contracts. Resolve coverage omissions, responsibility overlap, and
semantic duplication using the pinned writer's allocation criteria. Individual `COMPLETE`
handoffs do not establish whole-set coherence.

Route every necessary generated correction through a distinct valid invocation of the public
writer with the updated plan and a newly frozen single-Candidate scope. Reauthor affected earlier
outputs as well as later ones, obtaining fresh `COMPLETE` handoffs for every changed Candidate.
Repeat the whole-set check until all requested outputs and their current handoffs agree with the
resolved plan. Keep this reconciliation before registration; do not edit an accepted Candidate
behind its handoff or use registration to replace it.

If a required correction belongs outside the frozen generation requests, including a retained
project Rule or SmartKit global Rule, stop and cancel the session. Follow the public writer's
owner-dependency and user-assistance path to obtain the separately authorized canonical-owner
correction, then restart from the accepted state. Preserve the pinned source and installation
caches; neither is a substitute correction target. An ownership discovery never widens this
session or a writer job's frozen scope.

A writer `NEEDS_INPUT` or `BLOCKED`, or unavailable required authority, dependency, access, or role,
stops generation. Preserve and report its exact blocker and evidence, cancel through **Stop and
recover**, and begin a fresh session only after resolution. Do not register partial work.

### Register the complete handoffs

Once whole-set review and every correction are complete, register each request once using its ID
and the exact paths from its current `COMPLETE` handoff:

```text
python "<skill-root>/scripts/workflow.py" register --session "<SESSION>" --request-id "<ID>" --output "<PATH>"
```

Repeat `--output` for supporting files in that handoff. Paths may be absolute beneath `GENERATED`
or target-relative beneath `.agents/`. The command validates and records one request's outputs;
it does not certify the writer's semantic handoff. Duplicate request registration is rejected
without replacing the earlier registration. Correct a registration input error and retry in the
same session only if that request remains unregistered and its claim was released. A claim cleanup
failure requires inspection of the reported session before retrying; target drift requires
cancellation and restart. If a semantic correction becomes necessary after registration begins,
cancel and restart rather than changing registered outputs. After all requests are registered,
continue to `finish`.

## Finish once

Run `finish` exactly once:

```text
python "<skill-root>/scripts/workflow.py" finish --session "<SESSION>"
```

Finish validates the complete outputs, frozen evidence, ownership, and plan, then applies the plan
and clean postcondition within one rollback boundary. Give it exclusive access to every planned
target path through completion or failure handling: filesystem checks cannot prevent an uncooperative
writer from being overwritten between a check and mutation. Success requires zero exit and JSON with
`phase: finish` and `check: clean`; only then is the session removed as a completed transaction.

## Stop and recover

If work must stop after `start` and before any `finish` attempt, cancel the session:

```text
python "<skill-root>/scripts/workflow.py" cancel --session "<SESSION>"
```

Before finish, unresolved declarations, ownership or digest conflicts, or setup-relevant target
drift require cancellation and a fresh session after correction. A cancel failure is terminal and
is reported unchanged.

After a pinned finish or transaction failure, preserve its exact error. The transaction attempts to
restore the pre-finish setup state and refuses a rollback mutation when its checks detect a
concurrent third-party change; a reported rollback failure identifies residual target state for
human inspection. The same filesystem limitation applies between a rollback check and its mutation,
so keep exclusive access through failure handling. Finish then attempts to remove its private session
and must report the exact session path if cleanup fails.

A cleanup failure can occur after the target already reached clean desired state or after a failed
transaction, so neither a zero-exit success nor rollback may be inferred. Never reuse, finish, or
cancel that residual session. Treat any remaining claim or partial session contents as
failure evidence. Inspect the reported target and session, remove only the verified
workflow-owned residue, resolve the original cause when present, and start a fresh session if setup
is still required.

## Handoff

Report the source mode, source root, source fingerprint, and commit when present; enabled hosts;
changed paths; external Skill sources and commits from the ownership result; preserved
project-owned paths; rollback or
residual-state evidence when applicable; and clean-check status. Ask the maintainer to review and
commit the project snapshot. This Skill grants no commit, push, publication, dependency
installation, target-external installation, or release.
