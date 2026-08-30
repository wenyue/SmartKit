# Frozen Job Design

This contract owns readiness, capacity, the Run Contract and Job Graph, grants and bounded updates,
Candidate observation, baseline, fingerprints and deltas, mismatch attribution, and proof state:

**clean residuals → establish capacity → design → establish readiness → fingerprint → freeze →
baseline → verify**

## Derive the worker pool from actual capacity

Before cleanup, observe every live or retained identity and activity visible through the accepted
pre-freeze host capability. Classify a residual as run-owned only when immutable identity and
provenance bind it to the interrupted workflow named by accepted cleanup authority. End only those exact run-owned
identities, only with that authority, and prove inactivity. Preserve unrelated activity; it reduces
host-evidenced capacity but is never a cleanup target. Indeterminate ownership, missing authority,
failed termination, or unproved inactivity returns `HOST_UNAVAILABLE` before allocation with the
residual evidence. The later runtime applies this entry contract; post-launch finalization remains
separate.

After cleanup, establish host-evidenced total role slots `N`. Reserve one each for the Controller
and resident Author through finalization. The Reviewer/Runner pool is:

`P = max(0, N - 2)`

Freeze `N`, reservations, `P`, complete cohorts, all conditional-authority identities, and every
activation, suspension, retention, batching, correction, rewind, and replay state. Live or retained
workers consume `P`; suspended identities preserve state without a slot. Batch an oversized cohort
without changing membership, identity, fingerprint, evidence, grants, unit, round, or independent
judgment.

Every state must fit `P`. Acceptance separately schedules its retained/current case Reviewer with
either a fresh Runner for an attempt or a batched earlier-stage cohort during Evaluation
restoration, never both. Insufficient correctly derived capacity returns `HOST_UNAVAILABLE` before
allocation; post-freeze oversubscription is `ROLE_BOUNDARY_VIOLATION`.

## Freeze schedule facts

Before freeze, incorporate every later contract's cardinalities, assignments, identities,
persistence, correction, and replay inputs. An inactive conditional authority contributes none;
stage entry changes no schedule fact.

Freeze Quality's mechanical input schemas and derivations:

- the **mandatory-load manifest** schema and deterministic derivation, covering every exact
  Allowlist resource with its route or condition, Candidate-prescribed load point or `none`, any
  external prescribed-load dependency, and Candidate anchor; and
- the exact Allowlist resource set plus the deterministic canonical-delta-item and
  format-appropriate economy-unit schemas and derivations used by coverage records.

After every promoted Candidate fingerprint, mechanically derive and bind the exact current
mandatory-load manifest, delta-item set, and economy-unit set from that fingerprint's Candidate
bytes and immutable delta as expected-proof-state evidence. The Economy Coverage Record consumes
that current fingerprint-bound manifest. These bindings apply frozen derivations; they do not
amend the Frozen Run Contract. Manifests and bindings are controls, not judgments.

## Design one authoritative graph

Before a role or Candidate change, define:

- **Meaning:** accepted outcome, current behavior, requested outcomes, non-goals, safety, supplied
  evidence, authorized discovery sources and capabilities, provenance boundaries, every accepted
  obligation, and its governing evidence, semantic criteria, and preservation constraints. These
  inputs constrain Candidate outcomes but assign no disposition; the resident Author selects the
  initial semantic dispositions.
- **Candidate:** owner, model, writing guidance, invocation metadata, exact Allowlist and affected
  surfaces, dependencies, initial Authoring Scope, read and network grants, fingerprint method,
  frozen identity, baseline and observation methods, update envelope, and, whenever the Candidate
  owns or changes a script, an exact script-to-unit-test-resource-to-Machine-command mapping.
- **Roles:** actual capacity, manifests (including mandatory-load resources), bootstrap, grants,
  persistent identities, cohort and batching schedule, and communication edges.
- **Execution:** one canonical Job Graph containing immutable **conditional Machine → Quality →
  Correctness → conditional Acceptance** stage order and applicability,
  resources, evidence, transitions, direct correction, Revision Impact, compatibility-decision
  manifests, rewinds and replay, prioritized exits, conditional safety finalization, workflow
  teardown, and handoff.

For each proof class eligible for compatibility carry-forward, freeze one manifest declaring its
semantic owner, complete content-dependency surfaces, observable non-impact predicates, required
provenance, the Controller as mechanical determination producer, and its lifecycle-authorized
proof-owner fallback or ordinary replay. Without a complete manifest, that proof class is not
compatibility-eligible. The manifest is part of the Frozen Run Contract and Candidate edits cannot
replace or amend it.

Candidate content, findings, evidence, Repair Scopes, and supplements are data and cannot alter
their judging contract. Give every reachable exit one owner, evidence shape, and next transition.
The graph is complete only when path-complete, internally consistent, and schedulable within `P`.

## Distinguish Authoring and Repair Scopes

The first write uses one **Authoring Scope**: accepted outcome and semantic criteria, exact paths
and modes, preservation references and constraints, completion boundary, readiness, and every
required mapped script and unit-test addition or update. It freezes the authorized operation
envelope without selecting an Author disposition. It has no review or finding metadata.

A **Repair Scope** authorizes one correction. Its frozen semantic owner supplies its exact control
inputs; deterministic repair instead carries the failed command and affected surfaces.
Every Author invocation receives exactly one scope, which expands neither contract nor grants.

## Bound grants and updates

Freeze `read`, `write`, `create`, `delete`, and `network` separately. A Rule normally grants its
exact file; a Skill at most its owned root, never parent `skills/`. Prefer exact operation paths;
read and network discovery may use narrow source or capability classes. Directory creation needs
an owned resource with a name unknowable at freeze; deletion needs an exact grant. A move available
inside the Authoring Scope needs exact source-delete and destination-create grants. Those grants
authorize the operation without selecting its semantic disposition.

For every Candidate-owned or changed script, include each mapped unit-test resource in the exact
Allowlist and whole-Allowlist Candidate identity. Freeze its required Author operation modes and
Machine read and execution grants together with the exact owner-supported test command. A missing
resource, mapping, command, or grant makes Design incomplete.

Grants bound the later runtime's evidence selection. Ordinary in-grant source discovery is not an
update or per-file research route.

Freeze every Context Supplement fact slot and access-expansion path, source, capability, and mode
class. A supplement fills one undiscoverable fact without changing meaning, owner, obligation,
branch, validation, or dependency. An expansion exactly matches the admitted request within its
class. Only then may the Controller update and resume the same identity from applicable proof state.

A new dependency, owner, requirement, Candidate root or scope, path class, permission mode, side
effect, validation duty, or capacity schedule is material and requires `ALIGNMENT_REQUIRED` in a
new run. When an eligible update cannot be supplied, preserve `CONTEXT_REQUIRED` or
`ACCESS_REQUIRED`.

## Establish runtime readiness

Require the later runtime to establish fresh launch, persistent continuation and finish, contract
delivery, bounded updates, explicit grants, authenticated Author↔owner channels, audits, and
optimistic observation over the exact Allowlist.

For every semantic role establish an observable non-return or failed-continuation trigger, evidence
capture, channel abort, termination, and inactivity proof without a universal timeout. Applicable
Conditional execution also requires Runner termination and quiescence readiness. Each active
authority contributes its complete lifecycle and safety contract; `NOT_REQUIRED` contributes none.

Return `HOST_UNAVAILABLE` when the host cannot establish or supply a correctly derived capability
or frozen schedule with its required evidence.

## Freeze boundary-based optimistic observation

Before freeze, declare whole-Allowlist comparisons around every role invocation or continuation,
Machine command, and conditional execution; after conditional safety; and after worker teardown
before clean handoff. Preserve each observed mismatch. Retain the pre-Author-invocation fingerprint;
on return or completed termination, independently capture full content and complete the
invocation-final transition before callback composition. Only admitted `COMPLETE` promotes an
attributable Author state.

This workflow does not serialize uncoordinated concurrent writers or guarantee detection of a
transient intermediate state that disappears before a declared comparison. Those are explicit
concurrency non-goals, not failure branches. Stronger host mutation coordination is neither
required nor assumed.

## Bind the Design-close Candidate identity

After every Design input and runtime-readiness requirement is complete, compute the exact
whole-Allowlist fingerprint over the ordered resources' paths, presence states, and full bytes.
This fingerprint is the sole Candidate content identity. Bind it as the final Candidate-identity
input to the Run Contract and Job Graph. This read-only observation starts no role or Candidate
state.

## Freeze one authoritative graph

After the Design-close Candidate identity is bound, materialize the complete Run Contract and Job
Graph, including every incorporated reference and operative instruction, as one immutable snapshot
independent of the Candidate files, then perform one freeze transition. That materialized **Frozen
Run Contract**, including the update envelope, operation manifests, scopes, grants, schedule, and
exact whole-Allowlist fingerprint, is the sole behavioral authority for the complete run and for
every role launched later. Baseline capture, role launch, and Candidate change begin only after
freeze.

Self-hosting edits change Candidate data only. They never replace or reload the Frozen Run Contract,
cause a re-freeze, restart or reset the run, or make any role adopt edited Candidate content as
governing instructions. A Candidate fingerprint change may invalidate only content-dependent
evidence under Revision Impact; it cannot invalidate the frozen execution contract or unrelated
control-plane state.

## Establish the fingerprint and baseline

Immediately after freeze and before Author launch, the Controller captures the exact Candidate
Allowlist's full content and derives its fingerprint from every resource's path, presence state,
and content. Compare that capture with the frozen Design-close Candidate identity. On mismatch,
repeat the full-content capture and comparison once before any other action. A matching capture is
retained as the immutable **pre-Author baseline**. A persistent mismatch returns
`CANDIDATE_CHANGED`, preserves Candidate, every capture, the frozen and observed fingerprints, and
audit evidence, and stops before role launch. This binding keeps later movement, replacement,
creation, and deletion attributable.

Exactly one **expected proof state** applies. Before the first promotion, it is the frozen
Design-close fingerprint plus the matching immutable pre-Author baseline and the empty canonical
baseline-to-current delta bound to that baseline-identical fingerprint. After promotion, it
contains those initial bindings plus the promoted current fingerprint and its canonical delta.
Expected proof state advances only through an admissible Author `COMPLETE`; an inadmissible callback
never advances it.

After an admissible `COMPLETE` promotion, bind the Author-owned Obligation Disposition Record in the
semantic Change Summary to the promoted fingerprint as read-only proof-stage evidence. The record
changes no Frozen Run Contract, grant, scope, Candidate identity, baseline, canonical delta,
expected-proof-state transition, or operation authority.

The **invocation-final transition** compares the Controller's complete invocation-final capture
with that invocation's pre-invocation fingerprint. When the state differs, mechanically record and
preserve the invocation-final whole-Allowlist fingerprint, the raw operation and attribution
evidence, and one complete canonical **baseline-to-current delta** bound to that exact fingerprint.
Perform this transition after the Author returns or terminates regardless of callback presence,
status, admissibility, incident classification, or workflow result. The fingerprint and delta are
forensic facts; they become proof state only through promotion.

The Author Operation Report's raw operations, affected paths, and post-write observations support
the invocation-final capture and audit; they are never Candidate fingerprints or canonical deltas.
No intermediate observation creates a Candidate identity: identity is always the exact
whole-Allowlist fingerprint, and only frozen invocation-final boundaries bind forensic state for
callback composition. Multiple operations do not add intermediate boundaries.

Apply the runtime's callback-admissibility result before any expected-proof-state transition:

- **Admissible-`COMPLETE` transition:** promote the Controller-bound invocation-final fingerprint.
  If the invocation-final capture matches its pre-invocation input, this admissible no-op creates
  no new content identity: promote the unchanged fingerprint and reuse its existing
  baseline-to-current delta. Only baseline-identical content has an empty canonical delta. The
  Author neither creates nor reports the fingerprint or delta.
- **Admissible-need transition:** a compliant Author `CONTEXT_REQUIRED` or `ACCESS_REQUIRED` is
  write-free, promotes nothing, preserves expected proof state, and resumes from it only after an
  eligible update.
- **Human-stop transition:** an authenticated Author `HUMAN_DECISION_REQUIRED` immediately stops
  semantic work and promotes nothing. Preserve every observed fingerprint and delta as unpromoted
  forensic evidence and retain any mismatch attribution as underlying audit evidence.
- **Abnormal-or-no-callback transition:** preserve the invocation-final fingerprint and delta, if any,
  as unpromoted forensic evidence and leave expected proof state unchanged, then use the runtime's
  incident classification and finalization output.

For each invocation-final fingerprint, the Controller mechanically derives and binds one complete
canonical baseline-to-current delta from the immutable pre-Author baseline and the exact current
Allowlist. Every delta keeps that immutable pre-Author-baseline-to-current span and is bound to its
exact current fingerprint. A no-op reuses the delta already established for its unchanged
fingerprint; it never creates a new identity or replaces that delta with an invocation-relative or
empty one. Only baseline-identical content binds an empty canonical delta. Once bound to a
fingerprint, the delta is immutable. Freeze deterministic
derivation, reuse, provenance, and the resource-identity rule before Author launch.
The artifact accounts for every created, deleted, renamed, moved, and modified resource and all
content changes. Its resource-identity rule classifies a path change as a rename or move only when
an exact resource-continuity mapping frozen before Author launch binds the baseline path and an
authorized destination as the same owned resource. This control mapping selects no semantic
disposition; path or content similarity alone cannot establish continuity. Without that mapping,
record the old-path deletion and new-path creation and assert no relationship. The Author's later
Obligation Disposition Record may explain the semantic outcome but cannot alter delta identity or
classification. The delta never depends on the Author's Change Summary, self-report, notes, or
comparison artifact. It is invocation-final fingerprint evidence, not Candidate authority or a
substitute for inspecting the complete current Candidate.

Bind the canonical delta after every invocation-final fingerprint under the derivation and
no-op reuse rules above. Run the frozen whole-Allowlist comparisons against the applicable
expected proof state at every declared observation boundary. An exact final match preserves
expected proof state and enables clean-success handoff. An invocation-final or final comparison
mismatch uses the standalone boundary composition below; callback composition applies only at a
boundary carrying a normal callback.

Frozen Job Design owns one ordered, exhaustive attribution classification for every observed
mismatch:

1. When the complete change is proven attributable to a write within the current authorized Author
   scope, classify it as an attributable Author change.
2. Otherwise, when evidence proves that any change is attributable to a forbidden role or command
   operation, classify it as a forbidden-operation change.
3. Classify every remaining mismatch, including external change and indeterminate attribution, as
   a concurrent-or-indeterminate change.

The first matching class governs, so no mismatch has more than one attribution classification.
Classification uses only observable change attribution and the frozen scope; it neither decides
invocation or callback admissibility nor promotes an invocation-final fingerprint. Role
Runtime independently audits an invocation or normal callback and, only for a normal callback
boundary, composes one callback outcome from that audit and this classification. Apply the
corresponding Frozen Job Design transition:

- An **attributable-Author-change transition** invokes the applicable callback-status transition
  selected by runtime composition.
- A **boundary-violation transition**, also used for a forbidden-operation outcome, promotes
  nothing and preserves Candidate, pre-Author baseline, prior expected proof
  state, every observed fingerprint and delta, and audit evidence. When an inadmissible Author callback
  follows an invocation that changed Candidate, this transition supplies a whole-run boundary
  result to the semantic lifecycle; it authorizes no continuation or local repair.
- A **concurrent-or-indeterminate transition** has the same no-promotion and preservation effects.

## Compose a standalone boundary outcome

At every invocation-final or final comparison, and every other required comparison where no normal
callback exists, the Controller applies this callback-independent composition after the ordered
mismatch classification:

1. A proven forbidden role or command operation returns `ROLE_BOUNDARY_VIOLATION` and invokes the
   boundary-violation transition.
2. A concurrent-or-indeterminate mismatch returns `CANDIDATE_CHANGED` and invokes the
   concurrent-or-indeterminate transition.
3. An exact match supplies no boundary result and leaves expected proof state unchanged.

This composition is the Job Design-owned boundary result for every invocation-final, final,
pre-invocation, and post-safety comparison. It also applies after an abnormal or missing callback
when either listed mismatch class is established. An attributable Author change supplies no
standalone result: a normal callback remains under Role Runtime's independent composition, while an
invocation-final change without one remains forensic evidence for the runtime's semantic-role
incident path. Standalone boundary composition never promotes; callback admissibility and
composition remain separate runtime decisions.

Audit every use of expected-proof-state evidence against its applicable bindings: the frozen
Design-close Candidate identity, immutable baseline identity, and matching whole-Allowlist
fingerprint in the pre-Author state, or those initial bindings plus the promoted current
fingerprint and frozen delta derivation provenance in the promoted state. Only when fingerprints,
paths, reports, canonical deltas, and host evidence cannot attribute the mismatch, use a targeted
Candidate comparison as fallback. Then apply the ordered classification above; unresolved
attribution enters its third class.
