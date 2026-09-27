# Full Session Protocol

Read this before full setup. The public workflow owns one immutable private session from source
selection through registration and one terminal `finish` or `cancel`. Explicit local synchronization
uses separate commands and does not enter this protocol.

## Preflight

Resolve material choices affecting shipped defaults, project-owned inputs or effects. Use qualified
repository evidence and ask only for genuinely unresolved choices.

`start` checks project-owned Matt context. When it reports incomplete setup, end this invocation and
ask the user to invoke `setup-matt-pocock-skills` in the target. Begin a fresh setup invocation after
that workflow completes. Setup neither creates nor owns Matt context.

Before each effect, establish its authority: private system-temporary storage, one read-only fetch
of canonical SmartKit `master`, configured external Skill fetches, generated authoring and target
mutations are distinct grants. Accepted setup intent may already supply them; do not repeat settled
confirmations. Downstream effects of generated authoring still need their own authority. Stop before
any unauthorized effect.

Fetches contact only their declared repositories and may create and remove private temporary
checkouts. They run non-interactively without ambient Git configuration, credential helpers,
proxies, SSH or askpass state. These grants do not include dependency installation, publication,
Git-history changes or unrelated target writes. If the canonical fetch is unavailable, `start` may
use the validated installed plugin root and reports `source_commit: null`. Configured external
sources still need their own network authority.

Scripts validate external source declarations, licenses, Skill trees, names, destination collisions
and recorded tag stability before target mutation. If `start` rejects input or a source, correct the
reported cause within accepted authority and begin a fresh invocation.

## Start one frozen session

Use the public entry:

```text
python "<skill-root>/scripts/workflow.py" start --target "<target-root>"
```

The session commands are `start`, `register`, `finish` and `cancel`; inspect each command's `--help`
for its arguments. `sync-project` and `sync-project-rules` are separate local operations.

Stop on a nonzero result. Retain returned `session` as `SESSION`, `generated` as `GENERATED`, and
`request`, `source_root`, `source_commit` and `source_fingerprint`. The request freezes setup inputs,
external snapshots, generation requests, source evidence and setup-relevant target fingerprints.
The public launcher refuses a pinned source that does not request every current catalog blueprint.
Confirm the complete request against accepted intent before authoring.

A canonical source is pinned by commit and fingerprint. An installed fallback is identified by its
root, null commit and fingerprint. Keep this source and request immutable throughout the session.

### Distinguish frozen setup evidence from unrelated work

The target fingerprint covers evidence setup consumes: project setup config, ownership and managed
assets, generated destinations, project Rule and rule-led Skill metadata, project Agent sources and
touched native host configuration. Git history/index state, caches, logs and other project-owned
work are outside that boundary.

Any change after `start` inside the frozen setup-relevant surface ends the session, even when a
separate authoring grant authorized that change. Cancel and restart from the accepted resulting
target. Changes outside that surface do not restart generation; preserve them as unrelated state.
This keeps separately authorized effects from being silently absorbed into an old setup request.

Keep exactly the returned private session until its terminal operation. If another operation holds
the session claim, preserve it and stop rather than competing for the same attempt.

## Finish once

After every request has its final registered outputs, invoke:

```text
python "<skill-root>/scripts/workflow.py" finish --session "<SESSION>"
```

Finish validates complete outputs, frozen evidence, ownership and plan, then applies the plan and
clean postcondition within one rollback boundary. Keep exclusive access to every planned target
path through completion or failure handling. A filesystem check cannot prevent an uncooperative
writer from being overwritten between the check and mutation.

Success requires exit 0 and JSON containing `phase: finish` and `check: clean`, with the private
session removed as the completed transaction. Use the complete result; target convergence alone
cannot establish successful session cleanup.

## Stop and recover

When work stops after `start` but before any `finish` attempt, cancel:

```text
python "<skill-root>/scripts/workflow.py" cancel --session "<SESSION>"
```

Unresolved declarations, ownership/digest conflicts or setup-relevant target drift before finish
require cancellation and a fresh session after correction. A cancel failure is terminal; report it
unchanged.

After a pinned finish or transaction failure, preserve the original error. The transaction attempts
to restore pre-finish setup state. Its guards refuse rollback mutations when they detect concurrent
third-party changes; reported rollback failure identifies residual target state for human
inspection. Exclusive access remains necessary through recovery because a third-party writer can
still act between a rollback check and mutation.

Finish then attempts private-session cleanup. If cleanup fails, it must report the exact residual
session path. This can happen after target convergence or after a failed transaction; infer neither
a successful operation nor rollback from the target's appearance.

Never reuse, finish or cancel such a residual session. Keep its remaining claim or partial contents
as failure evidence, and report the target and exact session path. Resolve the original cause and
any verified workflow-owned residue under appropriate recovery authority before a fresh session.
Limit cleanup to that verified residue.
