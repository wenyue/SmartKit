# Project Agent Entry

## Project rules

At the start of every task, read every project Rule matching `.agents/rules/0*.md`; any `Read when`
text shown for those Rules is metadata and does not narrow this unconditional load. Read any other
Rule listed below only when its `Read when` condition matches the task.

If a hook injects a packaged copy of a project Rule already loaded from this checkout and the copies
differ, use the checkout copy for that Rule. Resolve all other Rule conflicts under normal SmartKit
precedence.

| Read when | Rule | Strength |
| --- | --- | --- |
| Project-owned generated, delivered, or installed surfaces, setup-managed state, current-contract removal, public exposure, or verification of those changes | `.agents/rules/00-project-policy.md` | `Mandatory` |

Apply SmartKit plugin Rules for shared strength and precedence. Keep project Rule policy in the
files listed above.

## Agent skills

### Issue tracker

Issues and specifications are tracked in this repository's GitHub Issues. See
`docs/agents/issue-tracker.md`.

### Triage labels

Use the five default canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain context

`docs/agents/domain.md` is a nonnormative explanatory guide to repository domain context, while
accepted ADRs retain their separate decision authority.

For unfamiliar repository language in direct user communication only, optionally consult
`CONTEXT-MAP.md` as a nonnormative wording aid.
