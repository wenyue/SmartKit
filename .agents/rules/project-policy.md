# Project Policy

## Keep Authority with the Canonical Input

Each generated, delivered, or installed surface has one canonical input. Keep canonical plugin authority with that input, never with target state.

Change these surfaces through their canonical input and its owning generator or synchronizer. Deliver and expose surfaces only through declared owners and routes. Public manifests must expose only declared public surfaces.

Source authoring alone neither requires nor authorizes downstream generation, delivery, or installation.

Changes to setup must preserve the ownership and conflict boundaries defined in [Setup Project Agents](../../skills/setup-project-agents/SKILL.md).

## Retire Contracts as a Whole

When retiring a current contract, remove its implementation, documentation, tests, and handling together. Retain or add compatibility only when an accepted current contract requires it.

## Maintain Documentation for Its Readers

### Skill references

Project Rules reference Skills through their `SKILL.md` entries, without links to internal sections. Let each Skill own the reading path to its supporting guidance.

### Root READMEs

Keep `README.md` and `README.zh-CN.md` aligned as concise, human-facing plugin documentation. Provide a brief introduction and actionable installation instructions, including necessary prerequisites and activation steps.

Organize the Skill overview into three usage groups:

1. Explicit invocation only: Skills that require the user to invoke them.
2. User-invokable tasks: Skills users choose for a particular task, which Agents may also invoke automatically when applicable.
3. Generally invoked automatically by the Agent: Skills the Agent ordinarily selects to support the user's work.

These groups describe ordinary usage; Skill metadata remains authoritative for actual invocation restrictions.

Give each SmartKit Skill in the first two groups its own section, in the order its entry appears in the overview. Briefly explain when to use it and how to invoke it; include a short example when it makes usage clearer. Keep Skills in the third group in the overview without individual sections.

Keep internal workings, architecture, Rule delivery, discovery and precedence, implementation details, and maintainer or configuration reference material outside these READMEs.

### Rule and Skill mirrors

After changing a first-party English Rule or Skill maintained by this repository, whether public or project-local, synchronize its Simplified-Chinese documentation mirror with `smartkit:translate-agent-artifacts`.

## Verify Before Reporting Completion

Run the required owner checks in non-fixing mode for the actual changes and affected integrations. These checks must pass before reporting completion or success. Review any generated diffs and run `git diff <comparison-point> --check`.
