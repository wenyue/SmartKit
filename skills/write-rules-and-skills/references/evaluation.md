# Proof and Correction Lifecycle

This contract owns proof applicability and order, finding severity, correction, replay, and global
exits. Judgment is the default; the ordered proof and correction steps below are procedural because
changing their order can invalidate evidence or authorize unsafe writes.

## Select and run proof

Freeze applicability before Author work and run stages in this order on one current fingerprint:

| Order | Stage | Applicability and closure |
| --- | --- | --- |
| 1 | Machine | Conditional. NOT_REQUIRED only when Machine is inapplicable. When applicable, PASS requires every selected non-fixing command to exit successfully; one or more selected-command failures return FAIL and enter Machine correction below. |
| 2 | Quality | Always. Reviews' frozen Quality topology independently passes the complete Candidate on the same fingerprint. |
| 3 | Correctness | Always. Reviews' frozen Correctness topology passes the complete accepted contract on that fingerprint. |
| 4 | Acceptance | Static Scenario, Executable, or NOT_REQUIRED under the Acceptance contract. |

Machine's reportable stage verdict is PASS, FAIL, or NOT_REQUIRED.

Machine may check schemas, metadata, references, fixed flows, scripts, and owner-supported tests.
It never invents a check to avoid NOT_REQUIRED and never fixes the Candidate. Record the exact
commands, exits, and relevant output. A changed Candidate during Machine is a boundary stop, not a
test result.

Choose Acceptance when material uncertainty remains about judgment or branch behavior, tool or
environment feasibility, permissions, filesystem state, external effects, recovery, or runtime
exits. High-confidence semantics with no material runtime uncertainty is NOT_REQUIRED. Acceptance
is conditional for both Rules and Skills.

## Findings and severity

A supported finding states the problem, governing evidence and provenance, Candidate location,
unchanged impact, severity, affected obligation or path, preservation constraints, and bounded
repair direction. It proposes no replacement prose.

Quality may return:

- critical: correctness, authority, safety, ownership, executability, or terminal failure;
- material: a supported defect that materially reduces information quality, execution usability,
  or maintainability;
- advisory: a bounded nonblocking improvement or valid-choice opportunity.

Critical and material findings block Quality. Correctness and Acceptance Candidate defects are
critical only. Estimated repair size does not lower severity. Taste, symmetry, line count, or
textual difference alone establishes no defect.

Every supported critical, material, or advisory claim inside Q1's or Q2's owned lens is a finding
and follows this disposition lifecycle. A deferred surface is outside that Reviewer's lens or
verdict authority; it cannot substitute for an owned advisory or satisfy the Quality PASS gate.
A plausible blocking cross-lens issue follows Reviews' nonsemantic inspection-request route. The
request is neither a finding nor evidence, but proof cannot close until the owning lens
independently inspects the indicated Candidate location on that fingerprint.

## Correct one fingerprint

For each supported finding:

1. The Reviewer sends the full finding directly to the resident Author.
2. The Author independently returns repair, partial repair, or decline with an evidence-based
   reason.
3. The Reviewer determines whether its blocking claim is resolved, conditionally resolved by the
   proposed repair, or unchanged. New supported evidence may refine the finding.
4. If a blocker remains, the same pair continues until fixed point. Two consecutive rounds with
   the same claim, evidence, disposition, and approach return NO_PROGRESS.
5. Advisories close on the Author disposition and do not enter NO_PROGRESS.

HUMAN_DECISION_REQUIRED from any participant stops immediately. Preserve the request and continue
only in a new run.

After all discussions close, batch every agreed blocking repair and every Author-selected advisory
repair into one exact Repair Scope. The resident Author may independently realize those outcomes
inside the grant. A partial repair is eligible only when the Reviewer agrees that no blocking part
remains after the proposed change. A decline never authorizes a write.

After admissible Author COMPLETE, capture and promote the new fingerprint and bind the returned
semantic Change Summary to it once. Every prior semantic stage verdict is invalid. Rerun all
applicable proof in order from Machine. A review stage still open retains its Reviewer identities
through correction and recheck; every previously PASS and closed review stage invalidated or
reopened by the repair uses fresh identities under Role Runtime. Acceptance identities follow the
Acceptance contract. No semantic verdict carries forward.

Machine FAIL uses the same resident Author and a single exact Repair Scope containing the failed
commands and affected paths. Stop NO_PROGRESS after the same failure survives two repair-and-rerun
rounds without new evidence or approach.

## Select the exit

Before any result, finish started executable Acceptance safety and Role Runtime finalization.
Choose the first supported outcome:

1. ATTEMPT_INVALID, RUNNER_NOT_QUIESCENT, CLEANUP_FAILED, or another started-attempt safety
   terminal; retain any coincident human, Candidate, or boundary result as the underlying result;
2. CANDIDATE_CHANGED or ROLE_BOUNDARY_VIOLATION;
3. TEARDOWN_FAILED; retain any coincident lower-priority terminal as the underlying result;
4. HUMAN_DECISION_REQUIRED;
5. SEMANTIC_ROLE_UNAVAILABLE or HOST_UNAVAILABLE;
6. unavailable CONTEXT_REQUIRED or ACCESS_REQUIRED;
7. ALIGNMENT_REQUIRED, NO_PROGRESS, AMBIGUITY_UNRESOLVED, or EXECUTION_UNAVAILABLE;
8. COMPLETE only when all applicable proof passes on the final fingerprint, every advisory has an
   Author disposition, cleanup is complete, and the final boundary check matches.

A lower-priority result cannot erase higher-priority safety, boundary, or residual-state evidence;
every coincident displaced terminal remains an underlying result.
