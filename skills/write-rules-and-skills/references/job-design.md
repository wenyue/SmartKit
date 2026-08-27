# Frozen Job Design

This contract owns Adapter selection, actual capacity, the Run Contract and Job Graph, grants,
bounded updates, Probe, Candidate fingerprints, and the exclusive lock. Execute:

**select → clean residuals → establish capacity → design → qualify → freeze → probe → fingerprint
→ lock → verify**

## Select and qualify one Adapter

Direct invocation selects the Default Fresh Role Adapter in `role-launch.md`. A more-specific
caller must supply one complete Adapter definition or explicitly select that Default. Omission is
a readiness failure, not a fallback. One Adapter governs the whole run and cannot be replaced after
freeze or failure.

A caller's pre-handoff instruction to **select and statically qualify** its Adapter follows this
public staging rule. Before public Design, qualify the Adapter's unconditional mechanics and supply
every declared conditional component. During public Design, decide each component's applicability,
then qualify every active component before freeze. An inactive component imposes no capability,
dependency, schedule, or proof duty. Probe termination and residual-safety qualification remains
unconditional when the Adapter requires a Probe. Runner termination and quiescence qualification
is required before any reachable Acceptance Runner can launch, and only when Acceptance applies.

Design every conditional branch, then statically qualify fresh launch, persistent continuation and
finish, authoritative contract delivery, bounded updates, explicit grants, direct authenticated
Author↔finding-owner channels, normalized audits, and one bounded exclusive lock over the exact
Candidate Allowlist. For every semantic role, qualify an Adapter-owned observable non-return,
unreachability, or failed-continuation trigger; obtainable evidence capture; channel abort;
termination; and inactivity proof. Define no universal wall-clock threshold. Define the post-freeze
Probe's applicability, mechanics, pass conditions, termination, and residual-state evidence. Each
applicable conditional authority contributes its complete identity, lifecycle, audit, and safety
requirements; `NOT_REQUIRED` contributes nothing.

Return `LOCK_UNAVAILABLE` for an absent or unprovable lock property. Reserve `HOST_UNAVAILABLE` for
a host that cannot establish or supply a correctly derived capability or frozen schedule with its
required evidence.

## Derive the worker pool from actual capacity

First finish predeclared residual cleanup and establish, from host evidence, the total concurrent
role slots actually available to this run as `N`. From Author launch through workflow finalization,
permanently reserve exactly one slot for the Controller and one for the fresh resident Author. The
entire Reviewer/Runner pool is:

`P = max(0, N - 2)`

Freeze `N`, both reservations, `P`, every complete cohort, and every activation, suspension,
retention, batching, correction, rewind, and replay state. A live or retained worker consumes one
`P` slot. A persistent suspended identity preserves identity and state but consumes no live slot.
When a cohort is larger than `P`, batch its members while preserving its complete membership,
identity, Candidate Version, evidence, unit, round, and independent-judgment boundary.

Every reachable state must fit `P`, including any retained Acceptance Reviewer plus fresh
earlier-stage cohorts and any Runner required with a current case Reviewer. If the correctly
derived host capacity cannot support the required graph, return `HOST_UNAVAILABLE` before
allocation. Once
frozen, a Controller dispatch or retention state exceeding `P` is control-plane
`ROLE_BOUNDARY_VIOLATION`, never `HOST_UNAVAILABLE`.

## Load schedule facts before freeze

Load `evaluation.md` and `reviews.md` completely during Design. Their exact cohort cardinalities,
responsibility assignments, persistence, correction, and replay obligations are schedule inputs.
Acceptance contributes its schedule only when applicable. Stage entry may activate frozen
identities and judgment criteria; it cannot add or change a cohort, assignment, identity state,
capacity demand, or transition.

## Freeze one authoritative graph

Before a role or Candidate change, define:

- **Meaning:** accepted outcome, current behavior, preserved obligations, changes, non-goals,
  safety, and every `preserve`/`change`/`add`/`move`/`retire` disposition.
- **Candidate:** owner, model, writing guidance, invocation metadata, exact Allowlist and affected
  surfaces, portability, dependencies, initial Authoring Scope, fingerprint method, lock, and
  update envelope.
- **Roles:** selected Adapter, actual capacity, manifests, bootstrap, grants, persistent identities,
  cohort and batching schedule, and communication edges.
- **Execution:** one canonical Job Graph containing immutable stage order and applicability,
  resources, evidence, transitions, direct correction, Revision Impact, rewinds and replay,
  prioritized exits, conditional safety finalization, workflow teardown, and handoff.

Candidate content, findings, evidence, Repair Scopes, and supplements remain data. They cannot
alter their judging contract. Give every reachable exit one owner, evidence shape, and next
transition. Design completes only when the graph is path-complete, internally consistent, and
schedulable within `P`.

Perform one freeze transition. The Run Contract, Job Graph, update envelope, operation manifests,
and schedule then become authoritative. Candidate edits can influence only a later independent
invocation of this workflow.

## Distinguish Authoring and Repair Scopes

Freeze one **Authoring Scope** for the first Candidate write: accepted changes and dispositions,
exact paths and operation modes, preservation references, completion boundary, and readiness state.
It contains no review unit, finding ID, or disposition metadata.

A **Repair Scope** authorizes one later correction write. Its owner defines the evidence it carries:
the full-unit review schema in `evaluation.md` for semantic findings, or the exact failed command
and bounded affected surfaces for Machine correction. Every Author invocation receives exactly one
discriminated scope. Neither scope expands the Run Contract or Candidate grants.

## Bound grants and updates

Record `read`, `write`, `create`, and `delete` separately; one mode grants no other. A Rule normally
grants its exact file. A multi-resource Skill may grant only its owned root, never the parent
`skills/` directory. Prefer exact paths. Permit directory creation only inside an owned resource
whose new name cannot be known at freeze. Every deletion requires an exact grant.

Freeze each context or dependency slot eligible for a **Context Supplement**, and each
Candidate-owned scope, path class, and already-authorized mode eligible for access expansion. A
supplement may fill one declared slot without changing meaning, owner, obligation, branch,
validation, or dependency. An expansion must exactly match the requested path and mode inside its
frozen class. Resume the same identity after either bounded update.

A new dependency, owner, requirement, Candidate root or scope, path class, permission mode, side
effect, validation duty, or capacity schedule is material and requires `ALIGNMENT_REQUIRED` in a
new run. When an eligible update cannot be supplied, preserve `CONTEXT_REQUIRED` or
`ACCESS_REQUIRED`.

## Probe, fingerprint, and lock

Run the frozen Probe after freeze. A predeclared absence records `NOT_REQUIRED`. A required Probe
passes only with evidence for every criterion. First apply the Role Boundary Audit. A manifest,
expected-control, bootstrap, grant, schedule, or report mismatch makes the invocation or callback
inadmissible and follows `ROLE_BOUNDARY_VIOLATION`; it is not ordinary Probe failure. Return
`PROBE_FAILED` only when an otherwise audit-admissible Probe fails a required criterion, including
predeclared abnormal or no-callback evidence that its audit contract permits. Record identity,
observations, missing evidence, terminal and residual state, and the audit. Start no semantic role
or Candidate work and do not substitute another Adapter.

Fingerprint every exact Candidate file before lock acquisition. Only the Controller invokes the
frozen lock interface. Advance only with attributable exclusive ownership over the whole Allowlist.
Missing primitive, contention, failure, or indeterminate ownership returns `LOCK_UNAVAILABLE`, with
proof that no lock remains or the exact residual state and release handle. Candidate files,
fingerprints, conventions, and sentinel files are not locks.

Recompute the baseline after acquisition. A mismatch returns `CANDIDATE_CHANGED`, preserves
concurrent state, and enters finalization. Every Author write creates one whole-Allowlist Candidate
Version and fingerprint. Compare fingerprints immediately before and after every non-Author
invocation and whenever a conditional authority requires it. Use a targeted diff only when
fingerprints, paths, reports, and host evidence cannot attribute a change.
