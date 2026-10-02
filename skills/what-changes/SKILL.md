---
name: what-changes
description: Review accumulated intended changes in a read-only scope report when the user asks to execute many edits or edits discussed far apart in the active conversation.
---

# What Changes

Turn the active conversation's accumulated intended changes into a scope the user can review
immediately before implementation. Reconcile what is still intended, what has been set aside, and
what remains unclear; show how the proposed file changes serve that scope.

Run this workflow on explicit invocation, or when the user asks to execute many accumulated edits
or edits discussed far apart in the active conversation. Judge autonomous invocation by the intended
changes, not conversation length alone. Carry out small, clear requests normally.

The review is read-only. Invocation authorizes the inspection needed for the report, not
implementation or other changes.

## Reconstruct the Current Intent

Use the conversation and explicitly referenced source artifacts needed to understand its intended
changes. Inspect repository paths read-only when that helps identify affected files or modules.
Reconcile later decisions with earlier suggestions, rejected ideas, superseded plans, and completed
work so the report describes what remains to be done.

Distinguish an item's status from its age or origin. A still-active Agent suggestion belongs among
the goals even if the user has not explicitly endorsed it; identify it as a suggestion rather than
an agreed user requirement. An older unfinished, uncanceled goal belongs in pending confirmation
when its active status remains unclear. Put items there only when available evidence cannot settle
their status or a material detail.

State gaps in accessible history or evidence rather than inventing a decision or path. If missing
conversation history prevents a reliable scope review, carry that coverage gap into pending
confirmation.

## Present a Reviewable Scope

Use four semantic sections in this order, with these emoji-prefixed bold labels. Omit empty sections:

1. ❓ **Pending confirmation** — Unsettled status, material details, or coverage gaps. Keep any
   possible file scope for an unresolved item here, rather than presenting it as a decided change.
2. 🎯 **Goals** — The active outcomes under review, including still-active Agent suggestions.
3. 🚫 **Excluded ideas** — Relevant rejected or superseded suggestions and the decisions that
   displaced them.
4. 📝 **Planned file changes** — Only changes that serve the listed goals.

Keep relevant verification plans and evidence limits beside the items they qualify.

For each planned file or module, combine what will change and why in one explanation, making its
relationship to the applicable goal or goals clear. Name exact paths when the expected affected
set is modest and evidence supports them. At roughly 30 or more files, group by module where that
makes the scope readable, while still naming consequential individual files. Grouping should help
the user judge the changes, not hide their reach.

## Resolve Scope Before Asking to Implement

End the report by asking the user to resolve pending items. After each answer, update and recheck
the report. Ask whether to begin implementation only when no pending items remain; if the initial
report has none, end with that implementation question.

Implement only on an affirmative answer to that question. An earlier execution request does not
count as the answer. Resolving a pending item alone is not implementation confirmation.

## Example Report

These placeholders stand for conversation-supported goals, decisions, and paths. The example shows
all four sections and an unresolved goal; omit empty sections in an actual report.

❓ **Pending confirmation**

- Whether an older Goal C remains active is unclear. `<possible-file>` is only potential scope.

🎯 **Goals**

- **G1**: Deliver outcome A.
- **G2** (still-active Agent suggestion): Keep outcome B consistent with outcome A.

🚫 **Excluded ideas**

- Approach X was superseded by the later decision for G1.

📝 **Planned file changes**

| File or module | Goal | Planned change and reason |
| --- | --- | --- |
| `<file-a>` | G1 | Adjust the relevant behavior so outcome A is available. |
| `<module-b>/` (about 30 files, including consequential `<file-b>`) | G1, G2 | Update the shared behavior so outcome A works consistently with outcome B. |

Is the older Goal C still in scope?
