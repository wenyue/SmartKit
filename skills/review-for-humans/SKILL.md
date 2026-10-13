---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand a pull request or branch change: what changed, whether it is reasonable, whether its implementation is elegant and tasteful, and where their attention is needed. Use this Skill only when the user requests it. Review the selected scope read-only, then carry out only the effects authorized by the user's selected actions within the scope and verification rules below.

Load the necessary Skills and Rules to perform the review.

## Establish the review scope

### Choose the comparison

Identify the task's intended outcome and select the comparison below. Obtain its before-and-after evidence through available read-only Git or GitHub interfaces, such as a CLI, connector, or authenticated GitHub UI.

| Requested scope | Comparison |
| --- | --- |
| A pull request | Obtain the PR's changed files and comparison evidence, recording its base and head commit IDs. Review that fixed PR version, applying the file-level viewed-state filter below. |
| A branch, with or without an explicit base | Resolve the reviewed branch tip and a reliable comparison base; compare their merge-base with that tip, pinning both commit IDs. If the base cannot be established reliably, ask the user rather than assuming `main`. |
| Local changes, or no explicit scope | Compare the index with the current worktree, using `git diff` or equivalent evidence. |
| Selected files | Filter the applicable comparison to those files; count and report the selection rather than the full PR or branch. |

An explicit PR or branch comparison does not include local uncommitted changes unless the user requests them.

### Review local changes

The local default reviews only unstaged changes, using the index as the before version. Skip staged-only edits; for a partially staged file, review only its unstaged portion. If a staged edit is subsequently reverted in the worktree, that reversal relative to the index is an unstaged change to review. An explicit request to include staged changes or use another local comparison overrides this default. Do not include earlier commits or fall back to staged changes or the last commit when the selected comparison is empty. Exclude untracked files unless the user explicitly includes them; when included, review them as additions.

### Filter PR files

For a PR, default to skipping files marked viewed by the current authenticated GitHub viewer. Obtain the complete file-level states through an available authenticated read-only GitHub interface; GitHub GraphQL exposes them as [`PullRequestChangedFile.viewerViewedState`](https://docs.github.com/en/graphql/reference/pulls#pullrequestchangedfile). Exclude `VIEWED`; include `UNVIEWED` and `DISMISSED`, which means the file changed since it was last viewed. Complete any pagination and check that the PR's base and head remain unchanged while obtaining the file list and states, so the filter belongs to the pinned version. Current viewed states cannot establish a filter for an older PR snapshot. A PR approval, comments, or files displayed in an earlier chat are not evidence of a file's viewed state.

The user can explicitly include reviewed files, overriding that exclusion. If required viewed-state evidence is unavailable, name the missing prerequisite and pause the dependent review; ask for access to that evidence or whether to include all otherwise eligible files without the filter. Treat missing state as unknown rather than `UNVIEWED`.

### Keep a fixed snapshot and file list

Preserve this Skill's selected comparison when loading other review guidance with different scope defaults. When there is no usable `HEAD`, the requested refs or PR evidence are unavailable, or a required interface cannot be used, name the missing prerequisite and pause the dependent review.

Keep a fixed review snapshot and an ordered file list for displaying the report. Record comparison commit IDs for PRs and branches, the local comparison's before-and-after content including the index baseline, and the viewer identity and file-level states used for PR filtering. Retain the local index baseline even when an explicitly selected comparison uses another before version, so later staging can preserve existing staged work. For all review scopes, match GitHub's Files changed directory-tree order: at every directory, recursively list each subdirectory's changed files before the files directly in that directory. Use the pull request's actual tree sibling order when accessible; otherwise sort sibling directories and direct files by name. For example, `src/z/api.dart` precedes `src/a.dart`; sorting complete paths from `git diff` does not establish that order.

Skip test files entirely: do not review them or count them toward progress or modifications. Apply the scope filters before counting; skipped viewed PR files and staged-only local files receive no file reports, progress credit, or modifications. Count the remaining files before displaying the first group. Briefly identify the scope and exclusions so the reader can interpret the total. If no files require review, say so and finish without manufacturing a report or a progress fraction.

When scope, required guidance, or source evidence is unavailable, identify the missing input and its effect. Pause the dependent review rather than inventing facts, totals, or a completed assessment. A known file with incomplete evidence remains in the total; explain the gap in that file's report and use an insufficient-evidence evaluation where necessary.

## Explain each file through the problem it solves

Keep all report emoji outside bold spans, preserving emphasis on their accompanying text. When emphasizing a word, phrase, identifier, or label, keep surrounding separators and terminal punctuation outside bold; deliberately emphasized complete sentences may retain their sentence punctuation. Preserve punctuation intrinsic to code, identifiers, and paths.

Begin each file with 📄 **path** and a short overview of its responsibility and overall change. Include a source link and relevant line references when available. Explain in ordinary language what the change means for users or callers, retaining technical detail that affects the judgment.

Divide the explanation into modifications by business problem or human-understood scenario. Start by keeping related changes together. Split only when they are logically independent or cannot be explained jointly with one simple example. Methods, diff hunks, and individual implementation steps do not by themselves justify separate modifications. For example, tracking pending work, refusing new work, and waiting before closing a resource can be one modification about safely finishing work on shutdown.

Small accompanying edits, such as a comment typo, can be mentioned in the overview or omitted. Explain each localization translation file as one modification for the whole file, rather than separating its strings into several modifications.

Label modifications in the exact format `🔧 **M1** - **<modification title>**`, then M2, M3, and so on, with continuous numbering across all files and continuation groups in the same report. Keep the emoji and separator outside the bold spans, and use the same M-prefixed IDs in finding lists, suggestion lists, selections, and re-reviews.

### Assess every modification on two independent dimensions

Use the same reasoning coverage for every modification: establish what changed from before to after, its effects and supporting evidence, then judge reasonableness and elegance independently. Apply both dimensions to all kinds of changes, including fixes, features, refactors, documentation, and translations. For prose, elegance concerns clear expression and organization; for code, it concerns the mechanism and structure. Adjust the expression's length, not the assessment's coverage.

Use the fixed emoji ⚖️ for reasonableness and 🎨 for elegance in every modification, including compact modifications. Put each judgment in its own paragraph, with its emoji followed directly by the conclusion, without repeating the dimension's name. Give each dimension an explicit conclusion and a reason; the emoji identifies the dimension, not whether the judgment is favorable.

- ⚖️ **Reasonable**. The change serves the intended task; its behavior is correct and safe, its scope fits the task, and its costs are justified by the available evidence.
- ⚖️ **Unreasonable** (severity): A material defect, unnecessary scope expansion, or unjustified cost makes the change a poor choice under the task's requirements. Substitute the finding's actual severity from P0 to P3 in this label, explain the evidenced impact, and give a concrete recommendation with its advantage under the same requirements. A more elegant alternative, small optimization, or style preference alone does not meet this threshold.
- 🎨 **Elegant**. The change addresses the underlying problem at the appropriate responsibility or location, with clear structure and little unnecessary state, branching, or repetition. Explain which choices make it easy to understand and maintain.
- 🎨 **Can improve**. The behavior may be reasonable while its mechanism or expression creates avoidable complexity or repetition. Point to the concrete structure that could improve, suggest a simpler approach where supported, and explain the maintenance or clarity benefit. Distinguish that benefit from personal style preferences.
- ⚖️ **Insufficient evidence**. or 🎨 **Insufficient evidence**. Name what prevents a sound judgment on that dimension and what evidence would resolve it. Keep established facts and assumptions distinct. One dimension can have a supported conclusion while the other lacks evidence.

A reasonable change can be inelegant. An elegance concern alone is an optional improvement suggestion and does not trigger the mandatory fix-or-ignore pause. If the same structure also causes an evidenced material defect, risk, or unjustified cost, report that impact independently under reasonableness as well; that unreasonable finding follows the normal pause and repair procedure.

Assign P0–P3 only to unreasonable findings, never to a pure elegance suggestion or style preference. Use P0 for critical problems requiring immediate intervention, P1 for serious problems needing prompt correction, P2 for normal-priority problems, and P3 for lower-impact problems worth correcting. Base severity on evidenced consequences and affected conditions, not on how much code changed. For example, use ⚖️ **Unreasonable** (P1): followed by the impact and recommended repair, substituting the finding's actual severity. Bold only the judgment word; keep the severity plain in ASCII parentheses and place the ASCII colon after them.

Carry the underlying review's material findings and qualifications into the relevant modifications, including the basis of a standards or task-scope concern when that distinction matters. A readable explanation must retain limitations that could change the human reviewer's decision. Report checks actually performed and distinguish them from results merely supplied by the author.

### Choose how much to show

Use a compact explanation when the behavior change is straightforward, the affected scope is clear, and no material risk or trade-off needs elaboration. Compress only the before-and-after behavioral explanation into one short paragraph without an emoji prefix. Follow it with a separate ⚖️ judgment paragraph and a separate 🎨 judgment paragraph, each retaining its conclusion and reason. Omit the fixed Before and After labels and unhelpful code. Judge simplicity by what the reader needs to understand, not by the diff's line count: one changed line can affect exception handling or persistence.

Expand modifications involving complex mechanisms, important contracts, material risks or findings, consequential trade-offs, or key evidence gaps. Present ⏪ **Before**, then ⏩ **After**, then a separate ⚖️ reasonableness judgment paragraph, then a separate 🎨 elegance judgment paragraph, using emoji plus conclusion for both judgments. Explain the behavior before and after; a separate "consequence of not changing" field is unnecessary. Prefer short, simple actual code in the project's language, keeping only the parts that illustrate the scenario. Explain the code in plain language and preserve the behavior being compared. A simplified example must be recognizable as an illustration, not a claimed verbatim source excerpt. Omit code when it would not help, such as for prose organization.

## Display one group and handle actions

### Group files

Separate file blocks with `---` and display complete files in their established order. Finish the group after the file that brings its modification count to at least 10. Never split a file, even if it alone exceeds 10 modifications. For example, files with 3 and 8 modifications form one group of 11 modifications; the next file starts the next reply. Display the final shorter group when the scope ends.

End each group with `---` and 📊 **Progress**: **displayed files / files requiring review**, explicitly saying that the files have been displayed. Count displayed files, not modifications or conclusive judgments. Across replies, retain the snapshot, ordered file list, current displayed group's files and reviewed changes, next-unreviewed position, next modification ID, judgments, finding statuses, and outstanding elegance suggestions.

### Choose an action

Use the conversation's language for human-facing labels, summaries, action names, and questions. Localize action names and their descriptions consistently in that language, without pairing them with names in another language. Interpret natural-language selections by meaning, rather than requiring command syntax.

Modification IDs select that modification's relevant findings or suggestions. "All" covers only the current report's already displayed, outstanding modifications in the chosen dimension, including earlier groups. Clarify ambiguous, contradictory, or invalid selections before carrying out an action.

| Action | Without modification IDs | With modification IDs |
| --- | --- | --- |
| **fix** | Repair all pending, unignored unreasonable findings. | Repair only the selected pending, unignored unreasonable findings. |
| **ignore** | Ask which modifications to ignore; only explicit **ignore all** ignores every pending unreasonable finding. | Ignore the selected findings and automatically repair all remaining pending, unignored unreasonable findings. |
| **optimize** | Improve all outstanding, supported 🎨 **Can improve** suggestions. | Improve only the selected outstanding, supported elegance suggestions. |
| **pass** | Record review state for the current displayed group, then continue or finish as described below. | This action selects a whole group; clarify a selection of individual modifications before recording state. |
| **continue** | Display the next group or end an exhausted scope, retaining unimplemented elegance suggestions as advice. | This action advances the whole group; clarify a selection of individual modifications before advancing. |

**ignore** has no default, even for a lone finding. If the user has not specified which findings to ignore, ask them to identify the modifications or explicitly choose all, state that every remaining pending, unignored finding will be repaired, and wait without changes. Record ignored findings with their severity as ignored, not repaired or approved. Ignoring affects only reasonableness and leaves separately authorized elegance improvements available.

### Record a passed group

**pass** applies only to a local or PR comparison and only when no pending unreasonable findings remain. It covers the current displayed group's reviewed changes or files, including their latest displayed re-review, rather than all files in the comparison or earlier groups. It retains unimplemented elegance suggestions as advice. A branch comparison has no corresponding state-recording operation; offer ordinary **continue** there. Selecting **pass** authorizes staging or Viewed updates for this group, not a local commit, push, or PR approval.

For a local review, verify that the group's current worktree contents and relevant index entries match the retained snapshot before writing, and capture the complete current index as the write baseline. Stage only the group's displayed reviewed changes that are not already staged. Use a scoped patch when staging a whole file would include unseen or excluded changes. Preserve existing staged contents outside the authorized reviewed delta, including unrelated edits in a partially staged file, and leave the worktree unchanged. Verify that the resulting index equals the write baseline plus exactly that delta, all other entries remain unchanged, and the group's worktree contents still match the snapshot. If the snapshot is stale or the reviewed delta cannot be separated safely, pause the action, refresh and display the affected review, and obtain a new selection before staging.

For a PR review, obtain an available authenticated interface capable of marking files Viewed, and verify the viewer identity and pinned base and head immediately before writing. Mark only this group's reviewed file paths as Viewed for that viewer. Read back every selected file's `viewerViewedState` and the PR version; all selected files must be `VIEWED`, and both commit IDs must still match the reviewed snapshot before advancing. If the version changed, refresh and display the affected review before another selection; marking a newer version does not establish that version was reviewed.

If the required interface or snapshot evidence is unavailable, or a write or verification fails, pause without advancing or substituting **continue**. Report what is confirmed, failed, or still unknown, including any partial staging or Viewed updates. Inspect the current state before retrying so a lost response is not mistaken for a failed write. Only after verification succeeds, acknowledge the applicable operation and display the next group or end an exhausted scope. Recording state leaves the review snapshot, file total, and saved next-unreviewed position intact; do not reapply the unstaged or Viewed filters to remove passed files from progress.

### Make the closing choice readable

After progress, use Markdown to separate **Pending findings**, **Optional improvements**, and **Available actions**, omitting empty sections. List pending unreasonable findings by modification ID, severity, and a short impact summary. Use the exact label format `**M1** (P1): <impact summary>`, substituting the actual ID and severity; bold only the ID, keep the severity in plain ASCII parentheses, and place the ASCII colon after them. List supported elegance suggestions by modification ID, proposed improvement, and benefit. These summaries cover outstanding modifications from earlier groups as well as the current group.

Offer only the actions available under the continuation rules below, using the same short-bullet format for each action. Explain their effects and what an unqualified choice does: **fix** repairs all pending findings unless the user selects a subset; **ignore** needs a selection and automatically repairs the remaining findings, while explicitly ignoring all performs no repairs; **optimize** implements all supported outstanding suggestions unless the user selects a subset; **pass** records the current group's review state and then continues or finishes; **continue** displays the next group or ends an exhausted scope. Passing and continuing retain unimplemented suggestions as advice. When pending findings remain, say that optimization leaves them pending.

Describe **pass** using only the operation applicable to the actual comparison: for a local review, “Stage this group's reviewed changes and display the next group”; for a PR review, “Mark this group's reviewed PR files as Viewed and display the next group.” In the final group, replace “display the next group” with “end this review.” When elegance suggestions remain, say that they are retained as advice. Keep plain **continue** available alongside **pass**, and omit **pass** in branch reviews.

Keep concrete invocation syntax and numbered usage recipes out of closing menus; modification IDs belong in the finding and suggestion lists. End with one concise question asking for the applicable action and, when needed, selected modifications. If no choice remains, close without a question. The examples below illustrate the different result states; localize their wording for the conversation.

### Edit, re-review, and continue

For authorized repairs or optimizations, load the necessary guidance, limit edits to the authorized findings or suggestions, and run required checks. Optimization preserves existing supported behavior and contracts. If an action is blocked or a check fails, explain what remains and what is needed; pause without advancing.

After checks pass, re-review the revised content before moving on. Whenever reviewed content changes, refresh the snapshot and re-review every changed or affected previously reviewed part, including unexpected changes. Show updated explanations and both judgments in complete file blocks, in dedicated replies separate from unseen files. Retain modification IDs, explain the version transition, and update the file list and total when needed. Mark findings repaired or suggestions completed only after re-review confirms the result.

Use the same action rules and continuation flow after ordinary groups and dedicated re-reviews:

- **Pending unreasonable findings**: ask whether to **fix** or **ignore**, even in the final group; also offer **optimize** if supported elegance suggestions remain. Wait for the user's choice. **pass** and **continue** are unavailable; **optimize** alone neither authorizes repairs nor permits advancing.
- **No pending findings, but supported elegance suggestions remain**: offer **optimize**, **continue**, and, for a local or PR comparison, **pass**. Wait for the user's choice. Continuing resumes with the next file or closes an exhausted scope, retaining unselected suggestions as advice; passing records the group's state first.
- **Neither remains**: for a local or PR comparison, offer **pass** or **continue** and wait even in the final group, so the last group can be staged or marked Viewed. For a branch comparison, ask whether to continue and wait if files remain; close without a prompt if the scope is exhausted.

If explicit ignoring leaves no remaining repairs, resume automatically at the saved next-unreviewed position or close if the scope is exhausted, unless supported elegance suggestions remain; those still require a choice. This existing automatic continuation does not stage changes or mark PR files Viewed. Retain ignored findings and evidence gaps, and distinguish completed display from resolved findings.

## Reference report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, modifications, both reasoned judgments, and progress; use a vertical comparison only when the modification calls for expansion. These are illustrative files and snippets, not findings about a particular repository. This example is a local unstaged review containing three non-test files. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

📄 **`l10n/en.json`**

This file supplies English interface text. The changed label makes clear that the action deletes the account; all translation changes in this file are reviewed together.

🔧 **M1** - **Make the account-deletion label explicit**

The label changes from “Delete” to “Delete account,” naming the affected object.

⚖️ **Reasonable**. The label accurately describes the assumed action.

🎨 **Elegant**. Two plain words communicate the action clearly.

---

📄 **`lib/item_storage.dart`**

This file saves and deletes stored items. The change preserves the storage-box reference so deleting an item can still flush the deletion afterward.

🔧 **M2** - **Flush the deletion to the original storage box**

⏪ **Before**

```dart
await item.delete();
await item.box?.flush();
```

After deletion, `item.box` becomes null, so the flush is skipped.

⏩ **After**

```dart
final originalBox = item.box;
await item.delete();
await originalBox?.flush();
```

Saving the box reference first lets the code flush that same box after deleting the item.

⚖️ **Reasonable**. This directly repairs the promised deletion behavior with a small change. Flush failures reach the caller; flushing does not roll back the deletion, so a failed flush must not be described as a restored item.

🎨 **Elegant**. Keeping the original box reference at the deletion site directly handles the detachment mechanism without adding a separate lookup or new state elsewhere.

---

📄 **`ui/save_button.dart`**

This file handles the Save button. The change prevents repeated clicks from starting duplicate saves.

🔧 **M3** - **Refuse repeated clicks while saving**

Previously, repeated clicks could start duplicate saves; the handler now refuses another save while one is pending, and completion and cancellation both reset the pending flag correctly.

⚖️ **Reasonable**. This prevents duplicate saves within the requested scope.

🎨 **Can improve**. Both branches repeat the same flag reset; a shared completion path would make cleanup easier to maintain.

---

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending.

**Optional improvements**

- **M3**: Use a shared completion path for the flag reset to reduce duplication and make cleanup easier to maintain.

**Available actions**

- **Optimize**: Implement the optional improvement.
- **Pass**: Stage this group's reviewed changes and end this review, retaining the improvement as advice.
- **Continue**: End this review, retaining the improvement as advice.

🤖 **Would you like to optimize, pass, or continue?**

## Example closings for different results

These illustrative closings follow the file reports; they do not replace the two judgments in each modification. A complete display total does not mean findings have been resolved. The eligible examples name their local or PR scope to show the different **pass** descriptions; adapt them to the actual comparison. In a branch review, omit **pass** and close an exhausted scope without a question when no findings or suggestions remain.

### Pending findings and optional improvements

📊 **Progress**: **4/9 files displayed**.

**Pending findings**

- **M2** (P1): Closing the resource can lose unsaved data.
- **M5** (P2): The error path leaves the button disabled.

**Optional improvements**

- **M7**: Share the repeated state-reset logic to reduce maintenance omissions.

**Available actions**

- **Fix**: Repair all pending findings, or the subset you select.
- **Ignore**: Choose which findings to ignore; the remaining findings will be repaired automatically. Explicitly ignoring all performs no repairs.
- **Optimize**: Implement the optional improvements, or the subset you select; the pending findings still need attention.

🤖 **Which action would you like? Identify modifications if selecting a subset or ignoring findings. Pending findings must be handled before continuing.**

### Only pending findings, including after the final group

📊 **Progress**: **9/9 files displayed**.

**Pending findings**

- **M5** (P2): The error path leaves the button disabled.

**Available actions**

- **Fix**: Repair the pending finding.
- **Ignore**: Explicitly select the finding to ignore; it will remain recorded as ignored.

🤖 **Would you like to fix the finding or explicitly ignore it? All files have been displayed, but the finding is still pending.**

### Only optional improvements, with files remaining in a PR review

📊 **Progress**: **4/9 files displayed**. No unreasonable findings are pending.

**Optional improvements**

- **M7**: Share the state-reset logic to reduce duplication.

**Available actions**

- **Optimize**: Implement the optional improvement.
- **Pass**: Mark this group's reviewed PR files as Viewed and display the next group, retaining this improvement as advice.
- **Continue**: Display the next group, retaining this improvement as advice.

🤖 **Would you like to optimize, pass, or continue?**

### Only optional improvements, after the final group in a local review

📊 **Progress**: **9/9 files displayed**. No unreasonable findings are pending.

**Optional improvements**

- **M7**: Share the state-reset logic to reduce duplication.

**Available actions**

- **Optimize**: Implement the optional improvement.
- **Pass**: Stage this group's reviewed changes and end this review, retaining the improvement as advice.
- **Continue**: End this review, retaining the improvement as advice.

🤖 **Would you like to optimize, pass, or continue?**

### No findings or suggestions, with files remaining in a local review

📊 **Progress**: **4/9 files displayed**.

No pending findings or optional improvements were found in this group or remain from earlier groups.

**Available actions**

- **Pass**: Stage this group's reviewed changes and display the next group.
- **Continue**: Display the next group.

🤖 **Would you like to pass or continue?**

### No findings or suggestions, after the final group in a PR review

📊 **Progress**: **9/9 files displayed**.

All files have been displayed. No pending findings or optional improvements remain in the reviewed scope.

**Available actions**

- **Pass**: Mark this group's reviewed PR files as Viewed and end this review.
- **Continue**: End this review.

🤖 **Would you like to pass or continue?**
