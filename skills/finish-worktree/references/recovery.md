# Evidence and Recovery

For shared recovery, read **Operation receipt** and **Resume the incomplete effect**. Read
**Partial file transfer** and **Batch transfer mechanism** only for `return-for-review`; read
**Read-only evidence** only when selecting that helper. These mechanism sections are conditional,
not prerequisites for publication, history preparation, integration or discard.

## Operation receipt

Before a state-changing effect, persist a small receipt outside every affected worktree. Use an
existing workflow record when it can survive removal of those worktrees; no new service or generic
workflow framework is needed. Record the job and selected route, source/target identities, accepted
authority, pre-state, intended effect, and the causal attempt identity. Append observations and any
residual state, with its continuation owner and retention/release condition. Include exact OIDs,
paths and host identities needed to distinguish completion from partial work. Store backups
separately when hashes alone cannot recover content.

One attempt groups operations that share one retry/recovery decision: a guarded file batch or the
history helper is one attempt; a push, PR creation and later removal are separate attempts. Record
child effects only as needed to identify completed, absent, in-flight or ambiguous work. Keep the
receipt current before starting the next dependent effect so a missing final response does not
make a completed push, merge or deletion disappear.

## Resume the incomplete effect

Re-observe through the authoritative Git/filesystem/host interface before any retry. Reconcile the
receipt with current facts: retain proven prefixes, prove an effect absent before attempting it,
and resume only the original incomplete suffix under still-valid authority and preconditions.
An ambiguous outcome remains unresolved while observation is unavailable. Never repeat a merge or
PR creation from a timeout or missing response alone. A proven push followed by PR failure resumes
PR establishment; a proven delivery followed by cleanup failure resumes cleanup.

A guard rejection is `stopped` only when observation proves the phase attempt effect-free. Any
partial effect, ambiguity or failed post-effect proof is `failed`. A later recovery record may
resolve uncertainty and support continuation, but retains the original cause and observations.
Preserve independently proven phase results and publication even when another phase cannot finish.

## Partial file transfer

Retain the source snapshot, readable external backups and any retained original objects under the
[transfer's user-acceptance requirement](return-for-review.md#apply-with-preservation-evidence).
On partial application, observe the exact written set and current state before considering
restoration. Restore only writes attributable to this attempt whose current state still matches its
recorded output, including content, type, mode, absence and any identity or metadata on which
preservation depends. Check affected ancestors and verify each consumed backup or retained original
against its frozen pre-state before a dependent write. Changed content, security, ownership or other
relevant metadata must not be overwritten or carried back into the target by recovery. A mismatch
or ambiguous write retains the partial target and recovery artifacts for their owner. Bounded
restoration is a separate recorded effect under the accepted transfer's recovery authority;
broader changes need their own authority.

If the whole transfer applied and its later verification failed, retain that reviewable combined
state and failure evidence. Restoration is not a way to erase the failed result. No recovery moves
target HEAD, changes its index or resets unrelated state.

## Read-only evidence

Probe `python "<skill-root>/scripts/worktree_evidence.py" --help` before use.
Snapshot writes JSON to stdout; compare reads an external snapshot. Neither command writes Git or
working-file state. Preserve the snapshot's UTF-8 JSON when redirecting stdout.

```text
python "<skill-root>/scripts/worktree_evidence.py" snapshot --repository "<physical-checkout>" --path "<relative-file>" > "<external-snapshot.json>"
python "<skill-root>/scripts/worktree_evidence.py" compare --snapshot "<external-snapshot.json>"
```

Repeat `--path` for the dependency set. With no paths, snapshot captures only repository/HEAD/index
boundary evidence. `--inventory` explicitly adds all working files, ignored contents and global Git
status; use it when retention, removal or another effect actually needs that inventory. A directory
path recurses within that scope. These are v2 snapshots; recapture older v1 evidence instead of
silently changing the scope of its comparison.

Every snapshot includes physical worktree/Git identities, registration, HEAD/ref, and hashes of the
complete raw index and split-index dependency. Bounded snapshots omit global status and do not read
unrelated working contents. Scoped paths include absence/type/mode/content hashes, symlink targets
and ancestor identities. Required preservation evidence also covers security, ownership and relevant
attributes where those could be affected; byte/mode equality alone is insufficient. The helper's
capability checks must establish that evidence before dependent effects. Nested repositories,
including ancestor crossings, submodules, symlink ancestors and physical file aliases require
separately owned evidence.

Snapshot takes two observations and rejects detected instability. Compare repeats the recorded
scope: exit 0 means equal, 1 means drift, and 2 means invalid input or failed observation. Evidence
is not a lock, raw-content backup, ownership judgment or semantic proof. It cannot guarantee a
globally atomic snapshot, detect edits reverted between observations, or establish remote state.

## Batch transfer mechanism

The bounded interface of `scripts/worktree_transfer.py` is `prepare`, `apply`, `inspect`, and `recover`;
probe `python "<skill-root>/scripts/worktree_transfer.py" --help` before use.
Use one new physical operation directory outside source, target and their
Git directories, on the same filesystem as destination parents. Keep that directory with the source
until the transfer's user-acceptance condition is met.

The helper handles admitted regular-file create/update/delete operations in existing real
directories. Its implementation owns host-specific capability and metadata checks. Use it only when
those checks establish the required content, security, ownership, attributes and identity
preservation for target paths, operation storage and every produced or consumed artifact. Capability
rejection stops the dependent effect; it is not permission to bypass a guard. Return unsupported
cases to their owning workflow, or use an already authorized mechanism that establishes the same
preservation contract.

Directory creation, rename resolution, ownership/security migration and semantic merging remain
outside this task-file mechanism. Preserve the intended observation and write boundary across path
aliases and indirect paths; unsupported types, metadata or access cannot be treated as ordinary
files merely because their bytes can be read.

Prepare one JSON plan with schema `smartkit.worktree-transfer/v1`:

| Field | Accepted input |
| --- | --- |
| `repository` | Absolute physical target checkout root. |
| `source` | A bounded v2 evidence snapshot covering every changed S path, in a distinct checkout of the same common repository. |
| `baseline` | Exact immutable shared B commit OID, an ancestor of both observed heads. |
| `authority`, `owner` | Accepted-request reference and continuation owner. These record Agent-established authority; the helper cannot grant it. |
| `changes` | A nonempty list sorted by unique normalized relative `path`. Each entry carries `before`, `after`, and `output`. |

`before` is that path's exact W file-state object from bounded evidence. `after` is the exact accepted
output file-state object: ordinary files carry `type`, `mode` as a JSON integer, `size`, `sha256`, and observed `uid`/`gid`;
absence is `{"type":"absent"}`. For a file, `output` is the absolute physical path to its prepared
contents outside affected worktrees, or the corresponding accepted source file itself. A direct
source output must match S. For deletion, `output` is null. Preserve target permission details unless
the accepted change intentionally alters them. The Agent establishes that each entry is part of
B → S and that combined outputs preserve compatible W changes; this manifest is no semantic bypass.

```text
python "<skill-root>/scripts/worktree_transfer.py" prepare --plan "<external-plan.json>" --operation "<new-operation-directory>"
python "<skill-root>/scripts/worktree_transfer.py" apply --operation "<operation-directory>"
python "<skill-root>/scripts/worktree_transfer.py" inspect --operation "<operation-directory>"
```

`prepare` freezes all accepted outputs, pending write copies and readable backups, and writes
`receipt.json` with pre-state, authority, owner and retention condition. Target drift, changed
accepted inputs or unsupported boundaries prevent application. `apply` admits only that prepared
attempt, verifies artifacts and shared dependencies once at entry, uses path/ancestor/output guards
inside the batch, and proves complete HEAD/index and output preservation at exit. It never stages,
commits, deletes backups or runs project verification. Identical before/after entries require no
working-file write. Whole-repository observations are independent of file count; bounded file work
scales with the affected paths.

The receipt records an in-flight child before writing and its attributable result afterward. A
failed or interrupted operation may leave partial content, a newly created path or a retained
original object; preserve that actual state and its causal record. The batch is not atomic. A
cooperative operation lock prevents two helper invocations from applying the same attempt together;
it does not exclude arbitrary external writers. The mechanism must keep enough persistent evidence
to observe and recover its effects, without promising universal power-loss durability.
`inspect` is read-only and reports boundary preservation, each path as before/after/both/other, the
receipt phase, and any in-flight child or lock. A missing success response requires this observation,
not another apply. Helper phases describe mechanical progress, not the Skill's public classification
or behavioral verification result.

For a partial attempt, establish that the original process has stopped before invoking:

```text
python "<skill-root>/scripts/worktree_transfer.py" recover --operation "<operation-directory>" --quiescent
```

`--quiescent` records the caller's established process fact; it permits replacing a stale operation
lock and must never be guessed from elapsed time. Recovery preserves the original error, restores
only recorded writes still matching this attempt, and stops on drift or ambiguous in-flight work.
A fully applied candidate stays reviewable, including after failed verification. An unresolved
receipt, partial preparation or unsafe restoration retains its backups, retained originals and other
artifacts for the named owner under the transfer's acceptance condition.
Every successful command exits 0; rejection/error exits 2 with its operation location. Re-observe
the receipt and files to distinguish effect-free rejection from partial failure before translating
the result into the public phase contract.
