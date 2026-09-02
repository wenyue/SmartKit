# Run Contract and Candidate Integrity

This contract owns the compact Run Contract, grants, bounded context and access recovery, capacity,
Candidate identity, fingerprints, write attribution, and boundary stops. Freeze procedure only
where order or protocol changes correctness.

## Freeze the Run Contract

Before any role or Candidate write, freeze one immutable Run Contract containing:

- accepted meaning, governing evidence, preservation constraints, Candidate model, and writing
  guidance;
- exact Candidate Allowlist, paths and presence states, and separate read, write, create, delete,
  move, network, command, and external-effect grants; every move grant names its exact source and
  destination and is never inferred from create or delete authority;
- one resident Author, the Quality and Correctness topology and lenses owned by Reviews, their
  identity lifecycle owned by Role Runtime, and Acceptance's selected mode-specific identity and
  capacity assignment;
- proof order, Machine applicability and owner-supported commands, Acceptance applicability and
  mode, communication edges, correction and replay;
- prioritized exits, abnormal-role containment, external-effect safety, termination, quiescence,
  cleanup, and final handoff.

The Run Contract freezes authority and accepted meaning, not ordinary method or a preselected
evidence inventory. It must fit observed host capacity. If the core Controller, Author, Quality,
or Correctness identity, capacity, Candidate observation, or semantic-role termination mechanics
cannot be supported before launch, return HOST_UNAVAILABLE. After Acceptance mode selection,
Acceptance exclusively owns its conditional identities, capacity, readiness, and prelaunch
terminal. Job Design freezes that assignment without reclassifying its result.

The Author alone may mutate the Candidate, under exactly one Authoring Scope or Repair Scope.
Reviewers are read-only. Machine is non-fixing. Acceptance mutation is limited to disposable
case-owned targets, never Candidate or setup inputs.

## Freeze self-hosting authority

When any governing contract resource is Candidate-owned or writable in the current scope, load and
freeze its complete pre-Author snapshot before mutation, even when its ordinary semantic first need
would be later. The frozen snapshot remains the same-run authority. Edited Candidate bytes are
data: they cannot replace, reload, or amend the governing snapshot for the current invocation.
Candidates that do not modify a governing resource retain ordinary progressive loading.

## Bind the Candidate

The Candidate identity is one deterministic fingerprint over every ordered Allowlist path, presence
state, and full bytes. Paths outside the Allowlist are not Candidate writes.

At Design close, capture the complete Candidate and fingerprint. Immediately after freeze and
before the Author begins, capture it again. An exact match becomes the immutable pre-Author
baseline. Repeat one indeterminate observation once; a persistent mismatch returns
CANDIDATE_CHANGED before any role or write.

Retain the baseline and a readable baseline-to-current delta as evidence. The fingerprint, not a
manifest of semantic subunits, binds every verdict and handoff.

## Verify boundaries

Immediately before every role launch and every Author write invocation, compare the complete
Candidate with the current expected fingerprint. After every Author return or termination, capture
the complete Candidate again before consuming the callback.

Classify a changed Candidate as:

1. attributable Author writes entirely inside the active grant;
2. a proven forbidden role or out-of-grant operation; or
3. concurrent or indeterminate change.

Only the first class may establish a new current fingerprint after an admissible Author COMPLETE.
After promotion, the Controller binds the Author's returned semantic Change Summary once to that
fingerprint. A forbidden change returns ROLE_BOUNDARY_VIOLATION. Concurrent or indeterminate change
returns CANDIDATE_CHANGED. Preserve the Candidate, observations, attribution evidence, and prior
accepted fingerprint; do not revert or promote uncertain state.

Normal Reviewer, Machine, and Acceptance activity must leave the Candidate fingerprint unchanged.
Check it after external-effect safety finalization and immediately before final handoff.

## Scope writes and repairs

The initial Authoring Scope contains the accepted outcome, exact write modes and paths, preservation
constraints, and completion boundary without preselecting semantic dispositions.

A Repair Scope contains the exact eligible findings, Candidate fingerprint, paths and modes, and
preservation constraints. It carries supported findings and Author dispositions without granting
Reviewer prose authority. Batch all eligible outcomes from one closed correction round into one
Repair Scope.

Any promoted repair creates a new fingerprint and invalidates all semantic proof. Rerun every
applicable proof stage in order from Machine on that fingerprint under Evaluation's replay and
Role Runtime's identity lifecycle. No prior semantic verdict carries forward.

A new Candidate root, owner, requirement, dependency, permission class, external effect,
validation duty, or role schedule exceeds the Run Contract. Return HUMAN_DECISION_REQUIRED or the
applicable alignment/access exit and continue only in a new run.

## Bound context and access recovery

Freeze the necessary-fact slots and access expansions eligible for same-run recovery. A context
slot names one missing fact and its use. An access expansion names the exact path or source,
capability, and mode. Eligibility requires unchanged accepted meaning, owner, Candidate scope,
dependencies, external effects, validation, and proof fingerprint.

The Controller authenticates an exact in-envelope request, supplies only that fact or access, and
resumes the same identity from unchanged proof state. An unavailable eligible update preserves
CONTEXT_REQUIRED or ACCESS_REQUIRED. Any out-of-envelope request ends the run with the applicable
alignment, human-decision, or access handoff; it never expands the frozen contract in place.

## Require finalization closure

The Run Contract incorporates Role Runtime's finalization, Acceptance's started-attempt safety, and
Evaluation's terminal precedence by reference. Job Design proves that those contracts fit capacity
and grants; it does not redefine their sequences or classifications. Design is complete only when
every reachable finalization path is schedulable and the final Candidate comparison is available.
