# Report Examples

These examples illustrate the report and closing formats defined in [Review for Humans](../SKILL.md). Consult them when calibrating presentation; the entry owns the scope, judgments, actions, and verification requirements.

## Complete report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, modifications, both reasoned judgments, and progress; use a vertical comparison only when the modification calls for expansion. These are illustrative files and snippets, not findings about a particular repository. This example is a local unstaged review containing three non-test files. The full branch inventory also contains their tests; all changes were introduced in this conversation and required checks passed. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

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

- **A**. **Optimize**: Implement the optional improvement.
- **B**. **Pass and finish**: Commit all branch changes, including the three reviewed files and their tests, verify the result, and end this review without pushing, retaining the improvement as advice.
- **C**. **Finish**: End this review without committing, retaining the improvement as advice.

🤖 **Enter an operation letter.**

## Example closings for different results

These illustrative closings follow file reports or dedicated re-reviews; they do not replace the two judgments in each modification. Localize them and use only the options available for the actual state.

### Incidental observation with a ready final group

In this illustrative local review, the selected change only adjusts export-button text. The branch inventory contains only the three text files changed in this conversation; required checks passed. The source location below is illustrative; an actual report uses an available source link.

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending.

📌 **Incidental observations (outside this review's scope)**

**O1**: The export button stays disabled after a failed export.

- **Location**: `src/export.ts:68`.
- **Evidence and impact**: The button is disabled before export and restored only on success. When export throws, users must refresh the page to retry.
- **Relationship to this change**: The same failure path exists in the before version; the text change neither triggers nor aggravates it.
- **Recommendation**: Restore the button in a shared completion path so users can retry after success or failure.

O1 remains advice, does not block completion, and is excluded from bulk fixes or optimizations. Handling it requires a separate selection.

**Available actions**

- **A**. **Pass and finish**: Commit all three branch changes, verify the result, and end this review without pushing, retaining O1 as advice.
- **B**. **Finish**: End this review without committing, retaining O1 as advice.

🤖 **Enter an operation letter.**

### Dedicated re-review after an O repair

The user separately authorized repairing O1 above. This follow-up is shown apart from the main file groups; its required checks passed, and the independent re-review below assesses the saved before-and-after evidence.

📌 **O1 — Restore the export button after failure**

**Location**: `src/export.ts:68`.

Previously, a rejected export left the button disabled because restoration occurred only on success. The repair restores the button in a shared completion path, while preserving the export error for the caller. The failure-path check confirms that the button becomes usable again when export rejects.

⚖️ **Reasonable**. Users can retry after failure, and callers still receive the original export error.

🎨 **Elegant**. A single completion path handles restoration after either success or failure without duplicating state changes.

**O1 status**: Repaired; required checks and independent re-review confirmed the result. Main-review progress remains **3/3 files displayed**. This separate re-review creates no M ID or additional Viewed eligibility.

**Available actions**

- **A**. **Pass and finish**: Commit all branch changes, including the three reviewed text files and O1's checked, re-reviewed repair, verify the result, and end this review without pushing.
- **B**. **Finish**: End this review without committing.

🤖 **Enter an operation letter.**

If O1's check or re-review is incomplete or fails, retain its unresolved status and leave completion that would include the repair unavailable. Confirmation to include branch content does not replace this re-review.

### Pending findings and optional improvements

📊 **Progress**: **4/9 files displayed**.

**Pending findings**

- **M2** (P1): Closing the resource can lose unsaved data.
- **M5** (P2): The error path leaves the button disabled.

**Optional improvements**

- **M7**: Share the repeated state-reset logic to reduce maintenance omissions.

**Pass and continue** and **continue** are unavailable until M2 and M5 are repaired or explicitly ignored.

**Available actions**

- **A**. **Fix**: Repair both pending findings, or the subset you select.
- **B**. **Ignore**: Choose which findings to ignore; other findings remain pending.
- **C**. **Optimize**: Implement the optional improvement; the pending findings still need attention.

🤖 **Enter an operation letter; include M IDs to select a subset.**

If the user replies “A, M2” or “a, M2,” repair only M2; M5 remains pending. If the user replies “B” or “b,” clarify which findings to ignore unless the context already identifies them or the user explicitly chooses all. Operation letters choose actions; M IDs choose their items.

If the user replies “continue,” explain: “M2 and M5 are still pending, so I cannot show the next group yet.” Reissue the lettered available actions and letter-entry prompt above.

### Local partial staging with extra content

📊 **Progress**: **1/3 files displayed**. The displayed unstaged save-handler fix is reasonable; required checks passed for the full proposed commit.

The branch commit will include all staged, unstaged, and untracked changes: the save-handler fix, two undisplayed source files, and its new test file. The test remains outside report progress. These changes were introduced in this conversation except for an already-staged label change in `ui/save_button.dart`, which changes “Save” to “Save draft.” That staged hunk shares a file with the displayed fix and was made before this conversation. The final worktree retains both changes; the original index state is saved for recovery.

**Available actions**

- **A**. **Confirm inclusion and pass and continue**: Include the extra “Save draft” label change, commit the full branch inventory above, verify the result, then show the next group without pushing.
- **B**. **Continue**: Show the next group without staging or committing.

🤖 **Enter an operation letter.**

If the user declines the extra content, leave full-branch completion pending; do not silently commit only the save-handler fix. If option A completes, display the remaining two source files from the retained review snapshot even though the worktree is now clean. They were included in the commit but have not yet been displayed or counted as reviewed.

### Clean branch without a PR

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending. All branch changes are already committed, the branch and worktree state are verified, and no PR publication was requested.

**Available actions**

- **A**. **Pass and finish**: Reuse the verified commits and end this review, with no empty commit or push.
- **B**. **Finish**: End this review without further writes.

🤖 **Enter an operation letter.**

### PR with no repairs and an unrelated submodule difference

📊 **Progress**: **4/9 files displayed**. No unreasonable findings or unpublished changes made for this review are pending, and no selected commit or publication remains unfinished. Required review checks passed; the four displayed remote files have complete coverage at the pinned PR base/head.

Read-only inspection found a local submodule checkout difference unrelated to this review. It leaves the fixed reviewed PR delta, its dependencies, and the four files' assessments valid, so it will be preserved. No commit or push is needed for this completion; the PR version, viewer, and Viewed write/readback interfaces are verified.

**Available actions**

- **A**. **Pass and continue**: Verify the reviewed PR version, mark the four displayed reviewed files Viewed, verify every selected file and the PR version by readback, then show the next group.
- **B**. **Continue**: Show the next group without marking Viewed.

🤖 **Enter an operation letter.**

### PR repaired locally and ready for completion

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired; required checks and re-review passed. The full local branch delta contains those two fixes, their tests, and an undisplayed release-note change introduced earlier in this conversation. All applicable checks passed and the four displayed files' assessments remain valid. The PR target, viewer, write interfaces, and full publication scope have been verified.

**Available actions**

- **A**. **Pass and continue**: Commit and push all branch changes listed above, including the tests and release note, verify the PR version, mark only the four displayed reviewed files Viewed and verify every readback, then show the next group.
- **B**. **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

🤖 **Enter an operation letter.**

### Extra unpushed content needs confirmation

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired. Required checks passed for the complete proposed publication, and affected re-review confirmed the displayed files' assessments.

The normal push would publish the two local fixes and existing unpushed commit `a1b2c3d`, which changes the export default from CSV to JSON. That commit was not introduced in this conversation and its files have not been displayed in this review. Users relying on the old default would need to choose CSV explicitly. Confirm inclusion of that extra commit before publication; it will not receive review progress or Viewed marking merely because it is pushed.

**Available actions**

- **A**. **Confirm inclusion and pass and continue**: Include `a1b2c3d` in publication, commit all outstanding branch changes, push the complete branch delta, verify the PR version, mark only the four displayed reviewed files Viewed, verify readbacks, then show the next group.
- **B**. **Continue**: Show the next group, retaining the local fixes and unpushed commit without publishing or marking Viewed.

🤖 **Enter an operation letter.**

If the commit's origin cannot be established, say so and request the same explicit inclusion decision. If inclusion is declined, preserve the branch and leave completion pending until the user chooses a revised outcome; do not automatically cherry-pick only the fixes, rewrite history, or publish a smaller delta.

### Extra content shares a displayed PR file

The current group already displayed the save-handler change in `ui/save_button.dart`. Full-branch publication will also include an independent label change in that same file, and the user explicitly confirmed its inclusion. Checks passed, but the label hunk has not been displayed or assessed.

**Pass and continue** is not yet ready to mark that file Viewed: the published file's complete PR delta must be covered. Show a dedicated re-review of the missing label change with both judgments, retain the file's original group and progress count, and then offer completion for the same selected Viewed set.

If the label hunk cannot be reviewed within the authorized scope, keep the file unmarked and explain the required scope choice. Do not infer review from inclusion consent, drop the file from completion, or subtract it from displayed progress. If publication already succeeded before the coverage gap was discovered, retain that verified push and resume only the missing review and recording steps.

### Resume partially completed PR recording

📊 **Progress**: **4/9 files displayed**. The selected completion's commit and push are verified. After access was restored, readback confirmed the expected PR version and viewer: two selected files are Viewed and two remain unviewed.

The selected **pass and continue** is unfinished. Ordinary **continue** is unavailable until the remaining recording and readbacks complete.

**Available actions**

- **A**. **Pass and continue**: Resume by marking the two remaining selected files Viewed, verify all four selected files and the PR version, then show the next group. The verified commit, push, and completed marking will be reused.

🤖 **Enter an operation letter.**

### Final group of a PR review

📊 **Progress**: **9/9 files displayed**. No pending findings, outstanding local changes, or unpublished branch commits remain; the full branch state and reviewed PR version are verified. Four files from earlier groups are verified Viewed; five reviewed files across the report, including files from groups advanced using continue, still await Viewed.

**Optional improvements**

- **M7**: Share the state-reset logic to reduce duplication and maintenance omissions.

**Available actions**

- **A**. **Optimize**: Implement the optional improvement.
- **B**. **Pass and finish**: Complete recording for all nine reviewed files across every group: mark the five remaining files Viewed, verify all nine files and the PR version, then end this review, retaining the improvement as advice.
- **C**. **Finish**: End this review without marking the remaining files Viewed, retaining the improvement as advice.

🤖 **Enter an operation letter.**
