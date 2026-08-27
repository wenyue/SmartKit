# Evaluation Lifecycle

This Design-time contract owns stage order and applicability, finding correction, Machine
Validation, Candidate Versions, Revision Impact, rewinds, replay, Scope Transfer, and global exits.
Freeze it into the Job Graph before any role or Candidate change.

## Freeze the proof path

| Order | Stage | Applicability and closure |
| --- | --- | --- |
| 1 | Quality | Always. Activate its frozen complete fresh cohort; it independently passes one Candidate Version. |
| 2 | Machine | Conditional on deterministic evidence for changed schema or metadata, references/resources, scripts, fixed flows, or sufficiently concrete/complex tools, permissions, filesystem state, procedure, or external effects. Broad judgment and high-confidence simple steps may be `NOT_REQUIRED`. |
| 3 | Correctness | Always after Machine `PASS` or valid `NOT_REQUIRED`. Activate its frozen complete fresh cohort; it independently passes one Candidate Version. |
| 4 | Acceptance | Conditional on concrete or sufficiently complex runtime behavior whose feasibility lacks high-confidence evidence. Load `acceptance.md` during Design or freeze `NOT_REQUIRED`. |

Acceptance signals include fixed multistep order, meaningful branching, retry, recovery or exit,
concrete tool calls, mutation, permission boundaries, external effects, or a Rule requiring such
behavior. A static walkthrough is not Acceptance. Design closes only when every applicability,
resource, identity schedule, dependency, transition, and exit is frozen.

Load this resource plus `reviews.md` completely during Design. Its cohort cardinalities,
assignments, correction duties, and replay states are immutable schedule inputs. Stage entry
activates those frozen facts and may add no identity, assignment, capacity, or transition.

## Treat findings as owned claims

A finding records stable ID, problem and accepted evidence, concrete counterexample, Candidate
location, severity, estimated Repair Scope, affected obligation or surface, preservation
constraints, and bounded repair direction rather than replacement prose. Use `N/A` with a reason
only where a field cannot apply.

- `critical`: semantic, authority, safety, ownership, executability, or exit failure.
- `material`: supported defect materially reducing information quality, reliability, or
  maintainability.
- `advisory`: smaller improvement or choice among valid solutions.

Critical and material claims normally merit repair; presume a small supported meaning-preserving
repair worth doing. The Author alone owns disposition. The finding owner alone decides whether the
claim remains and blocks its verdict. The full finding remains peer-only; the Reviewer exposes it
through the runtime `FINDING_READY → CHANNEL_OPEN` handshake.

## Run one independent correction unit

1. **Judge privately.** Give every cohort member the same complete Candidate Version, authorized
   evidence, unit, round, and independent-judgment boundary. Batching preserves those inputs. An
   eligible bounded update restarts that identity's private judgment.
2. **Open owning pairs.** For each recorded finding, emit the audited nonsemantic `FINDING_READY`
   result. After the Controller returns `CHANNEL_OPEN` for that prebound pair, send the complete
   finding directly to the Author. No Reviewer receives another's work.
3. **Choose privately.** The Author independently selects `repair`, `partial repair`, or `decline`,
   with an evidence-based reason. A partial repair identifies the retained claim and why.
4. **Deliberate directly.** Only the Author and finding owner exchange semantic content. Each
   assesses claims and reasons independently; agreement requires a reasoned bilateral fixed point.
   Candidate writes remain barred while any discussion is open.
5. **Close the round.** The Author freezes a disposition and the owner freezes the claim state,
   then both emit the runtime's nonsemantic `DISCUSSION_CLOSED` metadata. An owner may return
   current-version `PASS` only when no Candidate change is needed; otherwise the retained or revised
   finding remains pending through the write. Trust, voting, another Reviewer, and Controller
   interpretation decide nothing.
6. **Authorize one write.** After every cohort member finishes private judgment and every owning
   pair closes, the Controller issues one complete full-unit Repair Scope containing the unit,
   version, selected-for-write finding IDs and disposition metadata, authorized paths and modes,
   references to frozen preservation boundaries, and readiness state. It relays no semantic body.
   Only then may the same Author apply selected repairs.
7. **Recheck together.** A write creates a Candidate Version; every persistent cohort member
   independently rechecks the whole Candidate. Without a write, unaffected same-version `PASS`
   remains valid while finding owners reassess.

Consensus is independent `PASS` from the complete declared cohort on one Candidate Version and
evidence set. An open unit persists through local PASS. Reopening an invalidated closed unit
requires a wholly fresh cohort; prior identities and verdicts never return.

### Human stop and no progress

The first Author, Reviewer, or Controller `HUMAN_DECISION_REQUIRED` immediately ends all semantic
work and discussion. It is an owner-produced terminal control request, not a finding or discussion
body. Preserve only the exact decision, why evidence or authority cannot resolve it, decision
owner, and consequences of every live choice. Provisional findings, dispositions, and verdicts
become non-operative. Audit and finalize, then deliver the request unchanged. The human answer
starts a new run.

A disagreement round completes when the Author freezes a disposition and the finding owner
reassesses without resolution. Initial judgment is not a round. Stop `NO_PROGRESS` after the same
disagreement completes two consecutive rounds without new evidence or a supported approach.

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
recipient independently inspects the complete Candidate and evidence. A note that may affect
passed proof invalidates that proof; the note acquires no semantic owner.

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
   version, or evidence.

Repeat after every write. No verdict survives a change that may affect its proof.

## Select the global exit

A Role Boundary Audit first decides invocation and callback admissibility. An inadmissible callback
normally contributes no payload result. The sole terminal-control exception is an authenticated,
attributable Author or Reviewer `HUMAN_DECISION_REQUIRED` whose exact request is obtainable. Stop
semantic work immediately, preserve and deliver that request unchanged, and require human
adjudication before a new run. Consume no other callback content or Candidate evidence. Finish any
started conditional execution under its safety contract and finalize the workflow; report the
external result as `HUMAN_DECISION_REQUIRED` while retaining `ROLE_BOUNDARY_VIOLATION` as underlying
audit evidence. If attribution or the exact request is unproven, this exception does not apply.

For every other inadmissible invocation or callback and every semantic-role incident, finish any
started conditional execution under its safety contract; its higher safety terminal governs when
one applies. Otherwise discard the inadmissible payload and preserve Candidate, audit, and residual
state. The Controller judges case by case whether Author or Reviewer behavior stayed within the
frozen boundaries and may intervene proportionately to enforce the control plane, never to decide
Candidate meaning, finding merit, or a semantic fixed point. When the contamination boundary is
proven, invalidate only the smallest affected unit while preserving its classification and every
established state outside it. When isolation cannot be proven, the incident classification becomes
a whole-run terminal and the workflow finalizes. An inadmissible invocation or callback is
`ROLE_BOUNDARY_VIOLATION`.

For admissible state, choose the first matching result:

1. first `HUMAN_DECISION_REQUIRED`: end semantic work and preserve its request for a new run;
2. `LOCK_UNAVAILABLE` or `CANDIDATE_CHANGED`: stop before Author change and preserve lock/baseline
   evidence;
3. started conditional execution: complete its safety finalization; its terminal governs, while
   successful finalization returns to the stage lifecycle;
4. whole-run `SEMANTIC_ROLE_UNAVAILABLE`: a semantic role meets its frozen abnormal-execution
   trigger without evidence of a boundary breach and isolation cannot be proven; preserve identity,
   channel, termination, and residual evidence;
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
