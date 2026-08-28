# Evaluation Lifecycle

This Design-time contract is the sole semantic owner of finding classification, disposition,
fixed-point, closure, correction, and consensus. It also owns stage order and applicability,
Machine Validation, Candidate Versions, Revision Impact, rewinds, replay, Scope Transfer, and
global exits. [`role-launch.md`](role-launch.md) owns authenticated transport and its nonsemantic
control metadata. Freeze both into the Job Graph before any role or Candidate change.

## Freeze the proof path

| Order | Stage | Applicability and closure |
| --- | --- | --- |
| 1 | Quality | Always. Activate its frozen complete fresh cohort; it independently passes one Candidate Version. |
| 2 | Machine | Conditional on deterministic evidence for changed schema or metadata, references/resources, scripts, fixed flows, or sufficiently concrete/complex tools, permissions, filesystem state, procedure, or external effects. Broad judgment and high-confidence simple steps may be `NOT_REQUIRED`. |
| 3 | Correctness | Always after Machine `PASS` or valid `NOT_REQUIRED`. Activate its frozen complete fresh cohort; it independently passes one Candidate Version. |
| 4 | Acceptance | Conditional on concrete or sufficiently complex runtime behavior whose feasibility lacks high-confidence evidence. Design freezes the stage as applicable with its complete contract contributions, or `NOT_REQUIRED`. |

Acceptance signals include fixed multistep order, meaningful branching, retry, recovery or exit,
concrete tool calls, mutation, permission boundaries, external effects, or a Rule requiring such
behavior. A static walkthrough is not Acceptance. Design closes only when every applicability,
resource, identity schedule, dependency, transition, and exit is frozen.

Freeze this lifecycle's correction and replay states and the review contracts' cohort
cardinalities, assignments, and correction duties as immutable schedule inputs. Stage entry
activates those frozen facts and may add no identity, assignment, capacity, or transition.

## Treat findings as owned claims

A finding records stable ID, problem and supported evidence with its owner and provenance,
the observed answer or supported counterexample, Candidate location, severity, unchanged impact,
estimated Repair Scope, affected obligation or surface, preservation constraints, and bounded
repair direction rather than replacement prose. Use `N/A` with a reason only where a field cannot
apply. A review question is only an investigation mechanism; a finding is the resulting supported
declarative claim. Never fabricate a counterexample to complete the record.

- `critical`: semantic, authority, safety, ownership, executability, or exit failure.
- `material`: supported defect materially reducing information quality, reliability, or
  maintainability.
- `advisory`: supported smaller improvement or valid-choice opportunity whose complete repair and
  replay scope is bounded enough to merit presentation.

Critical and material findings are blocking and require the bilateral lifecycle below. Advisory
findings are nonblocking; the Author alone selects repair, partial repair, or decline and supplies
an evidence-based reason. The finding owner alone owns claim validity and severity and may upgrade
an advisory only with new supported evidence. Severity describes impact if the Candidate remains
unchanged. Estimated Repair Scope describes cost and risk and never reduces severity; a contract
violation remains critical regardless of repair size. Pure taste, symmetry, file length, or
cheapness alone establishes no defect. The full finding remains peer-only; the Reviewer exposes it
through the runtime `FINDING_READY → CHANNEL_OPEN` handshake.

## Run one independent correction unit

1. **Judge privately.** Give every cohort member the same complete Candidate Version, supplied
   evidence, frozen evidence-selection policy and grants, unit, round, and independent-judgment
   boundary. Each judges without receiving the Author's reasoning or another Reviewer's work.
   Each fixes its complete finding set before emitting any finding. Batching preserves the common
   inputs. An eligible bounded update restarts that identity's private judgment.
2. **Open owning pairs.** For each recorded finding, emit Role Launch's audited nonsemantic
   `FINDING_READY` result and finding-set-completion evidence. After the Controller returns
   `CHANNEL_OPEN` for that prebound pair, send the complete finding directly to the Author. No
   Reviewer receives another's work.
3. **Choose privately.** The Author independently selects `repair`, `partial repair`, or `decline`
   for every finding, with an evidence-based reason. A partial repair identifies the retained claim
   and why.
4. **Assess the owned outcome.** For a critical or material finding, only the Author and finding
   owner deliberate directly over semantic content, including newly discovered supported evidence.
   Each assesses claims, reasons, support, and provenance independently; transmission grants no
   authority. For a blocking finding, a reasoned bilateral fixed point exists only when the owner
   no longer upholds a blocking claim without a write, or both independently agree that a selected
   repair or partial repair addresses every upheld blocking part pending write and recheck. When
   the owner still upholds a blocker and the Author declines, retains a blocking part, or proposes
   a path the owner finds non-resolving, fixed point is not reached and no write is selected from
   that unresolved path. For an advisory, the owner may answer or clarify the claim, but the Author
   alone freezes its disposition and reason; bilateral fixed point does not apply. Candidate writes
   remain barred while any channel is open. Evidence that changes only the current claim stays in
   that claim's lifecycle. Apply the finding-set reopening transition below only when newly
   available supported evidence independently supports a distinct unreported finding.
5. **Close the communication round.** After the Author freezes each disposition and the owner
   freezes each claim state, both emit the runtime's nonsemantic `DISCUSSION_CLOSED` metadata
   whether or not a blocking fixed point was reached. This event closes only the channel and round;
   it never establishes claim resolution. Its fixed-point control value is `reached` only for a
   resolving blocking outcome defined above, `not reached` whenever an upheld blocker lacks an
   agreed resolving path, and `not applicable` for an advisory. An unresolved blocking disagreement
   remains blocking, selects no write, and may enter the next frozen round through the existing
   `FINDING_READY → CHANNEL_OPEN` handshake after the current round closes.

   Before closing, an owner that has independently established a distinct unreported finding from
   newly available supported evidence fixes that finding and opaque ID and sets finding-set state
   to `reopened`; otherwise the state remains `complete`. Reopening invalidates prior completion
   evidence, is eligible only for newly available evidence, and must add at least one distinct ID.
   After every currently open channel closes, the same persistent Reviewer restarts private
   judgment on the unchanged Candidate Version with accumulated authorized evidence, emits each
   newly fixed finding through Role Launch, and restores completion on its final emission. An
   advisory owner may upgrade only upon new supported evidence; the upgraded claim then follows the
   blocking lifecycle. A Reviewer may return current-version `PASS` only when no unresolved
   blocking finding remains, every owned advisory has a frozen disposition, the latest finding-set
   state is complete, and no selected repair awaits its write. Trust, voting, another Reviewer, and
   Controller interpretation decide nothing.
6. **Authorize one write.** After every cohort member has supplied Role Launch's audited
   finding-set-completion evidence, every latest finding-set state is complete, and every emitted
   owning pair closes, batch all accepted blocking and advisory repairs in one complete full-unit
   Repair Scope containing the unit, version, selected-for-write finding IDs, disposition control
   metadata (class and selected-for-write state), authorized paths and modes, references to frozen
   preservation boundaries, and readiness state. It relays no semantic disposition body. Only then
   may the same Author apply the selected repairs.
7. **Recheck together.** A write creates a Candidate Version; every persistent cohort member
   independently rechecks the whole Candidate. Without a write, unaffected same-version `PASS`
   remains valid while blocking finding owners reassess; a declined advisory remains closed.

Consensus is independent `PASS` from the complete declared cohort on one Candidate Version with no
unresolved blocking finding and a frozen Author disposition for every advisory, using the same
supplied evidence, evidence-selection policy, and grants. An open unit persists through local
PASS. Reopening an invalidated closed unit requires a wholly fresh cohort; prior identities and
verdicts never return.

### Human stop and no progress

The first Author, Reviewer, or Controller `HUMAN_DECISION_REQUIRED` immediately ends all semantic
work and discussion. It is an owner-produced terminal control request, not a finding or discussion
body. Preserve only the exact decision, why evidence or authority cannot resolve it, decision
owner, and consequences of every live choice. Provisional findings, dispositions, and verdicts
become non-operative. Audit and finalize, then deliver the request unchanged. The human answer
starts a new run.

A blocking disagreement round counts when both peers close it with fixed-point control value
`not reached` and the claim remains unresolved. Initial private judgment is not a round. Stop
`NO_PROGRESS` after the same blocking disagreement completes two consecutive counted rounds
without new evidence or a supported approach. Advisory repair, partial repair, or decline closes
on the Author's frozen disposition and never enters disagreement or `NO_PROGRESS`.

## Validate deterministic facts

When Machine applies, run only non-fixing checks supported by affected owners: frontmatter or
schema validation, registration/metadata consistency, reference existence, owned scripts,
generated adapters, formatting, and repository tests. Invent no check merely to avoid
`NOT_REQUIRED`.

Fingerprint immediately before and after every command. Preserve and stop on an unattributable or
unauthorized change. Record exact command, exit, and relevant output. Give failure evidence to the
same Author in one complete Machine Repair Scope; rerun failed, invalidated, and dependent checks.
One Machine disagreement round is failure, repair, and rerun. Stop `NO_PROGRESS` after the same
failure survives two consecutive rounds without new evidence or approach.

Machine passes only when every applicable check passes one Candidate Version. Retain evidence only
when later changes cannot affect what it proves, then apply Revision Impact to Quality.

## Transfer scope without transferring judgment

A Reviewer may attach one **Scope Transfer Note** containing only Candidate location, intended
owner, and responsibility to inspect. It is not a finding and carries no observation, argument,
evidence, disposition, rationale, or verdict. Route it once to another current-cohort Reviewer, a
later stage before that stage starts, or an earlier passed stage after current local PASS. The
recipient independently inspects the complete Candidate and its authorized evidence sources.

When the frozen graph permits a later-stage note to an earlier passed unit, local PASS leaves that
earlier unit open and its complete cohort suspended through the declared transfer window. Resume
only the intended responsibility owner for inspection; no identity from a closed unit returns.
Close the earlier unit only after no later note can arrive and no routed inspection remains. A note
with no supported finding leaves passed proof valid. The note alone does not alter a verdict or
invalidate proof and acquires no semantic owner. A recipient-supported blocking finding invalidates
affected passed proof through the ordinary finding, rewind, and replay lifecycle. A
recipient-supported advisory remains nonblocking: decline leaves passed proof valid, while an
accepted write uses ordinary Revision Impact.

## Revise, rewind, and replay

Revision Impact uses the Author Change Summary, changed paths, whole-Allowlist fingerprints,
operation records, and a targeted diff only when necessary. After every write:

1. The affected live unit first reaches local PASS on the complete new Candidate Version.
2. Identify the earliest passed proof the change may affect. Future stages have no proof to
   invalidate; preserve only evidence demonstrably unaffected.
3. Reopen that earliest invalidated stage and every intervening dependency in frozen order. Bind a
   complete fresh cohort for each invalidated closed Quality or Correctness unit.
4. Apply each conditional authority's frozen retention and replay schedule. Retained live workers
   continue consuming `P`; batch fresh cohorts in the remaining pool without changing cohort,
   version, supplied evidence, or discovery grants.

Repeat after every write. No verdict survives a change that may affect its proof.

## Select the global exit

A Role Boundary Audit first decides invocation and callback admissibility. An inadmissible callback
normally contributes no payload result. When that audit establishes Role Launch's attributable
terminal-control exception, stop semantic work immediately, preserve and deliver the exact human
request unchanged, and require adjudication before a new run. Consume no other callback content or
Candidate evidence. Finish any started conditional execution under its safety contract and
finalize the workflow; report the external result as `HUMAN_DECISION_REQUIRED` while retaining
`ROLE_BOUNDARY_VIOLATION` as underlying audit evidence. Every other audited inadmissible state
follows the ordinary path below.

For every other inadmissible invocation or callback and every semantic-role incident, finish any
started conditional execution under its safety contract; its higher safety terminal governs when
one applies. Otherwise discard the inadmissible payload and preserve Candidate, audit, and residual
state. The Controller judges case by case whether Author or Reviewer behavior stayed within the
frozen boundaries and may intervene proportionately to enforce the control plane, never to decide
Candidate meaning, finding merit, or a semantic fixed point. When the contamination boundary is
proven, invalidate only the smallest affected unit while preserving its classification and every
established state outside it. An established `SEMANTIC_ROLE_UNAVAILABLE` is a whole-run terminal
because its required identity cannot be replaced. When isolation cannot be proven, every other
incident classification becomes a whole-run terminal and the workflow finalizes. An inadmissible
invocation or callback is `ROLE_BOUNDARY_VIOLATION`.

For admissible state, choose the first matching result:

1. first `HUMAN_DECISION_REQUIRED`: end semantic work and preserve its request for a new run;
2. `LOCK_UNAVAILABLE` or `CANDIDATE_CHANGED`: stop before Author change and preserve lock/baseline
   evidence;
3. started conditional execution: complete its safety finalization; its terminal governs, while
   successful finalization returns to the stage lifecycle;
4. whole-run `SEMANTIC_ROLE_UNAVAILABLE`: a semantic role meets its frozen abnormal-execution
   trigger without evidence of a boundary breach; preserve identity, channel, termination, and
   residual evidence;
5. `HOST_UNAVAILABLE`: the host cannot establish or supply the correctly derived and frozen
   capacity, identity, authenticated channel, schedule, or evidence;
6. unavailable eligible `CONTEXT_REQUIRED` or `ACCESS_REQUIRED`; an out-of-envelope request becomes
   `ALIGNMENT_REQUIRED` for a new run;
7. stage terminal such as `AMBIGUITY_UNRESOLVED`, `NO_PROGRESS`, or `EXECUTION_UNAVAILABLE`;
8. same-version stage `PASS` or valid `NOT_REQUIRED`: advance; graph closure permits success only
   after workflow finalization.

Controller oversubscription takes the inadmissible boundary path, never `HOST_UNAVAILABLE`. A lower
result cannot erase higher-priority evidence or required safety finalization. `TEARDOWN_FAILED`
preserves the underlying result and blocks clean success.
