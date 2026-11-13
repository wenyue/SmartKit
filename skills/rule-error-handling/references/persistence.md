# Persistence

Ordinary I/O failure propagation needs no reconstruction policy; changing or discarding data does.

## Establish what may be recovered or lost

Establish what must survive, what may be lost, and a valid resulting state from the data's purpose and owning contract. Corruption or a writable path grants no deletion authority.

| Data role | Establish before choosing recovery |
| --- | --- |
| Derived or cached | A rebuilding source and whether temporary or lasting absence is valid. |
| Access or local state | Who or what recreates it, and the capability unavailable until then. |
| Defaultable state | Valid defaults and accepted loss of displaced choices or progress. |
| Important, user-authored, imported, or sole-copy data | An authoritative replacement or permission for the specific loss, and a valid result. Preserve bytes while loss authority or resulting validity is unresolved. |

Within those bounds, prefer resetting, discarding, or rebuilding the smallest invalid unit; preserve other valid records. Add salvage, quarantine, or compatibility handling only when the data contract needs it.

Explain reconstruction assumptions and loss authority beside recovery when they are otherwise unclear.

## Distinguish access, interpretation, and repair

Distinguish failure to read, validate, migrate, or repair. Failed access or incomplete migration does not establish invalid current-format content and must not trigger corruption-based deletion.

Use supported historical formats and required migrations to interpret older data. Migration metadata controls that interpretation: establish the prior version and required transitions before repairing an invalid marker. Simply marking old records current can silently change their meaning.

A read-only library may skip invalid records under an explicitly degraded-result contract. Preserve the skipped-record impact and diagnostics for its caller, and verify promised repeat-read behavior without changing stored bytes. Persisted repair is required only when the promise requires it and the boundary may mutate storage.

When persisted repair is required, verify the stored change and the next read; a usable default alone proves neither. If repair fails, carry the invalid-content cause, repair failure, and affected data or location to the final owner.

## Preserve the actual write promise

Await the writes, flushes, or commit acknowledgements the storage contract requires. An in-memory update proves no persistence; an awaited backend call establishes only its documented guarantee.

Serializing callers does not make several writes atomic. If replacing session metadata succeeds but clearing history fails, preserve the failed reset outcome and known remaining state. Use the accepted repair or partial-completion contract. Verify next reads after failed or interrupted write sequences that can change retained meaning.
