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

Carry unresolved material loss, ownership, or required-state decisions to their owner. Preserve bytes whose loss is unauthorized.

Explain reconstruction assumptions and loss authority beside the recovery when code, types, and referenced contracts leave them unclear.

## Distinguish a readable result from a persisted repair

Locate the failing phase: reading bytes, validating their syntax or meaning, or executing repair. Valid syntax alone does not establish valid meaning. Failed access and invalid content need to remain distinguishable through handling.

A read-only library may fulfill its contract by skipping invalid records and returning an explicitly degraded result. Preserve the skipped-record impact and useful diagnostics for its caller, and verify that repeat reads behave as promised while the stored bytes remain unchanged. Recovery requires a persisted change only when the accepted promise requires it and the boundary has the necessary authority.

When the contract calls for persisted repair, verify the change and the next read. A usable default alone does not establish repair. For example, removing confirmed invalid sign-in data may restore a valid signed-out state when the data contract allows reconstruction through sign-in. Check removal and the next read if clean later reads are promised.

## Preserve the meaning of retained records

Treat migration metadata as part of the data interpretation contract. Replacing an invalid marker with a current version could falsely mark old records as migrated. Establish the prior version and apply the required transitions so retained records keep their meaning.

If repair fails, carry the invalid-content cause, the repair failure, and the affected data or location to the final owner.
