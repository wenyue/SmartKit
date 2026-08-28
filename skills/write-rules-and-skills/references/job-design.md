# Frozen Job Design

This contract owns concrete Role Launch readiness, actual capacity, the Run Contract and Job Graph,
grants, bounded updates, Candidate fingerprints, and the exclusive lock. Execute:

**clean residuals → establish capacity → design → establish readiness → freeze → fingerprint →
lock → verify**

## Derive the worker pool from actual capacity

First finish predeclared residual cleanup and establish, from host evidence, the total concurrent
role slots actually available to this run as `N`. From Author launch through workflow finalization,
permanently reserve exactly one slot for the Controller and one for the fresh resident Author. The
entire Reviewer/Runner pool is:

`P = max(0, N - 2)`

Record `N`, both reservations, `P`, every complete cohort, and every activation, suspension,
retention, batching, correction, rewind, and replay state as Design inputs. A live or retained
worker consumes one `P` slot. A persistent suspended identity preserves identity and state but
consumes no live slot. When a cohort is larger than `P`, batch its members while preserving its
complete membership, identity, Candidate Version, supplied evidence, discovery grants, unit,
round, and independent-judgment boundary.

Every reachable state must fit `P`, including any retained Acceptance Reviewer plus fresh
earlier-stage cohorts and any Runner required with a current case Reviewer. If the correctly
derived host capacity cannot support the required graph, return `HOST_UNAVAILABLE` before
allocation. Once frozen, a Controller dispatch or retention state exceeding `P` is control-plane
`ROLE_BOUNDARY_VIOLATION`, never `HOST_UNAVAILABLE`.

## Load schedule facts before freeze

Load `evaluation.md` and `reviews.md` completely during Design. Their exact cohort cardinalities,
responsibility assignments, persistence, correction, and replay obligations are schedule inputs.
Acceptance contributes its schedule only when applicable. Stage entry may activate frozen
identities and judgment criteria; it cannot add or change a cohort, assignment, identity state,
capacity demand, or transition.

## Design one authoritative graph

Before a role or Candidate change, define:

- **Meaning:** accepted outcome, current behavior, preserved obligations, changes, non-goals,
  safety, supplied evidence, authorized discovery sources and capabilities, provenance boundaries,
  and every `preserve`/`change`/`add`/`move`/`retire` disposition.
- **Candidate:** owner, model, writing guidance, invocation metadata, exact Allowlist and affected
  surfaces, dependencies, initial Authoring Scope, read and network grants, fingerprint method,
  lock, and update envelope.
- **Roles:** actual capacity, manifests, bootstrap, grants, persistent identities, cohort and
  batching schedule, and communication edges.
- **Execution:** one canonical Job Graph containing immutable stage order and applicability,
  resources, evidence, transitions, direct correction, Revision Impact, rewinds and replay,
  prioritized exits, conditional safety finalization, workflow teardown, and handoff.

Candidate content, findings, evidence, Repair Scopes, and supplements remain data. They cannot
alter their judging contract. Give every reachable exit one owner, evidence shape, and next
transition. The graph is complete only when it is path-complete, internally consistent, and
schedulable within `P`.

## Distinguish Authoring and Repair Scopes

Define one **Authoring Scope** for the first Candidate write: accepted changes and dispositions,
exact paths and operation modes, preservation references, completion boundary, and readiness state.
It contains no review unit, finding ID, or disposition metadata.

A **Repair Scope** authorizes one later correction write. Its owner defines the evidence it carries:
the full-unit review schema in `evaluation.md` for semantic findings, or the exact failed command
and bounded affected surfaces for Machine correction. Every Author invocation receives exactly one
discriminated scope. Neither scope expands the Run Contract or Candidate grants.

## Bound grants and updates

Record `read`, `write`, `create`, `delete`, and `network` separately; one mode grants no other. A
Rule normally grants its exact file. A multi-resource Skill may grant only its owned root, never
the parent `skills/` directory. Prefer exact paths for Candidate operations; read and network
discovery may use narrowly owned source or capability classes. Permit directory creation only
inside an owned resource whose new name cannot be known at freeze. Every deletion requires an
exact grant.

Apply `role-launch.md`'s common evidence-selection policy to Authors and Reviewers under those
grants. Source selection permitted by that policy is ordinary discovery, not a bounded update or
per-file research route.

Define each necessary-fact slot eligible for a **Context Supplement**, and each authorized local
path class, external source and capability class, and already-authorized mode eligible for access
expansion. A supplement may fill one declared slot only when the fact cannot be discovered from
current authorized sources and capabilities, without changing meaning, owner, obligation, branch,
validation, or dependency. An expansion is exceptional missing access and must exactly match the
requested local path and mode or external source, capability, and network mode inside its frozen
class. Resume the same identity after either bounded update.

A new dependency, owner, requirement, Candidate root or scope, path class, permission mode, side
effect, validation duty, or capacity schedule is material and requires `ALIGNMENT_REQUIRED` in a
new run. When an eligible update cannot be supplied, preserve `CONTEXT_REQUIRED` or
`ACCESS_REQUIRED`.

## Establish concrete Role Launch readiness

Apply `role-launch.md` as the single fixed runtime and common evidence-selection policy for the run,
unchanged by public, project-local, or shared writers.
Using the completed graph, scopes, grants, applicability decisions, and schedule, establish fresh
launch, persistent continuation and finish, authoritative contract delivery, bounded updates,
explicit grants, direct authenticated Author↔finding-owner channels, normalized audits, and one
bounded exclusive lock over the exact Candidate Allowlist.

For every semantic role, establish an observable non-return, unreachability, or
failed-continuation trigger; obtainable evidence capture; channel abort; termination; and inactivity
proof. Define no universal wall-clock threshold. Runner termination and quiescence readiness is
required before any reachable Acceptance Runner can launch, and only when Acceptance applies.
Every active conditional authority contributes its complete identity, lifecycle, audit, and safety
requirements; `NOT_REQUIRED` contributes nothing.

Return `LOCK_UNAVAILABLE` for an absent or unprovable lock property. Reserve `HOST_UNAVAILABLE` for
a host that cannot establish or supply a correctly derived capability or frozen schedule with its
required evidence.

## Freeze one authoritative graph

After every Design input and concrete Role Launch requirement is complete, perform one freeze
transition. The Run Contract, Job Graph, update envelope, operation manifests, scopes, grants, and
schedule then become authoritative. Candidate edits can influence only a later independent
invocation of this workflow. Begin no role, fingerprint, lock acquisition, or Candidate change
before this transition.

## Fingerprint and lock

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
