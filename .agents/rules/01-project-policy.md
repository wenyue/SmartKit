# Project Policy

**Strength:** Mandatory  
**Scope:** SmartKit repository source changes, delivery, setup ownership, contract retirement,
verification, and Rule/Skill translation. These constraints govern repository operations; they do
not establish the meaning of portable authored artifacts.

## Delivery authority

Each generated, delivered, or installed surface has one canonical input. When changing those
targets, change that input and use its owning generator or synchronizer. Deliver and expose surfaces
only through declared owners and routes; public manifests expose only declared public surfaces.
Target state must not become canonical plugin authority. Source authoring alone does not require
or authorize downstream generation, delivery, or installation.

Changes to setup must preserve the ownership and conflict boundaries defined in
[Setup Project Agents](../../skills/setup-project-agents/SKILL.md#inputs-and-ownership).

When retiring a current contract, remove its implementation, documentation, tests, and handling
together. Retain or add compatibility only when an accepted current contract requires it.

## Verification

For actual changes and affected integrations, required owner checks must pass in non-fixing mode
before reporting completion or success. Review any generated diffs and run
`git diff <comparison-point> --check`.

## Translation

After changing a project-owned English Rule or Skill, use `smartkit:translate-agent-artifacts` to
synchronize its Simplified-Chinese documentation mirror.
