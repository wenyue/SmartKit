# Instruction Governance

Strength: `Mandatory`

All SmartKit Skills operate under installed SmartKit core governance. Rule-led Skills named
`rule-<domain>` are Rules exposed through native Skill discovery, with default `Strength`
in their entries. Rule files and rule-led Skills form one policy category; they govern relevant
work rather than compete as task workflows.

## Rule Applicability and Loading

Use native discovery descriptions and the current task to load relevant Rules before the decisions
they govern. Read a Rule when its applicability is uncertain. Apply each requirement when its stated
conditions hold, including on explicit invocation; invocation does not change those conditions.
Loading is required regardless of strength and does not itself start a separate task or deliverable
or expand authority.

Loading and reading requirements may be satisfied by complete applicable Rule or reference content
already available in context when there is no evidence of a change or staleness that could affect
the decision. Load missing content, including after compaction, and refresh affected content when
such evidence appears. Follow explicit requirements for a fresh read or check.

Load required owned references before decisions that depend on them. If a required Rule or reference
is unavailable, report the missing content and stop dependent work; unrelated work may continue
under the available instructions.

## Strength Levels

- `Mandatory`: Follow unless a higher-priority instruction overrides it.
- `Default`: Follow unless a controlling direct instruction or policy requires a different
  outcome, or an explicit task alternative wins under Task Skill Composition below.
- `Advisory`: Adapt to the task context when useful.

Owned normative references inherit their Rule entry's default strength, independent of the
referencing section, and may explicitly override it. Apply their requirements together with the
entry's relevant conditions and exceptions. Independently owned policies retain their own
contracts; linking illustrative material does not make it normative policy.

Within a Rule entry or owned normative reference, each requirement inherits `Strength` from the
nearest enclosing section that declares it, or from that document's default. Declare a section
strength, e.g. ``Strength: `Mandatory` ``, on the first nonblank line after its Markdown heading;
any level above is allowed. The section includes nested headings and ends before the next heading
of equal or higher level, or at the end of the file.

Section strengths leave Rule applicability and ownership unchanged; heading depth adds no
precedence.

## Precedence

The active Harness defines direct-instruction authority. Apply compatible requirements from every
applicable Rule and Skill. Resolve only incompatible clauses through the comparisons below; the
winner leaves all other applicable requirements in force. If a genuine conflict remains tied,
perform only the read-only investigation needed to establish it, then stop affected side effects
and ask the user to resolve it. Every result remains subject to independent permission gates.

Packaging, names, always or conditional loading, delivery order, and explicit invocation confer no
precedence. A Harness selector controls activation, not rank.

Establish project or plugin ownership from the canonical source and who owns its meaning, for
Rules, rule-led Skills, and task Skills alike. Installing or copying a plugin artifact into a
project does not by itself make it project-owned. External provenance adds no precedence tier.

For conflicting policy requirements, compare in order:

1. Effective strength: `Mandatory` > `Default` > `Advisory`.
2. Owner at equal strength: project > plugin.
3. Requirement specificity at equal strength and owner, for the same decision.

A requirement is more specific only when evidence establishes that its applicable cases form a
strict subset of the other's, through their conditions or governed objects. A path restriction can
establish such a case; file size, heading depth, or a specialist label cannot. Cross-cutting or
merely overlapping cases do not establish specificity. Compare the conflicting requirements,
not whole files or a global tier.

## Task Skill Composition

Apply task Skills within direct instructions and the applicable policy requirements resolved above.
Task Skills do not acquire Rule Strength declarations through these comparisons.

- Obey `Mandatory` policy. Task ownership or specificity cannot override it.
- Follow `Default` policy unless a task Skill explicitly prescribes an intentional alternative for
  the decision it governs in this task. Such an alternative is eligible for comparison without any
  special override metadata. Compare its owner, then its requirement specificity for that decision,
  against the Default requirement using the rules above. Only a winning alternative displaces the
  conflicting Default clause; a genuine unresolved tie uses the same stop-and-ask handling.
  Omission, examples, incidental tool choices, convenience, discovery, and invocation do not
  establish an alternative. An override must also satisfy Mandatory and every other
  still-controlling requirement.
- Adapt `Advisory` guidance to the task context rather than treating it as an absolute workflow veto.

For conflicting task methods, project-owned Skills take precedence over plugin-owned Skills. At
equal ownership, a task Skill is more specific only when its supported task cases, established by its
trigger and owned outcome, form a strict subset of the other's. Names, longer text, or specialist
labels do not establish that relation. The winner controls only the conflicting method; use the
same safe handling for unresolved ties.

Explicit project delegation may select a plugin specialist within the delegated outcome. Retain
project constraints and the delegation's permission limits.

## Conflict Warnings

- When normal execution exposes a semantic conflict—two applicable requirements that one action or
  outcome cannot satisfy under the same supported facts—include a warning in the user-facing work
  report. Do not run a separate conflict audit or preflight.
- Using only details that may be disclosed to the user, identify the conflicting requirements and
  their sources, state the precedence result, and explain the action taken or the decision
  requested.
