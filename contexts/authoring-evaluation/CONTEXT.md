# Authoring Evaluation

Authoring Evaluation describes the language used to discuss how SmartKit writes and reviews Rules,
Skills, and Setup Authoring Contracts.

This glossary is unstable, non-normative conversational guidance. Operative requirements remain in
the applicable Rules, Skills, accepted specifications, and ADRs; no runtime artifact may depend on
this file.

## Language

**Candidate（候选工件）**:
The complete Rule or Skill currently being authored and reviewed as one coherent artifact.
_Avoid_: Patch, generated target, isolated changed lines

**Author brief（作者任务说明）**:
A compact, self-contained assignment that gives the Author the accepted objective, change, evidence,
Candidate boundary, preservation constraints, validation, and completion conditions.
_Avoid_: Full session transcript, Reviewer packet, implementation outline

**Controller（流程控制者）**:
The role that aligns one authoring job, delegates it, routes session-only context, protects
boundaries, runs validation, manages review rounds, coordinates runtime evidence, and reports the
result without writing or judging the Candidate.
_Avoid_: Lead Author, semantic reviewer, workflow designer

**Author（作者）**:
The single role that owns the Candidate's meaning, structure, expression, and coherent repairs for
one authoring job.
_Avoid_: Controller editor, Reviewer scribe, per-finding fixer

**Common Reviewer contract（审查者公共契约）**:
The shared evidence-loading, communication, and result structure used by every Reviewer identity
alongside its assigned professional contract or contracts.
_Avoid_: General review method, fourth review perspective, Controller instructions

**Quality Reviewer（质量审查者）**:
The professional perspective that judges the current Candidate's overall quality, information
design, economy, elegance, and human and Agent readability. It may recommend holistic restructuring
when the artifact has grown through additive patches.
_Avoid_: Copy editor, correctness backstop, prose generator

**Change Reviewer（变更审查者）**:
The professional perspective that compares the baseline with the current Candidate to detect
semantic loss, unintended change, and regression rather than harmless textual difference.
_Avoid_: Diff summarizer, Quality Reviewer, current-state reviewer

**Correctness Reviewer（正确性审查者）**:
The professional perspective that safeguards fidelity to the accepted job, safety, and critical
behavior. It requests runtime evidence when a material question cannot be resolved statically and
judges the resulting observations.
_Avoid_: General style reviewer, Runner, acceptance executor

**Runner（运行执行者）**:
The role that executes one bounded scenario and reports reproducible observations without judging,
repairing, or modifying the Candidate.
_Avoid_: Correctness Reviewer, self-judging executor, repair Agent

**Integrated Reviewer（整合审查者）**:
The single identity that applies the common Reviewer contract and all three professional contracts
during an Integrated Review, reporting each perspective separately.
_Avoid_: General Reviewer, reduced-scope Reviewer, interchangeable perspective

**Integrated Review（整合审查）**:
A review in which one Integrated Reviewer covers the Quality, Change, and Correctness perspectives
for a bounded change with closed obligations and no material uncertainty. It may require an
Independent Review when those conditions no longer hold or a judgment needs independence.
_Avoid_: Partial review, lower-standard review, selected-role review

**Independent Review（独立审查）**:
A review in which fresh Quality, Change, and Correctness Reviewer identities each load the common
contract and their own professional contract, then independently examine the same Candidate state.
It is used for self-hosting, broad, high-risk, or materially uncertain changes.
_Avoid_: More verbose review, unbounded review, repeated Integrated Review

**Review round（审查轮次）**:
One cycle in which all three professional perspectives examine the same Candidate state through the
selected review topology and the Author then makes at most one coherent repair after considering all
reports.
_Avoid_: One finding conversation, one file review, unlimited correction loop

**Candidate fingerprint（候选指纹）**:
A deterministic identity for the complete Candidate state, used to bind review results and detect
unexpected writes without serving as semantic evidence.
_Avoid_: Change summary, review verdict, persisted report

**Principle-led Skill（原则导向型技能）**:
A Skill that states its outcome, governing principles, consequential constraints, and completion
conditions while leaving ordinary method to Agent judgment.
_Avoid_: Rule artifact, vague Skill, unstructured Skill

**Procedure-led Skill（流程导向型技能）**:
A Skill that fixes steps or order because sequence or protocol materially affects the outcome,
correctness, safety, ownership, coordination, recovery, or external effects.
_Avoid_: Detailed Skill, long Skill, mandatory outline

**Hybrid Skill（混合型技能）**:
A principle-led Skill that prescribes procedure only for the parts whose order materially matters.
_Avoid_: Inconsistent Skill, partially specified Skill

**Setup Authoring Contract（项目设置编写契约）**:
A project-owned blueprint that supplies accepted meaning and evidence for a future project-local Rule
or Skill. It is neither the generated target nor the public authoring workflow.
_Avoid_: Generated target, shared SmartKit artifact

**Portable authoring（可迁移编写）**:
The qualification applied when a shared SmartKit Rule or Skill must preserve its meaning and
dependencies across representative target projects without inheriting source-project assumptions.
_Avoid_: Generic prose, source-project reuse, publication
