# Context Map

SmartKit separates its ubiquitous language by the capability area that owns each concept. Read the
map first, then load only the contexts relevant to the current topic.

## Contexts

- [SmartKit](./contexts/smartkit/CONTEXT.md) — read for Harness and Platform distinctions,
  instruction or workspace governance, setup ownership, and MCP delivery or readiness
- [Authoring Evaluation](./contexts/authoring-evaluation/CONTEXT.md) — read when classifying,
  authoring, qualifying, reviewing, correcting, or adopting a Rule, Skill, or Generation Contract
- [Worktree Lifecycle](./contexts/worktree-lifecycle/CONTEXT.md) — read for Task or Batch Worktrees,
  commit roles, ticket staging, delivery, completion, recovery, and finalization

## Relationships

- **SmartKit → Authoring Evaluation**: SmartKit governance and ownership boundaries constrain what
  Authoring Evaluation may classify, author, qualify, and adopt
- **SmartKit → Worktree Lifecycle**: Workspace Policy supplies the workspace selection, Git-state,
  commit-authority, and remote-action boundaries used throughout the Worktree Lifecycle
- **Authoring Evaluation → SmartKit**: Adoption Gate permits qualified authoring artifacts to enter
  the SmartKit repository only after every required Canary Candidate has passed its own gates
