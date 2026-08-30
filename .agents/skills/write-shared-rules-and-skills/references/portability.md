# Portable Shared Input and Coverage

This reference owns the private Adapter's complete portability model. It defines the input supplied
to the public authoring workflow and the projection applied to that workflow's handoff. It supplies
no authoring, evidence-selection, proof-stage, correction, replay, or finalization procedure.

## Portability boundary

A shared run produces one cross-project SmartKit Rule or Skill. Resolve ownership before collecting
other Shared Input facts. A supported owner must independently establish that the outcome and each
normative obligation apply across projects.

Continue only for a resolved cross-project SmartKit `rule` or `skill` owner. For any conclusively
resolved non-shared owner, return its supported ownership result immediately, before further Shared
Input work and without invoking the public authoring workflow:

- route a project-local artifact or Setup Authoring Contract to its supported owner;
- for `split`, return separate Rule and Skill requests;
- for `environment-owned`, name the active owner and return no Candidate; and
- for any other resolved non-shared owner, return its supported route.

Treat ambiguous, incompatible, or genuinely unresolved ownership as a missing material owner and
use the `ALIGNMENT_REQUIRED` path below.

Portable meaning may come from accepted decisions, specifications, governing contracts, observable
shared implementation, and representative evidence only when an independently established owner
and provenance authorize that meaning. Qualify each fact separately. Source-project policy, names,
layout, context documents, local success, Candidate text, packaging, visibility, discovery, host
injection, tool availability, and peer transmission supply no portable authority by themselves.
Project and host instructions govern execution within their authority; their observance adds no
Candidate meaning.

Condition platform behavior at its true seam. Every required Rule, Skill, tool, schema, environment
capability, and host behavior needs its shared-owned or target-owned route. A missing material fact,
owner, provenance, route, permission, validation duty, pass condition, or completion obligation
keeps Shared Input open. Return the public `ALIGNMENT_REQUIRED` payload before public invocation,
naming every missing choice, its evidence, decision owner, and material consequences.

## Shared Input schema

Shared Input is one complete, immutable-by-supply task/spec package. Close it before public entry;
the public workflow later performs the single authoritative freeze. Candidate content is data and
cannot amend Shared Input or any judging contract.

Every `OBL-*`, `DEP-*`, `SEAM-*`, `VAL-*`, and `DONE-*` record includes one exact per-ID pass
condition and the qualified evidence characteristics sufficient to close it. Category-specific
meaning, availability, observation, validation, and completion fields inform but do not replace
that condition. These fields define required closure only; the public workflow selects evidence,
assigns stages, and owns verdicts.

### Identity and accepted meaning

Record:

- the accepted portable outcome, non-goals, safety boundaries, prioritized exits, and final handoff;
- one supported cross-project `rule` or `skill` owner, its applicability, and the independent
  provenance supporting that ownership;
- every stable portability obligation as `OBL-<stable-name>`, with its accepted meaning, owner,
  provenance, and one `preserve`, `change`, `add`, `move`, or `retire` disposition;
- the exact Candidate resources, presence expectations, and intended public loading, discovery,
  and distribution routes; and
- the preserved invocation behavior and interface metadata for a Skill.

IDs remain stable for the run and identify semantic obligations rather than document positions.

### Portable evidence qualification

For every evidence source that may support portable meaning, record:

- source identity and provenance;
- the owner that authorizes its use;
- the exact fact or obligation it can support;
- applicability and representative scope;
- availability and discovery route; and
- limits that prevent source-local or incidental facts from becoming portable meaning.

The public workflow selects evidence under its own policy. These qualifications determine only
which selected evidence can support a portability item.

### Dependency manifest

Give each dependency a stable `DEP-<stable-name>` ID and record:

- dependency identity, kind, and required behavior;
- owner and provenance;
- applicability and the obligations or seams that consume it;
- shared-owned or target-owned loading, discovery, or execution route;
- representative availability facts and qualified evidence characteristics; and
- the observable condition for available, unavailable, and failed use.

The manifest is complete only when every direct and transitive required Rule, Skill, tool, schema,
environment capability, and host behavior has a supported route in every applicable seam. Ambient
availability is not a route.

### Representative-seam manifest

Give each materially distinct seam a stable `SEAM-<stable-name>` ID and record:

- the seam's applicability and the accepted target facts that distinguish it materially;
- the smallest supported representative target that covers it;
- every consumed `OBL-*` and `DEP-*` ID;
- required permissions and external-effect boundaries;
- critical success, blocked, failure, recovery, mid-path stop, and terminal paths and exits;
- expected observable results for each material path;
- qualified evidence sources and the characteristics of evidence capable of proving each result;
  and
- the proof characteristics needed to establish static conformance, machine-observable behavior,
  or runtime feasibility.

Choose the smallest nonempty target portfolio whose union covers every evidenced seam that can
materially change applicability, dependency availability, permission, execution, observation,
recovery, or exit. Names and layout alone do not create distinct seams. Representative-target
resources remain evidence or Acceptance inputs and receive no Candidate write authority.

Proof characteristics describe what must be established—for example, an observable route,
fingerprint binding, exit result, or isolated runtime observation. They are not commands, stage
assignments, case schedules, or verdict rules. The public workflow alone determines proof-stage
applicability and execution.

### Validation and pass conditions

Record each validation duty with a stable `VAL-<stable-name>` ID, the `OBL-*`, `DEP-*`, and
`SEAM-*` items it covers, its governing owner, required observations, evidence characteristics,
and exact pass, blocked, and failure conditions.

Shared Input must contain two separate mandatory portability validation duties:

- **Portable semantic authority:** independent public-workflow correctness closure for shared
  ownership, applicability, dependency closure, evidence qualification, and absence of operative
  source-project assumptions.
- **Representative behavior:** separate independent public-workflow correctness closure for every
  representative critical path and exit.

These duties require independent judgment outcomes and fingerprint-bound evidence. They assign no
private stage or Reviewer; the public workflow owns their assignment and execution.

Record portability completion obligations with stable `DONE-<stable-name>` IDs. At minimum they
require:

- accepted portable meaning with no operative source-project assumption;
- complete dependency closure through supported routes;
- coverage of every materially distinct seam by the representative portfolio;
- current independent public-workflow correctness closure for both mandatory portability
  validation duties;
- current public-workflow closure for every applicable validation duty and representative runtime
  input; and
- all closure evidence bound to the final Candidate fingerprint.

### Exact operation grants

Record separate grants for `read`, `write`, `create`, `delete`, `move`, and `network`. Each grant
names the exact resource path or narrowly bounded capability, operation mode, purpose, owner,
applicability condition, and allowed effect. A move records its exact source and destination.
Record an explicit empty set for every ungranted operation class.

Candidate mutation grants cover only exact Candidate resources. Representative targets may receive
only separately accepted evidence reads or execution effects needed as public Acceptance inputs.
The public workflow maps these task/spec permissions into its own role and execution design.

## Closing Shared Input

Close Shared Input only when:

- it describes one supported cross-project SmartKit Rule or Skill;
- every required field has one accepted value and every stable ID is unique;
- every obligation has an accepted disposition, owner, and provenance;
- the dependency manifest is transitively complete;
- the representative portfolio is nonempty, minimal, and collectively covers every material seam;
- both mandatory portability validation duties and their independent public-workflow closure
  conditions are present;
- every validation and completion condition identifies sufficient evidence characteristics;
- exact operation grants authorize the complete intended work and no other effect; and
- Candidate resources and representative-target resources remain disjoint mutation classes.

Supply the closed package unchanged at the public workflow entry as ordinary accepted task/spec
input. It governs portable meaning, evidence qualification, dependencies, validation duties,
permissions, and completion inputs. The public workflow remains sole owner of model selection,
design, the single freeze, roles, evidence selection, stage applicability, Quality, Machine,
Correctness, Acceptance, correction, replay, exits, and finalization. Its bounded
`CONTEXT_REQUIRED` and `ACCESS_REQUIRED` paths remain available after invocation. Shared Input adds
no role, stage, semantic channel, finding lifecycle, audit taxonomy, discovery interface, or
recovery path.

## Portability Coverage Ledger

Create one transient ledger in Agent context after Shared Input closes. Seed one item for every
`OBL-*`, `DEP-*`, `SEAM-*`, `VAL-*`, and `DONE-*` ID. Each item records:

- the stable ID and its Shared Input pass condition;
- the public-workflow-selected evidence and owner-produced verdicts that close it;
- the Candidate fingerprint to which that closure applies;
- any public compatibility binding that establishes closure at a later fingerprint; and
- `open` or `closed-current`, without changing the underlying public result.

The ledger is control and projection data. It is not a Candidate artifact, semantic authority,
proof stage, Reviewer verdict, Acceptance case, or substitute for any public judgment. Populate it
only from qualified evidence selected by the public workflow and closure produced or admitted by
that workflow. A public verdict remains authoritative and unchanged.

At handoff, compare every item with the public workflow's final Candidate fingerprint. An item is
`closed-current` only when its public closure evidence is bound to that fingerprint or the public
workflow supplies its current compatibility binding. Portable success requires both public success
and `closed-current` status for every ledger item.

On portable success, project an exhaustive ledger-derived account into the preserved public
handoff. For every portability ID, include its success fact, public-workflow-selected closure
evidence and owner-produced verdict, final-fingerprint or current compatibility binding, and all
representative-target evidence that supports its closure. Retain the public handoff's operation and
audit records unchanged. The projected account is handoff content, not a persistent ledger,
Candidate artifact, or new verdict.

Preserve any public terminal result without reinterpretation. When portable closure is incomplete,
report the open IDs and their missing fingerprint-bound closure without manufacturing a new public
verdict.

Keep Shared Input and the ledger transient. Create no Candidate copy, workflow report, permanent
fixture, publication, installation, commit, push, release, translation, or downstream effect.
