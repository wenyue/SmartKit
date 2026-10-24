# Authoring Decisions

## Review source-wide revisions, not only the requested Skill

The registry pins each upstream repository once. A seemingly narrow selection change can therefore upgrade every existing selection from that source. Keeping this consequence beside baseline selection prevents an unreviewed broad update hidden behind a single-Skill request.

## Separate mechanical compatibility from accepted behavior

The updater can prove that patches apply and recorded bytes agree; it cannot decide whether the combined instructions still preserve local authorization, recovery, and consumer outcomes. The workflow retains semantic review before applying and complete-content verification afterward so patch success cannot replace either judgment.

## Preserve the upstream/patch ownership boundary

Local adaptations belong in registry inputs and patches because distributed snapshots are regenerated. Normalization and transaction details remain in the entry because they affect whether a proposed patch preserves bytes and how failure recovery can be judged; they are not a substitute for the updater's live schema.
