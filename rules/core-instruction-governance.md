# Instruction Governance

All SmartKit Rules and Skills use the precedence below within the active Harness's instruction
authority. Every action must also satisfy its permission requirements.

## Resolve conflicting requirements

Apply all compatible requirements. When two requirements cannot both be satisfied for the same
decision, compare them in this order, stopping at the first difference:

1. **Source:** direct conversation instructions > project > plugin.
2. **Type, at equal source:** Task Skill > Rule Skill > Rule.
3. **Specificity, at equal source and type:** the requirement with narrower applicable conditions
   or governed objects takes precedence.

The type order represents increasing task focus: Rules provide general policy; Rule Skills provide
policy for a domain or condition; Task Skills guide a particular task or outcome. A Rule Skill is a
rule-led Skill named `rule-<domain>`. Its domain or condition must limit applicability; deferred
loading alone supplies no such limit.

Establish project or plugin ownership from the canonical source and who owns its meaning.
Installing, copying, or loading a plugin artifact in a project or conversation leaves that ownership
unchanged. Explicit project delegation to a plugin applies within its stated outcome and constraints.

Compare the actual conflicting clauses. A narrower condition can resolve a tie; merely overlapping
conditions cannot. The winner replaces only the conflicting requirement; all compatible requirements
remain in force. Advice and examples support judgment rather than creating requirements.

If a conflict remains unresolved, report the conflicting requirements and their sources, pause
affected actions, and ask the user to resolve it. Unrelated work may continue.

## Load applicable guidance

Use discovery descriptions and the current task to load relevant Rules, Rule Skills, and required
references before the decisions they govern. Read a Rule when its applicability is uncertain.
Apply requirements when their stated conditions hold. Apply owned normative references together
with their entry's conditions and exceptions; independently owned policies retain their own
contracts. Loading or explicit invocation does not expand applicability, task scope, or authority.

Reuse complete applicable content already in context unless there is evidence of change or
staleness. Load missing content, including after compaction, refresh affected content when needed,
and honor explicit fresh-read requirements. If required content is unavailable, report it and pause
dependent work; unrelated work may continue.
