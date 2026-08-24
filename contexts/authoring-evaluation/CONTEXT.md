# Authoring Evaluation

Authoring Evaluation defines how SmartKit classifies, authors, qualifies, reviews, corrects, and
adopts Rules, Skills, and Setup Authoring Contracts.

## Language

**Setup Authoring Contract（项目设置编写契约）**:
A project-owned input under `setup-assets/blueprints/` that guides `setup-project-agents` in using
the public authoring Skill to create one complete future project-local Rule or Skill. The contract
is generic across target projects but legitimately depends on this repository's setup catalog,
blueprint owner, and representative target evidence, so its simpler Author, machine-validation, and
static-review correction flow uses the Default Fresh Role Adapter rather than Soft Isolation. The
real target is later reviewed independently as a Rule or Skill candidate.
_Avoid_: Generated target, generator fixture

**Qualification Campaign（资格验证活动）**:
One bounded application of the Acceptance Standard across the representative canary classes needed
to qualify the SmartKit authoring workflow.
_Avoid_: Separate acceptance standard, full rewrite, canary cycle

**Acceptance Standard（验收标准）**:
The single quality contract every authored Rule, Skill, or Setup Authoring Contract must satisfy through
evidence-backed authoring, machine validation, fresh semantic review, risk-matched acceptance, and
explicit handoff.
_Avoid_: Qualification-only gate, ordinary acceptance

**Acceptance Portfolio（验收方案集）**:
The Controller-frozen set of executable cases for material runtime risks not already established
with supported high confidence. It contains at least one case for each distinct remaining risk,
always covers the applicable normal path, and adds an error or recovery path only when its behavior
is materially different. It has no fixed case count. When no such risk exists, the Executable
Acceptance Gate returns `NOT_REQUIRED`; a Setup Authoring Contract's representative walkthrough
belongs to Static Contract Review rather than this portfolio.
_Avoid_: Acceptance level, alternate standard, static acceptance

**Executable Acceptance Gate（执行验收判定关口）**:
The Controller-owned risk decision that requires an Acceptance Runner only when a candidate defines
sufficiently concrete or complex runtime behavior whose material correctness is not already
established with supported high confidence by machine validation, static Review, or an unchanged
previously accepted mechanism. Broad procedural guidance without a concrete tool protocol, and
simple environment-independent behavior with supported high confidence, do not require
Representative Acceptance. Skill Shape alone does not determine the verdict.
_Avoid_: Every Procedure-led Skill, Author confidence, any ordered list

**Canary Candidate（试点候选项）**:
One independently evaluated version of a representative Rule, Skill, or Setup Authoring Contract in
a Qualification Campaign.
_Avoid_: Candidate bundle, whole-campaign version

**Candidate Version（候选版本）**:
The complete current content state of one authored candidate. A content change creates a new
version; evidence does not transfer automatically, and only evidence before the earliest stage
invalidated by the Controller's Revision Impact Decision may be retained. A version does not
require a copied tree and is bound to evidence by one transient Candidate Fingerprint.
_Avoid_: Git revision, copied directory, inherited verdict

**Candidate Fingerprint（候选指纹）**:
A compact deterministic digest that the Controller computes from the canonical path set and bytes
of every file in the Candidate Version. It detects content or path changes and binds stage evidence
without loading file bodies or a complete diff into Controller context. It remains transient and is
not a semantic change description.
_Avoid_: Author summary, persisted manifest, diff review

**Author Change Summary（作者修改摘要）**:
The persistent Author's concise report after a candidate write, naming changed, created, and deleted
paths, affected obligations and semantic surfaces, actual Repair Scope, and uncertainty. The
Controller uses it with compact path and fingerprint evidence for the Revision Impact Decision and
opens only a targeted diff when those inputs are inconsistent or insufficient.
_Avoid_: Candidate Fingerprint, full replacement content, Author impact verdict

**Candidate Write Lock（候选写锁）**:
The Controller-enforced single-writer interval around each Author turn. It records the starting
Candidate Fingerprint, permits no other role or machine check to modify candidate paths, and compares
the ending fingerprint and changed path set with the Role File Allowlist and Author Change Summary.
An out-of-allowlist or unattributable change invalidates the result and stops without overwriting,
reverting, or concealing the conflicting state.
_Avoid_: Filesystem lock file, automatic rollback, concurrent reviewer edit

**Owner Gate（归属判定关口）**:
The pre-authoring decision point that classifies each obligation and its complete artifact as Rule,
Skill, Split, Environment-owned, or Ambiguous, then compares that verdict with the requested or
current owner.
_Avoid_: Approval gate, Rule approval

**Ownership Review（归属审查）**:
The read-only `write-rules-and-skills` branch that applies the Owner Gate to existing artifacts and
exits with supported ownership verdicts without creating a Candidate Version.
_Avoid_: Separate Skill, authoring workflow

**Policy Frame（规则框架）**:
The semantic structure of one Rule, relating its owner and strength, scope and applicability,
observable predicate-to-outcome mappings, exceptions, precedence, and ownership boundaries without
describing a triggered job procedure.
_Avoid_: Rule workflow, policy rationale

**Setup Contract Frame（项目设置契约框架）**:
The judgment-only descriptive structure of one Setup Authoring Contract, relating its future target
and owner, required evidence and obligations, permitted writes, validation, handoff, and
material-ambiguity stops. It never prescribes the Author's generation steps, ordering, or tools. A
future Procedure-led Skill may require procedural target semantics, but the contract describes those
required semantics rather than an authoring procedure. Neither the contract nor the future target it
specifies may derive terminology or operative meaning from a target project's `CONTEXT.md`.
_Avoid_: Generated target outline, mandatory authoring recipe, contract Job Graph

**Skill Shape（技能设计形态）**:
The authoring posture selected for one Skill from supported evidence: Judgment-led,
Procedure-led, or Hybrid.
_Avoid_: Skill type, document format

**Judgment-led Skill（判断主导型技能）**:
A Skill that constrains its objective, evidence, principles, invariants, decision boundaries, and
exits while leaving the method to Agent judgment.
_Avoid_: Descriptive Skill, unstructured Skill

**Procedure-led Skill（流程主导型技能）**:
A Skill that prescribes supported actions or ordering because the process materially affects
correctness, safety, external protocol compliance, coordination, recovery, or the accepted outcome.
_Avoid_: Detailed Skill, complete workflow

**Hybrid Skill（混合型技能）**:
A Judgment-led Skill containing one or more evidence-backed Procedural Islands while leaving the
remaining method to Agent judgment.
_Avoid_: Partially specified Skill, mixed document

**Judgment Frame（判断框架）**:
The semantic structure of a Judgment-led Skill, relating its objective, evidence, principles,
invariants, decision boundaries, and prioritized exits without prescribing an unsupported method.
_Avoid_: Job Graph, procedure outline

**Job Graph（任务执行图）**:
The semantic structure of a Procedure-led Skill or Procedural Island, relating its entry, actions,
branches, runtime resources, and prioritized exits independently of any document outline.
_Avoid_: Markdown outline, procedure draft

**Execution Path（执行路径）**:
One reachable route through a Job Graph from its entry to exactly one prioritized completion, stop,
or failure exit.
_Avoid_: Phase list, branch inventory

**Procedural Island（固定流程片段）**:
One bounded Procedure-led part of a Hybrid Skill that returns control to Agent judgment after its
prioritized exit.
_Avoid_: Workflow phase, procedural Skill

**Artifact Projection（工件职责映射）**:
The placement of each Judgment Frame, Job Graph, or Procedural Island obligation into its narrowest
reliable runtime owner and loading tier without changing the Skill's observable behavior.
_Avoid_: Content splitting, editorial reorganization

**Entry Sufficiency（入口信息完备性）**:
The property that a Skill's main file identifies its Skill Shape, objective or entry, applicable
Judgment Frame or Execution Path, and conditionally required resources without unrelated detail.
_Avoid_: Self-contained main file, short main file

**Path Sufficiency（路径信息完备性）**:
The property that a Skill's main file plus the resources selected by one Execution Path are enough
to execute that path to its unique prioritized exit.
_Avoid_: Whole-Skill self-containment, eager resource loading

**Frozen Canary（已冻结试点候选项）**:
A Canary Candidate whose own machine validation, semantic review, and representative acceptance
have passed and whose evidence has not been invalidated.
_Avoid_: Approved campaign, immutable file

**Adoption Gate（仓库纳入关口）**:
The all-or-none boundary that permits repository adoption only after every required Canary Candidate
has passed its own gates.
_Avoid_: Campaign restart, per-canary writeback

**Correction Loop（修正循环）**:
The authoring cycle that applies all current uniquely forced findings, reruns invalidated gates, and
continues while each revision makes progress toward a passing Candidate Version.
_Avoid_: User-confirmed retry, fixed correction budget, one-finding patch

**No-progress Stop（无进展停止）**:
The Controller-owned failure exit with no fixed total-round limit. It applies when the same finding
survives two consecutive Author repairs with no new viable approach; two complete repair
oscillations cannot satisfy all findings together; correction requires an unauthorized decision;
accepted requirements conflict; two materially different recoveries cannot clear one execution
blocker; or required isolation or role capacity cannot qualify. The Controller records the stage
and case, unresolved finding or blocker, attempted repairs or recoveries, latest Candidate Version,
valid and invalidated evidence, and the decision or external condition needed before closing the
Author and Reviewers.
_Avoid_: Retry budget, first failed revision, lack of immediate PASS

**Correction Cycle Protocol（修正周期协议）**:
The common single-stage protocol in which the same Reviewer or Reviewer group inspects, sends every
Review Finding to the persistent Author for a Finding Disposition, and reinspects the complete
candidate and dispositions after each Author revision until it returns Stage-local PASS. The
Reviewers remain active while the Controller makes the Revision Impact Decision and, when that
decision rewinds the Evaluation Sequence, until the sequence returns and they recheck. They finish
only when the Controller confirms the stage can close or a stop condition applies.
_Avoid_: One Reviewer per revision, immediate rewind, Reviewer-authored fix

**Stage-local PASS（阶段内通过）**:
A provisional stage verdict that its current evidence satisfies that stage's PASS condition. It
triggers the Controller's Revision Impact Decision after an Author revision but does not itself
close the stage or its Reviewers.
_Avoid_: Final acceptance, workflow completion, Reviewer shutdown

**Evaluation Sequence（评估顺序）**:
The fixed order Quality Review Cycle, machine validation, Correctness Review Cycle, then
Representative Acceptance only when required by the Executable Acceptance Gate. A stage not yet
reached has no evidence to invalidate and is executed normally when the sequence reaches it.
_Avoid_: Parallel gates, validation matrix, unordered checklist

**Machine Validation Cycle（机器验证周期）**:
The deterministic Evaluation Sequence stage in which the Controller runs required checks, sends
each exact failing command, final exit, and relevant output to the persistent Author, and reruns the
checks after each Author revision until they pass. No Reviewer participates. After Stage-local PASS,
the Controller makes the Revision Impact Decision; the No-progress Stop applies to two consecutive
repairs of the same failure with no new viable approach.
_Avoid_: First-failure stop, Controller-authored fix, semantic review

**Revision Impact Decision（修订影响判定）**:
The Controller-owned decision after an active stage returns Stage-local PASS following an Author
revision. It uses the accumulated Author Change Summaries, changed path set, and Candidate
Fingerprints, inspecting only a targeted diff when those inputs are insufficient, then selects the
earliest already-passed stage whose evidence is invalidated. The Evaluation Sequence resumes from
that stage; when no earlier stage is invalidated, the active stage closes and the sequence advances.
Future stages are not classified as invalidated. The Author cannot waive or select independent
checks.
_Avoid_: Author self-classification, validation matrix, future-stage invalidation

**Quality Review Cycle（质量审查周期）**:
The Correction Cycle Protocol whose Semantic Economy Reviewer and Information Design Reviewer
return Stage-local PASS when neither has an unresolved Review Finding that prevents passage after
considering the Author's Finding Dispositions. A later candidate change after the Controller closes
this cycle starts a new cycle with new Reviewers.
_Avoid_: Pruning Gate, correctness review, permanent reviewer session

**Semantic Economy Reviewer（语义精简审查者）**:
The Quality Reviewer that challenges duplicated, unnecessary, misplaced, environment-cached, or
no-op instruction while stating the behavior, authority, safety boundary, and exit that its proposed
reduction must preserve. It may identify repetition of another owner but does not decide which owner
is semantically correct or provide replacement prose.
_Avoid_: Pruner, copy editor, semantic correctness reviewer

**Information Design Reviewer（信息设计审查者）**:
The Quality Reviewer that evaluates information hierarchy, progressive disclosure, branch
placement, reference routing, terminology, clarity, and ambiguity without deciding whether the
candidate is semantically correct or providing replacement prose.
_Avoid_: Style reviewer, documentation linter, executability reviewer

**Correctness Review Cycle（正确性审查周期）**:
The Correction Cycle Protocol whose Semantic Fidelity and Ownership Reviewer and Agent
Executability and Behavioral Closure Reviewer return Stage-local PASS when neither has an unresolved
Review Finding that prevents passage after considering the Author's Finding Dispositions. Both
Reviewers recheck the complete candidate after every revision and remain active until the Controller
closes the cycle or a stop condition applies.
_Avoid_: One-reviewer-per-revision, acceptance run, author self-verification

**Semantic Fidelity and Ownership Reviewer（语义保真与归属审查者）**:
The Correctness Reviewer that checks every accepted obligation for loss, distortion, unsupported
addition, wrong semantic owner, authority, or applicability. It alone owns semantic ownership
correctness and does not evaluate information design, execution closure, or replacement wording.
It also checks Context-document Independence.
For a shared candidate, its existing scope also covers declared dependency closure, use of
source-project-only facts, and portable ownership and applicability across representative targets.
_Avoid_: Quality reviewer, executability reviewer, artifact Author

**Agent Executability and Behavioral Closure Reviewer（智能体可执行性与行为闭合审查者）**:
The Correctness Reviewer that checks triggers, inputs, tools, permissions, branches, recovery,
failures, handoff, and the unique prioritized exit of every applicable Execution Path. It does not
rejudge semantic ownership, information design, or replacement wording. For a shared candidate, it
applies the same checks to each representative target context supplied by the private workflow.
_Avoid_: Semantic fidelity reviewer, acceptance Runner, artifact Author

**Review Finding（审查问题）**:
A supported issue returned by a Reviewer with a stable finding identifier, problem statement,
evidence, candidate location or concrete counterexample, `critical`, `material`, or `advisory`
severity, estimated Repair Scope, affected obligation or semantic surface, and the behavior,
authority, owner, and exit a correction must preserve. The Reviewer may state correction constraints
but does not provide replacement prose or decide whether the Author should write a correction.
_Avoid_: Required edit, Worth-fixing Finding, unsupported preference

**Scope Transfer Note（职责转交说明）**:
A non-verdict observation used when a Reviewer sees a plausible issue outside its exclusive scope.
It names the evidence and intended owning Reviewer but neither creates a Review Finding nor blocks
the originating Reviewer's Stage-local PASS. The Controller routes it mechanically once; the
receiving persistent Reviewer independently decides whether its own scope supports a finding. If no
Reviewer owns a material issue, the workflow stops with an explicit ownership gap instead of passing
it between roles.
_Avoid_: Cross-scope finding, Controller semantic triage, reviewer ping-pong

**Finding Disposition（问题处置）**:
The persistent Author's `repair` or `decline` decision for one Review Finding. `repair` makes the
finding Worth-fixing; `decline` gives a concise supported reason. The same Reviewer considers the
disposition and revised complete candidate and alone decides its stage verdict. The Controller does
not make the semantic choice. The same unresolved Author-Reviewer disagreement after two complete
rounds triggers the No-progress Stop or an exact decision-required exit.
_Avoid_: Controller triage, Reviewer-authored correction, hidden rejection

**Worth-fixing Finding（值得修复的问题）**:
A Review Finding whose Author Finding Disposition is `repair` after considering severity, Repair
Scope, candidate coherence, and regression risk. Critical and material findings normally justify
repair whenever correction is authorized; an advisory finding with a Local Repair is presumed worth
fixing. A supported `decline` remains visible to the same Reviewer for its independent stage verdict.
_Avoid_: Reviewer-mandated edit, every suggestion, severity label

**Repair Scope（修复范围）**:
The semantic surface a proposed correction can affect, including behavior, ownership, dependencies,
loading, authority, side effects, and exits. Reviewers estimate it when triaging a finding; the
Author must report when the actual correction would exceed that estimate so disposition can be
re-evaluated before broadening the change.
_Avoid_: Line count, finding severity, implementation effort

**Local Repair（局部修复）**:
A correction normally limited to one or two sentences or one small contiguous block that preserves
behavior, ownership, dependencies, loading, authority, side effects, and exits. Physical size alone
does not make a repair local; changing any of those semantic surfaces requires a broader Repair
Scope.
_Avoid_: Small diff, quick edit, low-severity finding

**Authoring Protocol（编写协议）**:
The common Rule and Skill authoring process that owns candidate modeling, role coordination,
validation, Review, Acceptance, correction, invalidation, and handoff independently of how role
Agents receive project evidence.
_Avoid_: Project-local workflow, shared workflow, role launcher

**Context-document Independence（上下文文档独立性）**:
The candidate property that no terminology or operative trigger, obligation, decision, branch, tool
use, permission, dependency, validation, handoff, or exit is derived from a project `CONTEXT.md` or
equivalent domain-context document. Those unstable, non-normative documents may be consulted only to
interpret or explain language in user communication; they are not authoring or Review evidence.
Every durable meaning and name must instead come from an independently accepted source. A candidate
may use the same words only when it establishes their required meaning independently, remains usable
without the context document, and never instructs a runtime Agent to read it. Shared Rules and
Skills and Setup Authoring Contracts satisfy the same property through their existing cross-project
independence requirements.
_Avoid_: Context glossary as evidence, runtime CONTEXT.md dependency, glossary-driven naming

**Persistent Author（持续作者）**:
The one role Agent that writes the initial candidate and every later correction through the selected
Role Launch Adapter. It may discover project evidence only through its Adapter, edits only the Role
File Allowlist under the Candidate Write Lock, and returns an Author Change Summary,
CONTEXT_REQUIRED, or ACCESS_REQUIRED. It does not run validation, Review, Acceptance, network
access, or delegation, and remains available until workflow success or stop.
_Avoid_: Controller editor, per-revision Author, author-verifier

**Role Launch Interface（角色启动接口）**:
The seam through which the Authoring Protocol qualifies, starts, continues, and finishes role
Agents while preserving their required independence, lifecycle, capacity, access, and failure
behavior. One Role Launch Adapter is selected before the first role starts and remains fixed for
the run.
_Avoid_: Isolation mode, prompt override, subagent helper

**Role Capacity Gate（角色容量关口）**:
The pre-Author host qualification whose Rule or Skill branch requires capacity for at least four
concurrently active Agent roles including the Controller and at least two concurrently running
Subagent turns. Active capacity is distinct from retained identity capacity: an Acceptance rewind
can require the Controller, persistent Author, persistent Acceptance Reviewer, and two earlier-stage
Reviewers to remain resumable as five identities even though they do not all run simultaneously. A
host that counts idle identities against one limit must therefore support that retained set. The
Setup Authoring Contract branch requires three retained role identities and no parallel Subagent
turns. Both branches require resumable idle Agents, prompt-declared and expandable per-role access,
and enough observable evidence for a Role Boundary Audit after every Subagent callback. The Rule or
Skill branch also requires creation of a replacement Fresh Acceptance Runner after a prior Runner
finishes. Failure or uncertainty stops before the Author starts; the Controller must not serialize a
Reviewer pair, skip auditing, or replace a persistent role to fit a smaller host.
_Avoid_: Codex product limit, best-effort parallelism, total-identity and active-turn conflation

**Role Boundary Audit（角色边界审计）**:
The Controller check immediately after every Subagent callback and before using its result or
continuing that Agent. It compares the most recent turn's observed tools, paths, commands, reads,
writes, network activity, delegation, and output behavior with the selected Adapter, Role File
Allowlist, allowed tools, and role contract. It uses all host-observed operation records available,
the required Agent Operation Summary, Candidate Fingerprints, and changed paths. Soft Isolation is a
behavioral contract, so the absence of a complete host trace alone does not fail the Gate. PASS
admits the result; an observed violation or irreconcilable conflict among the available evidence
quarantines the result, invalidates affected Candidate or Soft-Isolation evidence, and stops without
automatic rollback.
_Avoid_: Final-workflow audit, hard-sandbox proof, ignored evidence conflict

**Operation Summary（操作摘要）**:
The concise Subagent report for its most recent turn, listing tools, commands, paths read or changed,
network activity, delegation, and any attempted operation outside its role contract. The Controller
cross-checks it against host-observed records, Candidate Fingerprints, and changed paths during the
Role Boundary Audit.
_Avoid_: Audit proof, workflow report, semantic change summary

**Default Fresh Role Adapter（默认独立角色适配器）**:
The public Role Launch Adapter that starts Agents without inherited parent turns and permits
role-appropriate read-only discovery of the current project plus Author writes within the Role File
Allowlist. Reviewers remain read-only. It is selected when no more-specific caller supplies another
Adapter.
_Avoid_: Project-local mode, Soft Isolation, Project Explorer

**Soft-Isolated Role Adapter（软隔离角色适配器）**:
The project-private Role Launch Adapter that qualifies Soft Isolation, excludes source-project
context, supplies declared semantic input, and states each role's Role File Allowlist as an explicit
prompt contract for shared portability evaluation. The Author may read and write its allowlist;
Reviewers may only read theirs; an Acceptance Runner receives only its case files and explicitly
required tools. No Soft-isolated role delegates. The Adapter does not claim that the host makes
undeclared paths technically inaccessible.
_Avoid_: Shared mode, public isolation option, prompt override

**Role File Allowlist（角色文件白名单）**:
The Controller-approved minimum behavioral access contract for candidate canonical files and owned
resources, with separate `read`, `write`, `create`, and `delete` modes for each path. The Controller
states it explicitly in the role prompt and audits observable behavior after each callback. Prefer
exact files. A Skill candidate may expose its own Skill root as one candidate-owned subtree so the
Author can manage references, scripts, assets, and interface metadata; this never grants its parent
`skills/` directory. A Rule normally exposes its exact file. Expansion requires ACCESS_REQUIRED,
owner and portability checks, and renewed qualification of the effective access boundary. It never
includes the repository root, unrelated source-project content, or undeclared dependencies. `write`
does not imply `create` or `delete`, and deletion always requires explicit permission.
_Avoid_: Workspace permission, broad glob, implicit access

**Role-fresh Agent（角色独立智能体）**:
An Agent that did not perform the role whose output it now evaluates. Role freshness prevents
authoring commitments or prior case results from entering a later judgment, but does not prove
source-project context isolation.
_Avoid_: New prompt in the same conversation, soft-isolated Agent

**Soft-isolated Agent（软隔离智能体）**:
A fresh Agent with no inherited turns that runs only after the current top-level workflow passes a
Soft-Isolation Probe and receives all semantic input through an explicit initial Context Packet and
any Context Supplements or declared files in its Role File Allowlist. A Soft-isolated Author edits
the allowed candidate files directly and returns a concise change summary. Soft isolation is a
verified behavioral boundary, not an adversarial security boundary.
_Avoid_: Context-clean Agent, ordinary source-project subagent, role-fresh Agent

**Soft-Isolation Probe（软隔离探针）**:
One disposable fresh Agent run with the same effective launch and file-access policy before the
first Soft-isolated Agent in a top-level authoring workflow and after each Role File Allowlist
expansion. It checks that the launch receives no inherited parent turns, receives its declared
prompt and files, and follows the behavioral access contract in the observable probe task. It does
not claim that undeclared filesystem paths are technically inaccessible. An observed violation or
contradictory evidence stops the workflow without fallback.
_Avoid_: Acceptance canary, per-role probe, Harness exception

**Portability Qualification（可迁移性验证）**:
The shared workflow's composite result rather than a separate Reviewer or correction cycle. PASS
requires the current Soft-Isolation Probe, declared dependency closure, both Correctness Reviewers'
shared-scope checks across representative target contexts, and Representative Acceptance when the
Executable Acceptance Gate requires it, all for the same Candidate Version.
_Avoid_: Fifth Reviewer, portability review stage, source-project simulation

**Context Packet（上下文包）**:
The complete semantic input known when one Soft-isolated Agent starts that is not supplied through
its Role File Allowlist, including accepted intent, explicit user decisions, preserved existing
obligations, selected evidence and dependencies, and any allowed non-file tools. A later missing
fact uses CONTEXT_REQUIRED and a Context Supplement rather than restarting the role.
_Avoid_: Workspace discovery, repository snapshot, persistent packet file

**Context Supplement（上下文补充）**:
Sourced, additive semantic input that the Controller sends to the same role Agent after
CONTEXT_REQUIRED. It fills a declared gap without retracting, correcting, or silently superseding
the initial Context Packet or an earlier Supplement. Any such invalidating change requires a fresh
role with one internally consistent replacement context.
_Avoid_: Complete replacement packet, unsourced hint, implicit correction

**CONTEXT_REQUIRED（需要上下文）**:
A non-verdict role response that identifies each missing material fact and why the role cannot
continue without it. An Agent using the Default Fresh Role Adapter first performs its own permitted
project discovery; an Agent using the Soft-Isolated Role Adapter requests the missing declared input
without reading the source project. The Controller normally supplies a Context Supplement and
continues the same Agent. Correction or withdrawal of prior context, a material task, owner, or
Acceptance Standard change, Soft Isolation contamination, or irreconcilable context requires a
fresh role instead.
_Avoid_: Project Explorer request, automatic role restart, speculative completion

**ACCESS_REQUIRED（需要访问权限）**:
A non-verdict role response that names each additional exact file or narrowly owned directory,
requested `read`, `write`, `create`, or `delete` mode, and why the role cannot continue without it.
The Controller grants only authorized candidate or owned-resource access that preserves the selected
Adapter's boundary, then renews required qualification and continues the same Agent. A request for
undeclared source-project context is answered through an eligible Context Supplement or stops; it
is not added to a shared Role File Allowlist. If the host cannot expand access while preserving the
persistent Agent, the Role Capacity Gate fails.
_Avoid_: Repository access, implicit permission expansion, context request

**Ambient Context（宿主附带上下文）**:
Context a Harness exposes outside the Context Packet. Project entry-file content and its Rule or
Skill pointers, plus Skill catalog metadata, may be observable, but the Agent must not follow those
pointers; any undeclared Rule or complete Skill body outside the Role File Allowlist invalidates
soft-isolation qualification.
_Avoid_: Context Packet, accepted dependency

**Fresh Reviewer（独立审查者）**:
A Role-fresh Agent started through the selected Role Launch Adapter that did not author the
Candidate Version it evaluates. A Setup Authoring Contract and a real target created later receive
separate Reviewers and do not inherit verdicts.
_Avoid_: Author self-review, inherited reviewer

**Acceptance Runner（验收执行者）**:
A Role-fresh Agent started through the selected Role Launch Adapter that applies one candidate to
one representative task. It receives tools only when the artifact's observable behavior requires
them and does not receive the semantic ledger, expected result, diff, author reasoning, review
findings, or prior case output. It reports observable operations, output, and side effects without
judging whether they pass.
_Avoid_: Acceptance reviewer, prepared-answer agent, paper walkthrough

**Acceptance Reviewer（验收审查者）**:
A Role-fresh Agent that compares an Acceptance Runner's reported observations with the frozen case
and pass conditions, then returns PASS or supported findings without executing the candidate or
modifying it. A failed observation is classified with evidence as `candidate-defect`,
`fixture-or-environment-defect`, or `ambiguous`; the Controller only routes that classification.
_Avoid_: Acceptance Runner, Author, self-judging executor

**Acceptance Correction Cycle（验收修正周期）**:
The Correction Cycle Protocol in which an Acceptance Reviewer returns Stage-local PASS when its
frozen case and pass conditions are satisfied. Each execution attempt uses a new Acceptance Runner.
The same Reviewer remains active across Author revisions, Revision Impact Decisions, rewinds, and
reruns until the Controller closes the case or a stop condition applies. The Controller freezes the
complete Acceptance Portfolio first, then runs its cases sequentially from highest to lowest risk.
A Candidate Version change invalidates only the previously passed cases selected by the Revision
Impact Decision; each invalidated case starts a new cycle with a new Reviewer. A fixture or
environment defect leaves the Candidate Version unchanged and reruns only each affected case after
the defect is corrected without changing the frozen pass conditions. An ambiguous failure receives
one targeted observation attempt from a new Runner while the same Reviewer persists; failure to
classify it then stops without modifying the candidate or weakening the case.
_Avoid_: One-shot acceptance, Runner self-repair, bypassed evaluation sequence

**Static Contract Review Cycle（静态契约审查周期）**:
The Setup Authoring Contract's simplified Correction Cycle Protocol with one persistent Static
Reviewer. After machine validation, the Reviewer jointly checks judgment-only form, minimality,
semantic completeness, and one representative walkthrough. Review Findings return to the persistent
Author until Stage-local PASS; the Controller then applies the normal Revision Impact Decision so an
invalidated machine check reruns before final closure. Quality and Correctness Reviewer pairs and
Acceptance Runners do not participate.
_Avoid_: Rule or Skill Evaluation Sequence, generated target test, procedural contract review

**Handoff Report（交接报告）**:
The Controller's concise final account of candidate paths, semantic type and owner, final Candidate
Fingerprint, machine commands and exits, every applicable review-stage verdict, Representative
Acceptance cases or its NOT_REQUIRED result when that branch exists, Role Boundary Audit status,
untested or unresolved surfaces, and any rewind, Context Supplement, or Role File Allowlist
expansion. It excludes complete Context Packets, finding history, Agent prompts, complete diffs,
and the internal semantic ledger.
_Avoid_: Author proof, persisted workflow dossier, full transcript

**Review Packet（审查材料包）**:
A bounded evidence view for one Reviewer and candidate. It includes the complete accepted decision
context and preserved existing obligations relevant to that Reviewer's scope, so Correctness Review
can detect an omission in the first Candidate Version without a separate standard-change phase. On
recheck it also includes that Reviewer's own prior findings and the Author's concise Finding
Dispositions. It excludes private author reasoning, intended fixes, candidate diffs, another
Reviewer's findings, and expected verdicts.
_Avoid_: Repository snapshot, author handoff
