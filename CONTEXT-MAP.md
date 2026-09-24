# Context Map

## Contexts

- [SmartKit](./contexts/smartkit/CONTEXT.md) — Harness and Platform distinctions, instruction and
  workspace governance, setup ownership, and MCP delivery and readiness
- [Authoring Evaluation](./contexts/authoring-evaluation/CONTEXT.md) — Rule, Skill, and Setup Authoring
  Contract classification, authoring, qualification, review, correction, and adoption
- [Worktree Lifecycle](./contexts/worktree-lifecycle/CONTEXT.md) — Task and Batch Worktrees, commit
  roles, ticket staging, delivery, completion, recovery, and finalization

## Relationships

- **SmartKit → Authoring Evaluation**: SmartKit defines the Rules, Skills, and setup capabilities
  whose authoring and review roles are described by Authoring Evaluation.
- **SmartKit → Worktree Lifecycle**: SmartKit's Workspace Policy governs workspace selection and
  Git authority; Worktree Lifecycle names the worktrees, commits, and delivery states used within
  those boundaries.
