## Project rules

At the start of every task, read every project Rule matching `.agents/rules/0*.md`; any `Read when`
text shown for those Rules is metadata and does not narrow this unconditional load. Read any other
Rule listed below only when its `Read when` condition matches the task.

If a hook injects a packaged copy of a project Rule already loaded from this checkout and the copies
differ, use the checkout copy for that Rule. Resolve all other Rule conflicts under normal SmartKit
precedence.

| Read when | Rule | Strength |
| --- | --- | --- |
{{project_rule_rows}}

Apply SmartKit plugin Rules for shared strength and precedence. Keep project Rule policy in the
files listed above.
