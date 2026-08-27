# Executable Acceptance

This conditional authority owns Acceptance design, case identity and portfolio, attempts,
judgment, Candidate and setup correction, replay, safety finalization, and terminal precedence.
Load it during Design only when Acceptance applies. When Design freezes `NOT_REQUIRED`, no
Acceptance capability, identity, or schedule gates the run.

## Qualify execution and identities

Extend concrete Role Launch readiness with disposable isolation, exact case grants, evidence capture,
fresh Runner launch, termination and quiescence for every return mode, cleanup, and bounded
recovery. Prove that the frozen worker schedule can run a fresh Runner while the current case
Reviewer remains retained, and can retain that Reviewer while complete fresh earlier-stage cohorts
run in batches through the remaining `P` slots.

Define one fresh persistent Reviewer per case. Bind its identity and schedule before the first
attempt, but start it only after that attempt finalizes safely. Keep at most the current case
Reviewer live or retained. Every Runner and retained Reviewer consumes one `P` slot; batch all
other work without changing cohort, version, or evidence. `HOST_UNAVAILABLE` means the host cannot
supply the correctly derived capability or frozen schedule. A Controller dispatch beyond `P` is
control-plane `ROLE_BOUNDARY_VIOLATION`.

Use full-job execution unless the Skill model proves **Finite Execution Projection** eligibility
and Design owns a preauthorized harness. The smallest eligible projection must execute every
materially affected runtime seam:

- the Runner applies Candidate behavior to frozen seam inputs and emits observable output;
- the harness performs only preauthorized identity and control mechanics and captures host
  evidence; the Runner never requests or controls identities; and
- one recursive-edge case reaches the exact observable re-entry condition: Candidate state plus
  the next invocation that would dispatch this same Acceptance graph. The harness terminates
  before dispatch; precursor state is insufficient.

A missing harness or runtime seam returns `EXECUTION_UNAVAILABLE`; a walkthrough cannot substitute.
Network or external effects require accepted case authority and proven host capability.

## Freeze immutable cases

During Design, freeze the smallest risk-ordered portfolio covering material runtime risk: normally
a success path and every materially distinct affected error, recovery, exit, and operating
condition. Define observable pass conditions without imposing an arbitrary case count. At stage
entry, bind those unchanged case units and execute them sequentially from highest risk.

Case definitions and pass conditions never change. Bind each case unit before its first attempt.
Preserve passed-case evidence across Candidate Versions only when Revision Impact proves the change
cannot affect what it establishes.

## Prepare one fresh attempt

Freeze an **Attempt Contract** for every attempt containing:

- disposable Execution Isolation, fixture, safe cleanup, and at most one preauthorized bounded
  cleanup recovery;
- exact case-scoped operations, tools, network, and external-effect grants;
- read-only Candidate Version, immutable case and pass conditions, and complete evidence capture;
  and
- fresh Runner inputs plus termination and quiescence mechanics.

Candidate, case, fixture definition, and pass conditions are immutable **setup inputs**. Only exact
case-owned execution targets and effects are mutable. Fixture or environment correction is a
separate Controller action between attempts.

Missing permission, safe isolation, or required capability returns `EXECUTION_UNAVAILABLE` with
the untested surface, never `PASS` or `NOT_REQUIRED`. Define one **Capture Record** for every
obtainable observation, capture failure, Runner report, termination and quiescence fact, Candidate
fingerprint and audit, residual state, cleanup, and recovery or unavailability. Invent no evidence.

## Execute, then always finalize

Launch one fresh Runner. It performs only frozen case effects against exact case-owned targets. It
does not alter setup inputs or Candidate, expand grants, judge, repair, correct setup, clean up,
control roles, or delegate.

After success, failure, abnormal behavior, non-return, or audit stop, always:

1. Preserve every obtainable observation and report; record every capture failure.
2. End the Runner through the frozen Role Launch mechanics and establish quiescence with
   termination evidence.
3. Complete its Role Boundary Audit and repeat the Candidate fingerprint audit, even when no
   report exists or quiescence cannot be established.
4. Only after quiescence, clean exact authorized case-owned targets. On failure, attempt at most one
   safe, supported, preauthorized recovery. Failed quiescence forbids cleanup; a boundary violation
   does not forbid safe cleanup after quiescence.
5. Select the attempt result in order: boundary or audit violation, or capture failure →
   `ATTEMPT_INVALID`; unestablished quiescence → `RUNNER_NOT_QUIESCENT`; cleanup failure after
   recovery or without an available recovery → `CLEANUP_FAILED`; otherwise attempt finalization
   succeeds.

An abnormal Runner may omit normalized reports only when the frozen contract permits it. Record
the absence and audit host and capture evidence. A terminal attempt result stops Acceptance:
report all obtainable evidence, residual state, and recovery; start no retry or Reviewer; make no
defect classification; issue neither case `PASS` nor `NOT_REQUIRED`. A prebound Reviewer remains
subject only to workflow finalization. Successful attempt finalization is evidence, not PASS.

## Judge finalized evidence

After the first attempt finalizes successfully, start the case's prebound Reviewer and retain that
same identity through later attempts, classification, Candidate correction, fixture/environment
correction, one ambiguity observation, and case PASS.

Give the Reviewer the complete Candidate Version, accepted behavior and evidence, immutable case
and pass conditions, fixture and permission boundaries, and every captured execution and
finalization fact. It independently judges attribution, pass conditions, permission, execution,
termination, quiescence, cleanup, residual state, and exit selection. It returns exactly one:

- common `PASS` when every condition holds and no Candidate finding is supported;
- common `FINDING_READY` for a **Candidate defect**, followed by the runtime's direct finding
  handshake and common-schema finding body;
- common `CONTEXT_REQUIRED`, `ACCESS_REQUIRED`, or `HUMAN_DECISION_REQUIRED`;
- **fixture/environment defect**, only when there is no Candidate defect: defect plus its exact
  preauthorized bounded setup correction, or confirmation that none exists;
- **ambiguous**, only when there is no Candidate defect: named live alternatives plus one targeted
  observation, bounded setup, and capture delta within current authority; or
- `AMBIGUITY_UNRESOLVED` after that observation, with initial and final alternatives, their change,
  both evidence sets, observation and capture delta, remaining ambiguity, and untested surface.

The Reviewer returns its classification directly and unchanged. Candidate findings alone use the
metadata-only runtime bootstrap before their semantic body reaches the resident Author. Author and
Reviewer then judge the claim and reasons independently through the common bilateral lifecycle.
The Controller performs only the selected lifecycle transition; it never receives, relays,
summarizes, or reinterprets finding or discussion content.

## Correct and reassess

- Candidate findings use the direct Author↔Reviewer lifecycle. After the complete full-unit Repair
  Scope authorizes a selected repair, a fresh Runner and the same Reviewer must regain current-case
  Stage-local PASS before Revision Impact.
- For a fixture/environment defect, the Controller applies only the Reviewer-selected
  preauthorized setup correction, starts a fresh attempt, and resumes the same Reviewer. Missing
  capability returns `EXECUTION_UNAVAILABLE`; no safe bounded recovery returns `NO_PROGRESS`.
- For `ambiguous`, add only the supplied setup and capture delta, run exactly one fresh targeted
  observation, and resume the same Reviewer. Any remaining material ambiguity returns
  `AMBIGUITY_UNRESOLVED`, even when alternatives narrow, change, or appear.

One **Acceptance correction attempt** comprises one Candidate repair or selected
fixture/environment correction, its fresh Runner attempt, and Reviewer reassessment. Count it only
while the same defect persists. A materially different defect or approach resets the consecutive
count. The ambiguity observation is not a correction attempt. Stop `NO_PROGRESS` when the same
defect survives two consecutive attempts or safe recovery is exhausted. A human request triggers
the immediate global semantic stop, while every started Runner still receives complete safety
finalization.

## Rewind and replay

**Stage-local PASS** is the current Reviewer passing the current case and Candidate Version on
successfully finalized evidence. It closes the active correction cycle but is neither case PASS nor
Acceptance PASS.

After a Candidate correction:

1. Run the current case with a fresh Runner and the same Reviewer until Stage-local PASS or stop.
2. Apply Revision Impact. When earlier non-Acceptance proof is invalidated, retain this Reviewer,
   bind complete fresh cohorts for every invalidated closed unit, and batch them through the
   remaining `P` slots. Restore each intervening stage, rerun this case, and regain Stage-local PASS
   before another Revision Impact decision.
3. At convergence, record current-case PASS, end its Reviewer, and inspect every previously passed
   case for invalidation regardless of position.
4. Restart the earliest invalidated case in frozen risk order: obtain one successfully finalized
   fresh attempt, then start that case's fresh Reviewer. Skip only demonstrably unaffected evidence.
5. When no prior case is invalid, advance to the next frozen case.

Never start another case Reviewer while retaining the current one. Replay uses the complete safety
lifecycle. A case passes only with Reviewer-owned PASS backed by unaffected, successfully finalized
evidence on the current Candidate Version.

Acceptance passes only when every frozen case records PASS, no evidence is invalidated, every
Runner is quiescent, all required cleanup and audits succeed, and no terminal remains. Return that
result through the Evaluation Lifecycle, then run workflow finalization.
