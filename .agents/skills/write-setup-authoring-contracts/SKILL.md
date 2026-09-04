---
name: write-setup-authoring-contracts
description: Author or revise a judgment-only Setup Authoring Contract under setup-assets/blueprints; excludes generated targets and shared SmartKit artifacts.
---

# Write Setup Authoring Contracts

Author or revise the smallest complete set of judgment-only Setup Authoring Contracts under
`setup-assets/blueprints/**`. Each contract provides the accepted foundation for one future Rule or
Skill. Candidate effects are limited to those contract files; the separate result is the handoff
report defined below. Before shaping a contract, read and apply the checkout-authoritative
`writing-for-agents` Skill.

## Principles

- **One contract, one target.** A contract owns the meaning and evidence for exactly one future Rule
  or Skill target. Include every contract required by accepted project intent and no speculative
  target.
- **Qualified evidence.** Derive meaning from accepted user decisions and current authoritative
  Issues, Specs, ADRs, governing contracts, target-owner evidence, and observable target behavior.
  Qualify each source by semantic owner and provenance. Existing contracts are completeness and
  regression evidence, not proof of completeness or design authority.
- **Descriptive contracts.** Specify what a future target must mean, permit, validate, return, and
  stop on. Leave setup discovery, ordering, tool choice, retries, writes, and generation mechanics
  to their runtime owners. A procedure-led target must express its supported procedure, but its
  Setup Authoring Contract remains descriptive.
- **Exact authority.** Create, replace, delete, or move a contract only when that exact path and
  operation are separately authorized; otherwise stop before writing. Nonnormative context,
  repository visibility, discoverability, tool availability, catalog metadata, or write access
  grants neither meaning nor permission. Preserve every unrelated path and independently owned
  surface.
- **Separated effects.** `setup-project-agents` alone owns downstream generation and setup
  execution. This Skill does not produce future targets or shared SmartKit artifacts, implement
  setup orchestration, translate, install, publish, commit, or push.

## What each contract establishes

Determine the exact paths in the smallest complete contract set. For every contract, make these
facts reconstructable from accepted evidence:

- the future target's objective, actor, trigger, exact path, Rule or Skill semantic type, and owner;
- the target-repository evidence and provenance that setup must make available to its future Author;
- every behavior-changing obligation, classified as preserve, change, add, retire, or non-goal;
- the future Author's exact Candidate and write paths; separately authorized create, replace,
  delete, and move operations; other permissions and permitted external effects; and required
  validation;
- every supported outcome of the future target and its future authoring run, each with an observable
  discriminator; and
- every missing authority, unsupported fact, or material ambiguity that must stop the future Author
  rather than supply an invented target fact, owner, policy, permission, or action.

Use the supplied task, Candidate, and evidence first. Discover additional material only for an
applicable instruction or concrete need and within the exact grants. Before writing, ensure that
every obligation has one accepted disposition or explicit stop and that every future operation fits
its grant.

Write each contract as a coherent specification, not an implementation recipe. Co-locate each
trigger with its outcome, discriminator, and exit, and keep every commitment with its semantic
owner. The set is minimal when each instruction can change a supported generation-or-stop outcome
and every such outcome follows without inventing a project fact.

## This Skill's stops

For the current contract-authoring run, use these exceptional results when the contract set cannot
yet be written safely:

- `ACCESS_REQUIRED` when necessary evidence or validation is inaccessible within the grant.
- `CONTEXT_REQUIRED` when authorized access exists but a necessary fact cannot be discovered from
  qualified evidence.
- `HUMAN_DECISION_REQUIRED` when a material choice lies outside accepted authority.

For missing access or context, report the exact need, why authorized discovery could not satisfy it,
the owner or condition that can resolve it, the consequence, and the authority and observable
condition required for a fresh run. For a decision, name its owner, live choices, evidence, and
consequences. Resume only in a new run after the missing input and retry authority are established.

## Validation and handoff

Run every applicable owner-supported deterministic non-fixing check. Record `NOT_REQUIRED` only
when qualified owner evidence establishes that no such check applies. Then statically prove that the
complete set:

- remains judgment-only and within blueprint ownership;
- accounts for every behavior-changing obligation and future Author permission;
- maps each supported input to exactly one observable generation-or-stop outcome; and
- reaches every outcome without an unsupported project fact.

An unresolved check failure, ownership conflict, or material ambiguity stops completion. Complete
only when every check passes or is `NOT_REQUIRED` and the static proof closes.

Return the exact contract paths and owners, supported outcomes, checks and results, preserved
constraints, and uncertain or untested surfaces. Hand the contracts off only as ready input to
`setup-project-agents`; do not invoke it or perform a downstream effect.
