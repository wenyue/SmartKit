---
name: write-setup-authoring-contracts
description: Author or revise a judgment-only Setup Authoring Contract under setup-assets/blueprints; excludes generated targets and shared SmartKit artifacts.
---

# Write Setup Authoring Contracts

## Frontier-Agent Principle

This is a judgment-led Skill for a capable current frontier Agent. State semantic authority,
evidence, invariants, and only boundaries whose omission could change correctness, safety,
ownership, permissions, external effects, executability, exits, or handoff. Leave ordinary
discovery, reasoning, tool choice, and drafting method to the Agent.

At the first need to shape or revise a contract, read and apply the installed `writing-for-agents`
Skill for information hierarchy, context pointers, completion bounds, co-location, and pruning.

The active Agent authors or revises the smallest complete set of judgment-only Setup Authoring
Contracts when accepted project intent requires contracts under `setup-assets/blueprints/**`.
Those contracts are the only owned outcome of this Skill.

## Authority and ownership

Begin with the supplied task, Candidate, and evidence. Discover additional material only for an
applicable instruction or concrete role need and within the current exact grants; do not
proactively load unrelated content. Derive contract meaning from accepted user decisions and the
current authoritative Issues, Specs, ADRs, governing contracts, target-owner evidence, and
observable target implementation evidence. Qualify every source by semantic owner and provenance.
Existing contracts are completeness and regression evidence, not design authority; nonnormative
context, repository visibility, discovery, tool availability, and catalog metadata grant no
meaning or permission.

A Setup Authoring Contract owns the meaning and evidence that a future Author must use for one Rule
or Skill target. `setup-project-agents` owns downstream generation and setup execution. This Skill
does not own or produce future targets, shared SmartKit artifacts, setup search or orchestration,
translations, installation, publication, commits, or pushes.

Write only the exact intended contract paths under `setup-assets/blueprints/**`. Create, delete, or
move a contract only when that exact operation is separately authorized; otherwise stop before the
operation. Preserve every unrelated path and independently owned surface.

## Establish the contract set

Determine the exact paths in the smallest complete contract set. For each contract, establish a
Setup Contract Frame from accepted evidence:

- the future target's objective, actor, trigger, exact path, Rule or Skill semantic type, and owner;
- the relevant target-repository evidence and its provenance that setup must make available to the
  future Author;
- every behavior-changing obligation, classified as preserve, change, add, retire, or non-goal;
- the future Author's exact Candidate and write paths, separate create, delete, and move authority,
  other permissions, permitted external effects, and required validation;
- every supported outcome with an observable discriminator; and
- each material missing authority, unsupported fact, or ambiguity that requires a stop rather than
  an invented target fact, owner, policy, permission, or action.

Use `CONTEXT_REQUIRED` when a necessary fact cannot be discovered within authorized access and
`ACCESS_REQUIRED` when necessary access is absent. These are exceptional fallbacks. Return the
exact missing fact or access, why authorized discovery could not obtain it, the owner or condition
that can resolve it, and the condition under which retry is authorized. Resume only in a new run
after the missing context or access is resolved and retry authority is established. Use
`HUMAN_DECISION_REQUIRED` for a material choice outside accepted authority, naming the decision
owner, live choices, evidence, and consequences. Writing begins only when every obligation has one
accepted value or explicit stop condition and every future operation fits its grant.

## Write the contracts

Express each Setup Contract Frame as a judgment-only contract: specify required meaning, evidence,
decisions, outcomes, and stops without prescribing how setup searches, orders work, selects tools,
retries, writes, or implements generation. A contract for a procedure-led target requires the
future target to express the supported procedure; it does not reproduce setup's implementation.

Co-locate each trigger, outcome, discriminator, and exit. Keep each operative commitment with its
semantic owner. The complete set is minimal when every instruction changes a supported
generation-or-stop outcome and every such outcome follows without inventing a project fact.

## Validate and hand off

Run existing applicable owner-supported deterministic non-fixing checks; record `NOT_REQUIRED`
when none exist. Within the granted contract paths, establish static proof that the complete set:

- remains judgment-only and within blueprint ownership;
- accounts for every behavior-changing obligation and future Author permission;
- gives each supported input exactly one observable generation-or-stop outcome; and
- requires no unsupported project fact to reach that outcome.

An unresolved check failure, ownership conflict, or material ambiguity is a stop, not a completed
contract. Complete only when the checks pass or are `NOT_REQUIRED` and the static proof holds.

Return the exact contract paths and owners, supported outcomes, checks and results, preserved
constraints, and uncertain or untested surfaces. Hand the contracts off only as ready input to
`setup-project-agents`; do not invoke it or perform any downstream effect.
