# Authoring Evaluation

Authoring Evaluation defines how SmartKit classifies, authors, qualifies, reviews, corrects, and
adopts Rules, Skills, and Setup Authoring Contracts.

This glossary is unstable, non-normative conversational guidance. Operative requirements remain in
the applicable project Rules, Skills, and accepted ADRs; no runtime artifact may depend on this
file.

## Language

**Setup Authoring Contract（项目设置编写契约）**:
A project-owned input under `setup-assets/blueprints/` that guides `setup-project-agents` in using
the public authoring Skill to create one complete future project-local Rule or Skill. The contract
is generic across target projects but legitimately depends on this repository's setup catalog,
blueprint owner, and representative target evidence, so its simpler Author, machine-validation, and
static-review correction flow uses the concrete project-aware Role Launch rather than risk-matched
Executable Acceptance. The real target is later reviewed independently as a Rule or Skill
candidate.
_Avoid_: Generated target, generator fixture

**Acceptance Standard（验收标准）**:
The quality contract for authored Rules and Skills: evidence-backed authoring, applicable machine
validation, fresh semantic review, conditional Executable Acceptance, and explicit handoff. Setup
Authoring Contracts instead use their independently owned machine-validation and Static Reviewer
flow.
_Avoid_: Qualification-only gate, ordinary acceptance

**Acceptance Portfolio（验收方案集）**:
The Controller-frozen set of executable cases for material runtime risks not already established
with supported high confidence. It contains at least one case for each distinct remaining risk,
normally covers an applicable success path when that path remains materially at risk, and adds an
error or recovery path only when its behavior is materially different. It has no fixed case count.
When no such risk exists, Executable
Acceptance returns `NOT_REQUIRED`; a Setup Authoring Contract's representative walkthrough
belongs to Static Contract Review rather than this portfolio.
_Avoid_: Acceptance level, alternate standard, static acceptance

**Executable Acceptance（执行验收）**:
The Controller-owned risk decision that requires an Acceptance Runner only when a candidate defines
sufficiently concrete, complex, or high-risk runtime behavior whose material correctness is not
already established with supported evidence and high confidence by machine validation, static
Review, or an unchanged previously accepted mechanism. It is conditional, not a normal requirement
for every candidate. Broad procedural guidance without a concrete tool protocol, and simple
environment-independent behavior with supported high confidence, do not require Executable
Acceptance. Skill Shape alone does not determine the verdict.
_Avoid_: Every Procedure-led Skill, Author confidence, any ordered list

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
The Controller-enforced single-writer interval acquired before the first Author and retained through
workflow finalization. It permits no other role or machine check to modify candidate paths and uses
Candidate Fingerprints, changed paths, the Role File Allowlist, and Author Change Summaries to audit
each turn. An out-of-allowlist or unattributable change invalidates the result and stops without
overwriting, reverting, or concealing the conflicting state.
_Avoid_: Filesystem lock file, automatic rollback, concurrent reviewer edit

**Owner Gate（归属判定关口）**:
The pre-authoring decision point that first routes any applicable more-specific authoring owner
before a Run Contract, role, or write. When none applies, it classifies each obligation and its
complete artifact as Rule, Skill, Split, Environment-owned, or Ambiguous, then compares that verdict
with the requested or current owner.
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

**No-progress Stop（无进展停止）**:
The Controller-owned exit when correction has no new supported path or needs a missing decision,
authority, isolation boundary, or role capacity. It identifies the blocker and what would be needed
to continue rather than treating an ordinary first failure as terminal.
_Avoid_: Retry budget, first failed revision, lack of immediate PASS

**Correction Cycle Protocol（修正周期协议）**:
The common review cycle in which a persistent Reviewer or Reviewer pair reinspects the complete
candidate and the Author's dispositions after each revision until its scope passes or a stop
condition applies. Runtime owners define the exact rewind and role-lifecycle behavior.
_Avoid_: One Reviewer per revision, immediate rewind, Reviewer-authored fix

**Stage-local PASS（阶段内通过）**:
The Acceptance-only result in which the current case's Reviewer finds nothing worth fixing for the
current Candidate Version after successful attempt finalization. Before sequential replay starts at
an invalidated earlier Acceptance case, the Controller records the current case PASS at Stage-local
PASS and closes its Reviewer. Stage-local PASS alone is not Acceptance PASS and does not establish
that every frozen case still passes.
_Avoid_: Generic stage verdict, final acceptance, workflow completion

**Evaluation Sequence（评估顺序）**:
The ordered evaluation lifecycle owned by the public authoring protocol. A stage not yet reached
has no evidence; its exact stages, order, and conditional branches remain defined by that owner.
_Avoid_: Parallel gates, validation matrix, unordered checklist

**Machine Validation Cycle（机器验证周期）**:
The deterministic stage in which the Controller runs applicable machine checks and routes failures
to the persistent Author. No Reviewer participates, and passing checks do not establish semantic
correctness.
_Avoid_: First-failure stop, Controller-authored fix, semantic review

**Revision Impact Decision（修订影响判定）**:
The Controller-owned decision about which prior evidence a Candidate Version change may have
invalidated. The Author reports changes and uncertainty but cannot waive checks or determine which
evidence remains valid.
_Avoid_: Author self-classification, validation matrix, future-stage invalidation

**Quality Review Cycle（质量审查周期）**:
The Correction Cycle Protocol for semantic economy and information design. Its Reviewer pair owns
the Quality Review verdict for its scope.
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
The Correction Cycle Protocol for semantic fidelity and ownership and for Agent executability and
behavior. Its Reviewer pair owns the Correctness Review verdict for its scope.
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
It names the evidence and intended owner, which is either a Reviewer scope or a Controller-owned
stage action, but neither creates a Review Finding nor affects the originating Reviewer's verdict.
The Controller routes it mechanically once. A receiving Reviewer alone decides whether its scope
supports a semantic finding and owns the resulting verdict. For a Controller-owned stage, the
Controller only performs or reruns the existing stage action under that stage's evidence contract;
it does not create a Reviewer or make the semantic decision. Missing authority or a required
decision stops the workflow.
_Avoid_: Cross-scope finding, Controller semantic triage, reviewer ping-pong

**Finding Disposition（问题处置）**:
The persistent Author's `repair` or `decline` decision for one Review Finding. A `repair` changes the
candidate; a `decline` gives a concise supported reason. The same Reviewer considers the disposition
and current complete candidate and alone decides whether an unresolved finding remains worth fixing,
prevents PASS, or has been resolved. The Controller does not make either semantic choice. The same
unresolved Author-Reviewer disagreement after two complete rounds triggers the No-progress Stop or
an exact decision-required exit.
_Avoid_: Controller triage, Reviewer-authored correction, hidden rejection

**Worth-fixing Finding（值得修复的问题）**:
A Review Finding that the same Reviewer judges still prevents PASS after considering its evidence,
severity, the current complete candidate, and the Author's Finding Disposition. The Author owns the
`repair` or `decline` choice but does not decide worth-fixing status. An advisory finding with a Local
Repair is presumed worth fixing when the repair preserves meaning. A supported `decline` remains
visible to the same Reviewer for its independent stage verdict.
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
The property that a candidate derives no durable terminology or operative meaning from a project
context document. Such documents are unstable, non-normative conversational aids rather than
authoring or Review evidence or runtime dependencies.
_Avoid_: Context glossary as evidence, runtime CONTEXT.md dependency, glossary-driven naming

**Persistent Author（持续作者）**:
The one role Agent that owns the candidate's meaning and writes its initial content and later
corrections. It remains the same identity throughout the workflow but does not own validation,
Review, or Acceptance verdicts.
_Avoid_: Controller editor, per-revision Author, author-verifier

**Role Launch Runtime（角色启动运行时）**:
The fixed authoring machinery that preserves role identity, independence, capacity, channels,
authority, reports, audits, abnormal-execution containment, and finalization. Public authoring
combines it with Project-aware Role Launch as one concrete behavior. Shared authoring keeps this
runtime and applies its private Soft-isolated Role Launch.
_Avoid_: Public role selector, isolation option, subagent helper

**Role Capacity Gate（角色容量关口）**:
The pre-authoring qualification that the host can preserve the identities, concurrency, access,
freshness, and observable audit evidence required by the selected workflow. Uncertain or inadequate
capacity stops before the Author starts.
_Avoid_: Codex product limit, best-effort parallelism, total-identity and active-turn conflation

**Role Boundary Audit（角色边界审计）**:
The Controller's reconciliation of a role's reported and observed operations against its frozen
manifest, access, and role contract after every callback and available terminal report. Runner termination
also requires a Candidate Fingerprint comparison even when no report is available. It is behavioral
evidence rather than proof of a hard security boundary; a supported violation prevents use of the
result.
_Avoid_: Final-workflow audit, hard-sandbox proof, ignored evidence conflict

**Operation Summary（操作摘要）**:
The complete callback bundle of Operation Report, Peer Report, and Host-Governance Report. The
private Tool Boundary Record accompanies this unchanged bundle rather than entering it. The Role
Boundary Audit compares the bundle and any required companion record with host-observed evidence.
_Avoid_: Operation Report alone, Tool Boundary Record, semantic change summary

**Operation Report（操作报告）**:
The Operation Summary member that reports `read`, `write`, `create`, `delete`, `network`,
`delegation`, and `machine checks` from the latest callback or available terminal report, using
`none` for an empty category.
_Avoid_: Complete Operation Summary, audit proof, workflow report

**Project-aware Role Launch（项目感知角色启动）**:
The concrete public evidence policy for fresh roles. Authors and Reviewers directly inspect
authorized repository evidence and Candidate resources without an intermediary. Evidence gains
authority from its owner and provenance rather than repository or host-envelope presence.
_Avoid_: Default Adapter, selectable project mode, Project Explorer

**Soft-isolated Role Launch（软隔离角色启动）**:
The project-private evidence and access policy for shared portability evaluation. It supplies
declared semantic input and prompt-enforced allowlists that exclude undeclared source-project
meaning without removing mandatory Host Governance or claiming technical filesystem isolation.
_Avoid_: Shared public mode, hard sandbox, prompt override

**Role File Allowlist（角色文件白名单）**:
The Controller-approved behavioral access contract for a role's candidate files and owned
resources. It distinguishes operation modes and can expand only through the runtime owner's access
and qualification rules.
_Avoid_: Workspace permission, broad glob, implicit access

**Role-fresh Agent（角色独立智能体）**:
An Agent that did not perform the role whose output it evaluates. Freshness supports independent
judgment but does not prove source-project context isolation.
_Avoid_: New prompt in the same conversation, soft-isolated Agent

**Soft-isolated Agent（软隔离智能体）**:
A fresh Agent supplied only declared semantic input and behavioral access under the private
Soft-isolated Role Launch. Soft isolation is a verified behavioral boundary, not an adversarial
security boundary.
_Avoid_: Context-clean Agent, ordinary source-project subagent, role-fresh Agent

**Role Launch Probe（角色启动探针）**:
The private shared workflow's mandatory post-freeze qualification gate, run once before Candidate
fingerprinting, lock acquisition, semantic roles, or Candidate writes. Its disposable Probe checks
the frozen soft-isolated launch and access properties. Candidate edits and eligible Role File
Allowlist expansion preserve its result; a material launch or evidence-policy change requires a new
run. Public project-aware authoring has no Probe stage.
_Avoid_: Acceptance canary, per-role probe, allowlist-expansion reprobe

**Portability Qualification（可迁移性验证）**:
The shared workflow's composite result rather than a separate Reviewer or correction cycle. PASS
requires portable meaning, declared dependency closure, both Correctness Reviewers' shared-scope
checks across representative target contexts, and applicable Acceptance evidence to converge on
one Candidate Version. Soft-isolation qualification and Role Launch Probe PASS belong to the same
frozen run; Candidate edits neither version-bind nor replay them.
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
continue without it. A project-aware role first performs its own permitted project discovery; a
soft-isolated shared role requests missing declared input without reading unrelated source-project
content. The Controller normally supplies a Context Supplement and continues the same Agent.
Correction or withdrawal of prior context, a material task, owner, or Acceptance Standard change,
Soft Isolation contamination, or irreconcilable context requires a fresh role instead.
_Avoid_: Project Explorer request, automatic role restart, speculative completion

**ACCESS_REQUIRED（需要访问权限）**:
A non-verdict role response that names each additional exact file or narrowly owned directory,
requested `read`, `write`, `create`, or `delete` mode, and why the role cannot continue without it.
The Controller grants only authorized candidate or owned-resource access that preserves the frozen
evidence and access policy, then continues the same Agent. A shared Role Launch Probe is not rerun
for an eligible expansion. A request for undeclared source-project context is answered through an
eligible Context Supplement or stops; it is not added to a shared Role File Allowlist. If the host
cannot expand access while preserving the persistent Agent, the Role Capacity Gate fails.
_Avoid_: Repository access, implicit permission expansion, context request

**Ambient Context（宿主附带上下文）**:
Context a Harness exposes outside the Context Packet. Project entry-file content and its Rule or
Skill pointers, plus Skill catalog metadata, may be physically observable without invalidating soft
isolation. Qualification fails when a role accesses or uses undeclared content as semantic evidence,
follows a pointer outside its authority, or contradicts the frozen envelope/profile evidence. The
distinction is behavioral and makes no claim that undeclared content is physically unavailable.
_Avoid_: Context Packet, accepted dependency

**Fresh Reviewer（独立审查者）**:
A Role-fresh Agent started through the frozen Role Launch contract that did not author the Candidate
Version it evaluates. A Setup Authoring Contract and a real target created later receive separate
Reviewers and do not inherit verdicts.
_Avoid_: Author self-review, inherited reviewer

**Acceptance Runner（验收执行者）**:
A Role-fresh Agent started through the frozen Role Launch contract that applies one candidate to one
representative task. It receives tools only when the artifact's observable behavior requires
them and receives the frozen observable pass criteria needed for that case, but no Reviewer verdict
or intended interpretation beyond those criteria. It does not receive the semantic ledger, diff,
author reasoning, review findings, or prior case output. Each attempt uses a fresh Runner. It
reports observable operations, output, and side effects without judging whether they pass; the
Controller must end it and establish quiescence before cleanup or Reviewer activity.
_Avoid_: Acceptance reviewer, prepared-answer agent, paper walkthrough

**Acceptance Reviewer（验收审查者）**:
A Role-fresh Agent started only after the case's first Runner attempt finalizes successfully. It
compares captured execution and finalization evidence with the frozen case and pass conditions,
then returns PASS or supported Candidate findings without executing or modifying the candidate.
When no Candidate finding is supported, a failing or inconclusive observation has exactly two
special classifications: `fixture/environment defect` or `ambiguous`; the Controller only performs
the bounded orchestration in that Reviewer-owned payload.
_Avoid_: Acceptance Runner, Author, self-judging executor

**Acceptance Correction Cycle（验收修正周期）**:
The Correction Cycle Protocol in which the Controller runs and successfully finalizes a case's first
fresh-Runner attempt before starting its Acceptance Reviewer. Started-attempt finalization captures
evidence, audits, establishes Runner quiescence, and then cleans up. Its terminal priority is
`ATTEMPT_INVALID`, `RUNNER_NOT_QUIESCENT`, then `CLEANUP_FAILED`; missing permission, isolation, or
authority before a Runner starts is `EXECUTION_UNAVAILABLE`. A terminal result starts or resumes no
Reviewer. The same Reviewer persists through later successfully finalized attempts, Author
correction, fixture or environment recovery, ambiguity observation, and case PASS.

The Controller freezes the Acceptance Portfolio first, runs cases sequentially from highest to
lowest risk, and keeps only one current case Reviewer. If an earlier passed Acceptance case is
invalidated, it records the current case PASS at Stage-local PASS and closes that Reviewer before
replay restarts at the earliest invalidated case. That evidence remains valid on the same Candidate
Version; a later affecting Author change invalidates and reruns it normally. Replay preserves other
unaffected case evidence and runs a fresh first attempt before each fresh Reviewer. A fixture or
environment defect leaves the Candidate Version unchanged and retries with a fresh Runner after its
bounded correction. An ambiguous result receives one targeted fresh-Runner observation under full
attempt finalization while the same Reviewer persists.
_Avoid_: One-shot acceptance, Runner self-repair, bypassed evaluation sequence

**Static Contract Review Cycle（静态契约审查周期）**:
The Setup Authoring Contract's simplified Correction Cycle Protocol with one persistent Static
Reviewer. After machine validation, the Reviewer jointly checks judgment-only form, minimality,
semantic completeness, and one representative walkthrough. Review Findings return to the persistent
Author until Static Reviewer PASS. After every Author edit, the Controller applies machine-result
invalidation and reruns every affected machine check before the same Static Reviewer rechecks the
Candidate Version. Quality and Correctness Reviewer pairs and Acceptance Runners do not participate.
_Avoid_: Rule or Skill Evaluation Sequence, generated target test, procedural contract review

**Handoff Report（交接报告）**:
The Controller's concise final account of candidate paths, semantic type and owner, final Candidate
Fingerprint, machine commands and exits, every applicable review-stage verdict, Acceptance case
verdicts or `NOT_REQUIRED` when that branch exists, Role Boundary Audit status,
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
