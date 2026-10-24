---
name: what-changes
description: Review accumulated intended changes in a read-only scope report when the user asks to execute many edits or edits discussed far apart in the active conversation.
---

# What Changes

Before implementation, turn accumulated intended changes into a scope the user can review. Reconcile active goals, displaced ideas, and unresolved questions, then connect the proposed file changes to those outcomes.

Run this workflow on explicit invocation, or when the user asks to execute many accumulated edits or edits discussed far apart in the active conversation. Judge autonomous invocation by the intended changes, not conversation length alone. Carry out small, clear requests normally.

The review is read-only. Invocation authorizes the inspection needed for the report, not implementation or other changes.

## Reconstruct intent from the active conversation

Use the conversation and explicitly referenced source artifacts needed to understand its intended changes. Inspect repository paths read-only when that helps identify affected files or modules. Reconcile later decisions with earlier suggestions, rejected ideas, superseded plans, and completed work so the report describes what remains to be done.

Classify each item by its current status, not its age or origin:

- Include a still-active Agent suggestion among the goals even without explicit user endorsement; label it as a suggestion, not an agreed user requirement.
- Put an older unfinished, uncanceled goal in pending confirmation when its active status remains unclear.
- Use pending confirmation only when available evidence cannot settle the item's status or a material detail.

State gaps in accessible history or evidence rather than inventing a decision or path. If missing conversation history prevents a reliable scope review, carry that coverage gap into pending confirmation.

## Present goals and file changes together

Use four semantic sections in this order, with these emoji-prefixed bold labels. Omit empty sections:

1. ❓ **Pending confirmation** — Unsettled status, material details, or coverage gaps. Keep any possible file scope for an unresolved item here, rather than presenting it as a decided change.
2. 🎯 **Goals** — The active outcomes under review, including still-active Agent suggestions.
3. 🚫 **Excluded ideas** — Relevant rejected or superseded suggestions and the decisions that displaced them.
4. 📝 **Planned file changes** — Only changes that serve the listed goals.

Keep relevant verification plans and evidence limits beside the items they qualify.

For each planned file or module, explain the change and its reason together, linking it to the applicable goals. Name exact paths when evidence supports a modest affected set. At roughly 30 or more files, group by module where useful for readability and still name consequential individual files. Grouping should expose the reach of the work, not conceal it.

## Resolve open items, then confirm implementation

End the report by asking the user to resolve pending items. After each answer, update and recheck the report. Ask whether to begin implementation only when no pending items remain; if the initial report has none, end with that implementation question.

Implement only on an affirmative answer to that question. An earlier execution request does not count as the answer. Resolving a pending item alone is not implementation confirmation.

## Example report

These placeholders stand for conversation-supported goals, decisions, and paths. The example shows all four sections and an unresolved goal; omit empty sections in an actual report.

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
