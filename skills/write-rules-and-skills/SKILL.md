---
name: write-rules-and-skills
description: Author or revise one English Rule or Agent Skill.
---

# Write Rules and Skills

Deliver one **Candidate**: a Rule or Skill and its scoped supporting resources. The active Agent is the Controller; read the [Controller contract](references/controller.md) before alignment and apply it throughout.

The Author alone writes. Quality, Change, and Correctness judge the result; Correctness may commission a Runner for bounded observations. The Controller manages alignment, evidence, roles, rounds, and finalization while each role owns its judgments.

Work within established user authority. Repository visibility grants no permission, and this workflow grants no publication, installation, commit, push, release, translation, network access, or other downstream effect without separate user authorization.

## 1. Align

Establish the Candidate, owners, dependencies, and self-contained Author brief under the Controller contract. Resolve material choices, facts, access, and permissions before writing. If alignment cannot close, return `NEEDS_INPUT` with the exact gap.

## 2. Freeze the job

Resolve `<skill-root>` to this loaded Skill directory and inspect `python "<skill-root>/scripts/candidate_evidence.py" --help`. Before any Candidate write, freeze:

- **Baseline:** capture the complete Candidate and fingerprint with that CLI. Keep snapshots, review records, and validation logs outside Candidate scope.
- **Authority:** record exact allowed operations and permissions, non-fixing validation commands, and finite runtime and resource bounds. Authorize moves explicitly; permission to add and delete does not imply permission to move. Preserve unrelated staged, unstaged, and untracked work.
- **Governing text:** retain the complete pre-write copy of any governing instruction in the Candidate, including this Skill. It governs this invocation; edited text becomes governing only on a later invocation.

Assign one resident Author for writing and repairs. Choose [Integrated or Independent Review](references/controller.md#choose-and-adjust-review-topology) and have each identity read its assigned contracts.

## 3. Author and validate

Confirm the Candidate still matches the baseline. Start the Author with the brief as its only session context, plus the baseline locator, fingerprint, and [Author contract](references/author.md). Retain the full user-intent record with the Controller and Correctness.

After **every Author return**, capture the complete Candidate and apply this gate:

| Return or evidence | Action |
| --- | --- |
| Authenticated `COMPLETE`, with attributable changes inside frozen scope | Run validation. |
| `NEEDS_INPUT` or `BLOCKED` | Check boundaries, preserve partial changes as evidence, clean up, and return that result. |
| Out-of-scope or indeterminate change | Preserve uncertain state and return `BLOCKED`. |

Run every frozen owner-supported validation command without fixing. Record commands, exits, and the current fingerprint; review starts only when all pass.

- **Candidate-caused failure:** send the evidence to the same Author for one coherent repair, then repeat the return gate and validation.
- **Missing user-controlled input or permission:** return `NEEDS_INPUT`.
- **Other unresolved failure, or correction without new evidence or progress:** return `BLOCKED`.

## 4. Review and correct

Start all reviewers on the same fingerprint with the [common Reviewer contract](references/reviewer.md), their professional contracts, and each contract's evidence inputs:

| Perspective | Judgment |
| --- | --- |
| [Quality](references/quality-reviewer.md) | Is the current artifact clear, economical, and usable? |
| [Change](references/change-reviewer.md) | Does the change preserve and realize the accepted meaning? |
| [Correctness](references/correctness-reviewer.md) | Does the result faithfully and safely deliver user intent? |

Supply topology, Candidate paths, fingerprint, round number, stable file-backed evidence, and the baseline locator for Change and Correctness. Independent identities receive only their perspective's context; an Integrated identity receives the union. Keep identities while topology stays unchanged, for at most **three rounds**.

Each round has three steps:

1. **Review.** Reviewers send findings and necessary questions directly to the responsible role. Track returns without judging or relaying findings; verify an unchanged Candidate fingerprint after every Reviewer return.
2. **Repair.** If findings remain, the Author waits for every applicable return, then makes one coherent repair.
3. **Revalidate.** Apply the Author-return gate and all frozen checks. In the next round, every reviewing identity rechecks the complete new fingerprint.

A blocking finding after round three yields `BLOCKED`. Use the Controller contract for a required [topology switch](references/controller.md#choose-and-adjust-review-topology) or [alignment problem](references/controller.md#maintain-alignment-and-handle-blockers). Correctness owns runtime evidence within the frozen bounds.

## 5. Finalize and hand off

Finalize on every exit. Stop safely if a required role is unavailable, a boundary is crossed, Candidate state becomes untrustworthy, or runtime work cannot be terminated or cleaned up. End active roles, record residual state, and check the final Candidate boundary.

Return:

- Candidate type, exact paths, final fingerprint, and the Author's semantic summary bound to it;
- topology and separate Quality, Change, and Correctness results, including Correctness's intent-fidelity coverage;
- validation commands and results, plus Runner scenarios and observations when used;
- remaining risks, residual state, and `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED`.

`COMPLETE` requires all three perspectives to `PASS` and every validation command to pass on the same final fingerprint.
