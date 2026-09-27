# Response Format

Apply this Rule only while composing the final response presented to a human user. Choose the
content the work calls for, then use the conventions below to make it easy to scan.

## Language

Use Simplified Chinese unless the user explicitly requests another language.

## Work Reports

- For implementation work, list the main changed files and summarize the change in one or two
  sentences.
- For reviews, put findings first in severity order and include file and line references when
  possible.
- For plans and design notes, make material trade-offs explicit.

## Response Tags

Use inline body labels for non-trivial replies. Select the labels that serve the reply and omit
empty tags; use plain prose for very small replies. Compose final replies without Markdown
headings. Use lists, tables, bold or emphasis, and code blocks where useful.

| Tag | Purpose |
| --- | --- |
| `🎯` | The user's goal. |
| `⚠️` | Material risks, constraints, prerequisites, or assumptions. |
| `✅` | Completed result, main changed files, and brief change summary. |
| `❌` | Failure or blocker and what is needed to proceed. |
| `🤖` | One user question, a small set of choices, or concrete recommended next steps with an execution question. |

Preferred order: `🎯 → ⚠️ → ✅ or ❌ → 🤖`. For a review that must begin with findings, omit a
goal preface; the preferred order does not move those findings behind optional context.

## Tag Rules

Start each tagged passage with its icon and associated text in the same paragraph. When `🎯` is
present, put it first and include only the goal statement. Use `⚠️` only for meaningful information,
with no more than three items. When reporting a result in a tagged reply, choose exactly one of
`✅` or `❌`.

### When the user needs to choose

Use `🤖` for needed input or recommended follow-ups awaiting user choice. When proposing actions,
ask whether to execute them. Execution remains subject to existing authorization and the active
workflow; complete already-authorized necessary work without renewed confirmation.

When a material unresolved `⚠️` calls for action, recommend concrete next steps under `🤖`. If
missing facts prevent a sound recommendation, ask for the specific input needed. Informational or
resolved caveats need no follow-up proposal.

Put `🤖` last and end the reply after asking for input.
