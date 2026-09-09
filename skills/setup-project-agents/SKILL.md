---
name: setup-project-agents
description: Set up or update a repository’s Rules, Skills, Agents, and MCP across Codex, Cursor, Copilot, and Qoder; explicitly synchronize project-owned changes when broader setup is not requested.
---

# Setup Project Agents

Full setup is the default for first setup and every unqualified setup or update. It reauthors every
current catalog-declared project Rule and Skill, including supporting resources, from immutable
Setup Authoring Contracts and current project evidence. Unchanged upstream fingerprints and existing
outputs do not skip authoring.

Use project-only synchronization when the caller explicitly limits intent to local Rule/Skill
discovery and project Agent/MCP mappings. A request limited to the `AGENTS.md` Rule index stays within
that smaller operation. Infer neither narrow intent from an unchanged upstream nor full-setup
authority from a local synchronization request.

## Inputs and ownership

Identify this loaded Skill directory as `<skill-root>` and the repository as `<target-root>`.
Read [ownership](references/ownership.md) before either workflow. It defines project inputs,
recorded ownership, generated-output retirement, native-field preservation, and readiness boundaries.
For local synchronization, `source_root` is the plugin root containing this loaded Skill; full setup
uses the source root returned by its frozen session.

The Skill owns intent routing, project evidence, whole-set coherence, pinned writer coordination,
and handoff. Scripts own selection, validation, mappings, transaction, recovery evidence, and command
status. Use their help and returned paths rather than reconstructing protocol state:

```text
python "<skill-root>/scripts/workflow.py" --help
```

## Full setup

1. Read the [full session protocol](references/session-protocol.md). Resolve material project-input
   choices and any missing effect grants. Accepted setup intent can already authorize those effects.
   If `start` reports missing Matt context, end this invocation and have the user invoke
   `setup-matt-pocock-skills`; resume through a fresh setup invocation after it completes.
2. Start one frozen session and retain its returned request, source provenance, and generated root.
   Confirm its complete generated set and project inputs match accepted intent before authoring.
3. Read and execute [generated authoring](references/generated-authoring.md). Load the public writer
   and its dependencies from the pinned source, plan generated and retained Rules and related Skills
   together, and obtain an individual `COMPLETE` for every request. Reconcile whole-set coverage and
   overlap before registering only the final complete handoffs. A correction outside generation
   scope remains an owner dependency and ends this session.
4. Finish the registered session through the protocol’s transaction and clean postcondition. Follow
   its stop/recovery branch on any failure; scripts own safe rollback and session cleanup.
5. Report source mode, root, fingerprint and commit when present; enabled hosts; changed and preserved
   paths; external provenance; clean-check status; and any recovery evidence. Hand the snapshot to
   the maintainer for review and commit.

## Explicit project synchronization

Use the local operation after editing supported project sources or `.agents/config.json`:

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>" --check
```

It validates current project discovery, updates the owned Rule index and declared Agent/MCP mappings,
and retires only recorded project mappings for deleted or renamed declarations. Project Skills use
the existing direct discovery route; validation/preservation may require no adapter change. This
operation performs no fetch, authoring, contract regeneration, or shared/plugin/external upgrade,
and requires no Matt preflight or generation session. An absent or older project-mapping ownership
record requires full setup first. A changed external Skill declaration also requires full setup.
Report that requirement without silently widening local intent.

Apply with authority for these project mappings:

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>"
```

For an intent limited to `AGENTS.md`, use the standalone Rule-index operation. It retains its
no-session, no-fetch usability even before full setup:

```text
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>" --check
```

```text
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>"
```

Both local operations preserve every byte in `AGENTS.md` outside its owned `## Project rules`
section and apply atomically with an idempotent clean postcondition. Check mode never mutates the target. Exit 0 with
`check: clean` proves convergence; exit 1 with `check: drift` reports proposed changed paths; exit 2
reports a refusal or failure. Preserve the exact evidence for malformed inputs, ambiguous ownership,
unmanaged collisions, relevant concurrent drift, or rollback failure. Resolve the cause within the
accepted scope before retrying. Keep exclusive access to planned paths through apply and rollback;
filesystem checks cannot protect against an uncooperative writer between a check and mutation.

Report the selected operation, status, changed paths, preserved sources where reported, and any
refusal or recovery evidence. Hand successful changes to the maintainer for review and commit. This
Skill grants no commit, push, publication, release, dependency installation, or installation outside
the target repository.
