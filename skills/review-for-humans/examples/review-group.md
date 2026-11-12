# A Review Group with a Defect and Independent Observations

This fictional report shows the final main group of a PR review.

This group covers both eligible non-test files in the fixed PR comparison; tests and previously Viewed files were excluded before counting.

---

📄 **[src/editor/labels.dart](http://127.0.0.1:47821/diff?example=labels)**

M1 · Save confirmations use the existing draft-label formatter so unnamed drafts show the same fallback label as in the draft list.

---

📄 **[src/editor/save_controller.dart](http://127.0.0.1:47821/diff?example=complete-report)**

This controller saves drafts and reports progress. The change names the saved draft and moves pending-state cleanup.

M2 · The save confirmation names the draft so users can tell what was saved.

**M3** · **Move cleanup into outcome branches**

> ⚖️ ❌ **Unreasonable** · **P2** · Dismissing the confirmation leaves `pending` set, so the guard rejects the next save in the same editor session.\
> 🎨 ❌ **Needs improvement** · The outcome branches leave cancellation without a cleanup owner, so restore one completion block for every exit after setting `pending`.
>
> ⏪ A completion block clears pending state after every save attempt.
>
> ```dart
> if (pending) return;
> pending = true;
> try {
>   if (await confirmSave() == false) return;
>   await persistDraft(draft);
> } finally {
>   pending = false;
> }
> ```
>
> ⏩ Success and failure clear state separately after the cancellation check.
>
> ```dart
> if (pending) return;
> pending = true;
> if (await confirmSave() == false) return;
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

Both getters and their callers match in the pinned base and head. The save and confirmation paths do not use either getter. Reusing the comparator would preserve their current order and keep future ordering changes in one place.

---

📄 **[src/editor/draft_menu.dart](https://example.test/repo/blob/0123456/src/editor/draft_menu.dart#L25)**

**O2** · **Use the existing unnamed-draft label**

> 🎨 **Optional improvement** · The unchanged `renameAction` and `copyAction` repeat the label formatter's fallback, so calling that formatter would keep the menu and save confirmation under one label policy.

Both menu actions and the formatter's fallback match in the pinned base and head. The save confirmation is the only new caller of the formatter, and the menu actions still compute their own fallback independently.

---

M3 remains unreasonable at P2 because cancelling a save can disable the next save. O1 and O2 are optional improvements to reuse the comparator and formatter so each policy has one owner.

The confirmation handler returns `false` when dismissed. Source inspection traces that result through the early exit and the next save's guard. No repair checks have run.

📊 **Reviewed 2 / 2 files, with 3 modifications.**

- A. **Fix** (recommended): Restore M3's shared cleanup, run required checks, and show its dedicated re-review.
- B. **Optimize**: Apply O1 and O2 to reuse the comparator and label formatter, then check and re-review those changes.
- C. **Ignore**: Accept that cancellation can disable the next save under M3.

## Selecting Optimize while M3 is pending

Choosing B authorizes work on the two named observations. After their checks and re-review, M3 remains pending and main progress remains 2 / 2 files with 3 modifications.
