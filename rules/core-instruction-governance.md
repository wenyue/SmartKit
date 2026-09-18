# Instruction Governance

Strength: `Mandatory`

Scope: Rule applicability and loading, direct-instruction authority, Rule and Skill precedence,
and warnings for conflicts encountered during execution.

All SmartKit Skills operate under installed SmartKit core governance. Rule-led Skills named
`rule-<domain>` are Rules exposed through native Skill discovery, with declared `Scope` and default
`Strength` in their entries. They govern relevant work rather than compete as task workflows.

## Rule Applicability and Loading

Use native discovery descriptions and the current task to load relevant Rules before the decisions
they govern. Read a Rule when its applicability is uncertain. Apply every relevant policy within
its declared Scope, including on explicit invocation; invocation does not extend that Scope.
Loading is required regardless of strength and does not itself start a separate task or deliverable
or expand authority.

Load required owned references before decisions that depend on them. If a required Rule or reference
is unavailable, report the missing content and stop dependent work; unrelated work may continue
under the available instructions.

## Strength Levels

- `Mandatory`: Follow unless a higher-priority instruction overrides it.
- `Default`: Follow unless a higher-priority direct instruction or Rule requires a different
  outcome.
- `Advisory`: Adapt to the task context when useful.

Owned normative references inherit their Rule entry's default strength and scope, independent of
the referencing section. They may explicitly override strength and narrow scope. Independently
owned policies retain their own contracts; linking illustrative material does not make it
normative policy.

Within a Rule entry or owned normative reference, each requirement inherits `Strength` from the
nearest enclosing section that declares it, or from that document's default. Declare a section
strength, e.g. ``Strength: `Mandatory` ``, on the first nonblank line after its Markdown heading;
any level above is allowed. The section includes nested headings and ends before the next heading
of equal or higher level, or at the end of the file.

Section strengths leave Rule applicability, ownership, and file-scope specificity unchanged;
heading depth adds no precedence.

## Precedence

The active Harness defines direct-instruction precedence. Apply compatible requirements from every
applicable Rule and Skill. Resolve incompatible requirements by the Rule and Skill precedence
below. When the applicable precedence still leaves a tie, perform only the read-only investigation
needed to establish it, then stop before any side effect and ask the user to resolve it. Delivery
or loading order and naming confer no precedence. For Rules, compare:

1. Each requirement's effective strength: `Mandatory` > `Default` > `Advisory`.
2. Owner at equal strength: project > plugin.
3. Specificity at equal strength and owner: narrower applicable file scope > broader applicable
   file scope > the global tier. A Harness selector controls activation, not specificity.

## Task Skill Composition

- Apply every task Skill within direct instructions and applicable Rules.
- For conflicting task Skill requirements, one Skill is more specific only when its declared
  trigger and owned outcome form a strict subset of the other's for the current task. The
  more-specific Skill controls only the conflict.
- When specificity does not resolve a task Skill conflict, a project-local Skill takes precedence
  over a plugin-distributed Skill. External provenance adds no precedence tier.

## Conflict Warnings

- When normal execution exposes a semantic conflict—two applicable requirements that one action or
  outcome cannot satisfy under the same supported facts—include a warning in the user-facing work
  report. Do not run a separate conflict audit or preflight.
- Using only details that may be disclosed to the user, identify the conflicting requirements and
  their sources, state the precedence result, and explain the action taken or the decision
  requested.
