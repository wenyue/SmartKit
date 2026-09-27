---
name: write-rules-and-skills
description: Author or revise one English Rule or Agent Skill.
---

# Write Rules and Skills

Write an artifact that helps an Agent do a particular job well: make the right decisions,
understand the important constraints, and reach a useful result. A good Rule makes policy usable;
a good Skill supplies the knowledge and method its task needs. Neither is improved by accumulating
every instruction that might apply.

Each invocation produces one **Candidate**: a Rule or Skill and its scoped supporting resources.
The active Agent is the Controller. Read the [Controller contract](references/controller.md) to
prepare the assignment and manage it through handoff.

## How the work proceeds

The Controller establishes the actual request, editable scope, evidence, and completion conditions.
One [Author](references/author.md) receives the task context and a concise brief, then owns the
writing from the first draft through repairs. The brief locates the job and conveys the user's
requirements and reasons without prescribing the composition.

After the Author returns a complete draft and required checks pass, review it from three distinct
perspectives:

| Perspective | Question |
| --- | --- |
| [Quality](references/quality-reviewer.md) | Can the intended reader understand and use it well? |
| [Change](references/change-reviewer.md) | Does the change preserve or deliberately revise the right meaning? |
| [Correctness](references/correctness-reviewer.md) | Does it fulfill the actual request, and will its prescribed behavior work? |

Reviewers follow the [common conduct](references/reviewer.md) and their own professional contracts.
They identify evidenced defects; the Author chooses a coherent repair. The Controller arranges
independent identities when the job needs them, keeps all judgments tied to the same version, and
resolves questions that belong to the user. When behavior needs observation, Correctness may
commission a bounded [Runner](references/runner.md).

Repeat writing, checks, and review while material defects remain and the agreed iteration budget
allows useful progress. Acceptance standards stay fixed. Completion means the same final Candidate
has passed the required checks and all three reviews; a promising draft or an exhausted budget is
not that result.

The workflow returns `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED`, with exact files and supporting evidence.
It operates within the task's authority. Publishing, installing, translating, committing, and other
downstream actions retain their own authorization. When this Skill is itself being rewritten,
its pre-write instructions govern the current invocation.
