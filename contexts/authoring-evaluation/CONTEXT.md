# Authoring Evaluation

Authoring Evaluation defines how SmartKit classifies, authors, qualifies, reviews, corrects, and
adopts Rules, Skills, and Setup Authoring Contracts.

## Language

**Ordinary Artifact（直接使用型工件）**:
A Rule or Skill used directly as policy or as a triggered job rather than as instructions for
authoring another Rule or Skill.
_Avoid_: Runtime artifact, generated target

**Setup Authoring Contract（项目设置编写契约）**:
A project-owned input under `setup-assets/blueprints/` that guides `setup-project-agents` in using
the public authoring Skill to create one complete future project-local Rule or Skill. The contract
uses one role-fresh static review; the real target is later reviewed as an independent Ordinary
Artifact.
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
The artifact-specific cases, evidence contexts, executable checks, and static walkthroughs used to
demonstrate that one candidate satisfies the Acceptance Standard.
_Avoid_: Acceptance level, alternate standard

**Canary Candidate（试点候选项）**:
One independently evaluated version of a representative Ordinary Artifact or Setup Authoring Contract
in a Qualification Campaign.
_Avoid_: Candidate bundle, whole-campaign version

**Candidate Revision（候选修订版）**:
The complete current content state of one authored candidate. Validation, Review, and Acceptance
evidence applies only while that state is unchanged; it does not require a copied tree.
_Avoid_: Revision directory, inherited verdict

**Owner Gate（归属判定关口）**:
The pre-authoring decision point that classifies each obligation and its complete artifact as Rule,
Skill, Split, Environment-owned, or Ambiguous, then compares that verdict with the requested or
current owner.
_Avoid_: Approval gate, Rule approval

**Ownership Review（归属审查）**:
The read-only `write-rules-and-skills` branch that applies the Owner Gate to existing artifacts and
exits with supported ownership verdicts without creating a Candidate Revision.
_Avoid_: Separate Skill, Candidate Review

**Policy Frame（规则框架）**:
The semantic structure of one Rule, relating its owner and strength, scope and applicability,
observable predicate-to-outcome mappings, exceptions, precedence, and ownership boundaries without
describing a triggered job procedure.
_Avoid_: Rule workflow, policy rationale

**Setup Contract Frame（项目设置契约框架）**:
The semantic structure of one Setup Authoring Contract, relating its future target and owner, required
evidence and obligations, permitted writes, validation, handoff, and material-ambiguity stops while
leaving unsupported authoring method and order to Agent judgment.
_Avoid_: Generated target outline, mandatory authoring recipe

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
continues while each revision makes progress toward a passing Candidate Revision.
_Avoid_: User-confirmed retry, fixed correction budget, one-finding patch

**Role-fresh Agent（角色独立智能体）**:
An Agent that did not perform the role whose output it now evaluates. Role freshness prevents
authoring commitments or prior case results from entering a later judgment, but does not prove
source-project context isolation.
_Avoid_: New prompt in the same conversation, soft-isolated Agent

**Soft-isolated Agent（软隔离智能体）**:
A fresh Agent with no inherited turns that runs only after the current top-level workflow passes a
Soft-Isolation Probe and receives all semantic input through one explicit Context Packet. It is a
verified behavioral boundary, not a filesystem or security boundary.
_Avoid_: Context-clean Agent, ordinary source-project subagent, role-fresh Agent

**Soft-Isolation Probe（软隔离探针）**:
One disposable, tool-free fresh Agent run before the first Soft-isolated Agent in a top-level
authoring workflow. It proves that the launch receives its prompt but not parent-turn content,
project Rule bodies, SmartKit Rule bodies, Harness Rule bodies, or complete Skill bodies; failure
stops the workflow without fallback.
_Avoid_: Acceptance canary, per-role probe, Harness exception

**Context Packet（上下文包）**:
The complete semantic input explicitly supplied to one Soft-isolated Agent, including the candidate
or original content, accepted intent, selected evidence and dependencies, and any allowed tools or
file contents. Missing context returns to the controller for a new packet and fresh Agent.
_Avoid_: Workspace discovery, repository snapshot, persistent packet file

**Ambient Context（宿主附带上下文）**:
Context a Harness exposes outside the Context Packet. Project entry-file content and its Rule or
Skill pointers, plus Skill catalog metadata, may be observable, but the Agent must not follow those
pointers; any Rule or complete Skill body in Ambient Context invalidates soft-isolation qualification.
_Avoid_: Context Packet, accepted dependency

**Fresh Reviewer（独立审查者）**:
A Soft-isolated, Role-fresh Agent that did not author the Candidate Revision it evaluates. A Setup
Authoring Contract and a real target created later receive separate Reviewers and do not inherit
verdicts.
_Avoid_: Author self-review, inherited reviewer

**Accepted Standard Change（已接受标准变更）**:
A content-frozen statement of explicit Acceptance Standard changes, preserved obligations, and
non-goals that passed an independent Soft-isolated Review. It combines with the Previous Accepted
Standard to judge a self-modifying candidate before that candidate can become the latest Standard.
_Avoid_: Candidate-derived requirement, latest candidate standard

**Acceptance Runner（验收执行者）**:
A Soft-isolated Agent that applies one Ordinary Artifact to one representative task using only its
Context Packet. It receives tools only when the artifact's observable behavior requires them and
does not receive the semantic ledger, expected result, diff, author reasoning, review findings, or
prior case output; the Fresh Reviewer judges its returned result.
_Avoid_: Acceptance reviewer, prepared-answer agent, paper walkthrough

**Behavior Control（行为对照）**:
One Soft-isolated run before authoring that uses the previously accepted artifact for a rewrite or
no candidate for a new artifact. Use it only when a proposed instruction's sole supported purpose
is to change default Agent behavior and no observed failure already establishes that need.
_Avoid_: Mandatory baseline, repeated sampling, generation target

**Candidate Review（候选审查）**:
One bounded task in which a Fresh Reviewer performs Semantic Review first, then judges the
candidate's Acceptance Portfolio from Soft-isolated Acceptance Runner results. A Setup Authoring
Contract instead receives its project-private static review, and each route returns distinct
verdicts for its required gates.
_Avoid_: Review Board, combined verdict

**Review Packet（审查材料包）**:
The bounded evidence shared with the Fresh Reviewer for one candidate, excluding author reasoning,
suspected defects, intended fixes, and expected verdicts.
_Avoid_: Repository snapshot, author handoff
