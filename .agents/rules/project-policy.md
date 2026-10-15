# Project Policy

## Keep Authority with the Canonical Input

Each generated, delivered, or installed surface has one canonical input. Keep canonical plugin authority with that input, never with target state.

Change these surfaces through their canonical input and its owning generator or synchronizer. Deliver and expose surfaces only through declared owners and routes. Public manifests must expose only declared public surfaces.

Source authoring alone neither requires nor authorizes downstream generation, delivery, or installation.

Changes to setup must preserve the ownership and conflict boundaries defined in [Setup Project Agents](../../skills/setup-project-agents/SKILL.md).

## Reuse Shared Plugin Resources

SmartKit Skills may reuse shared documentation, scripts, and assets outside their own directories through supported plugin resource paths. Required resources must be declared and bundled in the supported plugin distribution; resolve them from the actual loaded Skill or plugin installation, rather than the target project's working directory or an authoring machine's absolute paths.

Keep each resource's canonical owner and applicable loading and failure requirements. State when and how to load or use it in the consuming Skill, or centrally in a core Rule guaranteed to load in the supported plugin environment. A consuming Skill may rely on that central route once the Rule is loaded, without repeating its shared guidance or pointers. Supported command interfaces and their help may supply use guidance.

Keep task-specific inputs, outputs, permissions, and lifetime contracts with the consuming Skill. If a required resource is unavailable, report the prerequisite gap and leave dependent work incomplete.

Skills need not be independently copyable when this supported route supplies their dependencies. This permission covers declared shared plugin resources; it grants neither access to another Skill's private resources or arbitrary project or external files, nor authority to package, publish, or install resources.

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
