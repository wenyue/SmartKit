# Project Policy

## Keep Authority with the Canonical Input

Each generated, delivered, or installed surface has one canonical input. Keep canonical plugin
authority with that input, never with target state.

Change these surfaces through their canonical input and its owning generator or synchronizer.
Deliver and expose surfaces only through declared owners and routes. Public manifests must expose
only declared public surfaces.

Source authoring alone neither requires nor authorizes downstream generation, delivery, or
installation.

Changes to setup must preserve the ownership and conflict boundaries defined in
[Setup Project Agents](../../skills/setup-project-agents/SKILL.md#inputs-and-ownership).

## Retire Contracts as a Whole

When retiring a current contract, remove its implementation, documentation, tests, and handling
together. Retain or add compatibility only when an accepted current contract requires it.

## Maintain Documentation for Its Readers

### Root READMEs

Keep `README.md` and `README.zh-CN.md` aligned as concise, human-facing plugin documentation.
Provide a brief introduction and actionable installation instructions, including necessary
prerequisites and activation steps.

Keep internal workings, architecture, Rule delivery, discovery and precedence, implementation
details, and maintainer or configuration reference material outside these READMEs.

### Rule and Skill mirrors

After changing a first-party English Rule or Skill maintained by this repository, whether public
or project-local, synchronize its Simplified-Chinese documentation mirror with
`smartkit:translate-agent-artifacts`.

## Verify Before Reporting Completion

Run the required owner checks in non-fixing mode for the actual changes and affected integrations.
These checks must pass before reporting completion or success. Review any generated diffs and run
`git diff <comparison-point> --check`.
