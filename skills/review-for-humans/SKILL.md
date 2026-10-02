---
name: review-for-humans
description: Explain supplied changes file by file in a readable review report for a human reviewer.
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand what changed, whether it is reasonable, and where their attention
is needed. Use this Skill only when the user requests it. Review the supplied scope without changing
the reviewed contents.

Load the necessary Skills and Rules to perform the review.

## Establish the review scope

Identify the task's intended outcome and obtain the supplied changes with their before-and-after
evidence. Keep a fixed review snapshot and an ordered file list. Follow the user's supplied file
order; for a pull request, follow its actual Files changed order. When reviewing selected files,
count and report that selection rather than the entire pull request.

Skip test files entirely: do not review them or count them toward progress or modification items.
Count the remaining files in the supplied scope before displaying the first group. Briefly identify
the scope and exclusions so the reader can interpret the total. If no files require review, say so
and finish without manufacturing a report or a progress fraction.

When scope, order, required guidance, or source evidence is unavailable, identify the missing input
and its effect. Pause the dependent review rather than inventing facts, totals, or a completed
assessment. A known file with incomplete evidence remains in the total; explain the gap in that
file's report and use an insufficient-evidence evaluation where necessary.

## Explain each file through the problem it solves

Begin each file with **📄 File: path** and a short overview of its responsibility and overall change.
Include a source link and relevant line references when available. Explain in ordinary language
what the change means for users or callers, retaining technical detail that affects the judgment.

Divide the explanation into modification items by business problem or human-understood scenario.
Start by keeping related changes together. Split only when they are logically independent or cannot
be explained jointly with one simple example. Methods, diff hunks, and individual implementation
steps do not by themselves justify separate items. For example, tracking pending work, refusing new
work, and waiting before closing a resource can be one item about safely finishing work on shutdown.

Small accompanying edits, such as a comment typo, can be mentioned in the overview or omitted.
Explain each localization translation file as one item for the whole file, rather than separating
its strings into several items.

Label modification items **🔧 1.**, **🔧 2.**, and so on, with titles and continuous numbering
across all files and continuation groups in the same report.

For each item, present **⏪ Before**, then **⏩ After**, then **Evaluation** vertically. Explain the
behavior before and after; a separate "consequence of not changing" field is unnecessary. Prefer
short, simple actual code in the project's language, keeping only the parts that illustrate the
scenario. Explain the code in plain language and preserve the behavior being compared. A simplified
example must be recognizable as an illustration, not a claimed verbatim source excerpt. Omit the
example when the change is very simple or code would not help, such as a comment correction.

Give every item a reasoned evaluation, prefixing its label with the corresponding emoji:

- **✅ Reasonable:** it serves the intended task and its behavior and costs are justified by the
  available evidence.
- **❌ Unreasonable:** a material defect, unnecessary scope expansion, or a clearly better supported
  approach makes this change a poor choice. Give a concrete recommendation and explain why it is
  better under the same requirements. Small optimizations and style preferences alone do not meet
  this threshold.
- **⚠️ Insufficient evidence:** name what prevents a sound judgment and what evidence would resolve
  it. Separate established behavior from assumptions instead of implying approval.

Carry the underlying review's material findings and qualifications into the relevant items, including
the basis of a standards or task-scope concern when that distinction matters. A readable explanation
must retain limitations that could change the human reviewer's decision. Report checks actually
performed and distinguish them from results merely supplied by the author.

## Display one group and continue on request

Separate file blocks with `---`. Add complete files in their established order until the group's
modification-item count reaches or exceeds 10, then finish the group. Never split a file across
groups. If file A has 3 items and file B has 8, display both as one 11-item group; the next file starts
the next reply. A file with more than 10 items stays together. Display the final shorter group when
the scope ends.

End each group with `---` followed by **📊 Progress: displayed files / files requiring review**. This
measures displayed files, not modification items or a claim that every judgment is conclusive. If
files remain, explicitly prompt the user to enter `继续` to continue the review, after the progress,
then wait. When the user continues, resume with the next file rather than repeating the previous
group. When all files have been displayed, say the report is complete and retain any unresolved
evidence gaps.

Keep the snapshot, ordered file list, next-file position, next-item number, and prior judgments
available across groups. If the reviewed content changes, identify which earlier explanations or
judgments are affected and refresh them against the new snapshot before reporting progress on it.
Rebuild the file list and total when necessary, account for affected files that need to be shown
again, and make the version transition explicit so the report does not mix versions.

## Reference report

Use the following shape as a guide, adapting the detail to the user. Exact wording is
flexible; preserve the file overview, business items, vertical comparison, judgment, and progress.
These are illustrative files and snippets, not findings about a particular repository. Assume that
deleting an item detaches it from its storage box and that the task promises to flush the deletion.
The selected scope contains the following two non-test files.

**📄 File: `lib/item_storage.dart`**

This file saves and deletes stored items. The change preserves the storage-box reference so deleting
an item can still flush the deletion afterward.

**🔧 1. Flush the deletion to the original storage box**

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

**✅ Evaluation: Reasonable.** This directly repairs the promised deletion behavior with a small change.
A flush failure still needs to reach the caller; flushing does not roll back the deletion.

---

**📄 File: `l10n/en.json`**

This file supplies English interface text. The changed label makes clear that the action deletes
the account; all translation changes in this file are reviewed together.

**🔧 2. Make the account-deletion label explicit**

**⏪ Before**

```json
{"deleteAccount": "Delete"}
```

The button does not say what will be deleted.

**⏩ After**

```json
{"deleteAccount": "Delete account"}
```

The button names the affected object.

**✅ Evaluation: Reasonable.** The text accurately describes the assumed action and helps the user
understand it before clicking.

---

**📊 Progress: 2/2 files displayed.** The report is complete for this selected scope.
