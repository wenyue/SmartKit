# Response Format

Strength: `Default`

Scope: Language, tag protocol, formatting, and work reporting in final responses presented to
human users.

## Applicability

- Apply this Rule only while composing the final response presented to a human user. Internal
  reasoning and all intermediate or non-final work are outside its scope.

## Language

- Use Simplified Chinese for all user-facing text unless the user explicitly requests another
  language.

## Response Tags

Use these inline body labels for non-trivial replies. Omit empty tags and use plain prose for very
small replies. Compose final replies without Markdown headings; use lists, tables, bold or emphasis,
and code blocks where useful.

| Tag | Purpose |
| --- | --- |
| `🎯` | The user's goal. |
| `⚠️` | Material risks, constraints, prerequisites, or assumptions. |
| `✅` | Completed result, main changed files, and brief change summary. |
| `❌` | Failure or blocker and what is needed to proceed. |
| `🤖` | One user question, a small set of choices, or concrete recommended next steps with an execution question. |

Preferred order: `🎯 → ⚠️ → ✅ or ❌ → 🤖`.

## Tag Rules

- Start each tagged passage with its icon and associated text in the same paragraph.
- When present, `🎯` comes first and contains only the goal statement.
- Use `⚠️` only for meaningful information and keep it to three items or fewer.
- When reporting a result, choose exactly one of `✅` or `❌`.
- Use `🤖` for recommended follow-ups awaiting user choice, and ask whether to execute them.
  Execution remains subject to existing authorization and the active workflow; complete
  already-authorized necessary work without renewed confirmation.
- When a material unresolved `⚠️` calls for action, recommend concrete next steps under `🤖`.
  If missing facts prevent a sound recommendation, ask for the specific input needed. Informational
  or resolved caveats need no follow-up proposal.
- `🤖` is terminal. Stop after asking for input.

## Work Reports

- For implementation work, list the main changed files and summarize the change in one or two
  sentences.
- For reviews, put findings first in severity order and include file and line references when
  possible.
- For plans and design notes, make material trade-offs explicit.
