---
name: write-rules-and-skills
description: Author or revise one English Rule or Agent Skill.
---

# Write Rules and Skills

## Frontier-Agent Principle

Design and execute this workflow for a capable current frontier Agent. State semantic authority,
evidence, invariants, and only decision boundaries, constraints, or exceptions whose omission can
materially change correctness, safety, protocol, ownership, coordination, external effects,
executability, or handoff. Leave ordinary method choice, evidence traversal, reliably inferable
decision boundaries and edge handling, and local judgment to the Agent.

This principle governs every stage and reference. The workflow is Hybrid: judgment-led by default,
with bounded procedural islands only where order or protocol changes the outcome.

The active Agent is the Controller. It owns orchestration and boundary enforcement, never Candidate
meaning or review judgment. One resident Author owns Candidate meaning and writes. Independent
Reviewers own findings and verdicts. A Runner, when required, performs only a frozen executable
Acceptance attempt.

## Load references progressively

Keep auxiliary Skill use aligned with the surface being authored. Author the Rule or Skill
contract—its instructions, semantics, structure, and prose—without code-design or code-authoring
Skills, including `codebase-design`. When a Skill contains executable scripts, those Skills may
design, implement, or validate only the scripts; their authority and output remain confined to the
script surface and must not determine or alter the surrounding contract. Plugin exposure,
visibility, or availability does not expand this boundary.

Load each complete contract at its first need, not at entry:

1. For ownership, alignment, and Candidate shape, read
   [Models](references/models.md) and the installed writing-for-agents Skill.
2. After alignment closes, read [Job Design](references/job-design.md). During Design, read
   [Role Runtime](references/role-runtime.md) when identity lifecycle and callbacks are frozen,
   [Reviews](references/reviews.md) when review topology and lenses are frozen, then
   [Evaluation](references/evaluation.md) when proof applicability and exits are frozen. If
   Evaluation selects Acceptance, read [Acceptance](references/acceptance.md) before freezing its
   mode, cases, identities, or safety; otherwise it remains unloaded and NOT_REQUIRED.
3. Read [Author](references/author.md) immediately before the resident Author begins.

Each reference owns one named contract. It states only local boundaries or exceptions that add to
the Frontier-Agent Principle; later orchestration does not restate those contracts. When this Skill
or another governing contract is itself in the write scope, follow
[Job Design's self-hosting freeze](references/job-design.md#freeze-self-hosting-authority); otherwise
progressive loading above is unchanged.

## 1. Align and model

Use Models to route exactly one Rule or Skill owner and close every material question about outcome,
authority, evidence, preservation, safety, boundaries, grants, validation, loading, and handoff.
Discover resolvable facts and follow Models' sole alignment route for any material choice outside
Agent authority. Continue only in the new run authorized by its alignment handoff.

Complete when one supported Candidate model and exact Candidate surface can express every accepted
obligation without an unresolved material decision.

## 2. Design and freeze

Freeze Job Design's compact Run Contract: accepted meaning; exact Candidate Allowlist and operation
grants; one resident Author; Reviews' Quality and Correctness topology; Role Runtime's identity
lifecycle; conditional Machine and Acceptance; deterministic checks; exits; external-effect
safety; and cleanup. Freeze proof order as conditional Machine, Quality, Correctness, conditional
Acceptance.

Capture the exact whole-Candidate baseline and fingerprint before Author work. A mismatch with the
Design-close Candidate stops before any role or write.

Complete when every reachable role, write, proof, stop, and cleanup action fits the grants and
available capacity.

## 3. Author

Launch the fresh resident Author with the accepted semantic inputs, baseline, exact grant, and
Authoring Scope. Immediately before the write and after the Author returns, verify the complete
Candidate as Job Design requires. Only attributable Author writes inside the grant may advance the
Candidate fingerprint. The Author returns the invocation fingerprint and semantic Change Summary;
after admissible promotion, the Controller binds that summary to the derived post-write
fingerprint.

Complete when an Author COMPLETE is admitted and bound to the promoted fingerprint, or a terminal
status is selected.

## 4. Prove and correct

Run every applicable stage in frozen order under Evaluation:

- Machine performs owner-supported deterministic, non-fixing checks.
- Quality applies Reviews' frozen independent lenses to the complete Candidate.
- Correctness applies Reviews' combined independent lens to the complete accepted contract;
- Acceptance uses its selected mode only when material uncertainty remains.

A Reviewer sends a supported finding directly to the resident Author. Eligible repairs are batched
into one exact Repair Scope. After Author COMPLETE, capture the new fingerprint and rerun every
applicable proof stage in order from Machine under Evaluation's replay and Role Runtime's identity
lifecycle. No semantic proof carries across a repair.

HUMAN_DECISION_REQUIRED stops semantic work immediately and continues only in a new run. Other
terminal outcomes follow Evaluation.

Complete when every applicable stage passes on the final fingerprint, no blocking finding remains,
and every nonblocking finding has an Author disposition.

## 5. Finalize and hand off

Apply Role Runtime's finalization contract, Acceptance's safety contract for every started attempt,
and Evaluation's terminal precedence. Claim success only after their closure requirements and the
final whole-Candidate boundary check pass.

Return a concise handoff containing:

- Candidate type, owner, exact paths, and final fingerprint;
- each stage verdict and Machine commands with exits, or NOT_REQUIRED;
- Acceptance mode and evidence, or NOT_REQUIRED;
- authored changes and repairs;
- unresolved, uncertain, or untested surfaces;
- external-effect cleanup and residual state;
- final boundary-check result; and
- the selected terminal result, every underlying terminal or result retained by Evaluation's
  precedence, and the exact HUMAN_DECISION_REQUIRED request when applicable.

This workflow grants no publication, installation, commit, push, release, translation, or other
downstream effect. Keep transient workflow evidence out of the Candidate.
