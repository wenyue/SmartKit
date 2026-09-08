---
name: write-rules-and-skills
description: Author or revise one English Rule or Agent Skill.
---

# Write Rules and Skills

The active Agent is the Controller. Before aligning the job, read
[the Controller role](references/controller.md) and apply it throughout the workflow.

## Principles

- **Independent judgments.** The Author owns the Candidate, Reviewers own their judgments, and a
  Runner supplies runtime facts when needed. The Controller owns task understanding, allocation,
  and the Author brief; it does not author the Candidate or substitute for professional verdicts.
- **Bounded authority.** Repository visibility does not grant meaning or permission. This workflow
  grants no publication, installation, commit, push, release, translation, network access, or other
  downstream effect unless the user separately authorizes it.
- **Acceptance on one fingerprint.** End successfully only when all three professional
  perspectives return `PASS` on the same fingerprint and automated validation also passes there.

## 1. Align the job

Apply the Controller contract to align the job. Advance to freezing only when one Candidate and
one self-contained Author brief express the accepted outcome, the state of owner dependencies is
explicit, and no material choice, fact, access, or permission remains missing.
Otherwise return `NEEDS_INPUT` with the exact unresolved input.

## 2. Freeze the Candidate and review scope

Resolve `<skill-root>` as this loaded Skill directory and invoke
`python "<skill-root>/scripts/candidate_evidence.py" --help`.

Capture the complete Candidate baseline and fingerprint before any write using that Python CLI.
Keep transient workflow evidence, such as baseline snapshots, review records, and validation logs,
outside the Candidate file scope so it stays separate from deliverables and does not affect the
Candidate fingerprint. Freeze the write scope, validation commands, and
permissions separately; an allowed addition and deletion
do not imply an allowed move. Preserve unrelated staged, unstaged, and untracked work.

When the Candidate includes this Skill or another governing instruction, also freeze its complete
pre-write text and use that copy as authority for the rest of the run. Newly authored text remains
Candidate evidence until the next invocation; it cannot govern its own review.

Assign one resident Author for the entire job. Select the review topology using the Controller's
[review independence criteria](references/controller.md#choose-review-independence).

The Controller manages this topology without substituting for professional judgments. Integrated
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

- Quality receives the accepted objective, session-only quality or expression constraints, and the
  responsibility allocation with its evidence locators, supported-loading assumptions, owner
  dependency state, and any caller-supplied allocation plan, for either a Rule or a Skill. Supply
  these independently of the Author brief; Quality does not depend on receiving that brief.
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
without relaying findings or deciding their merits.

Apply the Author-return gate after every repair, then run automated validation before the next
review round. A repair creates a new fingerprint, so every identity in the active topology rechecks
its complete evidence. Allow at most three rounds; return `BLOCKED` if a blocking finding remains
after the third.

When a Reviewer returns `INDEPENDENT_REVIEW_REQUIRED`, Correctness proves an Author-brief omission
or distortion, material intent ambiguity requires `NEEDS_INPUT`, or Correctness returns
`RUNTIME_REQUIRED`, load the matching branch in
[review escalation](references/review-escalation.md).

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
