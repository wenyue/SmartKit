# Persistence

Use this reference for recovery and failure decisions involving stored or serialized data. Ordinary I/O failure propagation needs no reconstruction policy; changing or discarding data does.

## Establish what may be recovered or lost

Identify the owner, the data's purpose, acceptable loss, and the valid state required by the accepted outcome. Establish whether recovery must change future reads and whether this boundary may mutate storage. A path, format, or finding of corruption supplies no authority to lose data.

| Data role | Establish before choosing recovery |
| --- | --- |
| Derived or cached | The rebuilding source, and whether absence is valid during rebuilding or after accepted discard. |
| Access or local state | The actor or service that recreates it, and the capability unavailable until then. |
| Defaultable state | Valid defaults and accepted loss of displaced choices or progress. |
| Important, user-authored, imported, or sole-copy data | An authoritative replacement or authority for the specific loss, plus a valid resulting state. Preserve the bytes while loss authority or resulting validity is unresolved. |
| Schema or migration metadata | How it controls retained-record interpretation and selection of required transitions. |

Prefer a direct reset, discard, or rebuild of the smallest invalid unit when that authority and resulting validity are established. Preserve other valid records. Add salvage, quarantine, or compatibility handling only when the data contract needs it. Carry unresolved material loss, ownership, or required-state decisions to their owner, preserving bytes whose loss is unauthorized.

Explain reconstruction assumptions and loss authority beside the recovery when code, types, and referenced contracts leave them unclear.

## Distinguish access, interpretation, and repair

Locate the failing phase: reading bytes, validating their syntax or meaning, applying required migrations, or executing repair. Valid syntax alone does not establish valid meaning. Failed access or an incomplete migration does not establish corrupt current-format content and must not trigger corruption-based deletion.

Treat migration metadata as part of the data interpretation contract. Replacing an invalid marker with a current version could falsely mark old records as migrated. Establish the prior version and apply the required transitions so retained records keep their meaning. Use the supported historical format and migration contract to distinguish older valid data from invalid current data.

A read-only library may fulfill its contract by skipping invalid records and returning an explicitly degraded result. Preserve the skipped-record impact and useful diagnostics for its caller, and verify that repeat reads behave as promised while the stored bytes remain unchanged. Recovery requires a persisted change only when the accepted promise requires it and the boundary has the necessary authority.

When the contract calls for persisted repair, verify the change and the next read. A usable default alone does not establish repair. For example, removing confirmed invalid sign-in data may restore a valid signed-out state when the data contract allows reconstruction through sign-in. Check removal and the next read if clean later reads are promised. If repair fails, carry the invalid-content cause, repair failure, and affected data or location to the final owner.

## Preserve the actual write promise

Await the writes, flushes, or commit acknowledgements required by the owning storage contract before reporting its promised completion. An in-memory update is not evidence of persistence; an awaited backend call establishes only that backend's documented guarantee.

Serialization of callers does not make several writes atomic. If rotating session metadata succeeds but clearing history fails, some reset effects remain. Preserve the known stored state and failed reset outcome; use the accepted repair or partial-completion contract rather than claiming rollback. Check the next read and any interrupted or failed write sequence that can change retained meaning.
