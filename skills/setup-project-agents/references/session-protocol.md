# Full Session Protocol

Full setup owns one immutable private session from source selection through registration, ending with one terminal `finish` or `cancel`. Explicit local synchronization does not enter this protocol.

## Preflight

Resolve material project-input choices and effect authority before dependent work. Accepted setup intent may already authorize effects; do not repeat settled confirmations.

Private system-temporary storage, one read-only canonical SmartKit `master` fetch, configured external Skill fetches, CodeGraph installation and target-local runtime preparation, generated authoring and target mutations are distinct grants. Setup alone does not authorize commit, push, release, unrelated dependency installation or downstream effects of generated authoring. An explicit maintenance-and-sync operation can delegate necessary full setup under its existing scope, then consume the local finish result for its separately owned scoped commit and normal push.

`start` requires project-owned Matt context. If incomplete, end this invocation and ask the user to invoke `setup-matt-pocock-skills` in the target; start a fresh setup invocation after it completes. Setup neither creates nor owns that context.

Prepare CodeGraph before `start` using `setup-codegraph` for the accepted target and active harness. Its `--approved` flag records existing authority for installation, indexing and startup; it does not create authority or require renewed consent. Readiness requires installation, a usable target index and an actually responsive runtime. Preserve existing data and independently owned host configuration; an obsolete or incomplete index needs separate repair. Use this scoped route instead of a broad host installer. Failed preparation leaves full setup incomplete, even when local progress remains.

### Source selection

Distinguish the selected SmartKit implementation source below from the project configuration authoring source. Repository-mode configuration uses authenticated GitHub/Git access and a persistent working copy under the shared [Project Configuration Maintenance](../../../runtime/project_config/maintenance.md) contract. Resolve and apply accepted input changes before freezing. That working copy can hold unique unpublished work and never belongs to private-session cleanup.

SmartKit and external Skill snapshot fetches contact only declared repositories and may create/remove private temporary checkouts. They run non-interactively without ambient Git configuration, credential helpers, proxies, SSH or askpass state. If the canonical fetch is unavailable, `start` may use the validated installed plugin root and reports a null `source_commit`; external sources retain their own network prerequisites.

The selected source requires the public launcher to support live CodeGraph verification, private-session cleanup and final `setupVersion` commit before preparation or mutation. Fetching a newer source does not upgrade the launcher. If compatibility is rejected, end the invocation, update the installed plugin and start fresh. Other source/schema/external-input rejection likewise requires correction within accepted authority and a fresh invocation.

## Start one frozen session

```text
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

Stop on nonzero status. Retain `session` as `SESSION`, `generated` as `GENERATED`, and the returned request, `source_root`, `source_commit`, `source_fingerprint`, setup versions and selected migrations. Confirm the complete blueprint request against accepted intent; read selected guides from that source before authoring.

The canonical source is pinned by commit and fingerprint; an installed fallback by root, null commit and fingerprint. Keep source and request immutable. The session commands are `writer-inputs`, `register`, `finish` and `cancel`; [Generated Authoring](generated-authoring.md) owns writer and registration order. Inspect each command's `--help` when needed. `inspect`, `setup-codegraph` and local synchronization are separate operations.

### Distinguish frozen setup evidence from unrelated work

The request freezes setup inputs, external snapshots, generation requests and source evidence. In repository mode, preserve the selected configuration-source identity and evidence alongside the target freeze; concurrent source changes require cancellation and a fresh assessment. Its target fingerprint covers consumed project config, ownership/managed assets, current and recorded generated Skill directories and destinations, project Rule and rule-led Skill metadata, project Agent sources, native Agent membership/content, project Codex declarations and in-target references, and touched native configuration.

Git history/index state, CodeGraph index/runtime state, caches, logs and unconsumed project work remain outside that boundary. Preserve unrelated changes. Any frozen-surface change after `start` ends the session, even if separately authorized: cancel and restart from accepted inputs. Setup-relevant changes made during runtime preparation therefore belong before `start`.

Keep the returned private session until its terminal operation. If another operation holds its claim, preserve it and stop rather than competing for the attempt.

## Finish once

After every request has its final registered outputs, confirm CodeGraph readiness. If the daemon idle-exited, rerun authorized `setup-codegraph` for the same target/harness before the first finish attempt. Runtime-only changes do not invalidate the freeze; setup-relevant changes do.

```text
python "<skill-root>/scripts/workflow.py" finish --session "<SESSION>"
```

Finish rechecks CodeGraph without preparing it, then validates complete outputs, frozen evidence and ownership. In repository mode it saves accepted generated project sources in the selected entry before the ordinary target application. It applies the target plan and checks convergence within the existing target rollback boundary. Source persistence, target application and remote publication are separate outcomes; target rollback does not imply that saved source work was discarded. Failed readiness prevents application and version advancement while normal session cleanup still applies.

The launcher removes the private session, then atomically records the source release as `setupVersion`, preserving other config values and refusing concurrent config drift. Success requires exit 0, `phase: finish`, `check: clean`, `codegraph.ready: true`, the reported successful setup version and completed cleanup. Configuration convergence alone is insufficient. CodeGraph preparation occurred outside this transaction and is not rolled back by a later setup failure. The resulting `setupVersion` records local full setup success even if a later authorized source push fails.

Keep exclusive access to planned target paths through apply and recovery. Guards cannot prevent an uncooperative writer from changing a path between check and mutation.

## Stop and recover

Before any finish attempt, unresolved declarations, ownership/digest conflicts, drift or blocked generation require cancellation:

```text
python "<skill-root>/scripts/workflow.py" cancel --session "<SESSION>"
```

Correct the cause through its owner before a fresh session. Cancel failure is terminal; report it unchanged.

After a pinned finish or transaction failure, preserve the primary error and any saved configuration-source changes. Report source persistence independently from target recovery.

For target application failures, preserve the primary error. Rollback attempts to restore pre-finish setup state; guards refuse rollback mutations over detected third-party changes. Report rollback failure and residual target state for inspection.

Finish attempts session cleanup even after failure. Failed cleanup reports the exact residual session; never reuse, finish or cancel it. Keep its claim/contents as evidence, resolve the cause and any verified workflow-owned residue under recovery authority, then start fresh. Limit cleanup to verified residue; target appearance proves neither success nor rollback.

Cleanup failure after configuration convergence leaves the previous `setupVersion`. Final version-commit failure may leave updated configuration and a removed session, while the guarded transaction retains or restores the prior baseline. Report failure and any rollback failure, preserve conflicting third-party changes, and use a fresh full session. Do not claim the earlier configuration transaction rolled back.
