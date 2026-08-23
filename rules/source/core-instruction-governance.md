# Instruction Governance

Strength: `Mandatory`

Scope: Direct-instruction authority, Rule and Skill precedence, and warnings for conflicts
encountered during execution.

## Strength Levels

- `Mandatory`: Follow unless a higher-priority instruction overrides it.
- `Default`: Follow unless a higher-priority direct instruction or Rule requires a different
  outcome.
- `Advisory`: Adapt to the task context when useful.

## Precedence

The active Harness defines direct-instruction precedence. Apply compatible requirements from every
applicable Rule and Skill. Resolve incompatible requirements by the Rule and Skill precedence
below. When the applicable precedence still leaves a tie, perform only the read-only investigation
needed to establish it, then stop before any side effect and ask the user to resolve it. Delivery
order does not break a tie. For Rules, compare:

1. Strength: `Mandatory` > `Default` > `Advisory`.
2. Owner at equal strength: project > plugin.
3. Specificity at equal strength and owner: narrower applicable file scope > broader applicable
   file scope > the global tier. A Harness selector controls activation, not specificity.

## Skill Composition

- Apply every Skill within direct instructions and applicable Rules.
- For conflicting Skill requirements, one Skill is more specific only when its declared trigger and
  owned outcome form a strict subset of the other's for the current task. The more-specific Skill
  controls only the conflict.
- When specificity does not resolve a Skill conflict, a project-local Skill takes precedence over a
  plugin-distributed Skill. External provenance adds no precedence tier.

## Conflict Warnings

- When normal execution exposes a semantic conflict—two applicable requirements that one action or
  outcome cannot satisfy under the same supported facts—include a warning in the user-facing work
  report. Do not run a separate conflict audit or preflight.
- Using only details that may be disclosed to the user, identify the conflicting requirements and
  their sources, state the precedence result, and explain the action taken or the decision
  requested.
