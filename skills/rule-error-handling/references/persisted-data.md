# Persisted Data

Use this reference before choosing, changing, or reviewing repair, reconstruction, discard, or degraded use of persistent or serialized data when authority, loss, later reads, or interpretation must be established. Ordinary I/O failure propagation alone needs no data-recovery decision.

## Establish what may be recovered or lost

Identify the owner, the data's purpose, acceptable loss, and the valid state required by the accepted outcome. Establish whether recovery must change future reads and whether this boundary may mutate storage. A path, format, or finding of corruption supplies no authority to lose data.

Use the data's role to identify the evidence that matters:

| Data role | Establish before choosing recovery |
| --- | --- |
| Derived or cached | The rebuilding source, and whether absence is valid during rebuilding or after accepted discard. |
| Access or local state | The actor or service that recreates it, and the capability unavailable until then. |
| Defaultable state | Valid defaults and accepted loss of displaced choices or progress. |
| Important, user-authored, imported, or sole-copy data | An authoritative replacement or authority for the specific loss, plus a valid resulting state. Preserve the bytes while loss authority or resulting validity is unresolved. |
| Schema or migration metadata | How it controls retained-record interpretation and selection of required transitions. |

The contract may support degradation, reconstruction, repair, or accepted discard. Exact reconstruction is unnecessary when another state fulfills the accepted contract. Carry unresolved material loss, ownership, or state decisions to their owner before dependent changes.

Explain reconstruction assumptions and loss authority beside the recovery when code, types, and referenced contracts leave them unclear.

## Distinguish a readable result from a persisted repair

Locate the failing phase: reading bytes, validating their syntax or meaning, or executing repair. Valid syntax alone does not establish valid meaning. Failed access and invalid content need to remain distinguishable through handling.

A read-only library may fulfill its contract by skipping invalid records and returning an explicitly degraded result. Preserve the skipped-record impact and useful diagnostics for its caller, and verify that repeat reads behave as promised while the stored bytes remain unchanged. Recovery requires a persisted change only when the accepted promise requires it and the boundary has the necessary authority.

For writable state, verify the particular repair rather than treating defaults as evidence of success. Suppose the parser establishes that saved sign-in state is invalid, the contract permits reconstruction through sign-in, and the application may remove the bytes. Discard can then be a supported repair. If it promises clean later reads, verify removal and the next read.

In this example, the operation that required authentication still reports it unavailable; restoring a valid signed-out state has not completed that operation.

## Preserve evidence and interpretation through repair

If repair fails, carry the invalid-content cause, repair failure, affected state, and actionable path to the final owner. A read-only store can prevent an otherwise authorized discard; returning defaults does not prove that repair established the intended state.

Any retry needs a condition that can change, safe repeated effects, and a stopping bound. Preserve sole-copy data when its loss is unauthorized, along with the failed outcome, while the owner resolves the disposition.

Treat migration metadata as part of the data interpretation contract. Replacing an invalid marker with a current version could falsely mark old records as migrated. Establish how the prior version is derived and missed transitions are performed, and verify that recovery preserves retained records' meaning.

Verify the responsible public operation's resulting state and repeat-read behavior. Include repair failure, asynchronous completion, interruption after partial writes, and other recovery effects where those paths exist. Apply the entry's recovery or remediation branch when the actual strategy also needs those constraints; persisted data alone creates no unconditional reference chain.
