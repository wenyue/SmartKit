# Acceptance Contract

This contract owns conditional scenario and runtime validation. Use the lightest mode that can
resolve a material uncertainty, and introduce procedural execution only when observation of a real
tool, environment, permission, effect, or runtime boundary is necessary.

Acceptance has exactly three outcomes at Design:

- NOT_REQUIRED for high-confidence semantics with no material scenario or runtime uncertainty;
- Static Scenario Acceptance for judgment or branch behavior that needs independent scenario
  validation but no real tool, permission, filesystem, environment, external effect, cleanup, or
  runtime feasibility observation; or
- Executable Acceptance only when one of those real conditions must be observed.

## Establish mode readiness

Acceptance exclusively owns its conditional identities, capacity, readiness, and prelaunch
terminal after mode selection:

- NOT_REQUIRED allocates no Acceptance identity or capacity.
- Static Scenario Acceptance allocates exactly one fresh independent Reviewer and no Runner. The
  Reviewer persists through correction and recheck. Failure to establish its identity, lifecycle,
  or one required slot returns SEMANTIC_ROLE_UNAVAILABLE with the untested scenarios.
- Executable Acceptance allocates one fresh persistent Reviewer for each active case and, for each
  attempt, one fresh Runner that can be live concurrently with that Reviewer. Only one case
  Reviewer is active at a time; its identity persists through that case's correction and recheck,
  ends at case closure, and is never reused for a materially distinct case. Failure to establish
  either identity or slot, Runner termination, quiescence, disposable isolation, cleanup, recovery,
  or another required execution capability returns EXECUTION_UNAVAILABLE with the untested
  surfaces before launch.

A walkthrough cannot substitute for required Executable Acceptance. No Acceptance readiness
failure is reclassified as HOST_UNAVAILABLE.

## Freeze cases

For either mode, freeze the smallest risk-ordered set of cases that resolves the material
uncertainty. Each case states accepted evidence, input and operating condition, branch or seam,
observable pass conditions, and material error, recovery, and exit variants. Case meaning and pass
conditions do not change during the run.

Acceptance findings are critical Candidate defects. They use Evaluation's direct correction loop
and the resident Author. Any repair creates a new Candidate fingerprint and returns proof to
Machine before Acceptance rechecks.

## Static Scenario Acceptance

Launch the frozen Static Reviewer and give it the complete Candidate and fingerprint, accepted
obligations and evidence, frozen cases, and pass conditions.

The Reviewer applies the Candidate to each scenario and records the selected decision or behavior,
its Candidate basis, and whether every observable condition follows without unsupported
assumption. It returns PASS, a supported Candidate finding, CONTEXT_REQUIRED, ACCESS_REQUIRED,
HUMAN_DECISION_REQUIRED, or AMBIGUITY_UNRESOLVED, plus complete case coverage and untested or
uncertain surfaces.

Static Acceptance passes only when every frozen case passes on the current fingerprint and no
critical finding or material ambiguity remains. If a repair occurs, the same persistent Reviewer
rechecks all frozen cases after earlier proof is restored.

## Executable Acceptance

Use Executable Acceptance only inside disposable isolation with exact case-scoped grants,
observable capture, safe termination, quiescence, cleanup, and recovery. Network and external
effects require accepted authority and host capability.

Use the active case's frozen persistent independent Reviewer and a fresh nonjudging Runner for
every attempt. The Runner executes only its case; it cannot alter the Candidate or fixture
definition, judge, repair, clean up, control identities, expand grants, or delegate.

Prefer full-job execution when it is safe and nonrecursive. Use a finite execution projection only
when full execution would re-enter this Acceptance workflow or require Runner identity control.
The frozen projection must exercise every materially affected seam and reach the observable
recursive or identity-control boundary; a prose simulation or precursor state is insufficient.

### Attempt contract

Before each attempt, freeze:

- Candidate fingerprint, immutable case and pass conditions;
- disposable fixture and exact mutable case-owned targets;
- tools, commands, permissions, network, and external-effect grants;
- capture of outputs, effects, termination, quiescence, cleanup, and residual state; and
- termination, cleanup, and at most one preauthorized safe recovery path.

Launch a fresh Runner. After every success, failure, abnormal return, non-return, or audit stop:

1. preserve every obtainable observation and capture failure;
2. terminate the Runner and establish quiescence;
3. verify the Candidate fingerprint and role boundary;
4. only after quiescence, clean exact case-owned effects and attempt the frozen recovery when safe;
5. record residual state and select the safety result.

After the safety sequence, select the attempt result in order: a capture failure or non-fingerprint
audit failure that makes evidence untrusted returns ATTEMPT_INVALID; unestablished quiescence
returns RUNNER_NOT_QUIESCENT; cleanup failure after the allowed recovery returns CLEANUP_FAILED;
otherwise safety finalization passes. Failed quiescence forbids cleanup whose safety depends on
inactivity. A Candidate or role-boundary mismatch remains an underlying result.

Every started attempt completes this sequence before any retry, semantic result, or workflow exit.
Any safety terminal governs a coincident result. ATTEMPT_INVALID permits no Reviewer launch,
semantic classification, or retry; it stops Acceptance while preserving every obtainable
observation and residual fact.

### Judge attempts

After a safely finalized attempt, give the persistent case Reviewer the complete Candidate,
accepted behavior, frozen case, pass conditions, capture, permissions, termination, quiescence,
cleanup, and residual-state evidence. The Reviewer, not the Runner or Controller, classifies:

- PASS when every condition is observed and no critical Candidate defect remains;
- a supported Candidate finding;
- a fixture or environment defect with one exact preauthorized correction, or confirmation that
  none applies and no safe bounded recovery remains;
- CONTEXT_REQUIRED, ACCESS_REQUIRED, or HUMAN_DECISION_REQUIRED; or
- AMBIGUITY_OBSERVATION_REQUIRED with one exact targeted observation, bounded setup and capture
  delta, and evidence need within existing authority; after that observation, any remaining
  material ambiguity returns AMBIGUITY_UNRESOLVED.

A fixture or environment correction occurs between attempts and cannot change the Candidate, case,
or pass conditions. Retry with a fresh Runner and the same Reviewer. Stop NO_PROGRESS when the same
defect survives two correction attempts without new evidence or approach.

After an attempted case, a fixture or environment defect with no exact preauthorized correction
and no safe bounded recovery returns NO_PROGRESS. Missing required capability discovered before
launch remains EXECUTION_UNAVAILABLE under mode readiness.

For AMBIGUITY_OBSERVATION_REQUIRED, the Controller copies the Reviewer-owned request without
interpretation into one fresh frozen Attempt Contract. A fresh Runner performs it under the full
attempt safety sequence, then the same Reviewer reassesses the resulting evidence. Permit this
transition once per case and fingerprint; it changes neither case meaning nor pass conditions.

Executable Acceptance passes only when every frozen case passes on the current fingerprint, every
Runner is quiescent, cleanup is complete, no unsafe residual state remains, and all boundary checks
match. The final handoff records cases, attempts, observed evidence, cleanup, and residual state.
