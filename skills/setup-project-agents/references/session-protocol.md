# Full session protocol

## Preflight

Resolve only material choices that affect shipped defaults, project-owned inputs, or authorized
effects. Prefer qualified repository evidence and ask only about genuinely unresolved choices.

`start` checks the project-owned Matt context. If it reports incomplete setup, end this invocation
and ask the user to invoke `setup-matt-pocock-skills` in the target; begin a fresh invocation after
that workflow finishes. Setup neither creates nor owns that context.

Before each effect, establish that accepted session intent authorizes it: private system-temporary
storage, one read-only fetch of canonical SmartKit `master`, configured external Skill fetches,
generated authoring, and the target mutations. These are distinct grants; accepted setup intent may
already supply them. Ask only for a missing grant, without repeating confirmations already settled.
Downstream effects of generated authoring still need their own authority.

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

Start one private session through the public `scripts/workflow.py` entry:

```text
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

The session operations are `start`, `register`, `finish`, and `cancel`. Use each command’s `--help`
for arguments; `sync-project` and `sync-project-rules` are separate local operations.

Stop on a nonzero result. Record `session` as `SESSION`, `generated` as `GENERATED`, and the returned
`request`, `source_root`, `source_commit`, and `source_fingerprint`. The request freezes setup
inputs, external snapshots, the generation requests, and source and setup-relevant target
fingerprints. The target fingerprint covers only evidence setup consumes: project setup config,
ownership and managed assets, generated destinations, project Rule metadata, project Agent sources,
and touched native host configuration. Git history and index state, caches, logs, and other
project-owned work remain outside it.
The public launcher rejects a pinned source that does not request every current catalog contract.
Confirm the returned request matches accepted intent before authoring. A canonical run is pinned to
its commit and fingerprint; an installed fallback is identified by its root, null commit, and fingerprint.

Keep exactly this private session until one `finish` or `cancel`. Treat the request and source as
immutable. If another operation holds the session claim, preserve the session and stop. Any target change after
`start` within the frozen setup-relevant surface—including a separately authorized authoring effect
on that surface—ends this session: cancel it and restart from the resulting accepted target state.
Changes outside that surface do not restart generation; preserve them as unrelated state. This
keeps authoring effects under their own grant instead of silently incorporating them into setup.

## Finish once

After every request has its final registered outputs, run `finish` once:

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
failure evidence. Report the target and exact residual session path for recovery. Resolve the
original cause and any verified workflow-owned residue under appropriate recovery authority before starting a fresh session.
Keep cleanup limited to verified workflow-owned residue.
