# Role Launch

This fixed runtime owns Host Governance, identity lifecycle, scheduling, semantic channels,
normalized reports, Role Boundary Audits, semantic-role failure, conditional-role composition, and
workflow finalization.

The exact three-report callback schema below is normative. An **Operation Summary** means the
complete bundle of Operation Report, Peer Report, and Host-Governance Report; it never omits or
replaces the Peer Report. A **bootstrap report** means the Host-Governance Report.
[`acceptance.md`](acceptance.md) owns Acceptance case design, attempts, judgment, correction, and
replay; this runtime owns the shared launch, audit, identity, and finalization mechanics that those
attempts use. These mappings add no second schema or owner.

When Acceptance applies, Design must prove termination and quiescence after every declared normal,
failed, abnormal, and non-return Runner mode before freeze and before any role launches.

## Keep Host Governance execution-only

Every role invocation includes one host-provided user-role envelope with exactly these ordered
classes:

1. recommended-plugin catalog metadata;
2. repository `AGENTS` instructions;
3. environment metadata.

Catalog and environment metadata are read-only, separately reported, and inert. Mandatory host or
project instructions govern only how an already-authorized operation executes. None supplies or
changes Candidate semantics, prose, evidence, scope, authority, permissions, dependencies,
Acceptance facts, role work, or frozen transitions; none grants an operation or access. An
independently owned Rule, Spec, or implementation may still supply evidence through its established
provenance and the frozen contract. Earlier turns, unrelated tasks, and undeclared content classes
remain outside the role's semantic input.

Before freeze, bind the canonical closed-bootstrap representation to one immutable **Envelope ID**
in each expected-operation manifest and supply the same value to the role and Controller. A role
references that ID; it never serializes or hashes the envelope. The reports below establish
observed conformance and execution-only use, not semantic authority.

## Preserve identities and capacity

Every semantic identity starts fresh without inherited parent-task turns. The frozen templates
contain one resident Author from launch through finalization, one complete fresh persistent
Reviewer cohort for each review unit, and every conditional authority's declared identities. The
Controller and resident Author retain their reserved slots throughout that interval. Bind a whole
cohort before its first action. Membership stays immutable while the unit is open, and each
identity persists through that unit's correction loop. Reopening an invalidated closed unit
requires a wholly fresh complete cohort.

For every batch and round, bind the unit, complete cohort, active subset, Candidate Version,
evidence, phase, independent-readiness event, permitted Author↔Reviewer pairs and directions, and
discussion state. Suspension preserves identity and state without consuming a live worker slot.
Retention keeps an identity live and consumes one `P` slot. Batching changes none of cohort,
identity, version, evidence, unit, round, or independent judgment. A Reviewer receives no other
Reviewer's work.

Only the Controller operates lifecycle mechanics and bounded updates. Every dispatch and retention
state must fit the frozen `P`. If the host cannot supply the correctly derived capacity, identity,
authenticated channel, schedule, or evidence, return `HOST_UNAVAILABLE`. If the Controller binds,
launches, or retains a state beyond the frozen schedule or `P`, return control-plane
`ROLE_BOUNDARY_VIOLATION`. Never replace the resident Author or a member of an open cohort.

## Preserve role authority

Freeze one role-specific prompt for the Controller, Author, each Reviewer, and each Runner. Each
prompt states that role's purpose, authorized context and actions, communication boundary, required
reports, and stop conditions, and incorporates its applicable manifest, scope, identity, version,
and evidence. The Controller prompt requires case-by-case judgment of Author and Reviewer behavior
and permits proportionate intervention only to enforce the frozen control plane and containment;
it leaves Candidate meaning, findings, and reasoned fixed points to their semantic owners.

Give the Author the complete Run Contract, Candidate model, writing guidance, accepted evidence,
current Candidate, grants, and exactly one current Authoring Scope or Repair Scope. The Author works
only within them and performs no Machine Validation, Acceptance, network use, or delegation. Only
the Author owns Candidate meaning, finding dispositions, and Candidate edits.

The Author returns exactly one status:

- `COMPLETE`: semantic Change Summary, exact changed/created/deleted paths, and uncertainty outside
  the current discriminated scope;
- `CONTEXT_REQUIRED`: missing fact and its authoring use;
- `ACCESS_REQUIRED`: exact path, mode, and reason; or
- `HUMAN_DECISION_REQUIRED`: exact decision, why evidence or authority cannot resolve it, decision
  owner, and consequences of every live choice.

Reviewers independently judge complete authorized inputs and own findings, classifications, and
verdicts. Authors and Reviewers use no network or delegation. Runners perform only frozen case
execution, never delegate, and own no judgment, repair, setup correction, cleanup, role control, or
role launch. Only the Controller starts, resumes, suspends, retains, or finishes an identity;
grants access; or supplies a bounded update.

## Close semantic-role abnormal execution

For every Author or Reviewer invocation and continuation, freeze an observable non-return,
lost-identity, or failed-continuation trigger and its evidence. It may use a supported host terminal
or a predeclared bounded detector; this contract supplies no arbitrary timeout.

When the trigger fires, the Controller preserves every obtainable report, channel record, host
fact, and Candidate fingerprint; aborts each open discussion through nonsemantic control metadata;
attempts the frozen termination operation; and audits all obtainable evidence. An absent callback
supplies no payload and is recorded rather than invented. Before the containment decision, start no
replacement identity, Candidate write, new discussion, or later stage.

Evidence of a boundary breach classifies the incident as `ROLE_BOUNDARY_VIOLATION`; otherwise
classify it as `SEMANTIC_ROLE_UNAVAILABLE`. Send either classification to the global exit's
containment decision. Failure to end the identity or prove it inactive becomes `TEARDOWN_FAILED`
during finalization. Preserve immutable cohort membership, resident-Author continuity, Candidate
state, and the underlying incident evidence.

## Open direct correction through metadata

Freeze no Reviewer↔Reviewer edge. Use this two-step bootstrap for every finding:

1. After private judgment fixes a complete finding and opaque stable ID, the Reviewer emits an
   audited nonsemantic `FINDING_READY` callback containing only unit, round, Candidate Version,
   Reviewer identity, finding ID, and the three normal reports.
2. After auditing that callback against the frozen pair and manifest, the Controller returns
   `CHANNEL_OPEN` metadata to that Author↔owner pair. Only then does the Reviewer send the complete
   finding directly to the Author.

The Author and owner exchange semantic claims, dispositions, evidence-based reasons, questions,
objections, and rebuttals directly. Each judges the feedback and reasons independently. Agreement
is a reasoned bilateral fixed point, never blind acceptance. The Controller sees only control
metadata; it never receives, interprets, summarizes, arbitrates, or relays finding bodies,
dispositions, or discussion content. The pair closes with audited `DISCUSSION_CLOSED` metadata
containing unit, round, Candidate Version, identities, finding ID, disposition class, delivery
state, and fixed-point state, but no semantic body. Peer traffic cannot operate roles, change
grants, or introduce evidence.

A Quality or Correctness Reviewer exposes exactly one Controller-facing judgment result at a time:
`PASS`, `FINDING_READY`, `CONTEXT_REQUIRED`, `ACCESS_REQUIRED`, or
`HUMAN_DECISION_REQUIRED`. Acceptance adds only its declared classifications. `DISCUSSION_CLOSED`
is a channel-lifecycle event emitted by each peer, not a semantic-role result or finding body.
Context, access, and human requests are owner-produced control or terminal payloads, not finding
or discussion bodies. The Controller may inspect only what is necessary to apply the frozen
eligibility or terminal transition and must preserve and deliver the payload unchanged; it never
decides its semantic merit. A Controller-owned `HUMAN_DECISION_REQUIRED` has the same immediate
global stop as one from the Author or a Reviewer.

## Audit before consuming a callback

Require every normal callback to carry all three reports:

- **Operation Report:** exact `read`, `write`, `create`, `delete`, `network`, `delegation`, and
  `machine checks` operations, using `none` for an empty category.
- **Peer Report** for Authors and Reviewers: unit, round, Candidate Version, readiness event, phase,
  identities, directions, message kinds, delivery, and Author participation; use `none` when peer
  traffic is forbidden. It contains no semantic body or verdict.
- **Host-Governance Report:** frozen Envelope ID, observed conformance or exact deviation, inert-use
  evidence for catalog and environment metadata, project instructions read and their execution-only
  effects or `none`, and confirmation that governance supplied none of the forbidden semantic or
  authority inputs.

Before consuming the payload, compare these reports with the frozen expected-operation manifest
and audit available host evidence for schedule conformance, identity continuity, grants, bootstrap,
Candidate fingerprints, and communication metadata. A conditional authority may explicitly permit
absent reports after abnormal execution; record the absence and audit every obtainable fact.

One terminal-control exception preserves the unconditional human stop without admitting Candidate
payload. When authenticated attribution establishes that an Author or Reviewer produced
`HUMAN_DECISION_REQUIRED` and the exact request is obtainable, preserve and deliver that request
unchanged even if another audit field makes the callback inadmissible. Stop semantic work
immediately, consume no other callback content, and use none of it as Candidate evidence or
authority. Report the external result as `HUMAN_DECISION_REQUIRED` and retain the
`ROLE_BOUNDARY_VIOLATION` as underlying audit evidence. When attribution or the exact request is
unproven, no owner-produced human request is established and the ordinary inadmissible path applies.

Except for the attributable terminal-control handling above, a forbidden operation, oversubscribed
dispatch, schedule or grant breach, unattributable Candidate change, missing or inconsistent
required report, forbidden peer edge, Envelope-ID mismatch, manifest-bound expected-control
mismatch, bootstrap or governance breach, or irreconcilable evidence makes the invocation or
callback inadmissible. Return `ROLE_BOUNDARY_VIOLATION` to the global exit's containment decision
unless a started conditional authority owns a higher safety terminal. Preserve Candidate, state,
and evidence without reverting, repairing, or concealing them.

## Finalize the workflow

Finalization applies after any role launch, successful lock acquisition, or acquisition that may
have left lock state:

1. Finish every started conditional execution under its own safety and terminal-precedence
   contract.
2. End every live, retained, and suspended identity while preserving reports, evidence, and
   Candidate state.
3. Establish exact residual activity. Only after all role activity ends, release the lock through
   its frozen interface and record attributable evidence. The Controller exits last.

An identity that cannot be ended or proven inactive, or a lock that cannot safely be released,
returns `TEARDOWN_FAILED`. Preserve the underlying result, exact residual identity/activity and
lock state, evidence, and safe teardown/release attempts. Keep the lock while residual activity
could race Candidate work. When a residual Runner or semantic role prevents complete teardown, the
Controller may issue the terminal report and exit after safely ending everything else; this is the
sole exception to exiting last. Claim only established quiescence, cleanup, teardown, and release.
