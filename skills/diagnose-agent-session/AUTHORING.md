# Authoring Decisions

## Keep acquisition failure separate from session diagnosis

The local Codex snapshot and Tokscale observations have different intervals, effects, and failure modes. Preserve their partial evidence independently: a provider timeout cannot prove a stuck session, and whole-session token totals cannot replace missing behavior or turn-cost evidence. Combining them into one health flag would create unsupported conclusions.

## Exclude only the identified acquisition call

Retain the fresh random acquisition ID and exactly-one-match rule. Historical diagnosis calls are real session activity; broad command matching could erase them, while reusing an ID could make self-call attribution ambiguous.

## Keep private source content out of every report path

The report is limited to metadata and derived observations even when acquisition fails. Raw provider or transcript content can include prompts, outputs, and credentials; troubleshooting does not justify changing that disclosure boundary.
