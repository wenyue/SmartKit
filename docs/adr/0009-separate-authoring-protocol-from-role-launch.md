# Separate the Authoring Protocol from Role Launch

Status: Accepted

Date: 2026-08-24

## Context

Project-aware Rule and Skill authoring needs role Agents to inspect the current repository, while
shared portability qualification must exclude source-project context and admit only declared
dependencies. Applying one isolation policy to both workflows either blocks necessary project
discovery or exposes private portability policy through the public Skill. Fully independent Skills
would instead duplicate Owner Gate, Review, Acceptance, correction, and invalidation behavior.

## Decision

SmartKit keeps two authoring entry Skills and one common Authoring Protocol. The public
`write-rules-and-skills` entry uses the Default Fresh Role Adapter. The project-private
`write-shared-rules-and-skills` entry supplies the Soft-Isolated Role Adapter and owns dependency
closure, source-context exclusion, representative target evidence, and portability pass
conditions.

The Authoring Protocol depends only on a Role Launch Interface that qualifies, starts, continues,
and finishes role Agents. An Adapter is selected before the first role starts and cannot be changed
or mixed during the run. The public workflow does not know Soft Isolation or shared portability,
and the private workflow does not override scattered public instructions or duplicate the common
authoring gates. Project-local Author and Reviewer roles may inspect the repository directly under
read-only access; the Author may also modify only its Controller-approved candidate Role File
Allowlist. No Project Explorer role mediates that evidence. The private Adapter gives every
Soft-isolated role its own minimum Role File Allowlist; a Soft-isolated Author edits allowed
candidate files directly and requests any expansion explicitly without gaining source-project
access.

Project context documents are unstable, non-normative conversational glossaries. Project-local
Authors and Reviewers may consult them only to interpret or explain language in user communication;
they must not use them as authoring or Review evidence, import their terminology as a stable
contract, or leave any operative meaning available only there. Every durable meaning and name comes
from an independently accepted source. Shared candidates and Setup Authoring Contracts satisfy the
same Context-document Independence through their existing cross-project requirements.

A Role File Allowlist separates read, write, create, and delete authority. A Rule normally exposes
its exact candidate file; a Skill may expose its own Skill root, but never the parent `skills/`
directory. Every Author returns a concise semantic Author Change Summary. The Controller separately
computes one compact transient Candidate Fingerprint to bind evidence without loading complete file
bodies or diffs into its context.

Each Author turn runs under a Controller-enforced Candidate Write Lock. After every Subagent
callback, the Controller performs a Role Boundary Audit against observed operations before using the
result or continuing the role. The allowlist is a behavioral prompt contract rather than a claimed
hard filesystem sandbox. The audit uses all host records available, the Agent's required Operation
Summary, Candidate Fingerprints, and changed paths; an absent complete host trace alone is not a
failure, while an observed violation or irreconcilable evidence conflict is. A host that cannot
preserve persistent Agents and their expanded prompt contracts fails qualification before authoring.

Generic output alone does not require Soft Isolation. `write-setup-authoring-contracts` legitimately
uses this repository's setup catalog, blueprint owner, and representative target evidence, so it
uses the Default Fresh Role Adapter with its own simpler machine-validation and static-review flow.
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

The former `ordinary-artifact.md` lifecycle branch has no replacement because the public Skill
already accepts only directly used Rule or Skill candidates. The former `pruning-agent.md`,
`semantic-review.md`, and `acceptance-runner.md` responsibilities move to their corresponding stage
owners. Public `soft-isolation.md` moves to the private shared workflow as
`soft-isolated-role-adapter.md`; that workflow also owns `portability.md`.

Quality Review uses parallel Semantic Economy and Information Design Reviewers; Correctness Review
uses parallel Semantic Fidelity and Ownership and Agent Executability and Behavioral Closure
Reviewers. Each returns evidence-backed findings in its exclusive scope, the persistent Author owns
repair or decline dispositions, and each Reviewer owns only its stage verdict. The Rule or Skill
workflow requires four concurrently active role slots including the Controller and two parallel
Subagent turns. Active capacity is distinct from retained identity capacity: an Acceptance rewind
can retain five identities including the Controller while some remain idle. The simpler Setup
Authoring Contract workflow requires three retained identities and one persistent Static Reviewer.
The Controller owns the final bounded Handoff Report.

An out-of-scope observation is a one-way Scope Transfer Note rather than a finding. The receiving
Reviewer alone decides whether it supports a finding. The Controller freezes an executable
Acceptance Portfolio only for material runtime risks not already established with supported high
confidence; otherwise Acceptance is `NOT_REQUIRED`. Each failed run is classified by its persistent
Acceptance Reviewer as a candidate defect, a fixture or environment defect, or ambiguous. Only a
candidate defect enters Author correction, and one still-ambiguous targeted rerun stops rather than
weakening the frozen case.

Shared portability adds no fifth Reviewer. Semantic Fidelity and Ownership covers dependency
closure, source-project-only assumptions, and portable ownership and applicability; Agent
Executability and Behavioral Closure applies its normal checks across representative target
contexts. Portability PASS composes the current Probe, both Correctness verdicts, and conditional
Representative Acceptance for one Candidate Version.

Every Correctness Reviewer receives the complete accepted user-decision context and the existing
obligations that remain in force. This same evidence basis covers a candidate that changes the
authoring or review standard itself: no separate Standard Change role, review cycle, or reference is
needed. Revision Impact controls which passed stages rerun after later edits; it does not replace the
Reviewer's requirement context.

## Consequences

The two real Adapters provide a stable seam for testing role independence, access, lifecycle,
capacity, and failure behavior while preserving one maintenance point for the common Acceptance
Standard. The private shared entry may evolve portability qualification without adding shared
branches to the public Interface.

This decision partially supersedes ADR 0008: Soft Isolation remains required for shared
portability qualification, but is no longer the universal role-launch policy for project-aware
authoring and review. Implementing the decision requires the public and private Skills, their
references, domain definitions, documentation translations, and representative Acceptance cases to
change together.
