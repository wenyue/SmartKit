# Transfer Mechanism

The route owns B/S/W judgment, acceptance and behavioral verification. These helpers supply
observations, capability checks and guarded mechanics. Read **Read-only evidence** whenever selecting
that helper for any route. For the helper used by [Transfer Back to a Checkout](return-for-review.md),
also read **Batch transfer mechanism**. Read **Partial file transfer** before recovering an
interrupted or partially applied transfer.

## Read-only evidence

Probe the CLI before use:

```text
python "<skill-root>/scripts/worktree_evidence.py" --help
python "<skill-root>/scripts/worktree_evidence.py" snapshot --repository "<physical-checkout>" --path "<relative-file>" > "<external-snapshot.json>"
python "<skill-root>/scripts/worktree_evidence.py" compare --snapshot "<external-snapshot.json>"
```

`snapshot` emits JSON to stdout; preserve UTF-8 JSON when saving it externally. `compare` reads that
snapshot. Neither operation writes Git or working-file state. Repeat `--path` for the actual
dependency set; a directory recurses within that scope. With no paths, the snapshot covers only the
repository/HEAD/index boundary. Use `--inventory` when an effect, such as removal, needs all working
files, ignored contents and global Git status. Recapture older v1 evidence as v2 rather than silently
changing the scope being compared.

Every snapshot includes physical worktree/Git identities, registration, HEAD/ref and hashes of the
complete raw index and its split-index dependency. Bounded snapshots avoid global status and
unrelated working contents. Scoped observations cover absence, type, mode, content hash, symlink
target and ancestor identity. Preservation may also depend on security, ownership and relevant
attributes: bytes and modes alone do not prove those unchanged. Establish the required evidence
through capability checks before dependent effects. Nested repositories, including ancestor
crossings, submodules, symlink ancestors and physical file aliases need separately owned evidence.

Two observations detect instability before a snapshot is returned. Compare uses the recorded scope:
exit 0 means equal, 1 means drift, and 2 means invalid input or failed observation. These observations
are neither a lock nor a raw-content backup, ownership decision or semantic proof. They do not
promise a globally atomic snapshot, detect changes reverted between observations or establish remote
state.

## Batch transfer mechanism

### Admit the boundary before preparing

```text
python "<skill-root>/scripts/worktree_transfer.py" --help
```

Use a new physical operation directory outside the source, target and their Git directories, on the
same filesystem as destination parents. Retain it with the source until the transfer's user-acceptance
condition is met.

The helper admits regular-file create/update/delete in existing real directories. Its implementation
owns host-specific capability and metadata checks for target paths, operation storage and every
produced or consumed artifact. Those checks must establish required preservation of content,
security, ownership, attributes and identity before a dependent effect. Capability rejection stops
that effect; return to the owning workflow or another already authorized mechanism with the same
preservation contract.

Directory creation, rename resolution, ownership/security migration and semantic merging are outside
this mechanism. Keep the intended observation and write boundary intact across aliases and indirect
paths. Readable bytes do not make unsupported types, metadata or access safe to treat as ordinary
files.

### Describe the accepted outputs

Prepare a JSON plan with schema `smartkit.worktree-transfer/v1`:

| Field | Accepted input |
| --- | --- |
| `repository` | Absolute physical target checkout root. |
| `source` | Bounded v2 evidence covering every changed S path, from a distinct checkout in the same common repository. |
| `baseline` | Exact immutable shared B commit OID, an ancestor of both observed heads. |
| `authority`, `owner` | Accepted-request reference and continuation owner, recording authority already established by the Agent. |
| `changes` | Nonempty list sorted by unique normalized relative `path`; each entry contains `before`, `after` and `output`. |

The helper's baseline admission is narrower than the route's general commit/tree description of B.
Use the helper only when this admission holds; do not substitute a different baseline to pass it.
Neither the plan nor the helper grants authority or proves the semantics of B → S and compatible W
changes.

`before` is the exact W file-state object from bounded evidence. `after` describes the accepted
output: a regular file has `type`, integer `mode`, `size`, `sha256` and observed `uid`/`gid`; absence
is `{"type":"absent"}`. A file's `output` is an absolute physical path to prepared contents outside
affected worktrees, or to the corresponding accepted source file itself. Direct source output must
match S. Deletion uses null `output`. Preserve target permission details unless the accepted change
intentionally changes them.

### Prepare, apply and inspect one attempt

```text
python "<skill-root>/scripts/worktree_transfer.py" prepare --plan "<external-plan.json>" --operation "<new-operation-directory>"
python "<skill-root>/scripts/worktree_transfer.py" apply --operation "<operation-directory>"
python "<skill-root>/scripts/worktree_transfer.py" inspect --operation "<operation-directory>"
```

`prepare` freezes all accepted outputs, pending write copies and readable backups. Its `receipt.json`
records pre-state, authority, owner and retention condition. Drift in the target or accepted inputs,
or an unsupported boundary, prevents application. Preparation can leave external artifacts even
when target files remain untouched; retain and account for them if preparation fails.

`apply` accepts only the original prepared attempt. It verifies shared dependencies and artifacts at
entry, uses path/ancestor/output guards within the batch, and proves complete HEAD/index and output
preservation at exit. It does not stage, commit, delete backups or run project verification.
Identical before/after entries require no working-file write. Whole-repository observations are
independent of file count; bounded file work scales with affected paths.

The receipt records an in-flight child before its write and the attributable result afterward.
Interruption or failure may leave partial content, a newly created path or a retained original
object. Keep that state and its causal record. The batch is not atomic. A cooperative operation
lock prevents concurrent helper invocations from applying the same attempt, but cannot exclude
arbitrary external writers. Persistent evidence supports observing and recovering effects without
a promise of universal power-loss durability.

`inspect` is read-only. It reports boundary preservation, each path as before/after/both/other,
receipt phase and any in-flight child or lock. After a missing response, inspect instead of applying
again. Helper phases report mechanical progress, not the Skill's public classification or the
result of behavioral verification.

### Recover only attributable partial writes

Before recovery, establish that the original process has stopped:

```text
python "<skill-root>/scripts/worktree_transfer.py" recover --operation "<operation-directory>" --quiescent
```

`--quiescent` records that established fact and permits replacing a stale operation lock; elapsed
time alone does not establish it. Recovery preserves the original error and restores only recorded
writes still matching the attempt. Drift or ambiguous in-flight work stops restoration. A fully
applied candidate remains reviewable, including after failed verification.

An unresolved receipt, partial preparation or unsafe restoration leaves backups, retained originals
and other artifacts with the named owner under the transfer's acceptance condition. Successful CLI
operations exit 0; rejection or error exits 2 with the operation location. Re-observe receipt and
files before mapping the result to public phases: target files being unchanged alone does not prove
that the entire attempt was effect-free.

## Partial file transfer

Keep the source snapshot, readable external backups and retained original objects under the
[transfer's user-acceptance requirement](return-for-review.md#apply-with-preservation-evidence).
Observe the exact written set and current state before considering restoration. Restore only writes
attributable to this attempt whose current state still matches the recorded output, including
content, type, mode, absence and any identity or metadata needed for preservation.

Check affected ancestors and verify each consumed backup or retained original against frozen
pre-state before writing. Recovery must neither overwrite changed content, security, ownership or
other relevant metadata nor carry such changes back into the target. Mismatch or ambiguity retains
the partial target and recovery artifacts for their owner. Bounded restoration is a separately
recorded effect within the accepted transfer's recovery authority; broader changes need their own
authority.

When the whole transfer applied and later verification failed, keep the reviewable combined state
and failure evidence. Restoration cannot erase that failed result. No recovery moves target HEAD,
changes its index or resets unrelated state.
