# Report Examples

These examples illustrate the report and closing formats defined in [Review for Humans](../SKILL.md). Consult them when calibrating presentation; the entry owns the scope, judgments, actions, and verification requirements.

## Complete report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, modifications, both reasoned judgments, and progress; use a vertical comparison only when the modification calls for expansion. These are illustrative files and snippets, not findings about a particular repository. This example is a local unstaged review containing three non-test files. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

The loopback URLs below illustrate filename-link formatting only; they are placeholders rather than generated previews. Actual reports use the shared tool's returned Markdown.

📄 **[l10n/en.json](http://127.0.0.1:47821/diff?repo=%2Fproject&path=l10n%2Fen.json&base=blob%3A1111111111111111111111111111111111111111)**

This file supplies English interface text. The changed label makes clear that the action deletes the account; all translation changes in this file are reviewed together.

🔧 **M1** - **Make the account-deletion label explicit**

The label changes from “Delete” to “Delete account,” naming the affected object.

⚖️ **Reasonable**. The label accurately describes the assumed action.

🎨 **Elegant**. Two plain words communicate the action clearly.

---

📄 **[lib/item_storage.dart](http://127.0.0.1:47821/diff?repo=%2Fproject&path=lib%2Fitem_storage.dart&base=blob%3A1111111111111111111111111111111111111111)**

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

📄 **[ui/save_button.dart](http://127.0.0.1:47821/diff?repo=%2Fproject&path=ui%2Fsave_button.dart&base=blob%3A1111111111111111111111111111111111111111)**

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

1. **Optimize**: Implement the optional improvement.
2. **Pass and finish**: Stage the remaining reviewed changes across all groups in this report and end this review, retaining the improvement as advice.
3. **Finish**: End this review without staging remaining changes, retaining the improvement as advice.

🤖 **Enter an operation number.**

## Example closings for different results

These illustrative closings follow file reports or dedicated re-reviews; they do not replace the two judgments in each modification. Localize them and use only the options available for the actual state.

### Incidental observation with a ready final group

In this illustrative local review, the selected change only adjusts export-button text. The source location below is illustrative; an actual report uses an available source link.

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending.

📌 **Incidental observations (outside this review's scope)**

**O1**: The export button stays disabled after a failed export.

- **Location**: `src/export.ts:68`.
- **Evidence and impact**: The button is disabled before export and restored only on success. When export throws, users must refresh the page to retry.
- **Relationship to this change**: The same failure path exists in the before version; the text change neither triggers nor aggravates it.
- **Recommendation**: Restore the button in a shared completion path so users can retry after success or failure.

O1 remains advice, does not block completion, and is excluded from bulk fixes or optimizations. Handling it requires a separate selection.

**Available actions**

1. **Pass and finish**: Stage the remaining reviewed changes across all groups in this report and end this review, retaining O1 as advice.
2. **Finish**: End this review without staging remaining changes, retaining O1 as advice.

🤖 **Enter an operation number.**

### Pending findings and optional improvements

📊 **Progress**: **4/9 files displayed**.

**Pending findings**

- **M2** (P1): Closing the resource can lose unsaved data.
- **M5** (P2): The error path leaves the button disabled.

**Optional improvements**

- **M7**: Share the repeated state-reset logic to reduce maintenance omissions.

**Pass and continue** and **continue** are unavailable until M2 and M5 are repaired or explicitly ignored.

**Available actions**

1. **Fix**: Repair both pending findings, or the subset you select.
2. **Ignore**: Choose which findings to ignore; other findings remain pending.
3. **Optimize**: Implement the optional improvement; the pending findings still need attention.

🤖 **Enter an operation number; include M IDs to select a subset.**

If the user replies “1, M2,” repair only M2; M5 remains pending. If the user replies “2,” clarify which findings to ignore unless the context already identifies them or the user explicitly chooses all. Operation numbers choose actions; M IDs choose their items.

If the user replies “continue,” explain: “M2 and M5 are still pending, so I cannot show the next group yet.” Reissue the numbered available actions and number-entry prompt above.

### PR repaired locally and ready for completion

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired; required checks and re-review passed. The fixes remain local. The PR target, viewer, write interfaces, and publication scope have been verified.

**Available actions**

1. **Pass and continue**: Commit and push the two fixes, verify the PR version, mark the four displayed reviewed files Viewed and verify every readback, then show the next group.
2. **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

🤖 **Enter an operation number.**

### Publication scope is not safe

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired; required checks and re-review passed.

**Pass and continue** is unavailable: pushing the current ancestry would also publish an unrelated unpushed commit. Completion first needs a separable publication scope containing only this report's authorized, checked fixes.

**Available actions**

1. **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

🤖 **Enter an operation number.**

### Resume partially completed PR recording

📊 **Progress**: **4/9 files displayed**. The selected completion's commit and push are verified. After access was restored, readback confirmed the expected PR version and viewer: two selected files are Viewed and two remain unviewed.

The selected **pass and continue** is unfinished. Ordinary **continue** is unavailable until the remaining recording and readbacks complete.

**Available actions**

1. **Pass and continue**: Resume by marking the two remaining selected files Viewed, verify all four selected files and the PR version, then show the next group. The verified commit, push, and completed marking will be reused.

🤖 **Enter an operation number.**

### Final group of a PR review

📊 **Progress**: **9/9 files displayed**. No pending findings or unpublished reviewed changes remain; the PR matches the reviewed version. Four files from earlier groups are verified Viewed; five reviewed files across the report, including files from groups advanced using continue, still await Viewed.

**Optional improvements**

- **M7**: Share the state-reset logic to reduce duplication and maintenance omissions.

**Available actions**

1. **Optimize**: Implement the optional improvement.
2. **Pass and finish**: Complete recording for all nine reviewed files across every group: mark the five remaining files Viewed, verify all nine files and the PR version, then end this review, retaining the improvement as advice.
3. **Finish**: End this review without marking the remaining files Viewed, retaining the improvement as advice.

🤖 **Enter an operation number.**
