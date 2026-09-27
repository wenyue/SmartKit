---
name: setup-project-agents
description: Set up or update project Rules, Skills, Agents, and MCP across Codex, Cursor, Copilot, and Qoder.
disable-model-invocation: true
---

# Setup Project Agents

Bring the project's declared agent configuration to a clean, owned state. Choose the operation from
the caller's intent before changing inputs or acquiring a source:

| Intent | Operation |
| --- | --- |
| First setup or an unqualified setup/update | Full setup: reauthor every current catalog-declared project Rule and Skill, including supporting resources, from immutable Setup Authoring Blueprints and current project evidence. |
| Explicitly limited to local Rule/Skill discovery and project Agent/MCP mappings | Project-only synchronization. |
| Explicitly limited to the `AGENTS.md` Rule index | Standalone Rule-index synchronization. |

Unchanged upstream fingerprints or existing outputs do not skip full authoring and do not imply
local-only intent. Conversely, a local synchronization request does not authorize full setup.

## Inputs and ownership

Resolve the loaded Skill directory as `<skill-root>` and the repository as `<target-root>`. Read
[Ownership](references/ownership.md) before either workflow. It defines project inputs, recorded
ownership, generated-output retirement, native-field preservation and the limits of readiness.
Local synchronization uses the plugin root containing this loaded Skill as `source_root`; full
setup uses the source root returned by its frozen session.

Setup owns intent routing, qualified project evidence, whole-set coherence, pinned writer
coordination and the handoff. Scripts own source selection, validation, mappings, transactions,
recovery evidence and command status. Inspect their interface and consume returned paths instead
of reconstructing session state:

```text
python "<skill-root>/scripts/workflow.py" --help
```

## Carry out full setup

Read the complete [Full Session Protocol](references/session-protocol.md) before starting. Resolve
material project-input choices and missing effect grants; accepted setup intent may already supply
them. If `start` reports missing Matt context, end this invocation and have the user invoke
`setup-matt-pocock-skills` in the target. Continue only through a fresh setup invocation after that
workflow completes.

Start one frozen session. Retain the returned request, source provenance and generated root, and
confirm that the complete requested generated set and project inputs match accepted intent.

Before authoring, read [Generated Authoring](references/generated-authoring.md). Setup plans the
resulting set of generated and retained Rules with relevant Skills and global policy, then supplies
qualified single-Candidate work to the public writer and dependencies from the pinned source. Obtain
an individual `COMPLETE` for every request. Reconcile the whole set's coverage, responsibility and
loading before registering only the final complete handoffs. A required correction outside the
frozen generation scope ends this session and goes to its owner.

Finish the registered session under the protocol's transaction and clean postcondition. On failure,
follow its original-attempt recovery branch; scripts own guarded rollback and private-session
cleanup. A clean target alone does not prove that failed cleanup completed the transaction.

After successful full setup, assess the complete direct project Rule set's always-loaded context
cost. Recommend specific branches for migration to native `rule-<domain>` Skills only when material
volume comes from policy needed under identifiable conditions. File size alone, or unconditional
baseline policy, does not justify migration.

Report source mode, root, fingerprint and commit when present; enabled hosts; changed and preserved
paths; external provenance; clean-check status; the context-load assessment; and any recovery
evidence. Hand the resulting snapshot to the maintainer for review and commit.

## Carry out explicit local synchronization

### Project discovery and Agent/MCP mappings

After supported local source or `.agents/config.json` edits, check the proposed operation:

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>" --check
```

This validates current project discovery and synchronizes the owned Rule index and declared
Agent/MCP mappings. It retires only recorded project mappings whose declarations were deleted or
renamed. Project Skills keep their direct discovery route, so validation and preservation may need
no adapter change.

No fetch, authoring, blueprint regeneration or shared/plugin/external upgrade belongs to this
operation. It needs neither Matt preflight nor a generation session. An absent or older
project-mapping ownership record requires full setup first; changed external Skill declarations
also require full setup. Report that dependency without widening the local request.

Apply only with authority for these project mappings:

```text
python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>"
```

### The Rule index alone

For intent limited to `AGENTS.md`, use the standalone operation. It remains usable before full setup
and needs no session or fetch:

```text
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>" --check
python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>"
```

### Interpret and preserve the local result

Both operations preserve every byte outside the owned `## Project rules` section in `AGENTS.md`.
Apply is atomic with an idempotent clean postcondition; check mode never mutates the target. Exit 0
with `check: clean` proves convergence. Exit 1 with `check: drift` reports proposed changed paths.
Exit 2 reports refusal or failure.

Retain exact evidence for malformed inputs, ambiguous ownership, unmanaged collisions, relevant
concurrent drift or rollback failure. Resolve the cause within accepted scope before retrying. Keep
exclusive access to planned paths through apply and rollback: filesystem checks cannot protect
against an uncooperative writer between a check and mutation.

Report operation, status, changed paths, preserved sources where supplied, and any refusal or
recovery evidence. Give successful changes to the maintainer for review and commit. Neither full
setup nor local synchronization grants commit, push, publication, release, dependency installation
or installation outside the target repository.
