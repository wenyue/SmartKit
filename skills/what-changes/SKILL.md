---
name: what-changes
description: Review accumulated intended changes in a read-only scope report when the user asks to execute many edits or changes across a broad scope.
---

# What Changes

Review the active conversation's accumulated intended changes immediately before implementation. Run this workflow when the user invokes it explicitly, or when the user asks to execute changes after many intended edits or edits across a broad scope have accumulated. Judge autonomous invocation by the intended changes, not conversation length alone; carry out small, clear requests normally. Produce a read-only scope report. Invocation authorizes inspection needed for the report, not implementation or other changes.

1. Reconstruct the current scope from the conversation and any explicitly referenced source artifacts needed to understand it. Inspect repository paths read-only when that helps identify affected files or modules. Reconcile later decisions with earlier suggestions, rejected ideas, superseded plans, and completed work. State any gap in accessible history or evidence instead of inventing a decision or path.
2. Classify discussion items by their current status. Put active goals in the goals section, including still-active Agent suggestions that the user has not explicitly endorsed. Put relevant rejected or superseded suggestions in the excluded ideas section. Use pending confirmation only when available evidence cannot settle the classification or a material detail. An older unfinished, uncanceled goal whose active status remains unclear belongs in pending confirmation. If inaccessible conversation history prevents a reliable scope review, explain the coverage gap there.
3. Report in four semantic sections, in this order: ❓ **Pending confirmation**, 🎯 **Goals**, 🚫 **Excluded ideas**, 📝 **Planned file changes**. Use these emoji-prefixed bold labels, translating the section names into the response language, and omit empty sections. Keep relevant verification plans and evidence limits with the items they qualify.
4. In planned file changes, list only changes that serve the goals. For each file or module, combine the planned change and its reason in one explanation, and make its relationship to the applicable goal or goals clear. Name exact paths when the expected affected set is modest and evidence supports them. At roughly 30 or more files, group by module where that makes the scope readable, while still naming consequential individual files. Mention possible file scope for an unresolved item only within pending confirmation, not as a decided change.
5. End the report by asking the user to resolve pending items or, if none remain, whether to begin implementation. After each pending answer, update and recheck the report, asking about implementation only when no items remain. Implement only on an affirmative answer to that question; an earlier execution request does not count.

## Example report

The placeholders represent conversation-supported goals, decisions, and paths. This example shows all four sections; omit empty sections in an actual report.

❓ **Pending confirmation**

- Whether an older Goal C remains active is unclear. `<possible-file>` is only potential scope.

🎯 **Goals**

- **G1**: Deliver outcome A.
- **G2**: Keep outcome B consistent with outcome A.

🚫 **Excluded ideas**

- Approach X was superseded by the later decision for G1.

📝 **Planned file changes**

| File or module | Goal | Planned change and reason |
| --- | --- | --- |
| `<file-a>` | G1 | Adjust the relevant behavior so outcome A is available. |
| `<module-b>/` (about 30 files, including consequential `<file-b>`) | G1, G2 | Update the shared behavior so outcome A works consistently with outcome B. |

Is the older Goal C still in scope?
