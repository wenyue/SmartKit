---
name: ponytail-debt
description: >
  List every `shortcut:` comment (and older `ponytail:` ones) as a debt ledger.
  One-shot report; saves a file only when authorized. Use for "ponytail debt",
  "what did ponytail defer", "list the shortcuts", /ponytail-debt.
---

Every deliberate ponytail shortcut is marked with a `shortcut:` comment naming
its ceiling, revisit trigger, and upgrade path (older code may say `ponytail:`). This collects them into one ledger so a deferral
can't quietly become permanent.

## Scan

Grep the repo for comment markers, skipping `node_modules`, `.git`, and build
output:

`grep -rnE --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build '(#|//|/[*]) ?(shortcut|ponytail):' .`  (add other comment prefixes if your stack uses them)

If the user names their own marker word (`/ponytail-debt TODO`), grep for that word instead.

Inspect hits in context to exclude strings, prose, and non-deferrals.
Each deferral comment is one ledger row, even if incomplete.

## Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. trigger: <WHEN to revisit>. upgrade: <HOW to improve>.`

The convention is `shortcut: <ceiling>; trigger: <WHEN>; upgrade: <HOW>`.
Extract fields from the comment and immediate context, including older formats;
mark missing facts `not stated`. For historical authorship, add
`git blame -L<line>,<line> -- <file>`.

Flag the rot risk: any marker comment that names no trigger gets a `no-trigger` tag, those are the ones that silently rot.

End with `<N> markers, <M> with no trigger.` Nothing found: `No deferral markers found in the searched scope.`

## Boundaries

Reads and reports only. When authorized, persist the ledger to a file
(e.g. `PONYTAIL-DEBT.md`). One-shot.
