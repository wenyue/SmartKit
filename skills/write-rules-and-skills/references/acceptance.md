# Executable Acceptance

## Decide whether Acceptance is required

Run Acceptance only when the candidate governs concrete or sufficiently complex runtime behavior
whose feasibility is not already established with high confidence by static review, machine checks,
or an accepted mechanism. Relevant signals include a fixed multi-step sequence, meaningful branch,
retry, recovery, exit, concrete tool call, file mutation, permission boundary, external side effect,
or a Rule that mandates such behavior.

Broad judgment guidance, a simple non-tool procedure, or behavior already supported with high
confidence does not require Acceptance. Record `NOT_REQUIRED` and skip the stage entirely. Do not
replace it with a static walkthrough called Acceptance.

## Freeze the portfolio

Before execution, freeze the representative cases and observable pass conditions. Use the smallest
portfolio that covers the material runtime risk: normally a success path and each materially
distinct error, recovery, or exit affected by the candidate. Do not impose a fixed case count.
Execute cases sequentially from highest risk to lowest.

## Execute and judge

For each attempt, the Controller prepares the disposable Execution Isolation, fixture, exact
case-scoped `read`, `write`, `create`, `delete`, and tool grants, observable-evidence capture, and
cleanup required by the selected Adapter. Keep the Candidate immutable. If any required permission,
safe isolation, or existing authority is unavailable, stop as `EXECUTION_UNAVAILABLE`, report the
untested surface, and do not issue `PASS` or `NOT_REQUIRED`. Network access or an external effect is
eligible only when the accepted task already grants explicit authority for that case and the
selected Adapter supports it.

For every attempt, start a fresh Runner in that Execution Isolation with
only the read-only Candidate, frozen case, fixture, exact case grants and permitted tools, and
observable pass conditions needed for that case. The Runner executes; it does not judge or repair
the Candidate, fixture, or environment.

### Finalize every started attempt

Once a Runner starts, the Controller enters finalization for that attempt whether the Runner
succeeds, fails, or cannot return normally, and whether evidence capture or the Role Boundary Audit
succeeds or fails. Preserve all obtainable observable evidence first, including any available
terminal Runner report, and record any capture failure. Then use the selected Adapter to finish,
stop, or otherwise end the Runner and establish quiescence, including after abnormal or non-returning
execution. Preserve any additional termination evidence. Only after quiescence is established may
the Controller attempt cleanup using the exact safe case-owned targets and grants already authorized
for the disposable isolation; never broaden authority or use an unsafe or broad deletion. If cleanup
fails, make at most one supported bounded recovery attempt, and only when it is safe and already
authorized. This is the attempt's single cleanup-recovery allowance.

A Role Boundary Audit violation has terminal precedence, but it does not prohibit safe cleanup when
the Runner is quiescent. If quiescence cannot be established, retain all obtainable evidence and
skip cleanup. After the termination attempt, fingerprint audit, and any cleanup permitted by
quiescence, select the attempt result in this priority:

1. Any Role Boundary Audit violation or evidence-capture failure yields `ATTEMPT_INVALID`,
   regardless of quiescence or cleanup.
2. Otherwise, failure to establish quiescence yields `RUNNER_NOT_QUIESCENT`.
3. Otherwise, failed cleanup after its one safe authorized bounded recovery, or absence of such a
   recovery, yields `CLEANUP_FAILED`.
4. Otherwise, finalization succeeds.

For any terminal result, report all obtainable evidence, any violation or capture failure,
quiescence and residual state, cleanup result, and the one bounded cleanup recovery attempted or why
none was available. Stop without creating or resuming a Reviewer or starting another attempt. No
terminal result is Candidate PASS, `NOT_REQUIRED`, or a fixture/environment defect.

If a case's first attempt reaches a terminal result, stop without starting an Acceptance Reviewer.
Finalization succeeds only when evidence capture, audit, Runner quiescence, and required cleanup all
complete successfully. Successful finalization does not make the case PASS. After the first attempt
finalizes successfully, start one fresh Acceptance Reviewer with the complete Candidate Version,
accepted behavior and governing evidence, frozen case and observable pass criteria, fixture and
permission boundary, and captured execution and finalization evidence. For every later successfully
finalized attempt in that case, resume the same Reviewer with the new captured evidence. Keep that
Reviewer through classifications, Candidate correction, fixture or environment recovery, ambiguity
observation, and case PASS. Retain only the current case's Reviewer; close it after case PASS. Apply
the common Correction Cycle packet on recheck.

When the observation satisfies the frozen pass conditions and supports no Candidate finding, the
Reviewer returns normal `PASS`. A Candidate defect returns one or more findings under the complete
common finding schema; the Controller sends them as one Repair Scope to the persistent Author and
continues the same Reviewer's Correction Cycle. When no Candidate defect is supported and the
observation fails or cannot conclusively satisfy the frozen pass conditions, the Reviewer returns
exactly one of two Acceptance-only classifications:

- `fixture/environment defect`: the payload names the evidenced defect and either the exact
  already-authorized bounded fixture or environment correction or states that none is available.
  The Controller performs only that supplied correction, launches a fresh Runner under the normal
  attempt contract, finalizes that attempt, and resumes the same Reviewer; when none is available,
  it uses the applicable prioritized exit below without inventing recovery; or
- `ambiguous`: the Controller launches the payload's exact targeted observation as a normal
  fresh-Runner attempt. The payload names the unresolved alternatives and the bounded setup and
  evidence-capture delta needed to distinguish them. The attempt remains inside existing authority
  and uses its required setup, audit, evidence capture, cleanup, and finalization; the Controller
  then resumes the same Reviewer and stops if the classification remains ambiguous.

Keep the frozen case and pass criteria through fixture/environment recovery. Each supported
correction attempt changes only the bounded fixture or environment. Stop as `NO_PROGRESS` when the
same defect recurs after two consecutive correction attempts or when no new safe bounded recovery remains; use
`EXECUTION_UNAVAILABLE` instead when a required environment capability is unavailable. Report the
attempts and terminal evidence. The single targeted fresh observation above remains the only retry
for an ambiguous classification.

## Rewind and replay cases

Stage-local PASS means the current Acceptance Reviewer finds nothing worth fixing for its case on
the current Candidate Version after successful finalization. It ends that Reviewer's correction
cycle when replay scheduling requires it, but it is not Acceptance PASS.

After an Author correction, keep the same Reviewer, run a fresh attempt, and obtain Stage-local PASS
for the current case before the Controller performs the Revision Impact Decision. Only after that
PASS:

- If an earlier non-Acceptance stage is invalidated, retain the current case's Reviewer as the one
  paused fifth identity while restoring the earliest invalidated and intervening stages with fresh
  Reviewers for closed review units. Then run the case again, resume that same Acceptance Reviewer
  with the successfully finalized evidence, obtain Stage-local PASS, and make the next Revision
  Impact Decision.
- If an already-passed earlier Acceptance case is invalidated, do not start its fresh Reviewer
  while retaining the current Reviewer. On the same Candidate Version, record the current case PASS
  at Stage-local PASS and close its Reviewer before restarting sequential evaluation at the earliest
  invalidated Acceptance case in the frozen highest-risk-to-lowest order. Preserve that current
  case evidence unless a later Author change can affect it; normal Revision Impact then invalidates
  and reruns every affected case. For each invalidated case when reached, run and successfully
  finalize its first fresh-Runner attempt before starting its fresh Reviewer; preserve and skip
  other unaffected case evidence.
- If no earlier stage or case is invalidated, record case PASS and close the current Reviewer.

Keep only one Acceptance Reviewer current or retained during replay. A replay correction repeats
the Stage-local-PASS-first rule, never retains one case Reviewer while starting another, and never
requires more than the qualified single paused fifth identity. Acceptance passes only when every
frozen case has Reviewer-owned case PASS supported by successful finalization and unaffected
evidence for the current Candidate Version.
