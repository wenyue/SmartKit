---
name: write-shared-rules-and-skills
description: Author or revise a portable cross-project SmartKit Rule or Skill; excludes project-local artifacts and Setup Authoring Contracts.
---

# Write Shared Rules and Skills

Qualify exactly one portable cross-project SmartKit Rule or Skill, author it through the public
[`write-rules-and-skills`](../../../skills/write-rules-and-skills/SKILL.md) workflow, and close its
portability obligations at handoff.

## Principles

- **Portability delta.** This Skill owns only qualification and handoff closure. Supply the closed
  input unchanged to the public workflow without adapting or recreating its mechanisms, and
  preserve its terminal result—`COMPLETE`, `NEEDS_INPUT`, or `BLOCKED`—and handoff.

Read the [portability reference](references/portability.md) completely when qualifying the request
and when closing the public handoff.

## 1. Qualify and prepare

Apply the reference's ownership, evidence, and input-closure requirements. Continue only when it
produces one closed portability input; otherwise follow its terminal route and stop.

## 2. Invoke the public workflow

Invoke the public workflow with the closed input and await its result.

For a self-hosting change to this Skill, use the pre-Author public and private contracts throughout
the run; the edited text applies only to a later invocation.

## 3. Close the portable handoff

Apply the reference's handoff-closure requirements without reinterpreting the public result.
Preserve the public handoff and append the resulting closure account.
