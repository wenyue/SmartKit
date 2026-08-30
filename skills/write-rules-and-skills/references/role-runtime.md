# Role Runtime

This fixed runtime serves public, project-local, and shared writers. It owns Host Governance,
identity and schedule enforcement, need-based evidence selection, channels, the three callback
reports, Role Boundary Audits, callback admissibility and composition, semantic-role failure, and
finalization. Frozen Job Design owns Candidate fingerprints, deltas, proof-state transitions, and
standalone boundary outcomes. Later semantic contracts own findings, judgment, correction, and
replay.

Any active Runner contract must prove termination and quiescence for every normal, failed,
abnormal, and non-return mode before freeze and role launch.

## Keep Host Governance execution-only

Every role invocation includes one host-provided user-role envelope with exactly these ordered
classes:

1. recommended-plugin catalog metadata;
2. repository `AGENTS` instructions;
3. environment metadata.

Catalog and environment metadata are read-only, separately reported, and inert. Mandatory host or
project instructions govern only an already-authorized operation's execution. None supplies or
changes Candidate semantics, prose, evidence, scope, authority, permissions, dependencies,
conditional-execution facts, role work, or frozen transitions; none grants an operation or access.
Independently owned Rules, Specs, implementations, or external sources may supply evidence through
established provenance and frozen discovery grants. Earlier turns, unrelated tasks, and undeclared
content classes remain outside the role's semantic input.

Before freeze, freeze the canonical closed-bootstrap representation directly in each
expected-operation manifest and supply it with that manifest to the role and Controller. The
reports establish observed conformance or deviation and execution-only use, not semantic
authority.

## Preserve identities and capacity

Every semantic identity starts fresh without parent-task turns. Freeze one resident Author, one
complete fresh persistent cohort per review unit, and all conditional-authority identities. Bind a
whole cohort before its first action; membership is immutable while open and every member persists
through correction. An invalidated closed unit gets a wholly fresh prebound cohort; no prior
identity returns.

For each batch and round bind unit, cohort, active subset, fingerprint, evidence, discovery grants,
phase, readiness event, permitted Author↔Reviewer pairs and directions, and discussion state.
Suspension preserves identity and state; retention consumes a live slot. Apply Job Design's
capacity rules. A Reviewer receives no other Reviewer's work.

When the frozen graph permits a later-stage Scope Transfer to an earlier passed unit, keep it open
after local PASS and suspend its complete cohort through the transfer window. Resume only the
intended responsibility owner for independent inspection. Close the unit and finish its cohort
only when no later note can arrive and no routed inspection remains. This continues one open unit;
no closed-unit identity returns.

Only the Controller operates lifecycles and bounded updates. Every dispatch and retention state
must fit the frozen schedule; apply Job Design's unavailability and oversubscription outcomes.
Never replace the resident Author or an open-cohort member.

## Select evidence by need

Authors and Reviewers start from the supplied task, Candidate, and evidence. When an applicable
instruction or concrete role need requires it, each may independently inspect task-relevant
Candidate resources, governing Rules, accepted Issues or Specs, owned implementation, tests,
configuration, repository conventions, or external sources through frozen read and network grants
and applicable host capability. They do not proactively inspect unrelated content, follow ambient
references, or use tools without that need.

Reviewers independently seek counterevidence without receiving the Author's reasoning or another
Reviewer's work; source choices and discoveries need not match across roles. A discovered source
may support Candidate judgment and be cited in a finding or direct discussion. Evidence derives
authority only from its owner and provenance, never repository or context visibility, host-envelope
presence, discovery, or peer transmission. Nonnormative context documents remain outside the
evidence basis unless a governing contract permits their narrow use.
The Controller does not interpret or relay project evidence.

Use Job Design's exact grants or narrow source/capability classes. Source selection inside them is
ordinary discovery. Use `CONTEXT_REQUIRED` only for an undiscoverable necessary fact and
`ACCESS_REQUIRED` for missing access; Job Design owns both bounded updates and the new-run boundary.
Authors receive Candidate operations only through the exact current Authoring or Repair Scope.
Reviewers remain read-only. Deterministic commands and conditional effects remain with their stage
owners and do not enter Author or Reviewer grants. Every operation is reported and audited through
this runtime.

## Preserve role authority

Freeze each role prompt with purpose, context, actions, communication, reports, stops, and its
manifest, scope, identity, fingerprint, and evidence. The Controller may intervene proportionately
only to enforce or contain the frozen control plane; semantic owners retain Candidate meaning,
findings, and fixed points.

Give the Author the complete frozen inputs defined by the Author contract and exactly one current
Authoring or Repair Scope. The Author performs no Machine Validation, conditional execution, or
delegation. Every Author and Reviewer applies [**Select evidence by need**](#select-evidence-by-need)
and returns its matching missing-context or access status when necessary.

A `CONTEXT_REQUIRED` payload identifies exactly one frozen necessary-fact slot, the missing fact,
and its role-specific use. The Controller compares those fields with the frozen update envelope
without judging semantic merit and preserves the owner-produced payload unchanged.

An `ACCESS_REQUIRED` payload identifies exactly one missing access target: exact path and mode for
local access, or exact source, capability, and network mode for external access. Both forms include
the reason.

The Author requests missing context or access before mutation and resumes after an eligible update
from unchanged expected proof state.

The Author returns exactly one status:

- `COMPLETE`: the Author-contract semantic Change Summary, uncertainty outside the current
  discriminated scope, and a reference to the accompanying Operation Report; the payload repeats
  no raw operation, affected path, or post-write-observation field;
- `CONTEXT_REQUIRED`: the common necessary-fact payload above;
- `ACCESS_REQUIRED`: the common missing-access payload above; or
- `HUMAN_DECISION_REQUIRED`: exact decision, why evidence or authority cannot resolve it, decision
  owner, and consequences of every live choice.

Reviewers independently own findings, classifications, and verdicts without Author reasoning or
another Reviewer's work. Authors and Reviewers never delegate and use network only within grant and
host capability. Runners execute only their frozen case; they never delegate or own judgment,
repair, setup correction, cleanup, or role control. Only the Controller operates identities,
grants access, or supplies bounded updates.

## Close semantic-role abnormal execution

For every Author or Reviewer invocation and continuation, freeze an observable non-return,
lost-identity, or failed-continuation trigger and its evidence, using a supported host terminal or
predeclared bounded detector. This contract supplies no arbitrary timeout.

When the trigger fires, the Controller preserves every obtainable report, channel record, host
fact, and Candidate fingerprint; aborts open discussions through nonsemantic control metadata;
attempts frozen termination; and audits all obtainable evidence. Record an absent callback without
inventing a payload. Before containment, start no identity, Candidate write, discussion, or later
stage.

After abnormal Author execution and completed termination, complete Job Design's whole-content
invocation-final capture and derive the forensic fingerprint and canonical delta. After abnormal
Reviewer execution and completed termination, compare the whole Allowlist with expected proof state
through Job Design's standalone composition; derive no Candidate fingerprint or canonical delta.

Proven breach returns `ROLE_BOUNDARY_VIOLATION`; otherwise return
`SEMANTIC_ROLE_UNAVAILABLE`. Send the incident to Evaluation's containment decision without
replacing the resident Author or an open-cohort member. Failure to end an identity or prove
inactivity may become `TEARDOWN_FAILED` during finalization. Preserve immutable cohort membership,
resident-Author continuity, Candidate state, and incident evidence.

## Open direct correction through metadata

Freeze no Reviewer↔Reviewer edge. Use this two-step bootstrap for every finding:

1. After private judgment fixes the complete finding set and every opaque stable ID, the Reviewer
   emits one audited nonsemantic `FINDING_READY` callback per finding. It contains only unit, round,
   Candidate fingerprint, Reviewer identity, finding ID, a finding-set-complete marker, and the
   three normal reports. Set the marker only on the final finding; an empty set uses a `PASS` bound
   to the current fingerprint. The marker attests only emission completeness, never finding meaning
   or verdict.
2. After auditing the callback against the frozen pair and manifest, the Controller returns
   `CHANNEL_OPEN` metadata to that Author↔owner pair. Only then does the Reviewer send the finding
   directly to the Author.

The Author contract supplies disposition and proposed-write judgment; the active review contract
supplies claim, severity, and fixed-point judgment; Evaluation maps their exact final results to
write eligibility. This runtime selects none of them. **Disposition control metadata**
is `repair`, `partial repair`, or `decline` plus proposed-write `true` or `false`.
**Write-eligibility control** is `eligible` or `ineligible`. Reasons, claims, evidence, argument,
and repair direction remain the peer-only semantic body.

Author and owner exchange semantic content directly and judge it independently. The Controller
sees only control metadata. Both close with audited `DISCUSSION_CLOSED`: unit, round, fingerprint,
identities, finding ID, exact final disposition and proposed-write control, delivery,
owner-produced fixed-point state (`reached`, `not reached`, or `not applicable`),
Evaluation-derived write-eligibility control, and finding-set state (`complete` or `reopened`), with
no semantic body. For a write-eligible outcome, both events also carry matching nonsemantic scope
control: exact Candidate paths and modes, preservation-reference IDs, and readiness. The Controller
authenticates and compares those fields against frozen grants and Evaluation's mapping; missing,
mismatched, or out-of-grant control makes the callback inadmissible. After all pairs close, the
Author emits one authenticated aggregate of the eligible IDs and matched scope controls; the
Controller may freeze-copy only that exact union into the Repair Scope.

`DISCUSSION_CLOSED` closes only the channel and round; another same-fingerprint round repeats
`FINDING_READY → CHANNEL_OPEN`. Peer traffic cannot operate roles or alter authority; transmission
grants no authority.

Each callback exposes one result from its frozen semantic contract. `DISCUSSION_CLOSED` is a
lifecycle event, not a result or finding. Preserve owner-produced requests unchanged; the
Controller inspects only transition fields, never semantic merit. Any authenticated Controller,
Author, or Reviewer `HUMAN_DECISION_REQUIRED` triggers the later semantic lifecycle's immediate
stop.

## Audit before consuming a callback

Require every normal callback to carry all three reports:

- **Operation Report:** the exclusive schema owner for exact raw `read`, `write`, `create`,
  `delete`, `move`, `network`,
  `delegation`, and `machine checks` operations, using `none` for an empty category. An Author also
  reports exact changed, created, deleted, and moved path identities plus its post-write
  observations. A read-only invocation reports `none` for these mutation fields. A raw `write`
  that leaves content unchanged remains in the raw `write` record and its unchanged-content
  post-write observation; it creates no changed path identity. It never reports or creates a
  Controller-observed Candidate fingerprint or canonical delta.
- **Peer Report:** Authors and Reviewers always include unit, round, one discriminated
  expected-proof-state reference, independent-readiness event, phase, and identities. Every Author
  invocation or continuation whose applicable state is pre-Author reports the immutable baseline
  identity, frozen Design-close whole-Allowlist fingerprint, and matching pre-Author baseline
  whole-Allowlist fingerprint. Every Author or Reviewer invocation whose state is
  promoted reports the applicable Candidate fingerprint supplied by the Controller. An Author's
  post-write observations remain exclusively in its Operation Report; it never claims the
  invocation-final fingerprint or canonical delta that the Controller derives.
  Runners
  map unit to the frozen case unit, round to the attempt ordinal, expected-proof-state
  reference to the Attempt Contract Candidate fingerprint, readiness event and phase to their exact
  manifest-bound Runner launch/attempt values, and identities to the Runner identity. Every role
  also includes directions, message kinds, delivery, and Author participation; use `none` for
  exactly these four traffic fields when peer traffic is forbidden or absent. The report contains
  no semantic body or verdict.
- **Host-Governance Report:** observed closed-bootstrap conformance or exact deviation, inert-use
  evidence for catalog and environment metadata, project instructions read and their execution-only
  effects or `none`, and confirmation that governance supplied none of the forbidden semantic or
  authority inputs.

When Frozen Job Design marks a Reviewer `PASS` as coverage-bearing, the Controller verifies only
its frozen structural manifest: unit, identity, fingerprint, marker, exact input sets, required
fields, allowed labels, nonempty anchors, unique opaque IDs, and closed ID cross-references.
Post-promotion coverage uses Job Design's current expected-proof-state delta-item and economy-unit
bindings.
Missing, extra, stale, or inconsistent data makes the callback inadmissible. The Controller judges
no semantic value or completeness.

After every Author return or completed termination, capture the whole Allowlist and invoke Job
Design's invocation-final transition before callback composition. Reconcile reported operations,
paths, and observations with that capture and host facts. Treat reports only as claims; run this
audit before consuming semantic payload even when the callback is absent or inadmissible.

Audit reports and host evidence against the expected-operation manifest for schedule, identity,
grants, bootstrap, fingerprints, writes, communication, and Job Design's applicable proof-state
bindings and delta provenance. Missing, stale, incomplete, or mismatched evidence is inadmissible.
When a conditional contract permits reports to be absent after abnormal execution, record absence
and audit every obtainable fact.

An authenticated, attributable `HUMAN_DECISION_REQUIRED` is terminal control: stop semantic work,
deliver it unchanged despite other audit defects, and consume no other payload. For an Author,
invoke Job Design's human-stop transition. Complete only audit and finalization; retain forbidden-
operation or concurrent/indeterminate mismatch classifications. Without exact attribution, use the
ordinary inadmissible or abnormal path.

Otherwise any forbidden operation, oversubscription, schedule/grant/peer-edge breach, missing or
inconsistent report, manifest/bootstrap/governance mismatch, or irreconcilable evidence is
inadmissible and supplies `ROLE_BOUNDARY_VIOLATION` to the semantic lifecycle unless conditional
safety governs. For an Author, invoke Job Design's boundary transition without reverting Candidate
or evidence.

For abnormal or absent Author callbacks, invoke Job Design's corresponding transition and
standalone mismatch outcome. Separately classify the role incident as `ROLE_BOUNDARY_VIOLATION`
when a breach is proven, otherwise `SEMANTIC_ROLE_UNAVAILABLE`; preserve both established results
and follow abnormal-execution containment and finalization.

For every other normal Author callback, apply Job Design attribution before audit. Unknown or
malformed status is inadmissible. A changed invocation plus inadmissible callback always takes the
whole-run boundary transition after conditional safety, consumes no payload, promotes nothing, and
permits no continuation; local containment requires an exact expected-proof-state match.

- Admissible `CONTEXT_REQUIRED` or `ACCESS_REQUIRED` requires no mismatch and uses the need
  transition. An attributable Author change takes the boundary transition; a concurrent or
  indeterminate change returns `CANDIDATE_CHANGED` through its transition.
- Admissible `COMPLETE` with attributable Author change or exact match uses the completion
  transition; the exact-match case reuses Job Design's canonical delta. Boundary evidence takes the
  boundary transition, and concurrent or indeterminate mismatch returns `CANDIDATE_CHANGED`.

For non-Author callbacks, boundary evidence governs; forbidden-operation mismatch returns its
boundary result, every other mismatch returns `CANDIDATE_CHANGED`, and exact match permits the
frozen transition. Mismatches never promote. This composition alone governs attribution uncertainty.

Before role launch and after conditional safety, compare the whole Allowlist with expected proof
state and apply Job Design's standalone composition. Launch only on exact match; these checks never
use callback composition or promote.

## Finalize the workflow

Finalization applies after any role launch:

1. Finish every started conditional execution under its own safety and terminal-precedence
   contract.
2. End every live, retained, and suspended identity while preserving reports, evidence, and
   Candidate state.
3. Establish exact residual activity.
4. After conditional safety finalization, invoke Frozen Job Design's post-safety whole-Allowlist
   comparison and standalone boundary outcome composition before selecting the pending result.
5. When all non-Controller role activity completes without a safety or teardown terminal, invoke
   Frozen Job Design's final whole-Allowlist comparison and standalone boundary outcome composition
   immediately before clean-success handoff. The standalone boundary never promotes.
6. The Controller exits last.

An identity that cannot be ended or proven inactive returns `TEARDOWN_FAILED`. Preserve the
underlying result, exact residual identity and activity, evidence, and safe teardown attempts. If a
residual Runner or semantic role prevents complete teardown, the Controller may issue the terminal
report and exit after safely ending everything else—the sole exception to exiting last. Claim only
established quiescence, cleanup, teardown, and final expected-proof-state match.
