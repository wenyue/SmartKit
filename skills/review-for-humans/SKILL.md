---
name: review-for-humans
description: Review pull requests and branch changes file by file for humans; default to the current worktree's net uncommitted changes.
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand a pull request or branch change: what changed, whether it is reasonable, whether its implementation is elegant and tasteful, and where their attention is needed. Use this Skill only when the user requests it. Review the selected scope read-only; change the reviewed contents only when the user authorizes repairs or elegance improvements through the actions below.

Load the necessary Skills and Rules to perform the review.

## Establish the review scope

Identify the task's intended outcome and select the comparison below. Obtain its before-and-after evidence through available read-only Git or GitHub interfaces, such as a CLI or connector.

| Requested scope | Comparison |
| --- | --- |
| A pull request | Obtain the PR's changed files and comparison evidence, recording its base and head commit IDs. Review that fixed PR version. |
| A branch, with or without an explicit base | Resolve the reviewed branch tip and a reliable comparison base; compare their merge-base with that tip, pinning both commit IDs. If the base cannot be established reliably, ask the user rather than assuming `main`. |
| No explicit scope | Compare the current worktree with the current branch's `HEAD`, using `git diff HEAD` or equivalent evidence. |
| Selected files | Filter the applicable comparison to those files; count and report the selection rather than the full PR or branch. |

The default comparison reviews the combined net effect of staged and unstaged changes, displaying each file once. It intentionally omits changes that cancel between the index and worktree: if staged content is subsequently reverted in the worktree to `HEAD`, no net change remains to review. Do not separately review index versions, include earlier commits, or fall back to the last commit when the comparison is empty. Exclude untracked files unless the user explicitly includes them; when included, review them as additions.

An explicit PR or branch comparison does not include local uncommitted changes unless the user requests them. Preserve this Skill's selected comparison when loading other review guidance with different scope defaults. When there is no usable `HEAD`, the requested refs or PR evidence are unavailable, or a required interface cannot be used, name the missing prerequisite and pause the dependent review.

Keep a fixed review snapshot, recording the comparison commits and the reviewed worktree content where applicable, and an ordered file list for displaying the report. For all review scopes, match GitHub's Files changed directory-tree order: at every directory, recursively list each subdirectory's changed files before the files directly in that directory. Use the pull request's actual tree sibling order when accessible; otherwise sort sibling directories and direct files by name. For example, `src/z/api.dart` precedes `src/a.dart`; sorting complete paths from `git diff` does not establish that order.

Skip test files entirely: do not review them or count them toward progress or modification items. Count the remaining files in the supplied scope before displaying the first group. Briefly identify the scope and exclusions so the reader can interpret the total. If no files require review, say so and finish without manufacturing a report or a progress fraction.

When scope, required guidance, or source evidence is unavailable, identify the missing input and its effect. Pause the dependent review rather than inventing facts, totals, or a completed assessment. A known file with incomplete evidence remains in the total; explain the gap in that file's report and use an insufficient-evidence evaluation where necessary.

## Explain each file through the problem it solves

Begin each file with **📄 File: path** and a short overview of its responsibility and overall change. Include a source link and relevant line references when available. Explain in ordinary language what the change means for users or callers, retaining technical detail that affects the judgment.

Divide the explanation into modification items by business problem or human-understood scenario. Start by keeping related changes together. Split only when they are logically independent or cannot be explained jointly with one simple example. Methods, diff hunks, and individual implementation steps do not by themselves justify separate items. For example, tracking pending work, refusing new work, and waiting before closing a resource can be one item about safely finishing work on shutdown.

Small accompanying edits, such as a comment typo, can be mentioned in the overview or omitted. Explain each localization translation file as one item for the whole file, rather than separating its strings into several items.

Label modification items **🔧 1.**, **🔧 2.**, and so on, with titles and continuous numbering across all files and continuation groups in the same report.

### Assess every item on two independent dimensions

Use the same reasoning coverage for every modification item: establish what changed from before to after, its effects and supporting evidence, then judge reasonableness and elegance independently. Apply both dimensions to all kinds of changes, including fixes, features, refactors, documentation, and translations. For prose, elegance concerns clear expression and organization; for code, it concerns the mechanism and structure. Adjust the expression's length, not the assessment's coverage.

Use the fixed emoji **⚖️** for reasonableness and **🎨** for elegance in every item, including a single-sentence item. Display each judgment as its emoji followed directly by the conclusion, without repeating the dimension's name. Give each dimension an explicit conclusion and a reason; the emoji identifies the dimension, not whether the judgment is favorable.

- **⚖️ Reasonable.** The change serves the intended task; its behavior is correct and safe, its scope fits the task, and its costs are justified by the available evidence.
- **⚖️ Unreasonable.** A material defect, unnecessary scope expansion, or unjustified cost makes the change a poor choice under the task's requirements. Label each finding with a severity from P0 to P3, explain the evidenced impact, and give a concrete recommendation with its advantage under the same requirements. A more elegant alternative, small optimization, or style preference alone does not meet this threshold.
- **🎨 Elegant.** The change addresses the underlying problem at the appropriate responsibility or location, with clear structure and little unnecessary state, branching, or repetition. Explain which choices make it easy to understand and maintain.
- **🎨 Can improve.** The behavior may be reasonable while its mechanism or expression creates avoidable complexity or repetition. Point to the concrete structure that could improve, suggest a simpler approach where supported, and explain the maintenance or clarity benefit. Distinguish that benefit from personal style preferences.
- **⚖️ Insufficient evidence.** or **🎨 Insufficient evidence.** Name what prevents a sound judgment on that dimension and what evidence would resolve it. Keep established facts and assumptions distinct. One dimension can have a supported conclusion while the other lacks evidence.

A reasonable change can be inelegant. An elegance concern alone is an optional improvement suggestion and does not trigger the mandatory fix-or-ignore pause. If the same structure also causes an evidenced material defect, risk, or unjustified cost, report that impact independently under reasonableness as well; that unreasonable finding follows the normal pause and repair procedure.

Assign P0–P3 only to unreasonable findings, never to a pure elegance suggestion or style preference. Use P0 for critical problems requiring immediate intervention, P1 for serious problems needing prompt correction, P2 for normal-priority problems, and P3 for lower-impact problems worth correcting. Base severity on evidenced consequences and affected conditions, not on how much code changed. For example: **⚖️ Unreasonable (P1).** followed by the impact and recommended repair.

Carry the underlying review's material findings and qualifications into the relevant items, including the basis of a standards or task-scope concern when that distinction matters. A readable explanation must retain limitations that could change the human reviewer's decision. Report checks actually performed and distinguish them from results merely supplied by the author.

### Choose how much to show

Use a compact explanation when the behavior change is straightforward, the affected scope is clear, and no material risk or trade-off needs elaboration. In one or two natural sentences, explain the change and include both emoji-marked judgments with their reasons. Omit the fixed Before, After, Reasonableness, and Elegance sections and unhelpful code. Judge simplicity by what the reader needs to understand, not by the diff's line count: one changed line can affect exception handling or persistence.

Expand items involving complex mechanisms, important contracts, material risks or findings, consequential trade-offs, or key evidence gaps. Present **⏪ Before**, then **⏩ After**, then the **⚖️** reasonableness judgment, then the **🎨** elegance judgment vertically, using emoji plus conclusion for both judgment labels. Explain the behavior before and after; a separate "consequence of not changing" field is unnecessary. Prefer short, simple actual code in the project's language, keeping only the parts that illustrate the scenario. Explain the code in plain language and preserve the behavior being compared. A simplified example must be recognizable as an illustration, not a claimed verbatim source excerpt. Omit code when it would not help, such as for prose organization.

## Display one group and handle actions

### Group files

Separate file blocks with `---` and display complete files in their established order. Finish the group after the file that brings its modification-item count to at least 10. Never split a file, even if it alone exceeds 10 items. For example, files with 3 and 8 items form one 11-item group; the next file starts the next reply. Display the final shorter group when the scope ends.

End each group with `---` and **📊 Progress: displayed files / files requiring review**, explicitly saying that the files have been displayed. Count displayed files, not items or conclusive judgments. Across replies, retain the snapshot, ordered file list, next-unreviewed position, next-item number, judgments, finding statuses, and outstanding elegance suggestions.

### Choose an action

Use the conversation's language for human-facing labels, summaries, action names, and questions. In a Chinese conversation, name the actions **修复**, **忽略**, **优化**, and **继续**; these have the same meanings as **fix**, **ignore**, **optimize**, and **continue** below. Interpret natural-language selections by meaning, rather than requiring command syntax.

Item numbers select that item's relevant findings or suggestions. "All" covers only the current report's already displayed, outstanding items in the chosen dimension, including earlier groups. Clarify ambiguous, contradictory, or invalid selections before editing.

| Action | Without item numbers | With item numbers |
| --- | --- | --- |
| **fix** | Repair all pending, unignored unreasonable findings. | Repair only the selected pending, unignored unreasonable findings. |
| **ignore** | Ask which items to ignore; only explicit **ignore all** ignores every pending unreasonable finding. | Ignore the selected findings and automatically repair all remaining pending, unignored unreasonable findings. |
| **optimize** | Improve all outstanding, supported **🎨 Can improve** suggestions. | Improve only the selected outstanding, supported elegance suggestions. |

**ignore** has no default, even for a lone finding. If the user has not specified which findings to ignore, ask them to identify the items or explicitly choose all, state that every remaining pending, unignored finding will be repaired, and wait without changes. Record ignored findings with their severity as ignored, not repaired or approved. Ignoring affects only reasonableness and leaves separately authorized elegance improvements available.

### Make the closing choice readable

After progress, use Markdown to separate **Pending findings**, **Optional improvements**, and **Available actions**, omitting empty sections. List pending unreasonable findings by item number, severity, and a short impact summary. List supported elegance suggestions by item number, proposed improvement, and benefit. These summaries cover outstanding items from earlier groups as well as the current group.

Offer only the actions available under the continuation rules below. Explain their effects in short bullets, including what an unqualified choice does: **fix** repairs all pending findings unless the user selects a subset; **ignore** needs a selection and automatically repairs the remaining findings, while explicitly ignoring all performs no repairs; **optimize** implements all supported outstanding suggestions unless the user selects a subset; **continue** displays the next group or ends an exhausted scope, retaining unimplemented suggestions as advice. When pending findings remain, say that optimization leaves them pending.

Keep concrete invocation syntax and numbered usage recipes out of closing menus; item numbers belong in the finding and suggestion lists. End with one concise question asking for the applicable action and, when needed, selected items. If no choice remains, close without a question. The examples below illustrate the different result states; localize their wording for the conversation.

### Edit, re-review, and continue

For authorized repairs or optimizations, load the necessary guidance, limit edits to the authorized findings or suggestions, and run required checks. Optimization preserves existing supported behavior and contracts. If an action is blocked or a check fails, explain what remains and what is needed; pause without advancing.

After checks pass, re-review the revised content before moving on. Whenever reviewed content changes, refresh the snapshot and re-review every changed or affected previously reviewed part, including unexpected changes. Show updated explanations and both judgments in complete file blocks, in dedicated replies separate from unseen files. Retain item numbers, explain the version transition, and update the file list and total when needed. Mark findings repaired or suggestions completed only after re-review confirms the result.

Use the same action rules and continuation flow after ordinary groups and dedicated re-reviews:

- **Pending unreasonable findings:** ask whether to **fix** or **ignore**, even in the final group; also offer **optimize** if supported elegance suggestions remain. Wait for the user's choice. **continue** is unavailable; **optimize** alone neither authorizes repairs nor permits advancing.
- **No pending findings, but supported elegance suggestions remain:** ask whether to **optimize** or **continue**. Wait for the user's choice. Continuing resumes with the next file or closes an exhausted scope, retaining unselected suggestions as advice.
- **Neither remains:** ask whether to continue and wait if files remain; close without a prompt if the scope is exhausted.

If explicit ignoring leaves no remaining repairs, resume automatically at the saved next-unreviewed position or close if the scope is exhausted, unless supported elegance suggestions remain; those still require a choice. Retain ignored findings and evidence gaps, and distinguish completed display from resolved findings.

## Reference report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, business items, both reasoned judgments, and progress; use a vertical comparison only when the item calls for expansion. These are illustrative files and snippets, not findings about a particular repository. The selected scope contains three non-test files. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

**📄 File: `l10n/en.json`**

This file supplies English interface text. The changed label makes clear that the action deletes the account; all translation changes in this file are reviewed together.

**🔧 1. Make the account-deletion label explicit**

Changing “Delete” to “Delete account” names the affected object. **⚖️ Reasonable,** because the label accurately describes the assumed action; **🎨 Elegant,** because two plain words communicate the action clearly.

---

**📄 File: `lib/item_storage.dart`**

This file saves and deletes stored items. The change preserves the storage-box reference so deleting an item can still flush the deletion afterward.

**🔧 2. Flush the deletion to the original storage box**

**⏪ Before**

```dart
await item.delete();
await item.box?.flush();
```

After deletion, `item.box` becomes null, so the flush is skipped.

**⏩ After**

```dart
final originalBox = item.box;
await item.delete();
await originalBox?.flush();
```

Saving the box reference first lets the code flush that same box after deleting the item.

**⚖️ Reasonable.** This directly repairs the promised deletion behavior with a small change. Flush failures reach the caller; flushing does not roll back the deletion, so a failed flush must not be described as a restored item.

**🎨 Elegant.** Keeping the original box reference at the deletion site directly handles the detachment mechanism without adding a separate lookup or new state elsewhere.

---

**📄 File: `ui/save_button.dart`**

This file handles the Save button. The change prevents repeated clicks from starting duplicate saves.

**🔧 3. Refuse repeated clicks while saving**

The handler now returns while a save is pending; completion and cancellation both reset the pending flag correctly. **⚖️ Reasonable,** because this prevents duplicate saves within the requested scope; **🎨 Can improve,** because both branches repeat the same flag reset, which a shared completion path would make easier to maintain.

---

**📊 Progress: 3/3 files displayed.** No unreasonable findings are pending.

**Optional improvements**

- **#3:** Use a shared completion path for the flag reset to reduce duplication and make cleanup easier to maintain.

**Available actions**

- **Optimize:** Implement the optional improvement.
- **Continue:** End this review, retaining the improvement as advice.

**🤖 Would you like to optimize or continue?**

## Example closings for different results

These illustrative closings follow the file reports; they do not replace the two judgments in each item. A complete display total does not mean findings have been resolved.

### Pending findings and optional improvements

**📊 Progress: 4/9 files displayed.**

**Pending findings**

- **#2 · P1:** Closing the resource can lose unsaved data.
- **#5 · P2:** The error path leaves the button disabled.

**Optional improvements**

- **#7:** Share the repeated state-reset logic to reduce maintenance omissions.

**Available actions**

- **Fix:** Repair all pending findings, or the subset you select.
- **Ignore:** Choose which findings to ignore; the remaining findings will be repaired automatically. Explicitly ignoring all performs no repairs.
- **Optimize:** Implement the optional improvements, or the subset you select; the pending findings still need attention.

**🤖 Which action would you like? Identify items if selecting a subset or ignoring findings. Pending findings must be handled before continuing.**

### Only pending findings, including after the final group

**📊 Progress: 9/9 files displayed.**

**Pending findings**

- **#5 · P2:** The error path leaves the button disabled.

**Available actions**

- **Fix:** Repair the pending finding.
- **Ignore:** Explicitly select the finding to ignore; it will remain recorded as ignored.

**🤖 Would you like to fix the finding or explicitly ignore it? All files have been displayed, but the finding is still pending.**

### Only optional improvements, with files remaining

**📊 Progress: 4/9 files displayed.** No unreasonable findings are pending.

**Optional improvements**

- **#7:** Share the state-reset logic to reduce duplication.

**Available actions**

- **Optimize:** Implement the optional improvement.
- **Continue:** Display the next group, retaining this improvement as advice.

**🤖 Would you like to optimize or continue?**

### Only optional improvements, after the final group

**📊 Progress: 9/9 files displayed.** No unreasonable findings are pending.

**Optional improvements**

- **#7:** Share the state-reset logic to reduce duplication.

**Available actions**

- **Optimize:** Implement the optional improvement.
- **Continue:** End this review, retaining the improvement as advice.

**🤖 Would you like to optimize or continue?**

### No findings or suggestions, with files remaining

**📊 Progress: 4/9 files displayed.**

No pending findings or optional improvements were found in this group or remain from earlier groups.

**🤖 Would you like to continue with the next group?**

### No findings or suggestions, after the final group

**📊 Progress: 9/9 files displayed.**

The review is complete. No pending findings or optional improvements remain in the reviewed scope.
