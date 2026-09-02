# Project Structure

Strength: `Advisory`

Scope: Setup Authoring Contract for target-repository structure, placement, responsibility, and
navigation recommendations.

## Contract frame

When `setup-project-agents` requests `.agents/rules/02-project-structure.md`, author that one
target-owned Advisory Rule titled `Project Structure`. It ranks supported choices among locations,
responsibility seams, or navigation entries after narrower or Mandatory validity policy. It does
not establish ownership, permit a dependency, or change delivery, installation, or exposure policy.

Qualify accepted intent and evidence by its target-repository owner and provenance. Relevant
evidence includes entry guidance and narrower Rules; accepted Issues, Specs, and ADRs; callers,
imports, consumers, tests, schemas, registries, generators, runtime entries, and canonical
documentation routes. Directory names, naming, co-location, package boundaries, and machine-local
state are clues, not authority. The existing target Rule is regression evidence, not design
authority.

Classify each inherited or proposed recommendation as preserve, change, add, retire, or non-goal.
Changing, adding, retiring, or excepting a supported recommendation requires accepted intent and
qualified evidence; otherwise preserve it or stop.

## Required recommendations

Each recommendation must answer a real competing choice with its predicate, ranked outcome,
evidence owner, and any exact exception. Preserve all evidenced mappings for:

- locality when one consumer retains deciding context and keeps policy, implementation, and tests
  cohesive;
- an established shared seam when independent consumers need one stable decision or copies create
  cross-owner coupling;
- a consumer-facing boundary for representation that adapts upstream intent without deciding it;
- the earliest established owner with enough context for repeated downstream policy or mechanics,
  unless moving upstream erases the selecting context; and
- a canonical navigation entry that leads to the owning source without duplicating an inventory.

An exception states its scope, predicate, and reason. Keep hard ownership, canonical-source,
dependency, generation, installation, delivery, exposure, and validation policy with its Mandatory
owner. Exclude package tours, cached layouts, generic layering, speculative architecture, setup or
authoring procedure, and advice that changes no supported choice.

## Author grant and terminal result

The future Author may inspect target evidence, run owner-supported read-only or non-fixing checks,
and create or replace only `GENERATED/.agents/rules/02-project-structure.md`, using the request root
from `setup-project-agents`. It may not delete or move that Candidate, write the live target, mutate
unrelated state, or create an external effect without separate accepted authority.

Return exactly one terminal result; the first matching discriminator has precedence:

1. `ACCESS_REQUIRED` when necessary evidence or validation cannot be accessed within the grant.
2. `CONTEXT_REQUIRED` when access exists but a necessary fact cannot be discovered from qualified
   evidence.
3. `HUMAN_DECISION_REQUIRED` when qualified evidence supports materially different rankings or a
   required owner, exception, obligation disposition, operation, or effect lacks accepted authority.
4. `VALIDATION_FAILED` when a check remains failed or a supported choice, obligation, operation, or
   boundary lacks one evidenced outcome or grant.
5. `READY` when every recommendation answers a supported choice, each supported input selects one
   observable outcome, no conclusion requires an unsupported project fact, and all applicable
   owner-supported deterministic checks pass or are recorded `NOT_REQUIRED`.

Every stop identifies the blocker, owner, consequence, and condition for a fresh attempt. `READY`
reports the Candidate, target and evidence owners, obligation dispositions, checks, preserved
constraints, and uncertain or untested surfaces. It is input only for `setup-project-agents` and
grants no downstream generation, installation, publication, commit, or push.
