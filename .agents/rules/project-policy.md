# Project Policy

Keep authority with canonical inputs, deliver through their declared owners, and verify the surfaces the task actually changes.

## Change the owning source

Each generated, delivered, or installed surface has one canonical input. Maintain it through that input and its owning generator or synchronizer; target state never becomes canonical plugin authority.

Deliver and expose surfaces only through declared owners and routes. Public manifests expose only declared public surfaces. Source authoring alone neither requires nor authorizes downstream generation, delivery, or installation.

Changes to setup must preserve the ownership and conflict boundaries in [Setup Project Agents](../../skills/setup-project-agents/SKILL.md).

When retiring a current contract, remove its implementation, documentation, tests, and handling together. Retain or add compatibility only when an accepted current contract requires it.

## Reuse resources through supported plugin routes

SmartKit Skills may share documentation, scripts, and assets outside their own directories when those resources are declared and bundled in the supported plugin distribution. Resolve them from the actual loaded Skill or plugin installation, independently of the target working directory and authoring machine.

Preserve each resource's canonical owner and applicable loading and failure requirements. State when and how to load or use it in the consuming Skill, or in a core Rule guaranteed to load in the supported environment. Once that central Rule is loaded, consumers may rely on its route without repeating the guidance or pointers. Supported command interfaces and their help may provide usage guidance.

Keep task-specific inputs, outputs, permissions, and lifetime contracts with the consuming Skill. If a required resource is unavailable, report the prerequisite gap and leave dependent work incomplete.

This supported route means a Skill need not be independently copyable. It permits use of declared shared plugin resources, not another Skill's private resources or arbitrary project or external files. It grants no packaging, publishing, or installation authority.

## Write documentation for its readers

### Route Rule readers through Skill entries

Project Rules reference a Skill through its `SKILL.md`, without links to internal sections. The Skill owns the reading path to its supporting guidance.

### Keep root READMEs concise and actionable

Keep `README.md` and `README.zh-CN.md` aligned as human-facing plugin documentation: a brief introduction and actionable installation instructions, including necessary prerequisites and activation.

Organize the Skill overview into these ordinary usage groups; metadata remains authoritative for invocation restrictions:

1. Explicit invocation only: Skills that require the user to invoke them.
2. User-invokable tasks: Skills users choose for a task and Agents may select automatically when applicable.
3. Generally invoked automatically by the Agent: Skills ordinarily selected to support the user's work.

Give each SmartKit Skill in the first two groups its own section, following overview order. Explain when and how to invoke it, with a short example when useful. Keep the third group in the overview without individual sections.

Place internal workings, architecture, Rule delivery, discovery and precedence, implementation details, and maintainer or configuration reference material outside these READMEs.

### Synchronize first-party mirrors

After changing a repository-maintained first-party English Rule or Skill, whether public or project-local, synchronize its Simplified-Chinese documentation mirror with `smartkit:translate-agent-artifacts`.

## Verify the actual change

Run required owner checks in non-fixing mode for the changed surfaces and affected integrations. Review generated diffs and run `git diff <comparison-point> --check`. Required checks must pass before reporting completion or success.
