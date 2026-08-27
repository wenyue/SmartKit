# Separate the Authoring Protocol from Role Launch

Status: Superseded by [ADR 0010](0010-concrete-public-authoring-and-private-shared-overrides.md)

Date: 2026-08-24

## Context

Project-aware Rule and Skill authoring needs role Agents to inspect the current repository, while
shared portability qualification must exclude source-project context and admit only declared
dependencies. Applying one isolation policy to both workflows either blocks necessary project
discovery or exposes private portability policy through the public Skill. Fully independent Skills
would instead duplicate Owner Gate, Review, Acceptance, correction, and invalidation behavior.

## Decision

SmartKit keeps one generic public Authoring Protocol with two entry routes. Direct
`write-rules-and-skills` uses the Default Fresh Role Adapter. Project-private
`write-shared-rules-and-skills` supplies the Soft-Isolated Role Adapter, dependency closure,
source-context exclusion, representative target evidence, and portability pass conditions before
roles start. It injects those private extensions without changing the public Reviewer scopes.

Before roles or candidate writes, the Controller freezes one complete Run Contract containing the
full existing behavior, accepted changes, all preserved and changed dispositions, ownership,
access, capacity, stage order, pass and stop conditions, validation plan, and exit. A complete
accepted Issue or Spec or uniquely supported local repair may establish alignment. Material
behavioral, ownership, permission, validation, or exit ambiguity returns `ALIGNMENT_REQUIRED` and
routes the user to explicitly invoke `grilling`. Later context additions are nonsemantic; a material
change requires a new run. Candidate edits in a self-modifying run affect only a later independent
invocation.

Default-adapter Authors and Reviewers inspect the repository directly; no Project Explorer mediates
evidence. One fresh Author persists through all Candidate Versions and alone edits its exact
Candidate Allowlist. Reviewers remain read-only. The Controller owns the pre-write fingerprint,
single-writer lock, later fingerprints, and Role Boundary Audit after every role callback. The
allowlist is a behavioral prompt contract, not a hard sandbox. Context-document use and its narrow
translation exception remain owned by the project Rule.

Generic output alone does not require Soft Isolation. `write-setup-authoring-contracts` legitimately
uses this repository's setup catalog, blueprint owner, and representative target evidence, so it
uses the Default Fresh Role Adapter with one persistent Author, applicable machine validation, and
one persistent Static Reviewer; it starts no Quality pair, Correctness pair, or Acceptance Runner.
Its Setup Authoring Contract is always a judgment-only description of target meaning, evidence,
ownership, writes, validation, handoff, and ambiguity stops; it does not prescribe generation steps,
ordering, or tools. Soft Isolation remains specific to shared Rule and Skill portability
qualification.

The public Skill routes the protocol through references with one owner each:

- `owner-gate.md` owns obligation and artifact ownership classification;
- `role-launch.md` owns the Role Launch Interface, Default Fresh Role Adapter, and Role Capacity
  Gate;
- `author.md` owns the persistent Author contract;
- `rule-semantics.md` and `skill-semantics.md` own their respective candidate models and cases;
- `correction-cycle.md` owns the common correction, finding, rewind, and no-progress protocol;
- `quality-review.md`, `machine-validation.md`, `correctness-review.md`, and `acceptance.md` own the
  ordered Evaluation Sequence stages.

Evaluation order is Quality pair, applicable machine validation, Correctness pair, then conditional
executable Acceptance. Pair identities persist until both pass the same Candidate Version; later
invalidation starts a fresh pair. Reviewers own findings and verdicts, the Author owns repair or
decline, and the Controller owns orchestration and the bounded handoff. Qualification requires four
concurrently active identities including the Controller and capacity to retain the paused fifth
Acceptance Reviewer required by a rewind.

Machine validation and executable Acceptance are conditional on deterministically testable or
material runtime risk. Acceptance freezes cases and pass criteria, retains one Reviewer per case,
and uses a fresh Runner with exact case-scoped grants in disposable isolation for every attempt.
The Candidate remains immutable. Before a Runner starts, missing permission, safe isolation, or
existing authority yields `EXECUTION_UNAVAILABLE`. Every started attempt captures evidence, audits,
ends the Runner with established quiescence, and only then performs safe authorized cleanup. Its
terminal precedence is `ATTEMPT_INVALID` for any audit or evidence-capture failure, otherwise
`RUNNER_NOT_QUIESCENT`, otherwise `CLEANUP_FAILED`; terminal evidence includes quiescence and
residual state. The Controller starts the case Reviewer only after the first Runner attempt
finalizes successfully. Only a candidate defect reaches the persistent Author; fixture defects may
rerun, and ambiguity receives at most one targeted fresh attempt. These attempt semantics are owned
by `acceptance.md`.

Shared portability adds no fifth Reviewer. The private caller injects dependency closure,
source-context exclusion, and representative target checks into the existing two Correctness roles
and conditional Acceptance. Portability PASS composes Soft-Isolation qualification and those
generic-stage verdicts for one Candidate Version.

Every Correctness Reviewer receives the complete accepted user-decision context and the existing
obligations that remain in force. This same evidence basis covers a candidate that changes the
authoring or review standard itself; no separate self-change role or review cycle is needed.
Revision Impact controls which passed stages rerun after later edits; it does not replace the
Reviewer's requirement context.

The project-private `translate-agent-artifacts` Skill is a separate model-invoked documentation
handoff. The project documentation owner selects the required final English Rule and Skill set; a
source at `<path>` maps to `docs/zh-CN/<path>`. One invocation updates the complete affected mirror
set once. It has no Reviewer, correction cycle, Acceptance, fingerprint, or authoring stage protocol.
A context glossary may help choose wording but cannot add, change, disambiguate, or resolve English
meaning.

For this authoring-system migration, executable self-host Acceptance is limited to two risks:
material ambiguity must return `ALIGNMENT_REQUIRED` before roles or writes, and self-modification
must continue under the frozen complete Run Contract while candidate changes affect only a later
invocation. Translation handoff receives normal content and test checks, not an Acceptance flow.

## Consequences

The two real Adapters provide a stable seam for testing role independence, access, lifecycle,
capacity, and failure behavior while preserving one maintenance point for the common Acceptance
Standard. The private shared entry may evolve portability qualification without adding shared
branches to the public Interface.

This decision fully supersedes ADR 0008's universal Soft-Isolation role policy. Soft Isolation
remains current only as the private shared Adapter for portability qualification; the historical
packet-only evidence, replacement-content Author, and per-version role behavior do not remain in
force. English candidates complete first; required Simplified-Chinese mirrors follow through the
independent translation handoff.
