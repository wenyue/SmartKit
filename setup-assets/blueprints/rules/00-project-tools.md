# Project Tools

Strength: `Mandatory`

Scope: Setup Authoring Contract for the target repository's safe command execution, synchronization,
mutation, complete-change verification, and existing Skill handoffs.

## Target meaning

The future target is one target-owned `.agents/rules/00-project-tools.md` Mandatory Rule used
directly by its repository. Its persistent policy covers only safe repository-tool execution,
source-change synchronization, mutation authority, complete-change verification, and handoff to an
existing Skill whose trigger owns a job.

The Rule's applicability, predicate-to-outcome mappings, exceptions, precedence, and ownership
boundaries come from current target evidence. Supported existing semantics remain unless accepted
intent selects their change or retirement. Its write boundary is the one target Rule. Any
materially outcome-changing ambiguity is a stop, including conflicting or unsupported
applicability, predicate or synchronization mappings, exceptions, precedence, owner boundaries,
mutation authority, comparison points, preservation, or required checks.

## Evidence and required mappings

Supported evidence consists of repository entry guidance; workspace and package manifests; runtime
and toolchain declarations; repository scripts and their help; task-runner and CI configuration;
version-control state; and discoverable Skill contracts.

The generated Rule contains only mappings established by that evidence:

- a working-directory or runtime prerequisite when it changes invocation success, pointing to its
  live owner rather than caching a discoverable value;
- each consequential canonical-source change and its required synchronization outcome, read-only
  alternative when one exists, and generated effects that require inspection;
- each consequential mutation and the authority that permits it, with the required read-only,
  scoped, or dry-run outcome when authority is absent;
- complete-change evidence from the declared comparison point, tracked and untracked changes,
  generated effects, affected surfaces, and their applicable non-fixing checks; and
- an existing Skill handoff only when its observable trigger and bounded result own the job.

An uncovered affected path or surface, or an unpassed required check, prevents a complete-
verification claim. Tool inventories, environment snapshots, command catalogs, setup procedure,
and behavior already owned by live configuration, scripts, command help, or Skills remain outside
the Rule.

## Ownership boundaries

Target-local policy owners retain hard API, generated-source, capability ownership, delivery,
installation, dependency, contract-evolution, and advisory placement decisions. This Rule may
reference those concerns when they select a tooling outcome but does not restate them. Deterministic
mechanics remain in repository-owned scripts.

## Qualified authoring input

The qualified input for the target authoring owner maps every included predicate and exact command
to authoritative target evidence. It contains preserved obligations, accepted changes,
evidence-backed omissions, unresolved surfaces, and a validation plan covering affected structured
and executable surfaces, including the evidence needed to decide whether machine validation or
executable Acceptance applies.
