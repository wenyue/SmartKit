# Authoring Decisions

## Keep the shared maintenance contract outside the user-only entry

Setup and enabled startup synchronization consume the supported reference and commands without invoking this user-only Skill. Keep binding, byte-preserving backup, application choices, receipts, and publication recovery in that shared owner. The entry guides an explicit maintenance task and relies on its required reference instead of duplicating every synchronization condition.

## Preserve snapshots without claiming setup success

Full-file backup deliberately copies native configuration and selected setup markers without regeneration or field conversion. A copied marker or successful restore cannot prove that this checkout ran setup or has its local prerequisites. Keep restoration, deliberate rendering, and full setup distinct so recovery neither rewrites accepted bytes nor bypasses required initialization.

## Require acceptance of actual differences

Automatic synchronization is an explicit startup preference, not advance acceptance of future source/target differences. The exact inspected-state choice covers the whole synchronization, while the receipt advances only after agreement is verified. A source-only fingerprint or silent three-way merge would weaken that accepted boundary.
