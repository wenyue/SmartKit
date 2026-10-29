# Report Examples

These examples illustrate the required review content and suggested presentation in [Review for Humans](../SKILL.md). Consult them when calibrating presentation; the entry owns the scope, judgments, actions, and verification requirements.

## PR workspace decisions

This illustrative PR belongs to `team/app`, with source branch `feature/export` in the same repository. Read-only inspection verifies that `/work/app` belongs to `team/app`, is clean, and has `main` checked out. Its existing local `feature/export` branch is not checked out elsewhere and is two commits behind the verified PR head `b7c9d21`; that target object and the fixed comparison evidence are available. Short commit IDs here are display abbreviations; actual comparisons and commands use the verified full IDs.

❓ **Q1** - **Check out the PR branch?**: The current workspace is the right repository, but it is on `main`. Switch `/work/app` to its existing `feature/export` branch before review?

- **A**. **Check out the branch** (recommended): Switch this clean workspace to the existing local `feature/export` branch, preserving both branch tips. This choice does not advance that branch's version.
- **B**. **Review the fixed PR snapshot**: Keep the checkout unchanged and use fixed snapshot links; those links do not open editable files in this workspace.
- **C**. **Cancel**: Leave the checkout unchanged and stop the review.

After A succeeds, verify the checkout and unchanged branch tips, then present the version choice before showing files:

❓ **Q2** - **Synchronize to the reviewed version?**: `/work/app` now has `feature/export` checked out, but it is two commits behind `b7c9d21`. The workspace remains clean, the PR target is unchanged, and a fast-forward to that exact commit is available.

- **A**. **Synchronize** (recommended): Fast-forward the local branch to `b7c9d21`, verify the resulting commit and clean state, then use live links bound to `/work/app`. This does not push anything.
- **B**. **Review the fixed PR snapshot**: Keep the older local version and use fixed snapshot links.
- **C**. **Cancel**: Stop here, retaining the completed checkout without synchronizing.

If another registered worktree already contains the PR branch, offer selecting that verified path in Q1; do not switch workspaces silently. If `main` happened to equal the target commit, Q1 would still resolve the branch mismatch, while a verified matching branch and commit would need no Q2. Adapt choices to actual dirty state, local commits, source-fork identity, and available safe plans; this clean fast-forward example supplies no permission for a reset, rebase, or loss of work.

## Complete report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, modifications, both reasoned judgments, and progress; a vertical comparison can help when the modification calls for expansion. These are illustrative files and snippets, not findings about a particular repository. This example is a local unstaged review containing three non-test files. The full branch inventory also contains their tests; all changes were introduced in this conversation and required checks passed. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

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

🎨 **Elegant**. The deletion and flush paths show that both operations need the same box instance. Compared with looking the box up again after deletion, keeping its reference at the deletion site expresses that dependency directly and avoids another lookup or owner elsewhere.

---

📄 **[ui/save_button.dart](http://127.0.0.1:47821/diff?repo=%2Fproject&path=ui%2Fsave_button.dart&base=blob%3A1111111111111111111111111111111111111111)**

This file handles the Save button. The change prevents repeated clicks from starting duplicate saves.

🔧 **M3** - **Refuse repeated clicks while saving**

Previously, repeated clicks could start duplicate saves; the handler now refuses another save while one is pending. Success, failure, and cancellation each repeat the same three-step cleanup: clear the pending flag, release the request token, and refresh button availability. Each copy currently works, and failures still reach the caller.

⚖️ **Reasonable**. This prevents duplicate saves within the requested scope.

🎨 **Needs improvement**. Inspecting all three outcome paths and nearby save handlers shows one cleanup operation copied across outcomes, while the established implementation uses a shared completion path. That direct alternative preserves the current results and error propagation, gives cleanup one owner, and removes future synchronization work at a small local change cost. Passing tests do not remove this structural burden. Optimize it or explicitly accept retaining it before finishing.

---

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending; M3 remains a required elegance improvement.

**Required elegance improvement**

- **M3**: Put the repeated cleanup in the established shared completion path, reducing duplication and future synchronization work.

**Pass and finish** and **finish** are unavailable until M3 is optimized and re-reviewed or explicitly accepted for retention. How would you like to handle it?

- **A**. **Optimize M3** (recommended): Consolidate cleanup, run the required checks, and show a dedicated re-review with both judgments and an updated menu.
- **B**. **Accept M3**: Retain the three cleanup copies and their synchronization cost, record that explicit acceptance, and show the updated menu without editing or advancing.

After an explicit acceptance of M3, retain its **Needs improvement — accepted** judgment and the disclosed maintenance cost. With all other prerequisites still verified, offer:

- **A**. **Pass and finish**: Commit all branch changes, including the three reviewed files and their tests, verify the result, and finish without pushing, retaining M3's accepted trade-off.
- **B**. **Finish**: Finish without committing, retaining M3's accepted trade-off.

If the user instead selects optimization, complete the checks and dedicated re-review before offering these advancing actions. A successful re-review can conclude **Elegant** because cleanup now has one owner; progress remains **3/3 files displayed**. Neither acceptance nor optimization alone authorizes the commit.

## Judgment boundaries

These independent illustrative cases calibrate the two judgments; they are not additional modifications in the report above. Each premise supplies the evidence that distinguishes extra defense, ordinary correctness, structural burden, and personal preference.

| Evidence and change | Reasonableness | Elegance |
| --- | --- | --- |
| A private helper removes a second null check after its only caller has established a non-null input. No supported path bypasses that caller. | **Reasonable**: the established input contract still holds; the missing duplicate check supplies no serious-risk finding. | **Elegant**: relying on the verified boundary guarantee removes redundant defense and keeps the operation visible. Do not request another check merely for hypothetical callers. |
| A handler adds repeated validation and fallback branches for values already guaranteed by its parser, while neighboring handlers call the same operation directly. The added paths preserve supported results but obscure the operation. | **Reasonable**: supported behavior and scope remain intact. | **Needs improvement**: remove the redundant checks and speculative fallbacks; their branches add a second validation story and obscure the established implementation pattern. Adding defense needs a concrete benefit. |
| A new cleanup route passes a request-controlled absolute path directly to recursive deletion. A request naming a directory outside generated output can erase unrelated user data. | **Unreasonable (P1)**: the reachable input and deletion effect establish a serious data-loss risk; add a containment check before deletion. | **Needs improvement**: express and enforce the allowed directory boundary once at the cleanup entry, so callers can understand its contract without scattered checks. Fixing the risk can also resolve this structural concern, subject to re-review. |
| A new private helper represents an option with several positional booleans, while adjacent equivalent helpers use a named option object. Its internal callers must repeatedly inspect the signature to distinguish the flags. | **Reasonable**: current callers pass the intended values and supported behavior works. | **Needs improvement**: align the helper and its internal callers with the established named-option interface, making calls readable and avoiding a second convention for the same concept. This is evidenced interface and style alignment, not a preferred naming fashion. |
| A local variable is already clear and follows nearby conventions; the reviewer prefers a different equally familiar name. | **Reasonable**: either name preserves behavior and scope. | **Elegant**: the current name serves its context. Omit the personal naming preference from the report; it supplies no worthwhile improvement. |

For a straightforward label edit like M1, the compact explanation and judgments are sufficient. For M2 and M3, the inspected dependencies and alternatives support a substantive design conclusion. If an alternative requires broader churn than its benefit warrants, omit that suggestion rather than turning the extra review effort into more report items.

## Example closings for different results

These illustrative closings follow file reports or dedicated re-reviews; they do not replace the two judgments in each modification. Adapt the wording and detail to the actual decision, localize the text, and include only actions that are ready and still need a choice. Reuse recognizable status cues and layouts where they help compare groups, and choose numbered question blocks when decisions need separate answers or stable references. The examples vary their presentation while preserving scope and authorization distinctions.

### Incidental observation with a ready final group

In this illustrative local review, the selected change only adjusts export-button text. The branch inventory contains only the three text files changed in this conversation; required checks passed. The source location below is illustrative; an actual report uses an available source link.

No unreasonable findings or required elegance improvements are pending. **3/3 files displayed**.

📌 **Incidental observations (outside this review's scope)**

**O1**: The export button stays disabled after a failed export.

- **Location**: `src/export.ts:68`.
- **Evidence and impact**: The button is disabled before export and restored only on success. When export throws, users must refresh the page to retry.
- **Relationship to this change**: The same failure path exists in the before version; the text change neither triggers nor aggravates it.
- **Recommendation**: Restore the button in a shared completion path so users can retry after success or failure.

O1 remains advice, does not block completion, and is excluded from bulk fixes or optimizations. Handling it requires a separate selection.

Commit the reviewed text changes and finish, keeping O1 as separate advice?

- **A**. **Pass and finish** (recommended): Commit all three branch changes, verify the result, and end this review without pushing, retaining O1 as advice.
- **B**. **Finish**: End this review without committing, retaining O1 as advice.

### Dedicated re-review after an O repair

The user separately authorized repairing O1 above. This follow-up is shown apart from the main file groups; its required checks passed, and the independent re-review below assesses the saved before-and-after evidence.

📌 **O1 — Restore the export button after failure**

**Location**: `src/export.ts:68`.

Previously, a rejected export left the button disabled because restoration occurred only on success. The repair restores the button in a shared completion path, while preserving the export error for the caller. The failure-path check confirms that the button becomes usable again when export rejects.

⚖️ **Reasonable**. Users can retry after failure, and callers still receive the original export error.

🎨 **Elegant**. A single completion path handles restoration after either success or failure without duplicating state changes.

**O1 status**: Repaired; required checks and independent re-review confirmed the result. Main-review progress remains **3/3 files displayed**. This separate re-review creates no M ID or additional Viewed eligibility.

Commit the reviewed text changes and the verified O1 repair, then finish?

- **A**. **Pass and finish** (recommended): Commit all branch changes, including the three reviewed text files and O1's checked, re-reviewed repair, verify the result, and end this review without pushing.
- **B**. **Finish**: End this review without committing.

If O1's check or re-review is incomplete or fails, retain its unresolved status and leave completion that would include the repair unavailable. Confirmation to include branch content does not replace this re-review.

### Pending unreasonable findings and required elegance improvements

⚠️ Two unreasonable findings and one required elegance improvement need attention. **4/9 files displayed**.

**Pending findings**

- **M2** (P1): Closing the resource can lose unsaved data.
- **M5** (P2): The error path leaves the button disabled.

**Required elegance improvement**

- **M7**: Three branches repeat the same multi-step state reset. Use the established shared completion path so future changes have one owner.

**Pass and continue** and **continue** are unavailable until M2 and M5 are repaired or explicitly ignored, and M7 is optimized and re-reviewed or explicitly accepted for retention.

How would you like to handle these items? Include M IDs to select a subset.

- **A**. **Fix** (recommended): Repair both pending findings, or the subset you select.
- **B**. **Ignore**: Choose which findings to ignore; other findings remain pending.
- **C**. **Optimize M7**: Consolidate the state reset, run checks, and show a dedicated re-review; M2 and M5 remain pending.
- **D**. **Accept M7**: Retain its duplication and maintenance cost; M2 and M5 remain pending and no code changes are authorized.

If the user replies “A, M2” or “a, M2,” repair only M2; M5 and M7 remain pending. If the user replies “B” or “b,” clarify which unreasonable findings to ignore unless the context already identifies them or the user explicitly chooses all. Operation letters choose actions; M IDs choose their items. Ignoring M2 and M5 does not accept M7, and accepting M7 does not ignore either unreasonable finding.

If the user replies “continue,” explain: “M2, M5, and M7 are still pending, so I cannot show the next group yet.” Reissue the concrete question and available lettered actions above. An explicit “accept M7 and continue” records that acceptance but cannot advance while M2 or M5 remains unresolved.

### Local partial staging with extra content

The displayed unstaged save-handler fix is reasonable; required checks passed for the full proposed commit. **1/3 files displayed**.

The branch commit will include all staged, unstaged, and untracked changes: the save-handler fix, two undisplayed source files, and its new test file. The test remains outside report progress. These changes were introduced in this conversation except for an already-staged label change in `ui/save_button.dart`, which changes “Save” to “Save draft.” That staged hunk shares a file with the displayed fix and was made before this conversation. The final worktree retains both changes; the original index state is saved for recovery.

Include the extra staged label change in the commit, or continue reviewing without committing?

- **A**. **Confirm inclusion and pass and continue**: Include the extra “Save draft” label change, commit the full branch inventory above, verify the result, then show the next group without pushing.
- **B**. **Continue** (recommended while inclusion is undecided): Show the next group without staging or committing.

If the user declines the extra content, leave full-branch completion pending; do not silently commit only the save-handler fix. If option A completes, display the remaining two source files from the retained review snapshot even though the worktree is now clean. They were included in the commit but have not yet been displayed or counted as reviewed.

### Clean branch without a PR

✅ The review is complete, with **3/3 files displayed** and no pending unreasonable findings or required elegance improvements. All branch changes are already committed, and the branch and worktree state are verified. No PR publication was requested, and no further Git write is needed.

### PR with no repairs and an unrelated submodule difference

In this example, the PR version, viewer, and Viewed write/readback interfaces are verified. There are no unpublished changes made for this review or unfinished selected commit or publication operations. The full application journey is outside this group's required checks.

✅ This group has no findings requiring repair. **4/9 files displayed**; the four reviewed files have complete coverage at the pinned PR base/head.

Formatting, diff checks, and targeted tests passed. Static analysis retains two unchanged dependency notices, confirmed against the baseline.

⚠️ Tests cover the affected behavior and Windows native components; the full application journey has not been run.

An unrelated local submodule checkout difference leaves the reviewed delta, its dependencies, and the assessments valid and will be preserved. No commit or push is needed; this group's Viewed recording is still pending.

❓ Mark the four reviewed files Viewed before continuing?

- **A**. **Pass and continue** (recommended): Verify the reviewed PR version, mark the four displayed reviewed files Viewed, verify every selected file and the PR version by readback, then show the next group.
- **B**. **Continue**: Show the next group without marking Viewed.

### PR repaired locally and ready for completion

M2 and M5 are repaired; required checks and re-review passed. **4/9 files displayed**. The full local branch delta contains those two fixes, their tests, and an undisplayed release-note change introduced earlier in this conversation. All applicable checks passed and the four displayed files' assessments remain valid. The PR target, viewer, write interfaces, and full publication scope have been verified.

Publish the checked branch changes and record the four reviewed files Viewed before continuing?

- **A**. **Pass and continue** (recommended): Commit and push all branch changes listed above, including the tests and release note, verify the PR version, mark only the four displayed reviewed files Viewed and verify every readback, then show the next group.
- **B**. **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

### Extra unpushed content needs confirmation

M2 and M5 are repaired. **4/9 files displayed**. Required checks passed for the complete proposed publication, and affected re-review confirmed the displayed files' assessments.

The normal push would publish the two local fixes and existing unpushed commit `a1b2c3d`, which changes the export default from CSV to JSON. That commit was not introduced in this conversation and its files have not been displayed in this review. Users relying on the old default would need to choose CSV explicitly. Confirm inclusion of that extra commit before publication; it will not receive review progress or Viewed marking merely because it is pushed.

Include `a1b2c3d` in publication, or continue reviewing without publishing?

- **A**. **Confirm inclusion and pass and continue**: Include `a1b2c3d` in publication, commit all outstanding branch changes, push the complete branch delta, verify the PR version, mark only the four displayed reviewed files Viewed, verify readbacks, then show the next group.
- **B**. **Continue** (recommended while inclusion is undecided): Show the next group, retaining the local fixes and unpushed commit without publishing or marking Viewed.

If the commit's origin cannot be established, say so and request the same explicit inclusion decision. If inclusion is declined, preserve the branch and leave completion pending until the user chooses a revised outcome; do not automatically cherry-pick only the fixes, rewrite history, or publish a smaller delta.

### Extra content shares a displayed PR file

The current group already displayed the save-handler change in `ui/save_button.dart`. Full-branch publication will also include an independent label change in that same file, and the user explicitly confirmed its inclusion. Checks passed, but the label hunk has not been displayed or assessed.

**Pass and continue** is not yet ready to mark that file Viewed: the published file's complete PR delta must be covered. Show a dedicated re-review of the missing label change with both judgments, retain the file's original group and progress count, and then offer completion for the same selected Viewed set.

If the label hunk cannot be reviewed within the authorized scope, keep the file unmarked and explain the required scope choice. Do not infer review from inclusion consent, drop the file from completion, or subtract it from displayed progress. If publication already succeeded before the coverage gap was discovered, retain that verified push and resume only the missing review and recording steps.

### Resume partially completed PR recording

The selected completion's commit and push are verified. **4/9 files displayed**. After access was restored, readback confirmed the expected PR version and viewer: two selected files are Viewed and two remain unviewed.

The selected **pass and continue** is unfinished. Ordinary **continue** is unavailable until the remaining recording and readbacks complete.

➡️ I will resume the authorized recording: mark the two remaining selected files Viewed, verify all four selected files and the PR version, then show the next group. The verified commit, push, and completed markings will be reused.

### Final group of a PR review

No pending unreasonable findings, required elegance improvements, outstanding local changes, or unpublished branch commits remain; the full branch state and reviewed PR version are verified. **9/9 files displayed**. Four files from earlier groups are verified Viewed; five reviewed files across the report, including files from groups advanced using continue, still await Viewed.

**Optional improvements**

- **M7**: Rename the local elapsed-time value to `elapsedMs` where it sits beside `timeoutSeconds`. The short conversion is already understandable, but this one local rename would expose the unit while scanning the two values; its limited change cost makes that concrete readability gain worthwhile. No structural defect needs acceptance.

Record the remaining five reviewed files Viewed and finish, or address M7 first?

- **A**. **Optimize**: Implement the optional improvement.
- **B**. **Pass and finish** (recommended): Complete recording for all nine reviewed files across every group: mark the five remaining files Viewed, verify all nine files and the PR version, then end this review, retaining the improvement as advice.
- **C**. **Finish**: End this review without marking the remaining files Viewed, retaining the improvement as advice.
