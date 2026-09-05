# Project Tools

Strength: `Mandatory`

Scope: Setup Authoring Contract for the target repository's tooling, MCP, runtime,
synchronization, mutation, and complete-change verification policy.

## Purpose and evidence

For a `setup-project-agents` request targeting `.agents/rules/00-project-tools.md`, the Author
produces one target-owned Mandatory Rule. It governs tool selection, canonical-source
synchronization, mutation authority, complete-change verification, and handoff to existing Skills.

Setup must make the relevant target evidence available: entry guidance, manifests and runtime
requirements, repository scripts and current help, task runners and CI, Git state, existing Rules
and Skills, and accepted Issues, Specs, or ADRs. Qualify each source by owner and provenance.
Accepted project intent governs; existing Rule text supplies preservation and regression evidence.
Classify obligations as preserve, change, add, retire, or non-goal, preserving supported policy
unless accepted intent changes or retires it. Visibility and access confer no authority.

## Policy to establish

The Rule connects each consequential condition to its required outcome:

- **Invocation:** working-directory and runtime requirements that determine whether a tool works.
- **Synchronization:** canonical changes, their required synchronization, supported read-only drift
  checks, and generated effects requiring review.
- **Mutation:** the authority for each operation and the permitted read-only, scoped, dry-run, or
  stop alternative when authority is absent.
- **Verification:** the complete change from its declared comparison point, including tracked,
  staged, unstaged, and untracked state, generated effects, affected surfaces, and every applicable
  non-fixing check.
- **Handoff:** an existing Skill's observable trigger and bounded result when that Skill owns the job.

Keep API, capability, generated-source, delivery, installation, dependency, contract-evolution, and
placement policy with their existing owners. Scripts retain deterministic mechanics; Skills retain
procedures. Include live-owner facts only when their omission changes a policy outcome, leaving
inventories, command catalogs, snapshots, and setup mechanics to those owners.

## Author boundary and result

The Author may inspect target evidence, run owner-supported read-only or non-fixing checks, and
create or replace `GENERATED/.agents/rules/00-project-tools.md`. `GENERATED` is the request root
supplied by setup. Deletion, moves, live-target writes, unrelated mutation, and external effects
require separate accepted authority.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Material policy alternatives remain, or a required mutation, effect, owner, comparison point, exception, or obligation disposition lacks accepted authority. |
| `VALIDATION_FAILED` | A required check fails, an exact command is unsupported, or a required mapping, affected surface, or supported input lacks an evidenced outcome. |
| `READY` | Every required mapping is present, each supported predicate selects one observable policy outcome without invented facts, and all applicable deterministic checks pass or are evidenced as `NOT_REQUIRED`. |

A stop names the blocker, owner, consequence, and condition for a fresh attempt. A ready handoff
identifies the Candidate, target and evidence owners, obligation dispositions, checks, preserved
constraints, and uncertain or untested surfaces. It is input to `setup-project-agents`; it grants
no downstream generation, installation, publication, commit, or push.
