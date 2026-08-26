---
name: write-rules-and-skills
description: Author or revise one English Rule or Agent Skill, or review its ownership without writes.
---

# Write Rules and Skills

Author the smallest complete English Rule or Skill for its supported owner. Apply
`writing-for-agents` for information hierarchy, purposeful Markdown, and Skill mechanics. A
read-only Ownership Review uses the same evidence and exits before candidate writes.

The active Agent is the Controller. It orchestrates access, role boundaries, Candidate Versions,
fingerprints, stage transitions, Revision Impact Decisions, and the bounded handoff. It does not
author candidate meaning, decide finding dispositions, issue semantic verdicts, or make semantic
repairs.

## Reach readiness and freeze the Run Contract

Read [`references/owner-gate.md`](references/owner-gate.md) completely and establish one supported
Rule or Skill owner. For an Ownership Review, return the verdict and stop. A `split` verdict becomes
separate Rule and Skill authoring runs; no Candidate Version spans both.

Read exactly one candidate model:

| Candidate | Reference |
| --- | --- |
| Rule | [`references/rule-semantics.md`](references/rule-semantics.md) |
| Skill | [`references/skill-semantics.md`](references/skill-semantics.md) |

Candidate meaning must be independently supported by accepted evidence and must not leave operative
meaning or terminology available only in a nonnormative ambient glossary.

Read [`references/role-launch.md`](references/role-launch.md) completely and apply its Adapter
selection, static qualification, freeze, and post-freeze qualification gate. A direct invocation
selects the Default Fresh Role Adapter. Every more-specific caller must explicitly select either
that public Default Adapter when no mechanics override is required or one complete caller-owned
Adapter. Omission fails readiness rather than selecting a fallback. Resolve the candidate paths,
model and invocation metadata, access, and applicable validation for the Run Contract.

Before any role starts or candidate file changes, resolve and freeze one complete Run Contract in
Controller context containing:

- the accepted outcome, full existing behavior, preserved obligations, accepted changes, non-goals,
  and safety boundaries;
- every `preserve`, `change`, `add`, `move`, and `retire` disposition;
- candidate ownership, exact paths and affected surfaces, with separate `read`, `write`, `create`,
  and `delete` grants and one preauthorized update envelope;
- available role capacity and persistent-identity retention;
- the selected Adapter, stage order, pass and stop conditions, validation plan, and final handoff;
  and
- the rule that this run remains governed by the frozen contract: candidate edits can affect only
  a later independent invocation.

An accepted Issue or Spec that completely supplies these facts, or a uniquely supported local
repair, may establish alignment. If material behavior, ownership, permission, validation, or exit
ambiguity remains, return `ALIGNMENT_REQUIRED` before roles or writes, name the unresolved choices,
and direct the user to explicitly invoke `grilling`. Add only nonsemantic Context Supplements after
the freeze under the Role Launch update envelope; a material change requires new alignment and a
new run. Complete the Role Launch post-freeze qualification gate before starting the Author.

## Author one Candidate Version

Read [`references/author.md`](references/author.md) completely. Before starting the Author, compute
the baseline Candidate Fingerprint and acquire the single-writer lock for the Candidate Allowlist.
Start one fresh Author without inherited parent turns and keep that identity through every
Candidate Version. Give it the complete
Run Contract, governing evidence, selected model, current candidate, and explicit Candidate
Allowlist. The selected Adapter and frozen access grants govern all Author inspection; the Author
directly edits only its Candidate Allowlist.

After every Author callback, perform the Role Boundary Audit and compute a compact Candidate
Fingerprint across every candidate file. The Author Change Summary describes semantic effects; the
fingerprint identifies content. Use a targeted diff only when those signals cannot support a
Revision Impact Decision; the Controller normally does not inspect a full diff.

## Evaluate in order

Read [`references/correction-cycle.md`](references/correction-cycle.md) completely. Each review
stage uses persistent Reviewer → Author correction or decline → same Reviewer recheck until PASS or
a defined stop.

Evaluate one Candidate Version in this order:

1. Read [`references/quality-review.md`](references/quality-review.md) and run its two persistent
   Reviewers concurrently.
2. Read [`references/machine-validation.md`](references/machine-validation.md) and run it when
   applicable.
3. Read [`references/correctness-review.md`](references/correctness-review.md) and run its two
   persistent Reviewers concurrently.
4. Read [`references/acceptance.md`](references/acceptance.md). Run executable Acceptance only when
   its evidence threshold is met; otherwise record `NOT_REQUIRED` and skip the stage entirely.

## Finish

Success requires the current Candidate Version to hold every applicable stage verdict with no
unresolved worth-fixing finding. A concise success report contains only the candidate paths and
type, owner, fingerprint, machine commands and exits or `NOT_REQUIRED`, review verdicts, Acceptance
verdict or `NOT_REQUIRED`, Role Boundary Audits, rewinds, context or access changes, and unresolved
or untested surfaces. A terminal report additionally includes every status and item of evidence
required by Acceptance and Role Launch finalization, including applicable residual state, evidence
capture, audit, cleanup, teardown, and lock-release failures. The Controller reports the statuses
and evidence produced by their owners without replacing or reinterpreting owned terminal semantics.

Apply the loaded Role Launch workflow-finalization contract before every success or terminal report
after lock acquisition or role launch.

Keep Run Contracts, prompts, findings history, diffs, and transient evidence in Agent context.
Create no workflow report, copied candidate tree, or permanent evaluation fixture. Publication,
installation, commit, push, and release remain separate owners.
