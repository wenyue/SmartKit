# Project Agent Entry

## Project rules

Read every project Rule whose `Read when` condition matches the current task.

| Read when | Rule | Strength |
| --- | --- | --- |
| Always | `.agents/rules/00-self-hosting-authority.md` | `Mandatory` |
| Always | `.agents/rules/01-project-policy.md` | `Mandatory` |

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
