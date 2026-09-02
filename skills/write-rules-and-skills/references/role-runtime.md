# Role Runtime Contract

This portable contract serves public, project-local, and shared writers. It owns identity, evidence
access, communication, normal callbacks, boundary auditing, abnormal execution, and finalization.
Keep routine role execution judgment-led and require detailed audit only when it establishes
authority, attribution, or safety.

## Enforce the host-input boundary

[Models' evidence-authority rule](models.md#close-alignment) is the sole semantic owner for host
and repository inputs. At role execution, enforce that accepted boundary and the frozen grants;
mandatory instructions may constrain only an operation already authorized by the Run Contract.
Portability across supported writer contexts changes no authority, path, compatibility, or
downstream delivery grant.

## Identities and independence

Start one fresh resident Author and keep that identity through the run. Launch the Quality and
Correctness topology frozen from Reviews. Each Reviewer is fresh at first launch and retains its
identity while its stage remains open through correction and recheck. If a previously PASS and
closed stage is invalidated or reopened by downstream repair or a blocking cross-lens inspection
request, launch fresh Reviewer identities for that stage; a closed identity does not return.
Acceptance exclusively assigns the identities, capacity, and prelaunch terminal for its selected
mode; this runtime launches only that frozen assignment and does not reclassify it. A Reviewer
receives no Author reasoning, another Reviewer's findings, verdicts, reasoning, notes, coverage
attestation, or preselected conclusions. Quality current closure and its fingerprint remain
Controller-owned launch gate metadata and are not supplied to Correctness as evidence.

The Controller owns lifecycle and capacity. Roles cannot delegate, expand grants, operate another
role, or change the Run Contract. Suspension preserves identity. If the required identity cannot
continue while its stage remains open, return SEMANTIC_ROLE_UNAVAILABLE rather than substitute a
new judge mid-stage.

## Evidence and grants

Supply accepted requirements, governing evidence, preservation constraints, current complete
Candidate, fingerprint, and the role's exact grants. The Author additionally receives its current
Scope and baseline. Q2 and Correctness receive the baseline and complete delta. A Runner receives
only its frozen case and attempt contract.

Roles select evidence by need within grants. Source visibility and peer transmission do not confer
authority. The Controller transports evidence and enforces boundaries without interpreting
Candidate meaning or findings.

A role returns CONTEXT_REQUIRED for one necessary but undiscoverable fact, or ACCESS_REQUIRED for
one exact inaccessible source, path, capability, or mode. Include why it matters. An expansion that
would change accepted meaning, ownership, Candidate scope, permission class, external effects, or
validation returns HUMAN_DECISION_REQUIRED for a new run.

The Controller compares each request with
[Job Design's frozen recovery envelope](job-design.md#bound-context-and-access-recovery). An exact
match supplies the bounded update and resumes the same identity on the unchanged fingerprint;
every other request follows that contract's new-run handoff.

## Normal callbacks

A normal callback is concise:

- role status or verdict and the invocation fingerprint supplied to it;
- Author semantic Change Summary and changed paths, or Reviewer findings and whole-Candidate
  coverage attestation;
- unresolved, uncertain, or untested surfaces; and
- for Machine, commands, exits, and relevant failure output; for Acceptance, mode and case evidence.

Do not require empty operation rows, peer rows, host rows, opaque coverage IDs, or resource-by-
resource manifests. Record raw reads, writes, messages, host facts, and operation detail only when
needed to establish write attribution, provenance, a boundary mismatch, abnormal execution,
external effects, cleanup, or another material authority or safety fact.

Before consuming a callback, authenticate the identity, role, fingerprint, grants, and permitted
communication. Reconcile Author changed paths with Job Design's post-return capture. Missing or
irreconcilable evidence on a material boundary returns ROLE_BOUNDARY_VIOLATION.

Transport an Acceptance Reviewer's AMBIGUITY_OBSERVATION_REQUIRED unchanged with its exact
observation, bounded setup and capture delta, evidence need, case, and fingerprint. The Controller
may copy that payload into the next frozen Attempt Contract; it cannot interpret or amend its
semantic content.

Transport a nonblocking observation classified by Reviews as outside the Reviewer's lens or
verdict authority only as a deferred surface. The Controller preserves it verbatim for the final
handoff without interpreting it, routing it to another Reviewer, treating it as a finding, or
changing current proof.

Transport a Reviews-classified blocking cross-lens inspection request only to its owning lens. The
request contains Candidate location, target lens, and fingerprint, with no originating reasoning,
assessment, or conclusion. It is not a finding or evidence; the receiving Reviewer inspects the
Candidate independently under Evaluation's closure gate.

## Direct correction

A Reviewer sends each supported finding directly to the resident Author after private judgment.
Only that pair discusses the claim. The Controller knows the finding identifier, fingerprint,
channel state, final Author disposition, blocking fixed-point state, and proposed Repair Scope; it
does not decide or rewrite semantic content.

Candidate writes remain closed while any discussion is open. After all channels close, the
Controller may batch only Evaluation-eligible findings into the exact Repair Scope. Reviewers never
communicate with one another.

An authenticated HUMAN_DECISION_REQUIRED stops semantic work immediately even if other callback
evidence is incomplete. Preserve the request unchanged and perform only safety and finalization.

## Abnormal execution and boundaries

Before launch, establish an observable non-return, lost-identity, or failed-continuation detector
and an authorized termination path for every role. Executable Acceptance also establishes Runner
quiescence and cleanup mechanics.

On abnormal execution, preserve obtainable Candidate observations, callback, external-effect,
channel, and host evidence; close channels; terminate the role; and prove inactivity. A proven
grant, identity, communication, Candidate-write, or schedule breach returns
ROLE_BOUNDARY_VIOLATION. Otherwise a failed semantic identity returns
SEMANTIC_ROLE_UNAVAILABLE. Runner safety terminals remain Acceptance-owned.

Routine callbacks need no full audit recital. Include detailed operation, peer, and host evidence
in the handoff only for abnormal execution, a boundary mismatch, external effects, or when required
to establish authority, attribution, cleanup, or residual safety.

## Finalize

After any role launch:

1. complete every started Acceptance attempt's safety sequence;
2. close channels and end live or suspended roles;
3. establish quiescence, cleanup, and residual activity;
4. perform the post-safety and final Candidate comparisons; and
5. let the Controller exit last when safe.

Under Evaluation's terminal precedence, TEARDOWN_FAILED overrides coincident non-safety,
non-boundary outcomes when a role cannot be ended or proven inactive, while preserving the
displaced result and residual state. Safely end every other role, report the exact residual role
and state, and allow the Controller to exit. This is the sole exception to complete teardown and
the Controller-exits-last rule.
