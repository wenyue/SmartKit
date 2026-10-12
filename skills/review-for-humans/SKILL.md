---
name: review-for-humans
description: Explain supplied changes file by file in a readable review report for a human reviewer.
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand what changed, whether it is reasonable, whether its implementation is elegant and tasteful, and where their attention is needed. Use this Skill only when the user requests it. Review the supplied scope read-only; change the reviewed contents only when the user explicitly chooses repairs as described below.

Load the necessary Skills and Rules to perform the review. Write the human report, including labels and action prompts, in the response language required by the conversation; English labels below specify their meaning.

## Establish the review scope

Identify the task's intended outcome and obtain the supplied changes with their before-and-after evidence. Keep a fixed review snapshot and an ordered file list for displaying the report. For all review scopes, match GitHub's Files changed directory-tree order: at every directory, recursively list each subdirectory's changed files before the files directly in that directory. Use the pull request's actual tree sibling order when accessible; otherwise sort sibling directories and direct files by name. For example, `src/z/api.dart` precedes `src/a.dart`; sorting complete paths from `git diff` does not establish that order. When reviewing selected files, count and report that selection rather than the entire pull request.

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

A reasonable change can be inelegant. An elegance concern alone is advice and does not trigger the mandatory fix-or-ignore pause. If the same structure also causes an evidenced material defect, risk, or unjustified cost, report that impact under reasonableness as well; that unreasonable finding follows the normal pause and repair procedure.

Use P0 for critical problems requiring immediate intervention, P1 for serious problems needing prompt correction, P2 for normal-priority problems, and P3 for lower-impact problems worth correcting. Base severity on evidenced consequences and affected conditions, not on how much code changed. For example: **⚖️ Unreasonable (P1).** followed by the impact and recommended repair.

Carry the underlying review's material findings and qualifications into the relevant items, including the basis of a standards or task-scope concern when that distinction matters. A readable explanation must retain limitations that could change the human reviewer's decision. Report checks actually performed and distinguish them from results merely supplied by the author.

### Choose how much to show

Use a compact explanation when the behavior change is straightforward, the affected scope is clear, and no material risk or trade-off needs elaboration. In one or two natural sentences, explain the change and include both emoji-marked judgments with their reasons. Omit the fixed Before, After, Reasonableness, and Elegance sections and unhelpful code. Judge simplicity by what the reader needs to understand, not by the diff's line count: one changed line can affect exception handling or persistence.

Expand items involving complex mechanisms, important contracts, material risks or findings, consequential trade-offs, or key evidence gaps. Present **⏪ Before**, then **⏩ After**, then the **⚖️** reasonableness judgment, then the **🎨** elegance judgment vertically, using emoji plus conclusion for both judgment labels. Explain the behavior before and after; a separate "consequence of not changing" field is unnecessary. Prefer short, simple actual code in the project's language, keeping only the parts that illustrate the scenario. Explain the code in plain language and preserve the behavior being compared. A simplified example must be recognizable as an illustration, not a claimed verbatim source excerpt. Omit code when it would not help, such as for prose organization.

## Display one group and handle findings

Separate file blocks with `---`. Add complete files in their established order until the group's modification-item count reaches or exceeds 10, then finish the group. Never split a file across groups. If file A has 3 items and file B has 8, display both as one 11-item group; the next file starts the next reply. A file with more than 10 items stays together. Display the final shorter group when the scope ends.

End each group with `---` followed by **📊 Progress: displayed files / files requiring review**. This measures displayed files, not modification items or conclusive judgments. Keep the snapshot, ordered file list, next-unreviewed position, next-item number, judgments, and finding status across replies.

When unreasonable findings are pending, list their item numbers and severities after progress. End with a choice between **fix** and **ignore**, then wait, even in the final group. The final sentence must require item numbers for ignoring when multiple items are pending; a lone item needs no number. Clarify ambiguous selections rather than ignoring every item. A plain continue reply leaves this choice unresolved.

**Fix** authorizes repairs of pending, unignored findings within applicable authority and constraints. Load the necessary guidance, limit changes to resolving those findings, and run the required checks. After checks pass, follow the re-review procedure below; mark findings repaired only when re-review confirms resolution. If repair is blocked or a check fails, explain what remains and what is needed, and pause without advancing.

**Ignore** leaves the selected items unchanged and records their findings and severity as ignored, not repaired or approved. If other items remain pending, offer the remaining choice and wait. Once none remain, resume at the saved next-unreviewed position or close if the scope is exhausted.

Whenever reviewed content changes, refresh the snapshot and re-review every previously reviewed part modified or affected by that change, including changes beyond the original findings. Display updated explanations and judgments in complete file blocks, in replies dedicated to the re-review and separate from not-yet-reviewed files. Repairs create revised content that deserves the human reviewer's attention before moving on. Preserve existing item numbers, make the version transition explicit, and rebuild the file list and total when necessary. Re-review findings use the same fix-or-ignore choice; affected parts must be re-reviewed and their pending findings repaired or explicitly ignored before advancing.

When no unreasonable findings are pending and files remain, end an ordinary group with a **continue** prompt and wait; resume with the next file on that reply. Apply the same pause after a fix's dedicated re-review: show its result, prompt for **continue**, and wait before reviewing remaining files. Ignoring resumes automatically as described above. When all files have been displayed and no unreasonable findings are pending, close without a continuation prompt. Distinguish completed display from resolved findings and retain ignored findings and evidence gaps.

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

**📊 Progress: 3/3 files displayed.** The report is complete for this selected scope. Item 3's elegance suggestion does not create an unreasonable finding or a fix-or-ignore pause.
