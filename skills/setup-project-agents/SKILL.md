---
name: setup-project-agents
description: Set up or update project Rules, Skills, custom Agents, and MCP across Codex, Cursor, Copilot, and Qoder.
disable-model-invocation: true
---

# Setup Project Agents

Bring the project's agent configuration up to date without erasing the decisions that still serve
it. Full setup examines the complete declared Rule and Skill set and every project custom Agent.
Each blueprint determines what deserves refreshing; valid content may remain byte-for-byte intact.
The steps below separate project decisions from frozen generation and mechanical application.

## 1. Choose the requested operation

Resolve this directory as `<skill-root>` and the repository as `<target-root>`. Select the operation
from the caller's intent before fetching sources or changing project inputs:

| Intent | Route |
| --- | --- |
| First setup, an unqualified setup/update, or required project migration | Full setup: continue through steps 2 through 8. |
| Explicitly limited to local Rule/Skill discovery and declared Agent/MCP mappings | Follow Local synchronization below. |
| Explicitly limited to the `AGENTS.md` Rule index | Follow the Rule-index-only branch below. |

A full run checks every current blueprint even when fingerprints match. That does not require new
wording in every artifact. A local synchronization request neither refreshes models nor authorizes
full setup. Inspect the supported command interfaces as needed:

```text
python "<skill-root>/scripts/workflow.py" --help
```

This step is complete when the target and operation match accepted intent. Carry unresolved scope
choices to the user before taking effects that depend on them.

## Inputs and ownership

Before either route, read [Ownership](references/ownership.md). Project inputs and recorded ownership
control which files and fields may change; proximity and apparent obsolescence do not confer ownership.
The catalog and schema own supported input shapes. Scripts own source selection, validation,
transactions and recovery. Setup owns project evidence, refresh choices, author coordination and the
coherence of the whole result. Source authoring does not grant commit, push, release, dependency
installation or installation outside the target repository.

## 2. Establish project state and migration requirements

Read [Full Session Protocol](references/session-protocol.md), including its effect grants and Matt
context prerequisite. Read the project configuration, ownership record, existing generated content
and the project's decision records through its documentation conventions. Preserve unrelated work.
Identify the last successful `setupVersion`, or record that an initialized project lacks a baseline.
Never infer a past version from installed plugin files.

Read [Project Migrations](references/migrations.md) for baseline establishment and required upgrade
actions. Release declarations, rather than version inequality, determine mandatory migration. A
project with no setup record is not forced to initialize by the hook. An initialized project without
a successful version must complete full setup; malformed ownership evidence needs diagnosis, not
replacement with an empty record. Apply all applicable entries across skipped releases in one run.

Prepare project-owned inputs under the schema in
`<skill-root>/../../setup-assets/catalog/project-config.schema.json`. Resolve material choices and
effect authority before `start`; ordinary setup intent may already supply them. The selected source
may differ from the loaded plugin. Step 4 confirms its exact migrations and schema before generation.

This step is complete when the existing state, intended migration and prerequisites are accounted
for. Missing Matt context ends this invocation: request `setup-matt-pocock-skills`, then use a fresh
setup invocation after it completes.

## 3. Discover and reconcile every project custom Agent

Inventory declared Agents and native Agent directories for all supported hosts. Inspect host config
references too, including nonstandard Agent locations. Use the bundled read-only inventory:

```text
python "<skill-root>/scripts/adopt_project_agents.py" inspect --target "<target-root>"
```

Distinguish project custom Agents from recorded plugin defaults. An unregistered custom Agent still
belongs in this assessment. Read its complete prompt and configuration. Match identities by actual
responsibility and references, not filename alone. Preserve tools, permissions, sandbox boundaries,
host-specific metadata and omitted settings that deliberately inherit defaults. A native document
may remain the canonical source through the schema's `native_source` branch; this retains settings
that the structured mapping cannot express. Structured mappings keep their shared prompt source.

Assess model and reasoning settings on every full run, using current official provider and host
information plus available model evidence. Choose a currently usable successor suited to the same
responsibility and cost/latency class, with compatible reasoning settings. Ask before crossing a
model tier, materially increasing cost, or changing an explicit project choice. Retain existing values
when availability cannot be verified, report the incomplete assessment, and continue other work.
Evidence that a current model is unusable pauses that affected Agent until a supported choice is
settled. A new model release alone is not a mandatory project migration.

For first adoption, prepare the complete final native content and a manifest from the inventory's
captured hashes. Explain any changed model fields and demonstrate preservation of the remaining
behavior. Apply the owner-supported import before freezing a session:

```text
python "<skill-root>/scripts/adopt_project_agents.py" apply --help
python "<skill-root>/scripts/adopt_project_agents.py" apply --target "<target-root>" --manifest "<adoption-plan.json>"
```

The helper atomically imports canonical native sources, records their declarations and aligns
previously unmanaged adapters. It checks captured bytes and independent ownership; it does not
choose models or certify semantic equivalence. For an already managed adapter, change only its
canonical source; full setup performs the rendering under existing digest protection. Keep relative
native references meaningful at the installed adapter location. Preserve complete content when
converting a structured declaration; resolve its source and setting ownership before applying an
import. Never edit the lock to bypass a collision.

If responsibilities, sources, permissions or explicit choices conflict, show both file paths, the
conflicting fields and values, the effect of each choice and the decision needed. Preserve the
conflicting inputs. Continue independent inspection, but do not declare full setup complete while
such a conflict remains. Unsupported native layouts need an explicit source-preserving relocation
or host-owner correction; an omitted Agent is not a successful inventory.

This step is complete when every custom Agent is mapped and accounted for, with model changes,
retentions and unresolved verification clearly distinguished. All accepted input changes occur
before `start`; later changes follow the protocol's cancel-and-restart rule.

## 4. Start and confirm one frozen session

```text
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

Stop on a nonzero result. Retain `session`, `generated`, `request`, source provenance, the previous
and target setup versions, and the selected migration entries. Read each selected guide from that
`source_root`. Confirm that every current blueprint is requested and that frozen inputs match the
accepted project and Agent decisions. If a selected migration needs another input change, cancel,
make that authorized correction and start fresh. Keep the source and setup-relevant target evidence
frozen; unrelated work remains outside the session boundary.

This step is complete only with a valid full request and all source-specific migration prerequisites
settled. Source availability, schema rejection and drift use the protocol's own stop/recovery routes.

## 5. Plan the complete generated set

Read [Generated Authoring](references/generated-authoring.md). Read every requested immutable
blueprint from the frozen source, along with the existing target content and qualified project
evidence. Follow its specific writing focus and refresh preference. Tool inventories and structural
maps should follow current facts; stable workflows should retain still-valid decisions. Neither a
changed fingerprint nor an unchanged one decides whether a sentence needs rewriting.

Plan coverage, responsibility and loading across generated and retained Rules, relevant Skills and
applicable global policy. For each requested artifact, identify what remains valid, what must change
and the evidence for that change. Preserve project additions, obligations and consequential exceptions.
Repair stale facts and genuine duplication; stylistic novelty alone is not a reason to rewrite.

This step is complete when every request has a justified refresh direction, required evidence and
an owner/loading place in the whole set. Resolve dependencies outside the frozen scope through their
owner under the protocol instead of silently enlarging generation.

## 6. Obtain and reconcile complete writer results

Use the pinned public writer and its same-source dependencies as specified in Generated Authoring.
Give each invocation exactly one Candidate, its blueprint, complete existing content and the common
plan. Every request needs an individual `COMPLETE`, including an unchanged artifact: the writer may
return a verified exact copy and its supporting files beneath `GENERATED`.

Check the combined result against the plan. Look for missing obligations, stale evidence, conflicting
owners, duplicate operative requirements and broken loading routes. Obtain fresh writer handoffs
for necessary corrections. Reconcile before registration; an individual writer result cannot prove
whole-set coherence.

This step is complete when every request has a final complete handoff and the combined set satisfies
its blueprints without losing valid project meaning. Missing authority, blocked writing or an
out-of-scope correction follows the protocol's cancellation route.

## 7. Register and finish

Register each final handoff once, with every supporting output path, then finish:

```text
python "<skill-root>/scripts/workflow.py" register --session "<SESSION>" --request-id "<ID>" --output "<PATH>"
python "<skill-root>/scripts/workflow.py" finish --session "<SESSION>"
```

Repeat `--output` for supporting files. Preserve the complete request set; copying an unchanged
artifact still supplies its complete outputs. Matching bytes converge without rewriting target files.
Finish validates, applies and checks the configuration, removes the private session, then atomically
records the source release as `setupVersion`. A failed apply, cleanup or version commit is not success
and does not establish a new baseline. Follow the original-attempt recovery branch; retain any
reported remaining target or session state rather than retrying a residual session.

This step is complete only with exit 0, `phase: finish`, `check: clean`, the reported successful setup
version and completed session cleanup. Local synchronization never advances this version.

## 8. Hand off the verified result

Assess the complete direct project Rule set's always-loaded context cost. Recommend moving policy
to native `rule-<domain>` Skills only when substantial volume is conditional on identifiable cases;
file size alone does not justify moving unconditional baseline policy.

Report source mode/root/fingerprint/commit, source release, previous and resulting setup versions,
applied migrations, enabled hosts, changed and preserved paths, custom Agent/model decisions and
external provenance. Include actual clean-check status, the context assessment, incomplete model
verification and any recovery evidence. Give the maintainer the snapshot for review and commit;
configuration convergence does not prove MCP runtime readiness.

The handoff is complete when the user can distinguish applied changes, preserved behavior and any
remaining limitation without reconstructing the session.

## Local synchronization

Read Ownership first. Local operations use the plugin root containing the loaded Skill and neither
fetch nor run generation, model assessment, blueprint refresh or shared/external upgrades.

1. **Check the requested change.** For local discovery and declared Agent/MCP mappings:

   ```text
   python "<skill-root>/scripts/workflow.py" sync-project --target "<target-root>" --check
   ```

   Broad synchronization needs an established project-mapping ownership record. Missing/older
   records or changed external Skill declarations require full setup; report that dependency without
   widening the request. For the Rule index alone, use `sync-project-rules --check`; it remains
   available before full setup.

2. **Apply the authorized scope.** Remove `--check` from the selected command. The Rule-index route is:

   ```text
   python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>" --check
   python "<skill-root>/scripts/workflow.py" sync-project-rules --target "<target-root>"
   ```

   Apply preserves bytes outside the owned `AGENTS.md` section and retires only recorded mappings.
   Check mode never writes. Exit 0 with `check: clean` establishes convergence; exit 1 with
   `check: drift` lists proposed changes; exit 2 is refusal or failure. Keep exclusive access through
   apply and rollback, and resolve reported ownership, malformed-input or drift causes before retrying.

3. **Report the result.** Give the operation, status, changed paths, preserved inputs and any exact
   refusal or recovery evidence. Completion requires the clean result; no local route updates the
   successful full-setup version or certifies runtime readiness.
