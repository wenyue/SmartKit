---
name: ponytail-debt
description: >
  Harvest `ponytail:` comments into a debt ledger. Use when a task calls for
  tracking marked shortcuts or deferrals, or the user says "ponytail debt",
  "/ponytail-debt", "what did ponytail defer", "list the shortcuts", "ponytail
  ledger", or "what did we mark to do later". One-shot report; saves a file only
  when authorized.
---

Collect deliberate ponytail shortcuts into one ledger so a deferral can't
quietly become permanent. A useful `ponytail:` comment records an actual known
limit: what was simplified, its ceiling, the observable trigger to revisit it
(WHEN), and the upgrade direction (HOW). Ordinary concise, correct code is not
automatically debt; report the markers' evidence without inventing missing facts.

## Scan

Search the requested repository scope for `ponytail:` with a supported read-only
search tool, skipping `node_modules`, `.git`, and build output. Match the target's
languages and comment syntax, including block or HTML comments where applicable.
Inspect each hit in context to verify it is an actual comment marker: a comment
prefix regex alone cannot exclude strings, documentation, or examples that merely
mention the convention. Include every applicable marker found, even if its facts
are incomplete.

Report the searched scope and exclusions, plus inaccessible or unscanned areas.
Distinguish a complete scan of that scope from partial or unavailable coverage;
report only what the readable evidence supports.

## Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. trigger: <WHEN to revisit>. upgrade: <HOW to improve>.`

Extract the simplification, ceiling, trigger, and upgrade direction from the
comment and its immediate code context. Mark absent facts as `not stated` rather
than guessing. The inherited convention is `ponytail: <ceiling>, <upgrade path>`;
a path describes HOW and does not by itself supply an observable WHEN. Any
`ponytail:` comment without a trigger gets the `no-trigger` tag, even if it names
an upgrade path. A missing direction is recorded separately as `upgrade: not stated`.

If historical attribution is useful, add `git blame -L<line>,<line>` for the
relevant file; blame identifies historical authorship, not proof of current
ownership.

End with `<N> markers, <M> with no trigger.` If none were found, report
`No ponytail: markers found in the searched scope.` An empty ledger does not
establish that the repository has no technical debt or that every file was scanned.
If the scan was unavailable, report that limitation instead of a zero-marker result.

## Boundaries

Reads and reports only by default. Persist the ledger to a file (e.g.
`PONYTAIL-DEBT.md`) only when the user requested or authorized that file output;
existing authorization is sufficient. Preserve target code, tests, required
behavior, and other project contracts; this reporting task authorizes no network,
production configuration, or other state changes.

This is an independent one-shot task whether explicitly invoked or selected for
an applicable task, including while continuous ponytail mode is off. Mode being
off is not itself a reason to start this task. Leave the current mode and global
default unchanged; no mode-state read or initialization is needed. Other
applicable skills, including standard code review and ponytail-review, retain
their own work.
