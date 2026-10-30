# Conversation Examples

These are synthetic conversations, not recorded executions or model-behavior evidence. Scenario facts stand in for inspection/check results. The Skill entry, Workspace, Completion, and helper guide own requirements; these dialogues only illustrate them. Placeholder links stand in for returned filename Markdown.

## Clear local scope: start, explain, finish

Scenario: the label edit was introduced earlier in this conversation. It is the only outstanding branch change; checks and source links are ready.

**User:** Review the unstaged change.

**Agent:** This is one unstaged file; there are no staged or untracked changes in the review.

📄 **[l10n/en.json](http://127.0.0.1:47821/diff?example=label)**

This file supplies English labels.

🔧 **M1** — **Name the deletion target**

“Delete” becomes “Delete account.”

⚖️ **Reasonable**. The button deletes the account, so the new label tells users what they will lose.

🎨 **Elegant**. Two plain words make the target clear without extra explanation.

**1/1 files displayed.** Checks passed. The branch has only this label edit.

- A. **Pass** (recommended): Commit this change, verify the commit, and finish without pushing.
- B. **Finish**: End the review and leave the edit uncommitted.

**User:** B.

**Agent:** Review finished: 1/1 files displayed. The edit remains uncommitted.

## A fact question without a menu

Scenario: local tracking does not establish the requested comparison base.

**User:** Review this branch.

**Agent:** Which branch should I compare it against?

**User:** release.

**Agent:** I checked its merge-base with release; it equals this branch's tip, so there are no changes to review.

## An incomplete finding selection

Scenario: M2 (P1) can lose a deletion flush; M5 (P2) leaves a retry button disabled. Both were displayed with their consequences.

**User:** Ignore.

**Agent:** Which findings: M2, M5, or both?

**User:** M2.

**Agent:** M2 (P1) is ignored; its data-loss risk remains recorded. M5 (P2) still leaves the retry button disabled after failure and needs a decision.

- A. **Fix** (recommended): Restore the retry button after failure, run checks, and show its re-review.
- B. **Keep**: Ignore M5 too, retaining the disabled-button impact.
- C. **Stop**: Stop with M5 unresolved.

## Mixed necessary issues and a valid subset

Scenario: 4/9 files were displayed. M2 misses the promised flush after deletion; M7 repeats three cleanup steps across success, failure, and cancellation.

**Agent:** M2 (P1) can leave the deletion unflushed. M7 currently works, but each cleanup change must be kept in sync in three places. I recommend addressing both.

- A. **Address** (recommended): Repair M2 and consolidate M7's cleanup, then run checks and re-review both.
- B. **Keep**: Ignore M2's risk and accept M7's duplication cost.
- C. **Stop**: Stop with these items unresolved.

You can also name a subset.

**User:** Only optimize M7 first.

**Agent:**

📄 **[ui/save_button.dart](http://127.0.0.1:47821/diff?example=m7-rereview)**

This file controls save-button availability and pending state. Cleanup now shares one completion path for success, failure, and cancellation.

🔧 **M7** — **Give cleanup one owner**

Previously, three outcome branches each cleared the pending flag, released the token, and restored the button. The change consolidates that sequence into one completion path.

⚖️ **Reasonable**. Cleanup still runs on all three outcomes, and the original error still reaches the caller.

🎨 **Elegant**. Resetting the flag, releasing the token, and restoring the button now have one owner.

Checks and dedicated re-review passed. Progress remains 4/9. M2 (P1) is still pending: deletion can still miss its promised flush.

- A. **Fix** (recommended): Repair M2, check it, and re-review it.
- B. **Keep**: Ignore M2 and retain its disclosed risk.
- C. **Stop**: Stop with M2 unresolved.

**User:** Fix M2 and continue.

**Agent:**

📄 **[lib/item_storage.dart](http://127.0.0.1:47821/diff?example=m2-rereview)**

This file deletes stored items and flushes their storage box. The fix preserves the box needed after deletion.

🔧 **M2** — **Flush the original box after deletion**

Previously, deletion detached the item and cleared its box reference before flushing. The path now captures that reference first and flushes the same box afterward.

⚖️ **Reasonable**. Deletion no longer clears the reference before the promised flush; flush errors still propagate.

🎨 **Elegant**. The two operations visibly share the same box without another lookup.

Checks and dedicated re-review passed. I will show the saved next group as requested, without committing, pushing, or recording Viewed.

## Structural necessity, not the size of the diff

Scenario: a new one-line public forwarding file adds no policy, adaptation, state, or lifetime responsibility. Its direct existing owner already supplies the accurate contract.

**User:** It is only one line. Does it really need changing?

**Agent:** Yes. Callers gain no capability or contract from this file, but have another public entry and another place to navigate.

⚖️ **Reasonable**. Calling through it currently returns the same result with the same failure behavior.

🎨 **Needs improvement**. Use the existing entry and remove the forwarding file. The extra boundary has no independent responsibility.

A parser with one caller could still deserve its own file if it owns format compatibility and validation. An ordinary local variable needs no separate necessity argument. Here, neither responsibility nor caller need supports the new public boundary.

## Optional advice does not displace the main path

Scenario: four reviewed PR files have complete coverage, checks passed, publication is current, and only Viewed recording remains. M8 is optional unit-name polish.

**User:** How is this group?

**Agent:** No necessary issues remain. M8 would make the time unit clearer, but the current calculation is already understandable. **4/9 files displayed.**

- A. **Pass** (recommended): Mark these four files Viewed, verify all four and the PR version, then show the next group.
- B. **Continue**: Show the next group without recording them.
- C. **Optimize**: Rename M8 first, then check and re-review it.

**User:** Continue.

**Agent:** I will show the saved next group. Those four files remain unrecorded and will still be included in final recording if you choose it.

## A fully verified checkout and synchronization plan

Scenario: /work/app is clean on main. Its existing feature/export branch is two commits behind pinned b7c9d21, not owned by another worktree. Target objects and exact fast-forward safety are verified; all facts use full commit IDs even though the display abbreviates them.

**Agent:** The review is for feature/export, but this workspace is on main. I can switch to the existing branch and fast-forward it to this PR's version. There are no uncommitted files to preserve; main stays unchanged.

- A. **Switch** (recommended): Switch /work/app to feature/export, fast-forward to b7c9d21, and verify the result. No push.
- B. **Snapshot**: Review the fixed PR contents without changing this checkout.
- C. **Stop**: Leave the workspace unchanged.

**User:** A.

**Agent:** The branch and target commit are verified, main is unchanged, and the workspace is still clean. I will now review the five eligible PR files.

## A later alignment step is still unknown

Scenario: current checkout can safely change to the source branch, but target objects needed to establish synchronization safety are unavailable. Independent PR snapshot evidence exists.

**Agent:** I can switch branches safely. I cannot yet verify the later synchronization, so this choice only switches the checkout.

- A. **Switch** (recommended): Switch to the existing feature/export branch and verify preservation.
- B. **Snapshot**: Review the fixed PR comparison without switching.
- C. **Stop**: Leave this workspace unchanged.

**User:** Switch.

**Agent:** Checkout is verified. Synchronization is still pending because the target objects are unavailable; no synchronization was performed. The fixed PR comparison is already verified.

- A. **Snapshot** (recommended): Review that fixed comparison without changing the branch version.
- B. **Stop**: Stop with the completed checkout retained.

**User:** Snapshot.

**Agent:** I will use fixed snapshot links. No further local alignment is needed for this review.

## Extra scope, partial success, and external failure

Scenario: 4/9 files were reviewed. Complete preparation/checks/coverage are ready. Publishing also includes the older commit a1b2c3d, which changes the export default from CSV to JSON; its independent file was not displayed. Its origin and effect are disclosed.

**Agent:** The push would include your reviewed fixes and a1b2c3d, which changes the export default to JSON. That older commit is outside the displayed files and will not be marked Viewed. Including it needs your confirmation.

- A. **Continue** (recommended): Show the next group without committing, pushing, or recording Viewed.
- B. **Pass**: Include a1b2c3d, commit the full disclosed outstanding changes, push the entire outgoing branch, mark only the four covered files Viewed, verify, then continue.

**User:** B.

**Agent:** Commit and push are verified. Two of the four selected files are confirmed Viewed. The readback service then became unavailable, so the other two and final version readback are unfinished. The operation and recovery evidence are retained. I cannot move to the next group yet.

**User:** The service is back. Finish that recording.

**Agent:** I verified the same viewer and PR version. Two paths were already Viewed; I recorded only the remaining paths and read back all four plus the unchanged PR version. The earlier commit and push were reused. I will now show the saved next group.

## An available uncovered hunk needs no new approval

Scenario: same-file extra inclusion was approved, publication was not selected, and the fixed label hunk is in review scope. Checks, PR identity/version/interfaces, and other coverage are ready.

**User:** What about the extra label?

**Agent:** I will review its already available change before offering publication.

📄 **[ui/save_button.dart](http://127.0.0.1:47821/diff?example=coverage)**

This button saves a draft. The extra label changes “Save” to “Save draft”; the earlier save-handler assessment is unchanged.

🔧 **M9** — **Name the saved result**

⚖️ **Reasonable**. The action saves a draft, and the label now tells users that result.

🎨 **Elegant**. Two words make the result explicit at the button, without another explanation layer.

The original group and existing M IDs are retained; M9 is the next modification ID. Checks and dedicated re-review passed, with displayed-file progress unchanged.

- A. **Pass** (recommended): Commit and publish the full disclosed checked contents, record the selected fully covered files, verify, then show the next group.
- B. **Continue**: Show the next group without publication or recording.

**User:** Continue.

**Agent:** I will continue from the saved comparison, retaining the checked local change without publishing or marking Viewed.

## Final recording includes earlier groups

Scenario: 9/9 files are displayed, including four earlier files advanced with Continue. No changes, publication, findings, or advice remain. All nine still await Viewed; version/viewer and required checks are verified.

**User:** Is the review done?

**Agent:** All nine files are reviewed. Recording them is the only remaining choice; that includes the four from earlier groups.

- A. **Pass** (recommended): Mark all nine reviewed files Viewed, read back all nine and the unchanged PR version, then finish.
- B. **Finish**: End without recording them.

**User:** Pass.

**Agent:** All nine files and the PR version are verified. The review and selected recording are complete.
