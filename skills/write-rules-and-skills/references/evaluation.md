# Evaluation Lifecycle

This contract owns public Quality and Correctness finding semantics and consensus, proof order and
applicability, Machine Validation, Revision Impact and replay, Scope Transfer, and global exits.
Later lens contracts own eligibility and verdict conditions. Job Design owns fingerprints, deltas,
and proof-state promotion;
Role Runtime owns transport and control metadata. Freeze all before any role or Candidate change.

## Freeze the proof path

| Order | Stage | Applicability and closure |
| --- | --- | --- |
| 1 | Quality | Always. Activate its complete frozen cohort. Current closure requires every independent PASS and required coverage record on one Candidate fingerprint. |
| 2 | Machine | Conditional on deterministic evidence for changed schema or metadata, references/resources, scripts, fixed flows, or sufficiently concrete/complex tools, permissions, filesystem state, procedure, or external effects. Broad judgment and high-confidence simple steps may be `NOT_REQUIRED`. |
| 3 | Correctness | Always after Machine `PASS` or valid `NOT_REQUIRED`. Activate its frozen complete fresh cohort; it independently returns PASS bound to one exact Candidate fingerprint. |
| 4 | Acceptance | Conditional on concrete or sufficiently complex runtime behavior whose feasibility lacks high-confidence evidence. Design freezes the stage as applicable with its complete contract contributions, or `NOT_REQUIRED`. |

Acceptance signals are fixed multistep order, meaningful branches, retry, recovery or exit,
concrete tools, mutation, permissions, external effects, or a Rule requiring them. A walkthrough
does not qualify. Freeze every applicability, resource, identity, dependency, transition, and exit.

Contribute this lifecycle's correction and replay states plus later lens-contract schedule inputs
to Job Design's generic schedule manifest.

## Treat findings as owned claims

A finding records its stable ID; problem and supporting evidence with owner and provenance; observed
answer or supported counterexample; Candidate location; severity; unchanged impact; estimated
Repair Scope; affected obligation or surface; preservation constraints; and bounded repair
direction, not replacement prose. Use reasoned `N/A` only where a field cannot apply. A review
question investigates; a finding is its supported declarative claim.

- `critical`: semantic, authority, safety, ownership, executability, or exit failure.
- `material`: supported defect materially reducing information quality, reliability, or
  maintainability.
- `advisory`: supported smaller improvement or valid-choice opportunity whose complete repair and
  replay scope is bounded enough to merit presentation.

Critical and material findings are blocking and use the bilateral lifecycle below. Advisories are
nonblocking; the Author alone selects repair, partial repair, or decline with an evidence-based
reason. The finding owner alone owns claim validity and severity and may upgrade an advisory only
with new supported evidence. Severity is unchanged-Candidate impact; estimated Repair Scope is
cost and risk and never reduces severity. A contract violation remains critical regardless of
repair size. Taste, symmetry, file length, or cheapness alone establishes no defect. The full
finding remains peer-only and enters through `FINDING_READY → CHANNEL_OPEN`.

## Run one independent correction unit

1. **Judge privately.** Give each member the common complete inputs plus only its frozen
   scope-specific evidence. It fixes its complete finding set without Author reasoning or another
   Reviewer's work. Batching preserves inputs; a bounded update restarts that identity's judgment.
2. **Open owning pairs.** Emit audited `FINDING_READY` and completion evidence for each finding.
   After `CHANNEL_OPEN`, send it directly to the Author; no Reviewer receives another's work.
3. **Choose privately.** The Author selects `repair`, `partial repair`, or `decline` with an
   evidence-based reason; partial repair identifies and explains the retained claim.
4. **Assess the owned outcome.** For a critical or material finding, only the Author and finding
   owner deliberate directly over semantic content, including newly discovered supported evidence.
   Each assesses claims, reasons, support, and provenance independently; transmission grants no
   authority. A blocking finding reaches reasoned bilateral fixed point only when the owner
   no longer upholds a blocking claim without a write, or both independently agree that a selected
   repair or partial repair addresses every upheld blocking part pending write and recheck. When
   the owner still upholds a blocker and the Author declines, retains a blocking part, or proposes
   a path the owner finds non-resolving, fixed point is not reached and no write is selected from
   that unresolved path. For an advisory, the owner may answer or clarify the claim, but the Author
   alone freezes its disposition and reason; bilateral fixed point does not apply. Candidate writes
   remain barred while any channel is open. Evidence changing only the current claim stays in its
   lifecycle. Reopen the finding set only when newly available supported evidence independently
   supports a distinct unreported finding.
5. **Close the communication round.** After the Author freezes each disposition and the owner
   freezes each claim's validity and severity, both emit the runtime's nonsemantic
   `DISCUSSION_CLOSED` metadata
   whether or not a blocking fixed point was reached. This event closes only the channel and round;
   it never establishes claim resolution. Its fixed-point control value is `reached` only for a
   resolving blocking outcome defined above, `not reached` whenever an upheld blocker lacks an
   agreed resolving path, and `not applicable` for an advisory. An unresolved blocking disagreement
   remains blocking and selects no write. It may enter the next frozen round only after the current
   round closes and the pair repeats `FINDING_READY → CHANNEL_OPEN` with current round and Candidate
   fingerprint metadata.

   Before closing, an owner that has independently established a distinct unreported finding from
   newly available supported evidence fixes that finding and opaque ID and sets finding-set state
   to `reopened`; otherwise the state remains `complete`. Reopening invalidates prior completion
   evidence, is eligible only for newly available evidence, and must add at least one distinct ID.
   After all open channels close, the same persistent Reviewer restarts private judgment on the
   unchanged Candidate fingerprint with accumulated authorized evidence, emits each newly fixed finding
   through Role Runtime, and restores completion on the last. An advisory owner may upgrade only
   with new supported evidence; the upgraded claim then follows the blocking lifecycle. A Reviewer
   may return `PASS` for the current fingerprint only when no unresolved
   blocking finding remains, every owned advisory has a frozen disposition, the latest finding-set
   state is complete, and no selected repair awaits its write. Trust, voting, another Reviewer, and
   Controller interpretation decide nothing.
6. **Select the write branch.** After all completion evidence is audited, latest finding sets are
   complete, and all pairs close, inspect only Role Runtime's authenticated scope-control aggregate.
   With zero selected writes, create no Repair Scope and invoke no Author; same-fingerprint
   Reviewers either `PASS` when eligible or a blocking owner enters the next authorized round. With
   one or more selected writes, freeze-copy the exact aggregate into one full-unit Repair Scope:
   unit, fingerprint, selected IDs and disposition control, paths and modes, preservation-reference
   IDs, and readiness—never a semantic body. Missing or mismatched scope control follows Role
   Runtime's inadmissible-callback path. Only then may the same Author write.
7. **Recheck together.** After an authorized write and admissible `COMPLETE` promote the
   invocation-final fingerprint,
   every persistent member rechecks the whole Candidate. Unpromoted fingerprints start no proof;
   without promotion, unaffected same-fingerprint `PASS` and declined advisories remain closed
   while blocking owners reassess.

Consensus is independent owner-produced `PASS` from the complete declared cohort, with every
conclusion satisfying current closure for one promoted Candidate fingerprint in expected proof
state, no unresolved blocker, and a frozen Author disposition for every advisory. Quality also
requires every mechanically admitted coverage record declared by its lens contract; an absent or
incomplete record cannot become `PASS`. An open unit persists through local PASS. Reopening an
invalidated closed unit requires a wholly fresh cohort; prior identities and verdicts never return.

### Human stop and no progress

The first Author, Reviewer, or Controller `HUMAN_DECISION_REQUIRED` immediately ends all semantic
work and discussion. Preserve its exact decision, unresolved reason, owner, and live-choice
consequences; all provisional semantic work becomes non-operative. For an Author, apply Job
Design's human-stop transition and retain independent mismatch classifications. Complete
conditional safety and finalization; absent a higher safety terminal, deliver the request unchanged
and continue only in a new run after the answer.

A blocking disagreement round counts when both peers close it as `not reached` and the claim
remains unresolved; initial private judgment is not a round. Stop `NO_PROGRESS` after the same
blocker completes two consecutive counted rounds without new evidence or a supported approach.
Advisories close on the Author's frozen repair, partial repair, or decline and never enter
disagreement or `NO_PROGRESS`.

## Validate deterministic facts

When Machine applies, run only affected-owner-supported non-fixing checks: frontmatter or schema,
registration/metadata consistency, reference existence, owned scripts, generated adapters,
formatting, and repository tests. Invent no check to avoid `NOT_REQUIRED`.

Fingerprint around every command and apply Job Design's standalone mismatch composition; Machine
contains no authorized Author write. On mismatch preserve class evidence and stop. Always record
exact command, exit, and relevant output.
Give failure evidence to the same Author in one complete Machine Repair Scope; rerun failed,
invalidated, and dependent checks. One Machine correction round is failure, repair, and rerun. Stop
`NO_PROGRESS` after the same failure survives two consecutive rounds without new evidence or
approach.

Machine closure requires every check, or `NOT_REQUIRED`, bound to the current fingerprint or carried
by an exact Revision Impact compatibility binding. Otherwise use the preauthorized proof-owner route
when eligible or rerun, then apply Revision Impact to Quality.

## Transfer scope without transferring judgment

A **Scope Transfer Note** contains only Candidate location, intended owner, and inspection
responsibility—no observation, evidence, rationale, disposition, or verdict. Route it once to a
current-cohort Reviewer, an unstarted later stage, or an earlier passed stage after local PASS; the
recipient inspects independently.

A permitted note to an earlier passed unit keeps that unit open and its cohort suspended through
the transfer window; resume only the intended owner and close after all possible notes and
inspections end. The note alone changes no verdict. A recipient-supported blocker uses ordinary
invalidation/replay; an advisory remains nonblocking unless its accepted write triggers Revision
Impact.

## Revise, rewind, and replay

After every promotion, Revision Impact uses the Author summary, Operation Report, current promoted
fingerprint, canonical delta, and their baseline/proof-state bindings; compare Candidate directly
only when those cannot resolve impact.

Evidence is content-dependent only when its conclusion may change with Candidate bytes, meaning,
paths, or delta. Identity-only fingerprint use is not; preserve unrelated transport, audit,
lifecycle, and control evidence.

An immutable **Revision Impact compatibility binding** records original and target fingerprints,
the unchanged owner conclusion and callback, provenance, canonical delta and impact evidence, and
the mechanical content-unaffected determination under the proof class's frozen manifest.

The Controller binds only when delta, surfaces, and provenance satisfy every observable predicate;
it cannot infer criteria or alter conclusions, callbacks, fingerprints, or provenance. The binding
changes neither Candidate identity, Frozen Run Contract, nor control evidence.

Semantic or indeterminate impact produces no compatibility binding. Route it to the explicitly
preauthorized proof owner through that owner's existing frozen assessment or recheck lifecycle only
when the identity and lifecycle still permit; any result is newly owner-produced and bound to the
current fingerprint. Otherwise apply ordinary invalidation, rewind, and replay.

Proof satisfies **current closure** only when the owner-produced conclusion is bound to the current
fingerprint or the unchanged original conclusion has an exact compatibility binding from its
fingerprint to the current fingerprint. Each further fingerprint change requires its own binding.
Affected or indeterminate proof receives none and follows the existing invalidation, rewind, and
replay path.

An Acceptance correction returns control here while retaining its case Reviewer. Evaluation
restores invalidated earlier stages in order, then Acceptance reruns the case before another impact
decision; Acceptance orchestrates no earlier stage.

1. The affected live unit first reaches local PASS bound to the complete new Candidate fingerprint.
2. Identify the earliest passed proof the change may affect. Future stages have no proof to
   invalidate. Preserve only evidence whose frozen observable criteria mechanically prove
   non-impact, and record the exact Revision Impact compatibility binding for each preserved
   conclusion.
3. Reopen that earliest invalidated stage and every intervening dependency in frozen order. A
   changed fingerprint's newly derived delta invalidates only reviews, callbacks, or other evidence
   whose content-dependent conclusion may be affected; an unchanged no-op retains unaffected
   evidence under these Revision Impact rules. Each fingerprint-bound delta remains immutable.
   Prebind a complete fresh cohort for each invalidated closed Quality or Correctness unit before
   its first action. Repeated invalidation uses wholly new membership; no prior identity or verdict
   returns.
4. Apply each conditional authority's frozen retention and replay schedule. Retained live workers
   continue consuming `P`; batch fresh cohorts in the remaining pool without changing cohort,
   fingerprint, supplied evidence, or discovery grants.

Repeat after every promotion. No verdict survives a promoted change that may affect its proof.

## Select the global exit

Consume Role Runtime's audited callback result and Job Design's selected proof-state transition.
Authenticated `HUMAN_DECISION_REQUIRED` applies [Human stop](#human-stop-and-no-progress) before
every other result; any other inadmissible payload is discarded.

The Controller may contain a remaining incident locally only when its contamination boundary is
proven and Candidate exactly matches expected proof state; invalidate the smallest affected unit,
preserve its classification and all state outside it, and continue only through an already frozen
identity and lifecycle path. An established `SEMANTIC_ROLE_UNAVAILABLE` is whole-run because its
required identity cannot be replaced. A changed invocation with inadmissible Author callback is
whole-run `ROLE_BOUNDARY_VIOLATION`; any other incident without exact proof-state match and isolation
is also whole-run. The Controller judges only boundary conformance and containment, never Candidate
meaning or findings.

Before issuing any global result, finish every started conditional execution under its safety
contract. Its safety terminal governs when one arises while preserving the pending underlying
result; successful safety finalization returns to the selection below. Then choose the first
matching result:

1. first `HUMAN_DECISION_REQUIRED`: end semantic work and preserve its request for a new run;
2. `CANDIDATE_CHANGED`: apply Frozen Job Design's selected no-promotion transition, then stop;
3. whole-run `ROLE_BOUNDARY_VIOLATION`: preserve its forensic state and audit evidence, promote
   nothing, and stop without semantic continuation;
4. whole-run `SEMANTIC_ROLE_UNAVAILABLE`: a semantic role meets its frozen abnormal-execution
   trigger without evidence of a boundary breach; preserve identity, channel, termination, and
   residual evidence;
5. `HOST_UNAVAILABLE`: the host cannot establish or supply the correctly derived and frozen
   capacity, identity, authenticated channel, schedule, or evidence before Author launch;
6. unavailable eligible `CONTEXT_REQUIRED` or `ACCESS_REQUIRED`; an out-of-envelope request becomes
   `ALIGNMENT_REQUIRED` for a new run;
7. stage terminal such as `AMBIGUITY_UNRESOLVED`, `NO_PROGRESS`, or `EXECUTION_UNAVAILABLE`;
8. stage current closure under Evaluation's same-fingerprint-or-compatibility rule: advance; graph
   closure permits success only after workflow finalization.

Controller oversubscription takes the inadmissible boundary path, never `HOST_UNAVAILABLE`. A lower
result cannot erase higher-priority evidence or required safety finalization. `TEARDOWN_FAILED`
preserves the underlying result and blocks clean success.
