---
name: write-rules-and-skills
description: Author or materially revise one Rule or Agent Skill in an explicitly supplied context; excludes Setup Authoring Contracts and shared-portability qualification.
---

# Write Rules and Skills

Author the smallest complete Rule or Skill from accepted intent and verified evidence. Apply
`writing-for-agents` for information hierarchy, purposeful Markdown, and Skill mechanics. This
Hybrid Skill owns ordinary candidate authoring and the common qualification gates; a more-specific
caller may add scope proof but may not weaken them.

The active Agent is the controller, not a semantic Author or Reviewer. It may discover authorized
project facts, select evidence, start fresh Agents, apply returned content unchanged, and run
deterministic checks. Semantic roles receive only explicit Context Packets.

## Establish obligations and ownership

Before authoring, establish:

- the requested outcome, preserved semantics, accepted changes, non-goals, and safety boundaries;
- the current and requested artifact owners, permitted writes, and affected loading, resource,
  discovery, generation, and distribution surfaces; and
- the applicable Rules, current behavior, validation seams, and environmental facts that can change
  a policy, job, action, target, or exit.

Keep one in-context semantic-ledger row for each independently changeable obligation, with its
evidence, requested or current owner, and `preserve`, `change`, `add`, `move`, or `retire`
disposition. Keep the ledger, authoring models, provenance, and review evidence out of runtime
artifacts.

Read [`references/owner-gate.md`](references/owner-gate.md) completely and apply it. For an
explicitly read-only Ownership Review, return its verdict and stop. Otherwise continue only when
every candidate has one supported Rule or Skill owner.

## Route and reach readiness

Every candidate is an Ordinary Artifact used directly. Read
[`references/ordinary-artifact.md`](references/ordinary-artifact.md) completely, then read exactly
one semantic reference:

| Candidate | Semantic reference |
| --- | --- |
| Rule | [`references/rule-semantics.md`](references/rule-semantics.md) |
| Skill | [`references/skill-semantics.md`](references/skill-semantics.md) |

When the Owner Gate returns `split`, create the separately owned Rule and Skill candidates selected
by the user. Ask only when supported evidence still permits materially different behavior,
ownership, writes, authority, side effects, or exits. Otherwise record the uniquely supported fact
and continue.

Read [`references/soft-isolation.md`](references/soft-isolation.md) completely. The top-level
controller must obtain one Soft-Isolation Probe `PASS` before starting a Behavior Control, Author,
Pruner, Reviewer, or Acceptance Runner. A more-specific caller may supply that `PASS` only from the
same top-level run and fresh-Agent launch mechanism. Never continue after Probe failure.

Apply any Behavior Control required by the Ordinary Artifact reference. Readiness passes when the
selected references can be applied without a material unknown.

## Author one Candidate Revision

Build a temporary Policy Frame for a Rule or the selected supported Skill Shape for a Skill. Project
each obligation into its narrowest reliable runtime owner and loading tier. Leave environment-owned
facts discoverable, disclose conditional material only at its trigger, and use a script only for
repeated fragile deterministic mechanics. An existing artifact is omission evidence, not the new
outline.

Start a Soft-isolated, tool-free Author with one Context Packet containing the accepted outcome,
semantic ledger, selected frame, complete current candidate and owned resources when they exist,
permitted evidence, applicable authoring guidance, and the complete canonical target map. For
project-aware authoring, include every required project fact or Rule body explicitly. The Author
returns either `CONTEXT_REQUIRED` or complete replacement content for every changed target; it does
not edit files.

On `CONTEXT_REQUIRED`, stop or build a complete replacement packet and start a new fresh Author.
Otherwise apply the returned content unchanged to the authorized canonical paths and verify the
result before continuing. The controller must not make a semantic correction while writing it.

A Candidate Revision is the complete current content state after that verified write. Read it
without its predecessor or diff. Continue only when another Agent can use it without inventing a
condition, fact, action, owner, or exit.

Classify every blocking finding independently:

- `uniquely-forced`: current evidence determines one in-scope correction without new policy,
  authority, behavior, scope, or side effects;
- `decision-required`: evidence leaves materially different supported outcomes or correction needs
  new intent, evidence, authority, scope, or external action. Name the exact unresolved choice, its
  decision owner, and evidence for each outcome.

## Prune, validate, review, and accept

1. Read [`references/pruning-agent.md`](references/pruning-agent.md) completely. Give the candidate
   to one Soft-isolated, tool-free Pruning Agent that did not author it. Keep that same Agent through
   pruning corrections. It cannot later review or run Acceptance.
2. Run the caller environment's required machine checks for every changed owner and affected
   surface. Machine checks prove structure and execution, not natural-language meaning. Stop on a
   nonzero required result and report the exact command, final exit, relevant output, unrun gates,
   and unverified surfaces.
3. Freeze writes. Read [`references/semantic-review.md`](references/semantic-review.md) and
   [`references/acceptance-runner.md`](references/acceptance-runner.md) completely. Give one new
   Soft-isolated, tool-free Reviewer the complete bounded evidence. It returns Semantic Review
   `PASS` or `FAIL` before Acceptance begins.
4. For each selected case, use a new Soft-isolated Acceptance Runner. The Reviewer judges its
   observable result and returns a separate Acceptance `PASS` or `FAIL`.

Stop when a required fresh Agent is unavailable. A tool-enabled Acceptance case is exceptional and
must satisfy the matching Probe and packet rules in the Acceptance Runner reference before it runs.

## Correct until stable

Stop for a valid `decision-required` finding. When all findings are `uniquely-forced`, give all of
them to the Author together. The Author returns complete revised content; the controller applies it
unchanged and verifies it. That write creates a new Candidate Revision and invalidates every
dependent machine, Review, and Acceptance result. Rerun gates in order with the same Pruning Agent,
a new Reviewer, and a new Runner for each affected case.

Stop for no progress when the same finding recurs unchanged or a correction would not change the
candidate. Success requires Pruning, machine validation, Semantic Review, and Acceptance to pass
for the same Candidate Revision.

Report the artifact type, owner, preserved and accepted changes, affected surfaces, baseline size
comparison, exact commands and exits, Probe and gate verdicts, corrections, and unresolved or
untested surfaces. Keep Context Packets, ledgers, Probe results, and review evidence in Agent context;
create no workflow report or temporary authoring directory. Leave shared-portability claims, Setup
Authoring Contract authoring, publication, installation, commit, push, and other external actions to
their owners.
