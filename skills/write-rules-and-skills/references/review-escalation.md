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

When the identity applying Correctness returns `RUNTIME_REQUIRED`, check its request against the
frozen job and existing authorization, then freeze the scenarios, attempt and resource bounds,
test conditions, and acceptance criteria before dispatch. A request outside the frozen job returns
`NEEDS_INPUT`. Start an independent Runner with [the Runner role](runner.md); retain ordinary
non-blind runtime checks when that is the requested evidence.

For behavioral execution, start a fresh task-performing Agent with only the Candidate and version,
normal task request and materials, and necessary execution, permission, and observation-capture
constraints. Keep acceptance criteria and expected outputs with the Controller and Correctness.
Exclude the Author brief, design discussion or history, Reviewer findings, expected behavior,
scoring rubric, and privileged scenario-design rationale from inherited context, prompts, fixtures,
adjacent files, and transcript references. Capture requirements must describe observations without
encoding the expected answer. Provide fresh context for each independent scenario and retry so prior
cases or answers cannot contaminate it. Host base instructions and tools still apply; record their
relevant limitations instead of claiming complete isolation.

Arrange access so ordinary task decisions, tools, questions, and authorized disposable fixture edits
can proceed while the Candidate remains immutable and unrelated state stays protected. Establish
the host's ability to isolate, capture, terminate, and clean up before starting. The Runner sends
observations directly to the requesting identity, whose Correctness perspective alone judges them.

Safely finalize every Runner attempt before consuming its observations. The requesting identity's
Correctness perspective also judges a Runner `NEEDS_INPUT`, `BLOCKED`, or incomplete observation:
return `NEEDS_INPUT` when essential user-controlled input or permission is missing, and `BLOCKED`
when necessary evidence cannot be produced within the frozen job, including unavailable required
isolation or capture. Dispatch additional attempts only within frozen bounds and existing authority
for Correctness's identified unresolved question and new evidence or changed approach. Exhausted
bounds do not authorize rerunning until `PASS`; necessary evidence remains required for acceptance.
