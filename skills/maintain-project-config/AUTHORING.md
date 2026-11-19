# Authoring Decisions

## Use one entry for maintenance operations

Routine maintenance, Setup, enabled startup synchronization and OpenWiki use the same Skill entry so changes to the maintenance contract reach every caller. The entry selects only the requested operation. Callers retain authority over their workflow and effects, including full Setup's source-first order. Keep the common commands and their decisions here to avoid branches drifting into separate procedures.

## Preserve snapshots without claiming setup success

Full-file backup deliberately copies native configuration and selected setup markers without regeneration or field conversion. A copied marker or successful restore cannot prove that this checkout ran setup or has its local prerequisites. Keep restoration, deliberate rendering, and full setup distinct so recovery neither rewrites accepted bytes nor bypasses required initialization.

## Use the receipt to establish which side changed

Maintenance records the successfully synchronized scope with the source fingerprint so it can compare complete local contents against the baseline after a repository update. Older receipts remain readable but supply no proof that only the repository changed. Both sides changing always requires a choice, avoiding a separate containment or merge analysis. Keeping this decision and the guarded write together lets Setup and startup use the same evidence. The caller owns the accepted scope and permissions. The receipt advances after source and target agree.
