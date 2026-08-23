# Authoring Evaluation

Authoring Evaluation defines how SmartKit classifies, authors, qualifies, reviews, corrects, and
adopts Rules, Skills, and Generation Contracts.

## Language

**Ordinary Artifact（普通工件）**:
A Rule or Skill used directly as policy or as a triggered job rather than as instructions for
authoring another Rule or Skill.
_Avoid_: Runtime artifact, generated target

**Generation Contract（生成契约）**:
A standalone instruction artifact that guides another Agent in authoring a complete future Rule or
Skill. The future target determines whether Rule or Skill semantics apply; the contract itself uses
static walkthrough, while a real target is reviewed later as an Ordinary Artifact.
_Avoid_: Generated target, generator fixture

**Qualification Campaign（资格认定活动）**:
One bounded application of the Acceptance Standard across the representative canary classes needed
to qualify the SmartKit authoring workflow.
_Avoid_: Separate acceptance standard, full rewrite, canary cycle

**Acceptance Standard（验收标准）**:
The single quality contract every authored Rule, Skill, or Generation Contract must satisfy through
evidence-backed authoring, machine validation, fresh semantic review, risk-matched acceptance, and
explicit handoff.
_Avoid_: Qualification-only gate, ordinary acceptance

**Acceptance Portfolio（验收组合）**:
The artifact-specific cases, evidence contexts, executable checks, static walkthroughs, and
regression defects used to demonstrate that one candidate satisfies the Acceptance Standard.
_Avoid_: Acceptance level, alternate standard

**Canary Candidate（金丝雀候选项）**:
One independently evaluated version of a representative Ordinary Artifact or Generation Contract
in a Qualification Campaign.
_Avoid_: Candidate bundle, whole-campaign version

**Candidate Revision（候选修订版）**:
The complete current content state of one authored candidate. Validation, Review, and Acceptance
evidence applies only while that state is unchanged; it does not require a copied tree.
_Avoid_: Revision directory, inherited verdict

**Owner Gate（归属判定门控）**:
The pre-authoring decision point that classifies each obligation and its complete artifact as Rule,
Skill, Split, Environment-owned, or Ambiguous, then compares that verdict with the requested or
current owner.
_Avoid_: Approval gate, Rule approval

**Ownership Review（归属审查）**:
The read-only `write-rules-and-skills` branch that applies the Owner Gate to existing artifacts and
exits with supported ownership verdicts without creating a Candidate Revision.
_Avoid_: Separate Skill, Candidate Review

**Policy Frame（政策框架）**:
The semantic structure of one Rule, relating its owner and strength, scope and applicability,
observable predicate-to-outcome mappings, exceptions, precedence, and ownership boundaries without
describing a triggered job procedure.
_Avoid_: Rule workflow, policy rationale

**Generation Frame（生成框架）**:
The semantic structure of one Generation Contract, relating its future target and owner, required
evidence and obligations, permitted writes, validation, handoff, and material-ambiguity stops while
leaving unsupported authoring method and order to Agent judgment.
_Avoid_: Generated target outline, mandatory authoring recipe

**Skill Shape（技能形态）**:
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

**Job Graph（作业图）**:
The semantic structure of a Procedure-led Skill or Procedural Island, relating its entry, actions,
branches, runtime resources, and prioritized exits independently of any document outline.
_Avoid_: Markdown outline, procedure draft

**Execution Path（执行路径）**:
One reachable route through a Job Graph from its entry to exactly one prioritized completion, stop,
or failure exit.
_Avoid_: Phase list, branch inventory

**Procedural Island（流程岛）**:
One bounded Procedure-led part of a Hybrid Skill that returns control to Agent judgment after its
prioritized exit.
_Avoid_: Workflow phase, procedural Skill

**Artifact Projection（工件投影）**:
The placement of each Judgment Frame, Job Graph, or Procedural Island obligation into its narrowest
reliable runtime owner and loading tier without changing the Skill's observable behavior.
_Avoid_: Content splitting, editorial reorganization

**Entry Sufficiency（入口充分性）**:
The property that a Skill's main file identifies its Skill Shape, objective or entry, applicable
Judgment Frame or Execution Path, and conditionally required resources without unrelated detail.
_Avoid_: Self-contained main file, short main file

**Path Sufficiency（路径充分性）**:
The property that a Skill's main file plus the resources selected by one Execution Path are enough
to execute that path to its unique prioritized exit.
_Avoid_: Whole-Skill self-containment, eager resource loading

**Frozen Canary（冻结态金丝雀候选项）**:
A Canary Candidate whose own machine validation, semantic review, and representative acceptance
have passed and whose evidence has not been invalidated.
_Avoid_: Approved campaign, immutable file

**Adoption Gate（仓库纳入门控）**:
The all-or-none boundary that permits repository adoption only after every required Canary Candidate
has passed its own gates.
_Avoid_: Campaign restart, per-canary writeback

**Correction Loop（修正循环）**:
The authoring cycle that applies all current uniquely forced findings, reruns invalidated gates, and
continues while each revision makes progress toward a passing Candidate Revision.
_Avoid_: User-confirmed retry, fixed correction budget, one-finding patch

**Fresh Reviewer（独立审查者）**:
An Agent that did not author the Candidate Revision it evaluates. A generation contract and a real
target created later default to different Fresh Reviewers, receive separate reviews, and do not
inherit verdicts.
_Avoid_: Author self-review, inherited reviewer

**Acceptance Runner（验收执行者）**:
An isolated fresh Agent that applies one Ordinary Artifact to one representative task using only
the candidate's runtime-visible content, the task, and its required context or tools. The Runner
does not receive the semantic ledger, expected result, diff, author reasoning, review findings, or
prior case output; the Fresh Reviewer judges its observable result.
_Avoid_: Acceptance reviewer, prepared-answer agent, paper walkthrough

**Behavior Control（行为对照）**:
One isolated run before authoring that uses the previously accepted artifact for a rewrite or no
candidate for a new artifact. Use it only when a proposed instruction's sole supported purpose is
to change default Agent behavior and no observed failure already establishes that need.
_Avoid_: Mandatory baseline, repeated sampling, generation target

**Candidate Review（候选审查）**:
One bounded task in which a Fresh Reviewer performs Semantic Review first, then judges the
candidate's Acceptance Portfolio from isolated Acceptance Runner results or the Generation
Contract's static walkthrough, and returns a separate verdict for each gate.
_Avoid_: Review Board, combined verdict

**Regression Corpus（回归语料库）**:
The maintained set of minimal, previously demonstrated authoring defects replayed in later
Qualification Campaigns.
_Avoid_: Exhaustive scenario matrix, ad hoc mutants

**Review Packet（审查材料包）**:
The bounded evidence shared with the Fresh Reviewer for one candidate, excluding author reasoning,
suspected defects, intended fixes, and expected verdicts.
_Avoid_: Repository snapshot, author handoff

**Defect Card（缺陷卡片）**:
One minimal Regression Corpus case containing a supported input, one injected semantic defect, and
the review gate it should violate.
_Avoid_: Full broken candidate, string assertion
