# Instruction Governance

Strength: `Mandatory`

Scope: Rule strength and precedence, Skill authority and overlap, and reporting of semantic
conflicts encountered during execution.

## Strength Levels

- `Mandatory`: Follow unless a higher-priority instruction overrides it.
- `Default`: Follow unless a higher-priority direct instruction or Rule requires a different
  outcome.
- `Advisory`: Adapt to the task context when useful.

## Rule Precedence

The active Harness defines direct-instruction precedence. Resolve conflicts between applicable
Rules by this tuple:

1. Strength: `Mandatory` > `Default` > `Advisory`.
2. Owner at equal strength: project > plugin.
3. Specificity at equal strength and owner: narrower applicable file scope > broader applicable
   file scope > the global tier. Globally applicable Rules and Rules scoped only by Harness share
   the global tier.

## Skill Composition

- Apply every Skill within direct instructions and applicable Rules, including when it specializes
  procedure or completion gates.
- When applicable Skills overlap, apply the more-specific Skill. At equal specificity, apply a
  project-local Skill before a plugin-distributed Skill; external provenance alone creates no
  additional precedence tier.

## Conflicts Encountered During Execution

- A semantic conflict is encountered when, under the same supported facts, two applicable
  requirements cannot be satisfied by one action or outcome. Handle a conflict when execution
  exposes it; do not add a separate conflict audit, preflight check, or configuration-time
  inference.
- Apply the governing instruction precedence and the Rule precedence tuple to every encountered
  conflict. When precedence selects one requirement, follow it and continue execution.
- When incompatible requirements remain tied after precedence, perform only the read-only
  investigation needed to establish the tie, then stop before any side effect and ask the user to
  resolve it. Do not use delivery order as an implicit tiebreaker.
- Report every encountered conflict in the user-facing work report, whether precedence resolved it
  or execution stopped. Identify the conflicting requirements and their sources, state the
  precedence facts and result, and explain the action taken or the unresolved decision requested.
