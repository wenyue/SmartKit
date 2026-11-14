# CodeGraph Preparation

This public reference exposes Setup's scoped CodeGraph preparation command to authorized callers. Reading it and using the command do not invoke the user-only Setup workflow or require a configuration session. The caller owns when preparation is useful, its permissions, and the effect of unavailable CodeGraph on its task.

## Prepare the selected working tree

Resolve `<skill-root>` to the loaded `setup-project-agents` directory and `<target-root>` to the selected physical working-tree root. Establish authority for CodeGraph installation if absent, target-local indexing and service startup before running:

```text
python "<skill-root>/scripts/workflow.py" setup-codegraph --help
python "<skill-root>/scripts/workflow.py" setup-codegraph --target "<target-root>" --harness "<active-harness>" --approved
```

`--approved` records existing authority; it neither grants permission nor requires repeated consent. The command installs a missing executable, initializes a missing local index, synchronizes pending changes in a usable index, and starts the runtime when needed. It reuses a healthy index and service. Use this scoped route rather than CodeGraph's broad host installer, which can rewrite independently owned host configuration.

Keep each working tree's index in its own `.codegraph` directory. Copying or linking another tree's mutable database is not preparation. Readiness checks require the local database, matching project and worktree identity, a complete synchronized index, and a responsive runtime. Queries must identify the intended tree with `projectPath`; a parent tree's response does not establish readiness here.

## Interpret the result

Success requires exit 0 with `phase: setup-codegraph` and `ready: true`. It establishes current CodeGraph readiness, not configuration setup completion or project health. Reuse the local index on later visits; refresh only when current evidence shows missing or stale readiness. CodeGraph owns automatic synchronization; the worktree's lifecycle owner handles its local resources and services during cleanup.

On failure, preserve existing data, partial output and diagnostics. An incomplete, obsolete or mismatched existing index needs separate repair; this command does not replace it. Resolve unavailable tooling, permission or runtime prerequisites before retrying. Report the gap and continue independent work through direct source inspection where the caller's task permits; do not treat another tree's index as current-tree evidence. A caller that requires CodeGraph remains incomplete. Hook checks remain read-only reminders and authorize no preparation.
