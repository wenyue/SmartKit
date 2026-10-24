---
name: setup-project-agents
description: Initialize or upgrade project agent configuration, or update or restore local configuration from a configuration repository.
disable-model-invocation: true
---

# Setup Project Agents

Use this Skill only on the user's explicit invocation. Choose the requested outcome first: full setup, restoration from a configuration repository, or limited local synchronization. Each route owns different effects and completion conditions.

Full setup reassesses every declared blueprint and project custom Agent, including unchanged fingerprints, and prepares CodeGraph for the target. Restoration copies the accepted backup's bytes into the current project and checks this machine's prerequisites; it does not regenerate configuration.

## 1. Choose the requested operation

Resolve this directory as `<skill-root>`, its sibling maintenance entry `<skill-root>/../maintain-project-config/scripts/maintain.py` as `<maintain>`, and the business project as `<target-root>`. Read [Ownership](references/ownership.md) before the selected operation to establish canonical inputs and replacement boundaries. The catalog and schema define supported inputs; scripts validate and apply them. Setup chooses the operation, resolves project decisions, coordinates authors and checks that the resulting configuration works as a whole.

When the user has named an operation, follow it directly:

| Requested work | Route | Why this route fits |
| --- | --- | --- |
| Initialize, upgrade or migrate project configuration | Full setup, starting at step 2 | The request needs configuration reassessment and the full setup lifecycle. |
| Update or restore local configuration from a configuration repository | The restoration branch below | The request needs an existing backup applied to this project. |
| Synchronize local Rule/Skill discovery and declared Agent/MCP mappings only | Local synchronization | The request is limited to rendering established local inputs. |
| Update only the `AGENTS.md` Rule index | The narrower Rule-index branch under Local synchronization | Only the generated Rule list needs updating. |

Keep an operation already chosen in the conversation and any stated scope limit. Ask the user to choose an operation only when their request leaves that choice open.

### When the user has not chosen an operation

Establish local state before recommending one. Read [Project Configuration Maintenance](../maintain-project-config/references/maintenance.md) for binding, snapshot and local-receipt evidence, then run these read-only inspections before fetching sources or changing project inputs:

```text
python "<skill-root>/scripts/workflow.py" inspect --help
python "<skill-root>/scripts/workflow.py" inspect --target "<target-root>"
python "<maintain>" inspect --target "<target-root>"
```

Use the findings, existing managed content, and, where needed, `.agents/config.json`, `.agents/smartkit.lock.json`, and `.agents/project-config-sync.json` to answer two independent questions:

1. **Is the local managed configuration usable?** A fresh checkout may already have usable configuration. Checkout age, copied setup records and runtime readiness do not answer this question. If usability is uncertain, resolve only the facts needed to classify it.
2. **Is the backup source established?** Check that the binding has a matching local receipt recording successful application under the maintenance contract. A copied binding without that receipt is a source proposal to confirm with the user. It does not make otherwise usable local configuration unusable.

A lock or copied `setupVersion` alone does not prove successful setup on this checkout. Likewise, `automatic: false` alone does not establish whether a successful receipt exists. Unavailable source evidence means the source is still unknown; report the gap and leave only source-dependent decisions pending. Obtain missing source details from the user rather than guessing from business remotes or scanning known repositories or other checkouts.

Use those answers to present the applicable choices in the user's language:

| Situation | Choices to offer | Recommendation and reason |
| --- | --- | --- |
| Local managed configuration is usable, including in a fresh checkout | A. Upgrade or reassess it. Also offer B. Update or restore from the configuration repository when its binding is established or the user confirms its source. | Recommend A: there is existing configuration to reassess. Retain its maintenance choice. Confirm a copied binding before treating restoration as ready. |
| Local managed configuration is absent or established as unusable, and a confirmed source has an existing backup entry | A. Update or restore from the configuration repository. B. Initialize configuration. | Recommend A: the user already has configuration to reuse. Initialization remains available and preserves existing content under Ownership. |
| Local managed configuration is absent or established as unusable, and there is no known backup and no unresolved source evidence | A. Initialize configuration. B. I already have a configuration backup. | Recommend A. Choice B starts source confirmation; it does not claim a restoration is ready to run. |

Explain the effects before asking for the choice. Full setup reassesses configuration and prepares local CodeGraph. Restoration runs from **configuration repository → current project** and may add, overwrite or delete local files within the accepted snapshot's scope. Saving local changes back to that repository is a separate adoption/publication operation. For a known source, show available changed paths and say whether they come from the local snapshot; inspection without an update does not establish the remote's latest contents.

Wait for the user's operation choice, then continue that route without asking the same question again. This choice settles what to do. Source confirmation, acceptance of actual differences, maintenance mode and startup synchronization remain their own decisions where required; an operation recommendation settles none of them.

Inspection failures block only decisions that need the missing evidence. Report those gaps; restoration does not require entering full setup, Matt initialization or CodeGraph preparation. New checkouts invoke this Skill manually. Session hooks neither discover missing configuration nor ask to restore it; configuration startup handling serves only an explicitly enabled, valid existing checkout binding. Other readiness checks retain their owners.

## Update or restore local configuration from the configuration repository

Use this branch both to recover lost or changed local configuration and to apply configuration-repository changes, in new checkouts or already configured projects. Read [Project Configuration Maintenance](../maintain-project-config/references/maintenance.md) for binding, backup scope, restoration, Git exclusions and failure recovery. Use its supported commands directly without invoking the user-only maintenance Skill. This route needs neither full-session preflight nor Matt context, migrations, custom-Agent reassessment or generated authoring.

1. **Establish which backup to use.** Reuse still-current local findings from step 1 and inspect the selected checkout:

   ```text
   python "<maintain>" inspect --target "<target-root>"
   python "<maintain>" bind --help
   ```

   With an established binding and matching successful local receipt, reuse its repository address, branch and entry. With only a copied binding, ask the user to confirm that proposed source. With no binding, obtain the missing values from the user. Ask only about missing information, source confirmation or a requested source change; never infer a source from the business remote or scan known repositories.

   Verify that the entry exists and is the intended backup before binding it. A missing entry leaves restoration incomplete; creating a new backup would serve a different operation. Use the maintenance reference's repository `bind` route only when needed, preserving existing source and target work. A copied binding alone grants neither restoration nor automatic-sync authority.

2. **Show what applying that backup will change.** Update the bound source, then inspect the actual effects:

   ```text
   python "<maintain>" update --target "<target-root>"
   python "<maintain>" inspect --target "<target-root>"
   ```

   Authentication, fetch or update failure stops application. Retain existing state and report the cause. After a successful update, show differences for the selected complete files and directories, including additions, overwrites and deletions.

   When there are differences, pause the whole synchronization and offer **A. Keep local** or **B. Use the configuration repository**. This choice applies to every differing application, including changes made only in the repository. A ends this restoration as skipped, preserves target contents and the prior receipt, and leaves work requiring convergence pending. B applies the complete reviewed restoration with the exact inspection fingerprint passed through `--accept-existing`. Apply no partial selection while the choice is pending. If source and target already agree, no difference-acceptance token is needed.

   Explain that keeping local does not save those files back to the repository. Preserving an intended target edit there requires the maintenance owner's separately accepted adoption route. If either side changes after inspection, show the new differences and obtain a new choice before applying them; the earlier choice covered different contents.

3. **Set the separate startup preference and apply.** When no preference is recorded, offer A. Enable automatic startup synchronization; B. Disable it, with off as the default. Retain a recorded preference unless the user requests a change. Explain that enabling it permits source update and inspection at startup; differences still need the whole-synchronization choice above. This preference does not accept future overwrites.

   Apply with the recorded or newly accepted preference, adding `--accept-existing "<inspect-fingerprint>"` whenever differences were accepted:

   ```text
   python "<maintain>" apply --help
   python "<maintain>" apply --target "<target-root>" --auto-sync off
   python "<maintain>" inspect --target "<target-root>"
   ```

   Use the recorded or newly accepted value for `--auto-sync`. Verify source-target agreement, the target-local synchronization receipt and applicable Git exclusions through the shared reference's read-only Git checks. The result is the restored snapshot's bytes. Copied `setupVersion` or ownership records establish neither successful full setup nor runtime readiness for this checkout.

4. **Check whether this machine can use the restored configuration.** Use the owners' supported read-only checks for local tools, credentials and services. Report missing or unverifiable prerequisites without installing tools, starting services or rewriting the snapshot as part of restoration.

   Report the source, restored/preserved paths, synchronization preference, exclusions, actual prerequisite results and any failure or recovery evidence. Distinguish restored content from local readiness and explicitly state that full setup was not performed. Restoration neither generates configuration, records a new successful setup version, commits nor publishes source changes. A requested initialization or upgrade follows the separate full-setup route.

## 2. Establish project state and its maintenance mode

Full setup starts here after initialization, upgrade or migration has been selected. Read [Full Session Protocol](references/session-protocol.md) for effect authority, Matt context, SmartKit source selection and recovery; [Project Migrations](references/migrations.md) for baseline and release obligations; and [Project Configuration Maintenance](../maintain-project-config/references/maintenance.md) for configuration-source binding, private repository access, application and publication. Setup uses the maintenance reference, supported commands and configuration engine without invoking that user-only Skill.

Obtain both read-only inspections below. Reuse still-current results from operation selection, and refresh affected findings after inputs change. Command help explains the reported checks and exits:

```text
python "<skill-root>/scripts/workflow.py" inspect --help
python "<skill-root>/scripts/workflow.py" inspect --target "<target-root>"
python "<maintain>" inspect --target "<target-root>"
```

Read the findings alongside complete project configuration, ownership, existing generated content and decision records reached through the project's documentation conventions. Resolve prerequisite errors before their dependent step. Exit 0 from setup inspection still leaves its `pending_assessment` to Setup; it is not a completed assessment. Missing Matt context is completed below, within this invocation after the maintenance source is settled.

### Choose where configuration will be maintained

This decision is the same for first setup and upgrade. When inspection reports `selection_required`, ask once in the user's language and present all three choices together. Otherwise retain the recorded mode, repository, branch and entry. Existing `local` means Project shared; a missing maintenance declaration alone does not mean the project is new.

| Choice | What it does | Why choose it |
| --- | --- | --- |
| A. Project shared (`local`) | Keep canonical configuration in the business project for versioning with its repository. | The configuration belongs with the shared project. |
| B. This machine only (`local-only`) | Keep canonical configuration in the business project and locally exclude it from business Git. No GitHub source is needed. | The configuration should stay local to this machine. |
| C. Separate configuration repository (`repository`) | Maintain configuration in a personal private GitHub repository and locally exclude target configuration from business Git. | The configuration needs its own repository, separate from business-project history. |

Record a newly accepted choice through the maintenance command's `bind` route. Switch a recorded mode or entry only when the user requests it, after comparing and preserving old source and target work. Follow the maintenance reference for Git exclusions and already tracked files: choosing a mode does not itself untrack existing files.

For C, explain that full setup includes an exact scoped source commit and normal push after successful local finish, unless the user requests a local result. The shared publication contract governs that outcome; establishing a binding alone does not complete setup.

### Establish the source and account for existing work

For first setup, identify existing project instructions, personal configuration and independent owners before deciding what setup will manage. For an upgrade, establish the last successful setup version and collect every applicable migration without guessing missing history. An initialized project with no successful version keeps its ownership record and content while this full setup establishes the baseline.

Both local modes use the project's canonical inputs. In repository mode, establish the personal repository identity, branch and project entry. Connect an existing private repository, or create one only with the user's specified owner and name. Different projects may use separate entries in the same repository. Import only identified and accepted existing personal files; preserve tracked business-project content and independently owned configuration. Connecting an existing entry on another machine requires comparison with the current target before initial application.

Update the persistent repository source before editing it. If binding or earlier maintenance already refreshed it and produced accepted pending changes, verify and retain that evidence, then continue from those changes; another clean-checkout update would interrupt that accepted work. Assess migrations against both the business project and the selected source entry. Make repository-mode configuration corrections in that entry first, using the source paths reported by inspection and evidence from the business project.

Before applying repository files, follow the maintenance reference's full-file backup scope, target-local state boundaries and difference-acceptance contract. When source and target differ, show the actual differences, including changes made only in the repository, and offer **A. Keep local** or **B. Use the configuration repository** for the whole synchronization. A skips synchronization and leaves dependent full setup pending. B applies the complete reviewed result using its exact inspection fingerprint; changes on either side require inspection and a new choice. When both sides agree, no difference-acceptance token is needed. Saving intended target edits back to the source requires the separate accepted adoption route.

Apply accepted source changes through the maintenance command before freezing a session. Continue preparation when the maintenance choice is recorded, the source is available, and initial imports or collisions have accepted resolutions. Full setup completes only after applicable migrations, successful local finish and the publication outcome required by step 8.

### Choose automatic startup synchronization separately

Only repository mode has this preference. If none is recorded, offer **A. Enable** or **B. Disable**, default off. Explain that enabled startup synchronization updates and inspects the source; it still asks before applying any differences. Choosing a repository as the configuration source does not settle this separate preference.

After source refresh, inspection and resolution of differences, record a new or deliberately changed preference through the maintenance command's `apply --auto-sync on|off` route. Retain an existing preference during routine setup or upgrade; use an explicit flag only to establish or deliberately change it. Startup synchronization requires a valid existing checkout binding and matching successful local receipt as well as this opt-in.

### Complete missing Matt context

Once the maintenance choice, source and initial collisions are settled and accepted source changes are applied, rerun setup inspection and read its current `matt` result:

| Finding | Action | Reason |
| --- | --- | --- |
| Context is present | Preserve it and continue. | This prerequisite is already met. |
| Context is incomplete | Read and follow the complete shared reference at `<skill-root>/../setup-matt-pocock-skills/references/project-context.md` to initialize or supplement it within this invocation. | Full setup needs that project context before it can freeze the request. |
| The reference or a required resource is unavailable, a material choice is unresolved, or a required write is declined or fails | Report the gap and leave dependent full setup incomplete; continue independent inspection if useful. | The prerequisite has not been met. |

Use the reference directly without invoking the user-only Matt Skill. Reuse accepted project decisions, preserve existing content and obtain its draft acceptance for new or changed writes. Supply the business target for exploration and the authoritative output paths for writing: project canonical inputs in local modes, selected source copies in repository mode. Resolve any repository backup-scope addition under the maintenance contract, then apply accepted changes through its guarded route. Completing Matt context does not expand backup or replacement authority.

Reinspect after application and continue this same invocation once `matt.present` is true. Other findings keep their own readiness requirements. Restoration, local synchronization and Rule-index-only operations do not enter this prerequisite.

### Prepare the final inputs for the full run

Reconcile configuration under the schema identified in Ownership and preserve unrelated work. Edit the selected canonical inputs and apply accepted repository-source changes before `start`. Carry accepted initial imports and preparatory source changes, with their provenance, into final publication. On an unborn branch this includes the full accepted import, not only the later generated delta.

The project configuration source above is separate from the SmartKit implementation source. Preflight migrations come from the loaded plugin; step 4 confirms the SmartKit source selected for the session. Continue when project state, source choice, input decisions, migration requirements and prerequisite gaps are accounted for.

## 3. Discover and reconcile every project custom Agent

Use the preflight inventory; refresh it after project input changes:

```text
python "<skill-root>/scripts/adopt_project_agents.py" inspect --target "<target-root>"
```

Automatic discovery covers the four supported native Agent directories and project `.codex/config.toml` role `config_file` references, resolved relative to the declaring config. The inventory deduplicates matching discoveries and reports conflicting identities, unsafe paths, and unavailable files; it never reads outside the target.

Fileless Codex roles appear in `role_declarations`: assess their declaration and inherited settings without requiring file-backed conversion. Explicit invalid references remain issues. See the [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) for native role semantics.

Inspect other enabled host discovery mechanisms manually. User configuration and unsupported layouts are outside automatic coverage; unsupported layouts need host-owner correction or a source-preserving relocation.

Read every custom Agent's complete prompt and configuration, including undeclared Agents; distinguish recorded plugin defaults under Ownership. Match identities by responsibility and references, preserving tools, permissions, sandbox boundaries, host metadata and intentionally inherited settings.

Assess every Agent's model and reasoning settings on each full run, using current official provider/host information and available model evidence. A new release alone does not require migration. Use the following conditions to decide whether to retain a setting, select a successor or ask the user:

| Situation | Action or choice | Reason |
| --- | --- | --- |
| A successor is appropriate and verified usable within the same responsibility and cost/latency class | Choose it with compatible reasoning settings, unless this changes an explicit project choice. | The Agent should retain its role and operating trade-offs. |
| A proposed change crosses a model tier, materially increases cost or changes an explicit project choice | Explain the alternatives and effects, then ask the user before changing it. | This changes a decision the project owner needs to make. |
| Availability cannot be verified | Retain the values, report incomplete assessment and continue independent work. | Missing evidence does not justify replacing a setting. |
| Evidence shows the model is unusable | Pause that Agent until a supported choice is settled. | A known unusable model cannot count as a working Agent. |

Use Ownership's `native_source` route when retaining a complete native document. An inventory item marked `requires_relocation` needs an explicit source-preserving relocation before adoption: resolve the active host reference and keep relative prompt/config references meaningful at the installed location. Copying a file alone does not redirect the host.

For first adoption, prepare complete final native content and a manifest from the inventory's captured hashes. Explain model changes and preservation of other behavior, then use the guarded import in any maintenance mode:

```text
python "<skill-root>/scripts/adopt_project_agents.py" apply --help
python "<skill-root>/scripts/adopt_project_agents.py" apply --target "<target-root>" --manifest "<adoption-plan.json>"
```

In repository mode, the guarded import first saves accepted source and configuration changes in the selected source entry, then applies its existing protected target transaction and records the applied source. Its inventory, hash and ownership guards remain required. Preserve saved source work and report target recovery independently if that transaction fails.

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

Make the handoff easy to inspect across these concerns:

| Concern | Report |
| --- | --- |
| Source and scope | Maintenance mode and repository entry when applicable, SmartKit source provenance, previous/resulting setup versions, migrations, enabled hosts, changed/preserved paths, and external provenance. |
| Decisions | Custom Agent/model decisions and the direct Rule set's context assessment. |
| Verification and limitations | Actual configuration checks, Git exclusions and already tracked paths, CodeGraph installation/index/runtime results, incomplete verification, and recovery evidence. |

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
