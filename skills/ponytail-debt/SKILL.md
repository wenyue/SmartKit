---
name: ponytail-debt
description: >
  Harvest every `ponytail:` comment in the codebase into a debt ledger, so the
  deliberate shortcuts and deferrals ponytail leaves behind get tracked instead
  of rotting into "later means never". Use when the user says "ponytail debt",
  "/ponytail-debt", "what did ponytail defer", "list the shortcuts", "ponytail
  ledger", or "what did we mark to do later". One-shot report; saves a file only when authorized.
---

Every deliberate ponytail shortcut is marked with a `ponytail:` comment naming
its ceiling and upgrade path. This collects them into one ledger so a deferral
can't quietly become permanent.

## Scan

Grep the repo for comment markers, skipping `node_modules`, `.git`, and build
output:

`grep -rnE '(#|//) ?ponytail:' .`  (add other comment prefixes if your stack uses them)

Inspect each hit in context to exclude strings and prose merely mentioning
the convention. Each actual comment marker is one ledger row, even if incomplete.
Report material scan limitations.

## Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. trigger: <WHEN to revisit>. upgrade: <HOW to improve>.`

The convention is `ponytail: <ceiling>, <upgrade path>`; an upgrade path (HOW)
is not a trigger (WHEN). Extract these facts from the comment and immediate
context; mark missing facts `not stated`. For historical authorship, add
`git blame -L<line>,<line>` with the file path.

Flag the rot risk: any `ponytail:` comment that names no
trigger gets a `no-trigger` tag, those are the ones that silently rot.

End with `<N> markers, <M> with no trigger.` Nothing found: `No ponytail: markers found in the searched scope.`

## Boundaries

Reads and reports only. When authorized, persist the ledger to a file
(e.g. `PONYTAIL-DEBT.md`). One-shot.
