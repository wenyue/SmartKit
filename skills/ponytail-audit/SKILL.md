---
name: ponytail-audit
description: >
  Whole-repo audit for over-engineering. Like ponytail-review, but scans the
  entire codebase instead of a diff: a ranked list of what to delete, simplify,
  or replace with stdlib/native equivalents. Use when the user says "audit this
  codebase", "audit for over-engineering", "what can I delete from this repo",
  "find bloat", "ponytail-audit", or "/ponytail-audit". One-shot report, does
  not apply fixes.
---

ponytail-review, repo-wide. Scan the whole tree instead of a diff. Rank
useful simplifications by evidenced maintenance benefit and impact; size
savings can inform that judgment, never authorize a deletion.

## Tags

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Hunt

Deps the stdlib or platform already ships, single-implementation interfaces,
factories with one product, wrappers that only delegate, files exporting one
thing, dead flags and config, hand-rolled stdlib.

These patterns and small file counts are clues, not findings by themselves.
Confirm requirements, usage, and observable behavior before recommending a
cut or replacement. Preserve necessary behavior, validation, error handling,
security, accessibility, correctness, and tests in every recommendation.
Where the evidence cannot establish that preservation, state the uncertainty
instead of presenting the cut as safe.

Inspect available local repository evidence with supported read-only search.
Aim for the whole tree, accounting for skipped, inaccessible, or unscanned
areas; incomplete coverage limits conclusions about usage and dead code.

## Output

State the scanned scope, skipped or unavailable areas, and material limits.
One concise entry per finding, ranked: `<tag> <what to cut>. <replacement>.
[path]`. Include enough requirements, usage, or behavior evidence to judge
why the replacement preserves what is needed and reduces maintenance work;
use extra lines where needed to make the proposed replacement concrete.

End with `net: -<N> lines, -<M> deps possible.` when an estimate is supported;
otherwise say the savings are unquantified. With no supported findings,
report no over-engineering findings in the scanned scope, qualified by the
coverage limits. This is not ship approval or evidence about unread areas.

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security holes,
and performance are outside this audit's finding categories; route them to
an appropriate normal review pass. This narrow remit does not relax the
preservation required of simplification recommendations. Standard code-review
and ponytail-review may also apply; this audit does not replace them.

Lists findings, applies nothing. One-shot. Explicit invocation and autonomous
selection run this same task when applicable, even with continuous Ponytail
off; being off alone is not a reason to start an audit. Leave continuous mode
and the global default unchanged. This task needs no mode-state read or
initialization and authorizes no repository, configuration, or state writes.
