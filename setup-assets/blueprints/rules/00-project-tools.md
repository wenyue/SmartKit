# Project Tools

Strength: `Mandatory`

Scope: Setup Authoring Contract for the target repository's project-tool, MCP, runtime,
synchronization, mutation, and complete-change verification policy.

## Contract frame

When `setup-project-agents` requests `.agents/rules/00-project-tools.md`, author that one
target-owned Mandatory Rule. It applies to project tooling, MCP, runtime, or verification and owns
only the persistent policy needed to select a safe tool outcome, synchronize canonical-source
changes, authorize mutation, verify a complete change, or hand a job to an existing Skill.

Use accepted project intent and evidence qualified by its target-repository owner and provenance.
Relevant evidence includes entry guidance; manifests and runtime declarations; repository scripts
and current help; task-runner and CI configuration; version-control state; existing Rules and
Skills; and accepted Issues, Specs, or ADRs. The existing target Rule is preservation and regression
evidence, not design authority. Preserve its supported policy unless accepted intent expressly
changes or retires it; visibility, tool availability, or write access grants no meaning or
permission.

## Required policy

Require every consequential mapping supported by qualified evidence:

- the working directory or runtime predicate that changes whether an invocation succeeds, and the
  resulting requirement;
- each canonical-source predicate, its required synchronization outcome, any supported read-only
  drift check, and the generated effects that require review;
- each mutating operation, the exact authority that permits it, and the read-only, scoped, dry-run,
  or stop outcome when that authority is absent;
- complete-change verification from the declared comparison point across tracked, staged, and
  untracked state, generated effects, affected surfaces, and all applicable non-fixing checks; and
- an existing Skill handoff only when its observable trigger and bounded result own the job.

Keep target-local API, generated-source, capability, delivery, installation, dependency,
contract-evolution, and placement policy with their existing owners; deterministic mechanics stay
in repository scripts and procedures in the invoked Skill. Exclude inventories, snapshots, command
catalogs, setup mechanics, and facts recoverable from a live owner unless omission changes an
outcome.

## Author grant and terminal result

The future Author may inspect target evidence, run owner-supported read-only or non-fixing checks,
and create or replace only `GENERATED/.agents/rules/00-project-tools.md`, where `GENERATED` is the
request root supplied by `setup-project-agents`. The Author may not delete or move that candidate,
write the live target, mutate unrelated target state, or create an external effect without separate
accepted authority.

Return exactly one terminal result; the first matching discriminator has precedence:

1. `ACCESS_REQUIRED` when necessary evidence or validation cannot be accessed within the grant.
2. `CONTEXT_REQUIRED` when access exists but a necessary fact cannot be discovered from qualified
   evidence.
3. `HUMAN_DECISION_REQUIRED` when qualified evidence permits materially different policies or the
   required mutation, effect, ownership, comparison point, or exception lacks accepted authority.
4. `VALIDATION_FAILED` when a check remains failed, an exact command is unsupported, or a required
   mapping, affected surface, or supported input has no evidenced outcome.
5. `READY` when the one candidate contains every required mapping, each supported predicate selects
   one observable policy outcome, and all applicable owner-supported deterministic checks pass or
   are recorded `NOT_REQUIRED`.

Every stop identifies the blocker, owner, consequence, and condition for a fresh attempt. `READY`
reports the candidate, evidence owners, obligation dispositions, checks, and untested surfaces; it
is input only for `setup-project-agents` and grants no downstream generation, installation,
publication, commit, or push.
