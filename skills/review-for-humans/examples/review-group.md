# A Review Group with a Defect and Independent Observations

In this fictional PR, the fixed comparison contains two production files. Moving save cleanup introduced a cancellation defect. Necessary reading also found two unchanged places that duplicate existing draft-display policies; the base and head establish that this PR did not introduce, trigger, or aggravate those observations. The following is the final main group.

This group covers both eligible non-test files in the fixed PR comparison; tests and previously Viewed files were excluded before counting.

---

📄 **[src/editor/labels.dart](http://127.0.0.1:47821/diff?example=labels)**

M1 · Save confirmations use the existing draft-label formatter so unnamed drafts receive the same fallback label everywhere.

---

📄 **[src/editor/save_controller.dart](http://127.0.0.1:47821/diff?example=complete-report)**

This controller saves drafts and reports progress. The change names the saved draft and moves pending-state cleanup.

M2 · The save confirmation names the draft so users can tell what was saved.

**M3** · **Move cleanup into outcome branches**

> ⚖️ ❌ **Unreasonable** · **P2** · Cancelling a save leaves the pending flag set, disabling the next save.\
> 🎨 ❌ **Needs improvement** · Outcome branches split ownership of the pending flag, so restore one completion block that clears it on every exit.
>
> ⏪ A completion block clears pending state after every save attempt.
>
> ```dart
> pending = true;
> try {
>   if (cancelled) return;
>   await persistDraft(draft);
> } finally {
>   pending = false;
> }
> ```
>
> ⏩ Success and failure clear state separately after the cancellation check.
>
> ```dart
> pending = true;
> if (cancelled) return;
> try {
>   await persistDraft(draft);
>   pending = false;
> } catch (_) {
>   pending = false;
>   rethrow;
> }
> ```

**O1** · **Use the existing draft-ordering policy**

> 🎨 **Optional improvement** · The unchanged `recentDrafts` and `pinnedDrafts` getters duplicate the comparator owned by the draft list; using that existing comparator would keep all three views under the same ordering policy.

Both getters match in the pinned base and head and are outside the save path. Their current order is correct; this suggestion removes duplicate policy rather than repairing M3.

---

📄 **[src/editor/draft_menu.dart](https://example.test/repo/blob/0123456/src/editor/draft_menu.dart#L25)**

**O2** · **Use the existing unnamed-draft label**

> 🎨 **Optional improvement** · The unchanged `renameAction` and `copyAction` repeat the label formatter's fallback, so calling that formatter would keep the menu and save confirmation under one label policy.

This file is unchanged by the PR, and its menu actions do not participate in the cancellation defect.

---

M3 remains unreasonable at P2: cancelling a save can disable the next save. O1 and O2 are optional improvements outside the main changes.

Source and control-flow inspection establish the cancellation defect. No repair checks have run.

📊 **Reviewed 2 / 2 files, with 3 modifications.**

- A. **Fix** (recommended): Restore M3's shared cleanup, run required checks, and show its dedicated re-review.
- B. **Optimize**: Apply O1 and O2 to reuse the comparator and label formatter, then check and re-review those changes.
- C. **Ignore**: Accept that cancellation can disable the next save under M3.

## The user chooses the independent improvements first

**User:** Only optimize O1 and O2.

**Agent:** I will update the draft-order and label callers and check and re-review those changes under O1 and O2. M3's cancellation defect remains pending; this selection does not repair it or authorize delivery.

The explicit selection covers the two independent observations, so the Agent can perform that bounded work while keeping the main defect visible. The saved main progress remains 2 / 2 files and 3 modifications.

## The same report after M3 has already been repaired

In this variation, M3's checks and re-review have passed, O1 remains worthwhile, and O2 has been declined. There is no pending delivery selection. The closing offers Optimize scoped to O1, Pass leaving O1 unchanged, and Finish without delivery. The cleared main defect makes those choices available; O1's separate origin does not hide a supported improvement from the user.
