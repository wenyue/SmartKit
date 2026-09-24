---
name: ponytail-review
description: >
  Review diffs for over-engineering: unnecessary dependencies, speculative
  abstractions, dead flexibility, and code covered by the standard library or
  platform. Use for complexity-focused review, requests to simplify or find
  what can be deleted, or explicit ponytail-review invocation. Complements
  standard code-review.
---

Review diffs for unnecessary complexity. Report supported findings and concrete
replacements without applying fixes. Prefer less code when it preserves the
confirmed requirements and observable behavior.

Use this task skill when the work calls for it, whether selected autonomously or
explicitly invoked. It remains applicable while continuous Ponytail is off, but
being off alone is not a reason to start a review. This task neither reads nor
initializes mode state and changes neither the conversation mode nor the global
default.

## Format

State the diff or comparison reviewed and the supporting code inspected. Use
available read-only search to trace requirements, callers, behavior, and tests
that bear on each proposed simplification. Report inaccessible or unscanned
material as a coverage limit; missing evidence is not proof that code is unused.
Withhold a finding whose safety depends on unresolved evidence and identify the
material gap.

Default to one concise line per finding:
`L<line>: <tag> <what and evidence>. <replacement>.`, or
`<file>:L<line>: ...` for multi-file diffs. Expand when needed to explain material
evidence or verification gaps.

Tags:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function and establish equivalent required behavior.
- `native:` dependency or code doing what the platform already does. Name the feature and establish that it meets the requirements.
- `yagni:` unnecessary abstraction, config, or layer, supported by actual requirements and caller evidence.
- `shrink:` same required behavior expressed more clearly with less code. Show the shorter form.

One implementation or caller is a clue to investigate, not deletion proof.
Judge whether the abstraction still serves a required boundary, behavior, or test
seam. Line reduction alone does not establish a useful simplification.

## Examples

These examples illustrate findings after the stated evidence is established;
the same code shapes can be necessary in another context.

Vague: "This EmailValidator class might be more complex than necessary."

Concrete: `L12-38: stdlib: validator duplicates the required re.fullmatch check; callers need only its Boolean result and tests cover the accepted inputs. Use the same pattern with re.fullmatch.`

`L4: native: moment.js is used only for this display format; Intl.DateTimeFormat matches the required locale, timezone, and output behavior. Replace the call and remove the unused dependency.`

`repo.py:L88: yagni: AbstractRepository only forwards calls; caller and test inspection establishes no required isolation or substitution role. Inline the forwarding layer.`

`L52-71: delete: retry wrapper has no recoverable failure to handle under the local call's documented contract and adds no required timing or error behavior. Nothing replaces it; idempotence alone would not justify deletion.`

`L30-44: shrink: the loop only pairs equal-length inputs with dict assignment; dict(zip(keys, values)) preserves duplicate-key, ordering, and evaluation behavior here. Use dict(zip(keys, values)).`

## Scoring

When useful, end with an estimate: `net: -<N> lines possible.` Treat line savings
as supporting information alongside readability, maintenance, and preserved
behavior, not the only measure of quality.

If there are no supported findings, say `No supported complexity findings in the
reviewed scope.` Include material coverage or verification limits. This outcome
is not ship approval or evidence that unreviewed code is lean.

## Boundaries

Scope: over-engineering and complexity only. Correctness, security, and
performance audits belong to a normal review pass. This specialization composes
with standard code-review when both apply; it does not replace or suppress it.
Every proposed simplification must still preserve confirmed requirements,
necessary validation and error handling, security, accessibility, correctness,
and required performance behavior. Route concerns outside this scope to normal
review rather than endorsing a simplification that knowingly violates them.

Preserve tests and test infrastructure needed for required behavior and existing
project contracts. A smoke test or assert-based self-check can be useful; there
is no one-test ceiling, and necessary frameworks, fixtures, or suites are not
bloat. Test deletion needs evidence that required coverage remains sufficient.

This task only reads and reports. It authorizes no target edits, network actions,
production configuration changes, or state writes. Complete the review with
scoped findings or the scoped no-finding result and any material limits.
