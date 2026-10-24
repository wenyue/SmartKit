---
name: write-rules-and-skills
description: Author, revise, or rewrite one English Rule or Agent Skill.
---

# Write Rules and Skills

Write guidance that helps an Agent do a particular job well. Aim for the minimum guidance that makes ordinary capable readers very likely to share the intended understanding in normal use. Alignment comes before brevity: preserve accepted outcomes, consequential boundaries, and the explanation needed to understand them. Use practical judgment rather than trying to prevent every possible misreading.

## Establish one Candidate and its design

Each invocation produces one **Candidate**: a Rule or Skill and its scoped supporting resources. The active Agent is the Controller; read the [Controller contract](references/controller.md) to establish the request, authority, evidence, and completion conditions. One resident [Author](references/author.md) owns the design and writing through repairs.

For a rewrite, reconsider content, structure, and mechanisms from the artifact's current goals and necessary constraints, including file layout and Skill metadata. Retain sound choices when justified; polishing existing sentences alone does not complete a rewrite.

Read a target Skill's `AUTHORING.md` when present. Create or update it only for a deliberate trade-off that a future writer is likely to undo and whose accidental reversal would be costly. Skip obvious or easily reversed choices. Record the decision and reason; add alternatives or consequences only when worth remembering. Ordinary use of the target does not load this record.

## Review a complete, checked version

After a complete draft passes required checks, obtain three judgments:

| Perspective | Question |
| --- | --- |
| [Quality](references/quality-reviewer.md) | Can the intended reader understand and use it well? |
| [Change](references/change-reviewer.md) | Does the change preserve or deliberately revise the right meaning? |
| [Correctness](references/correctness-reviewer.md) | Does it fulfill the actual request, and will its prescribed behavior work? |

Reviewers apply the [common conduct](references/reviewer.md) and their professional contracts. They identify evidenced defects; the Author chooses the repair. The Controller selects the required independent identities, keeps judgments tied to the same version, and routes user-owned questions. Correctness may commission a bounded [Runner](references/runner.md) when behavior needs observation.

## Close with evidence

Repeat writing, checks, and review within the agreed iteration budget. Keep acceptance standards fixed; optional improvements need not delay an accepted result. Return `COMPLETE` only when all required checks and all three reviews pass on the same final Candidate. Otherwise return `NEEDS_INPUT` or `BLOCKED`, identify the unresolved dependency, and preserve evidence.

This workflow grants no downstream publishing, installation, translation, commit, or other authority. When rewriting this Skill, its complete pre-write instructions govern the current invocation.
