# Review Escalation

Load only the branch selected by a review result or condition. The Controller coordinates these
branches without taking over the Author's or Reviewers' professional judgment.

## Independent review required

When an Integrated Reviewer returns `INDEPENDENT_REVIEW_REQUIRED`, end it and start three fresh
Independent Reviewers on the current fingerprint. The Integrated verdict cannot stand in for an
Independent verdict or bias the new Reviewers. The switch replaces the Integrated attempt in the
current round rather than creating a repair round. Return `NEEDS_INPUT` if the switch or its cause
requires broader write scope, access, or permission.

## Author-brief correction or user input

When the identity applying Correctness proves that the Author brief omitted or distorted user
intent, correct the brief only within the finding and cited evidence, then return it to the same
Author for one coherent Candidate repair. The Controller owns the brief, not the semantic verdict.
Treat the repair as the next round under the normal Author gate, fingerprint, validation, and review
cycle.

If authoritative context cannot resolve a material intent ambiguity, present the Reviewer's
question to the user without supplying an interpretation and return `NEEDS_INPUT`.

## Runtime evidence required

When the identity applying Correctness returns `RUNTIME_REQUIRED`, its request names the scenario,
inputs, permissions, and observable conditions. If the request fits the frozen job, start an
independent Runner with a pointer to [the Runner role](runner.md). The Runner sends observations
directly to that same identity, whose Correctness perspective alone judges them. A request outside
the frozen job returns `NEEDS_INPUT` rather than expanding authority in place.

Safely finalize every Runner attempt before consuming its observations. The requesting identity's
Correctness perspective also judges a Runner `NEEDS_INPUT`, `BLOCKED`, or incomplete observation:
return `NEEDS_INPUT` when essential user-controlled input or permission is missing, and `BLOCKED`
when necessary evidence cannot be produced within the frozen job. Retry only within existing
authority and with new evidence or an approach that can make progress.
