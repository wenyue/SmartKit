---
name: write-rules-and-skills
description: Author or revise one English Rule or Agent Skill.
---

# Write Rules and Skills

The active Agent is the Controller. It manages one authoring job and its boundaries; the Author
owns the Candidate, Reviewers own their judgments, and a Runner supplies runtime facts when needed.
The Controller does not write, review, or interpret their semantic work.

## 1. Align the job

Identify exactly one Rule or Skill from the requested outcome and governing evidence. A Rule is a
persistent policy across triggered work; a Skill is a triggered job with a bounded outcome. If the
request mixes owners, split it before continuing. If code, configuration, a schema, or another
active owner already owns the requested fact, route the work there instead.

Discover facts that can be established from authoritative sources. Resolve material choices about
the intended outcome, current behavior, non-goals, preservation and compatibility, dependencies,
permissions, validation, safety, distribution, and handoff. Existing Candidate text is regression
evidence, not design authority; repository visibility does not grant meaning or permission.

Keep the user exchanges that establish the job's intent as authoritative user-intent evidence: the
original request; later corrections, confirmations, and decisions that affect meaning, scope, or
non-goals; and the proposals, questions, or options those responses refer to. Preserve this evidence
separately from the Controller's interpretation and from the Author brief.

Prepare a self-contained Author brief containing:

- the objective and requested change;
- the exact Candidate paths and allowed create, edit, move, or delete operations;
- accepted constraints and authoritative evidence paths;
- required automated validation; and
- the observable completion conditions.

Return `NEEDS_INPUT` when a missing user decision, fact, access grant, or permission could
materially change the job. Continue when one Candidate and one brief can express the accepted
outcome without an unresolved material choice.

## 2. Freeze the Candidate and review scope

Capture the complete Candidate baseline and fingerprint before any write, using the bundled
`candidate_evidence` script for the host platform. Keep the snapshot outside the Candidate. Freeze
the write scope, validation commands, and permissions separately; an allowed addition and deletion
do not imply an allowed move. Preserve unrelated staged, unstaged, and untracked work.

When the Candidate includes this Skill or another governing instruction, also freeze its complete
pre-write text and use that copy as authority for the rest of the run. Newly authored text remains
Candidate evidence until the next invocation; it cannot govern its own review.

Assign one resident Author for the entire job. Both review topologies cover Quality, Change, and
Correctness; select between them by the independence the job needs:

- **Integrated Review** assigns all three perspectives to one Integrated Reviewer. Use it when the
  affected obligations, paths, and integration context are closed, material uncertainty is absent,
  and the risk is bounded.
- **Independent Review** assigns Quality, Change, and Correctness to three separate Reviewers. Use
  it for self-hosting, broad impact, high risk, or uncertainty about ownership, safety, permissions,
  external effects, recovery, validation, or critical paths.

The Controller manages this topology without interpreting professional judgments. Integrated
Review loads one identity with the common Reviewer contract and all three professional contracts.
Independent Review loads three identities with the common contract and one professional contract
each. The identities read their assigned files; the Controller does not.

## 3. Author and validate

Confirm the Candidate still matches the baseline, then start the Author with the Author brief as its
only session context. Also supply the baseline locator, current fingerprint, and a pointer to
[the Author role](references/author.md); do not supply the full user-intent evidence. Only that
Author may write the Candidate.

After the Author returns, capture the complete Candidate again. Advance only from an authenticated
Author `COMPLETE` whose changes are attributable to that Author and fit the frozen write scope. An
Author `NEEDS_INPUT` or `BLOCKED` ends the job with that result after boundary checks and cleanup;
preserve any partial changes as evidence but do not adopt them for validation or review. Treat an
out-of-scope or indeterminate change as `BLOCKED` and do not revert uncertain state.

Run the frozen, owner-supported, non-fixing automated validation before review. Every applicable
command must succeed on the current fingerprint before review begins and before final `COMPLETE`.
Record each command and exit. If a failure is caused by the Candidate, give its evidence to the
same Author for one coherent repair, then apply the Author-return gate, fingerprint, and validate
again. Return `NEEDS_INPUT` for a missing user-controlled fact, access, or permission; return
`BLOCKED` for another unresolved failure or repeated correction without new evidence or progress.
Neither case authorizes a Candidate write or permits review to continue.

## 4. Review and correct

### Start the review

Start the selected topology on one fingerprint. Give every reviewing identity a pointer to the
[common Reviewer contract](references/reviewer.md) and the professional contracts assigned by the
topology:

- [Quality Reviewer](references/quality-reviewer.md)
- [Change Reviewer](references/change-reviewer.md)
- [Correctness Reviewer](references/correctness-reviewer.md)

Give every identity its assigned perspectives, review topology, Candidate paths, current
fingerprint, and review-round number. Add the baseline locator for Change and Correctness. Point to
file-backed evidence instead of copying it; each professional contract determines which stable
evidence its perspective reads.

Route only session context that a Reviewer cannot recover from those sources:

- Quality receives the accepted objective and session-only quality or expression constraints.
- Change receives the requested change, preservation and compatibility decisions, and the Author's
  semantic change summary.
- Correctness receives the complete authoritative user-intent evidence and Author brief as distinct
  inputs, session-only critical behavior and safety decisions, and automated-validation results.

An Independent Reviewer receives only the context for its perspective. An Integrated Reviewer
receives the union for all three.

### Run review rounds

Keep the same identities for at most three review rounds while the topology is unchanged. Reviewer
evidence, communication, and results follow the common and professional contracts. The Author waits
for every identity before making one coherent repair; the Controller tracks completion and rounds
without relaying or deciding semantic content.

Apply the Author-return gate after every repair, then run automated validation before the next
review round. A repair creates a new fingerprint, so every identity in the active topology rechecks
its complete evidence. End successfully only when all three professional perspectives return
`PASS` on the same fingerprint and automated validation also passes there. Allow at most three
rounds; return `BLOCKED` if a blocking finding remains after the third.

When a Reviewer returns `INDEPENDENT_REVIEW_REQUIRED`, Correctness proves an Author-brief omission
or distortion, material intent ambiguity requires `NEEDS_INPUT`, or Correctness returns
`RUNTIME_REQUIRED`, load the matching branch in
[conditional Controller review orchestration](references/controller-review.md).

Verify after every Reviewer and Runner return that the Candidate fingerprint is unchanged.

## 5. Finish

Stop safely when a required role is unavailable, a role crosses its boundary, the Candidate state
is untrustworthy, or a started runtime check cannot be terminated or cleaned up. End all active
roles, record any residual state, and perform the final Candidate boundary check.

Return only the useful handoff:

- Candidate type and exact paths;
- Integrated or Independent Review and each professional perspective's final result;
- automated validation commands and results;
- Runner scenarios and observations, when used;
- the Correctness perspective's user-intent coverage and fidelity result;
- the Author's final semantic change summary, bound unchanged to the final fingerprint;
- remaining risks and residual state;
- final fingerprint; and
- `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED`.

This workflow grants no publication, installation, commit, push, release, translation, network
access, or other downstream effect unless the user separately authorizes it. Keep transient
workflow evidence outside the Candidate.
