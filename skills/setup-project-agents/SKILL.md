---
name: setup-project-agents
description: Initialize or upgrade project agent configuration, choose its maintenance mode, and prepare supported development tools.
disable-model-invocation: true
---

# Setup Project Agents

Initialize or upgrade the project's agent configuration while preserving decisions that still serve it. Full setup assesses every declared blueprint and project custom Agent, even when fingerprints match, and prepares CodeGraph for the local target. Valid artifacts may remain byte-for-byte intact. This Skill requires the user's explicit invocation.

## 1. Choose the requested operation

Resolve this directory as `<skill-root>`, its sibling maintenance entry `<skill-root>/../maintain-project-config/scripts/maintain.py` as `<maintain>`, and the repository as `<target-root>`. Select the route before fetching sources or changing project inputs:

| Intent | Route |
| --- | --- |
| First setup | Establish the project and choose its maintenance mode in step 2, then complete steps 3 through 8. |
| Upgrade, an unqualified setup/update of an existing project, or required project migration | Preserve the existing baseline and maintenance choice in step 2, then complete steps 3 through 8. |
| Explicitly limited to local Rule/Skill discovery and declared Agent/MCP mappings | Local synchronization below. |
| Explicitly limited to the `AGENTS.md` Rule index | The Rule-index branch under Local synchronization. |

Before either route, read [Ownership](references/ownership.md) for canonical inputs, discovery, loading meaning and replacement boundaries. Catalog and schema own supported input shapes; scripts own validation and application; Setup owns project decisions, author coordination and whole-set coherence. Resolve material scope choices before dependent effects.

## 2. Establish project state and its maintenance mode

Read [Full Session Protocol](references/session-protocol.md) for effect authority, Matt context, source selection and recovery, and [Project Migrations](references/migrations.md) for baseline and release-specific obligations. Read [Project Configuration Maintenance](../maintain-project-config/references/maintenance.md) for source binding, private repository access, application and publication boundaries. Setup consumes that Skill's supported reference, command interface and configuration engine without invoking the user-only maintenance Skill. Begin with both read-only inspections; their help explains the reported checks and exits:

```text
python "<skill-root>/scripts/workflow.py" inspect --help
python "<skill-root>/scripts/workflow.py" inspect --target "<target-root>"
python "<maintain>" inspect --target "<target-root>"
```

Use the findings alongside complete project configuration, ownership, existing generated content and decision records reached through the project's documentation conventions. Resolve prerequisite errors before the affected step; exit 0 from setup inspection leaves the returned `pending_assessment` to Setup. Missing Matt context follows the protocol's fresh-invocation route.

### First setup

Identify existing project instructions, personal configuration and independent owners before choosing what setup will manage. A missing maintenance declaration alone does not identify a new project. Retain an existing recorded choice. When inspection reports `selection_required`, ask once in the user's language, presenting these three complete choices together:

| Choice | Recorded mode | User-facing result |
| --- | --- | --- |
| Project shared | `local` | Keep configuration in the business project for versioning with its repository. |
| This machine only | `local-only` | Keep configuration in the business project and locally exclude it from business Git; no GitHub source is needed. |
| Separate configuration repository | `repository` | Maintain configuration in a personal private GitHub repository and locally exclude target configuration from business Git. |

Record the accepted choice through the maintenance command's `bind` route. For repository mode, communicate that setup includes the exact scoped source commit and normal push after successful local finish under the shared publication contract, unless the user requests a local result. Follow that reference for Git exclusion behavior and already tracked files; mode selection does not itself change existing tracked status.

For repository maintenance, establish the personal repository identity, branch and project entry. Connect an existing private repository or create one only with the user's specified owner and name. Different projects can use distinct entries in the same repository. Import only identified and accepted existing personal files; preserve tracked business-project content and independently owned configuration. Connecting an existing entry on another machine requires comparing its source with the current target before initial application.

Continue when the maintenance choice is recorded, the selected source is available, and initial imports or collisions have an accepted resolution. First setup completes only after successful local finish and the publication outcome required by step 8; an established binding alone is insufficient.

### Upgrade an existing project

Establish the last successful setup version and collect every applicable migration without guessing missing history. An initialized project without a successful version keeps its ownership record and content while full setup establishes the baseline. If inspection reports `selection_required`, present the same three complete choices above and record the answer once; otherwise retain the recorded mode, repository, branch and entry. Existing `local` means Project shared, not an unresolved choice. Switch modes or entries only when the user requests that change, after comparing and preserving the old source and target work.

In repository mode, communicate the same publication default and update the persistent source checkout before editing it. When binding or earlier maintenance already refreshed it and produced accepted pending changes, verify and retain that evidence and continue from those changes instead of running the clean-checkout update again. Read relevant migration decisions against both the business project and its source entry, and make portable configuration corrections in that entry first. Refresh the applied target through the maintenance command before freezing a session. Upgrade completes only after all selected migrations, successful local finish and the publication outcome required by step 8.

### Prepare accepted inputs for the full run

Reconcile configuration under the schema identified in Ownership, preserving unrelated work. In either local mode, edit the project's canonical inputs. In repository mode, use the source paths reported by inspection, with business-project evidence, and apply accepted source changes before `start`. Carry accepted initial imports and preparatory source changes with their provenance into final publication, including the full accepted import on an unborn branch rather than only the later generated delta. Keep binding and local state with their target owners. The shared reference explains how initial collision acceptance differs from adopting a later target edit.

Preflight migrations come from the loaded plugin source; step 4 confirms the SmartKit source selected for the session. Continue when project state, source choice, input decisions, migration requirements and prerequisite gaps are accounted for.

## 3. Discover and reconcile every project custom Agent

Use the preflight inventory; refresh it after project input changes:

```text
python "<skill-root>/scripts/adopt_project_agents.py" inspect --target "<target-root>"
```

Automatic discovery covers the four supported native Agent directories and project `.codex/config.toml` role `config_file` references, resolved relative to the declaring config. The inventory deduplicates matching discoveries and reports conflicting identities, unsafe paths and unavailable files; it never reads outside the target. Fileless Codex roles appear in `role_declarations`: assess their declaration and inherited settings without requiring file-backed conversion. Explicit invalid references remain issues. Inspect other enabled host discovery mechanisms manually; user configuration and unsupported layouts are outside automatic coverage. Unsupported layouts need host-owner correction or a source-preserving relocation. See the [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) for native role semantics.

Read every custom Agent's complete prompt and configuration, including undeclared Agents; distinguish recorded plugin defaults under Ownership. Match identities by responsibility and references, preserving tools, permissions, sandbox boundaries, host metadata and intentionally inherited settings.

Assess model and reasoning settings on every full run using current official provider/host information and available model evidence. Choose a usable successor suited to the same responsibility and cost/latency class with compatible reasoning settings. Ask before crossing a model tier, materially increasing cost or changing an explicit project choice. When availability cannot be verified, retain the values, report incomplete assessment and continue independent work. Evidence that a model is unusable pauses that Agent until a supported choice is settled; a new release alone does not require migration.

Use Ownership's `native_source` route when retaining a complete native document. An inventory item marked `requires_relocation` needs an explicit source-preserving relocation before adoption: resolve the active host reference and keep relative prompt/config references meaningful at the installed location. Copying a file alone does not redirect the host.

For first adoption, prepare complete final native content and a manifest from the inventory's captured hashes. Explain model changes and preservation of other behavior, then use the guarded import in any maintenance mode:

```text
python "<skill-root>/scripts/adopt_project_agents.py" apply --help
python "<skill-root>/scripts/adopt_project_agents.py" apply --target "<target-root>" --manifest "<adoption-plan.json>"
```

In repository mode, the guarded import first saves accepted canonical native sources and portable Agent declarations in the selected source entry, then applies its existing protected target transaction and records the applied source. Its inventory, hash and ownership guards remain required. Preserve saved source work and report target recovery independently if that transaction fails.

For managed adapters, edit their selected canonical sources; full setup renders them under existing digest protection. Resolve source and setting ownership before converting structured declarations. The helper neither chooses models nor certifies semantic preservation.

For conflicts, show the paths, fields and values, effects of the alternatives and needed decision. Preserve conflicting inputs and continue independent inspection. Continue to freezing only when every custom Agent is mapped and accounted for, reported issues are resolved, and model changes, retentions and incomplete verification are distinguished. An omitted Agent or unresolved conflict cannot count as completion.

## 4. Prepare CodeGraph and start one frozen session

After target, active harness and input decisions are settled, establish the protocol's CodeGraph effect authority and prepare the runtime before freezing:

```text
python "<skill-root>/scripts/workflow.py" setup-codegraph --target "<target-root>" --harness "<active-harness>" --approved
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

Run `start` only after preparation returns exit 0, `phase: setup-codegraph` and `ready: true`. Retain the session, request and source/version/migration provenance returned by `start`. Read selected migration guides from that source; verify the complete blueprint request against accepted project and Agent decisions. A newly required input correction follows the protocol's cancel-and-restart rule.

Continue only with verified runtime readiness, a valid full request and source-specific prerequisites settled.

## 5. Plan the complete generated set

Read [Generated Authoring](references/generated-authoring.md). From the frozen source, read every requested blueprint and its refresh focus, together with complete existing content and qualified project evidence. Plan responsibilities, coverage and loading across generated and retained Rules, relevant Skills and applicable global policy.

For every request, identify what remains valid, what must change and why. Preserve project obligations and consequential exceptions; repair stale facts and genuine duplication. Neither fingerprint changes nor stylistic novelty justify rewriting. Continue when every request has a justified direction, evidence and place in the whole-set plan.

## 6. Obtain and reconcile complete writer results

Save the resolved common plan in the private session outside `GENERATED`, including qualified evidence references and owner-dependency state. Prepare inputs using the live session:

```text
python "<skill-root>/scripts/workflow.py" writer-inputs --help
python "<skill-root>/scripts/workflow.py" writer-inputs --session "<SESSION>" --plan "<SESSION>/common-plan.md"
```

Follow Generated Authoring to invoke the pinned public writer for one Candidate per request and reconcile the combined results. The bundle supplies evidence, not a semantic handoff. Continue only when every request, including unchanged artifacts and their supporting outputs, has its final individual `COMPLETE` and the whole set satisfies the plan. Corrections, blocked writing and dependencies follow that reference's registration and cancellation boundaries.

## 7. Register and finish

Register each reconciled handoff once, listing its complete outputs. The command help supplies path syntax:

```text
python "<skill-root>/scripts/workflow.py" register --help
python "<skill-root>/scripts/workflow.py" register --session "<SESSION>" --request-id "<ID>" --output "<PATH>"
python "<skill-root>/scripts/workflow.py" finish --session "<SESSION>"
```

Before the first `finish` attempt, confirm CodeGraph readiness and follow the protocol's runtime-refresh branch if its daemon idle-exited. In repository mode, finish saves accepted generated project sources to the entry before applying the ordinary target plan; preserve both source and target evidence if either part fails. Accept only the protocol's successful local finish result, including cleanup and the final setup-version record, before proceeding to publication. A failed finish blocks this operation's publication and follows the original-attempt recovery route.

## 8. Publish and hand off the verified result

After successful local finish, complete repository-mode publication under [Publish an exact verified scope](../maintain-project-config/references/maintenance.md#publish-an-exact-verified-scope). That contract governs the accepted scope, required checks, publication exceptions, normal push verification and retained-commit recovery. Neither local maintenance mode has a configuration-repository push. Use the supported command directly, without invoking the user-only maintenance Skill:

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/manifest.json" --path "projects/<entry>/files/.agents/rules/example.md" --message "Set up project configuration"
```

Replace the example paths with the complete exact accepted source-file scope retained through this setup; repeat `--path` for each file. A verified retained commit uses the command's `--commit` route and the shared recovery contract instead. Confirm the remote result before reporting repository-mode completion. A publication failure preserves the successful local `setupVersion` and requires reporting local setup success with incomplete remote synchronization.

Assess the complete direct project Rule set's always-loaded context cost. Recommend native `rule-<domain>` Skills only for substantial policy conditional on identifiable cases; size alone does not justify moving unconditional policy.

Report the configuration maintenance mode and repository source entry when applicable, SmartKit source provenance, previous and resulting setup versions, migrations, enabled hosts, changed/preserved paths, custom Agent/model decisions and external provenance. Include actual configuration checks, Git exclusion results and already tracked paths, CodeGraph installation/index/runtime results, context assessment, incomplete verification and recovery evidence.

Report local setup and remote publication separately, including the exact saved source scope, local finish evidence, and verified remote result or the shared contract's applicable publication exception. Distinguish a failed required publication from intentional local-result deferral or a setup with neither owned source changes nor a retained verified commit to publish; preserve saved source and retained commits for recovery.

## Local synchronization

Use `<maintain>` from the loaded plugin and read its [Project Configuration Maintenance](../maintain-project-config/references/maintenance.md) reference before synchronization. These commands use the maintenance-owned engine; setup's `project-config`, `sync-project` and `sync-project-rules` workflow phases remain forwarding entry points to that same owner. This route performs no fetch, generation, model assessment, blueprint/shared/external refresh or CodeGraph preparation. Ownership defines the prerequisites and retained boundaries; `clean` establishes configuration convergence only.

1. Check the requested scope:

   ```text
   python "<maintain>" sync-project --target "<target-root>" --check
   ```

   Broad sync requires established project-mapping ownership and unchanged external Skill declarations. Report a full-setup dependency without widening the request. For the Rule index alone, use `sync-project-rules --check`; it is available before full setup.

2. Apply the authorized scope by omitting `--check`. The Rule-index route is:

   ```text
   python "<maintain>" sync-project-rules --target "<target-root>" --check
   python "<maintain>" sync-project-rules --target "<target-root>"
   ```

   Keep exclusive access through apply and rollback. Exit 0 with `check: clean` establishes convergence; exit 1 with `check: drift` lists proposed changes; exit 2 is refusal or failure. Resolve reported causes before retrying.

3. Report operation, result, changed/preserved paths and any refusal or recovery evidence. Neither local route advances `setupVersion`.
