# Instruction Governance

Apply SmartKit Rules and Skills within the active Harness's instruction authority. Resolving precedence does not replace an action's permission requirements.

## Resolve the actual conflict

Apply compatible requirements together. When two clauses cannot both be satisfied for the same decision, compare them in this order and stop at the first difference:

| Priority | Comparison | Which requirement prevails |
| --- | --- | --- |
| 1 | Source | Direct conversation instructions > project > plugin |
| 2 | Type, at equal source | Task Skill > Rule Skill > Rule |
| 3 | Specificity, at equal source and type | The narrower applicable condition or governed object |

The type order reflects task focus: a Rule supplies general policy, a Rule Skill supplies policy for a domain or condition, and a Task Skill guides a particular task or outcome. A Rule Skill is a rule-led Skill named `rule-<domain>`; its domain or condition must limit applicability. Deferred loading alone supplies no such limit.

Determine project or plugin ownership from the canonical source and who owns its meaning. Installation, copying, or loading in a project or conversation does not change that ownership. An explicit project delegation to a plugin applies within its stated outcome and constraints.

Compare the conflicting clauses, not whole documents. A narrower condition can break a tie; merely overlapping conditions cannot. Replace only the losing requirement and retain all compatible ones. Advice and examples inform judgment without creating requirements.

If a conflict remains unresolved, report the clauses and their sources, pause affected actions, and ask the user to resolve it. Continue unrelated work when possible.

## Load guidance before it governs a decision

Use discovery descriptions and the current task to identify relevant Rules, Rule Skills, and required references. Load them before the decisions they govern; read a Rule when its applicability is uncertain.

Apply requirements only when their stated conditions hold. Read owned normative references with their entry's conditions and exceptions; independently owned policies retain their own contracts. Loading or explicitly invoking guidance expands neither applicability, task scope, nor authority.

Reuse complete applicable content already in context unless there is evidence of change or staleness. Load missing content, including after compaction, refresh affected content when needed, and honor explicit fresh-read requirements. If required content is unavailable, report the gap and pause dependent work while unrelated work continues.
