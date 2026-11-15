# A Review Group with a Defect and Independent Observations

This fictional report shows the first and only main group of a PR review.

The editor asks for confirmation before saving and shows a message after saving succeeds. People need to know which draft was saved and be able to try again after dismissing the prompt. This PR aims to name the saved draft even when it has no name and make cleanup easier to follow. The fixed PR comparison covers two eligible files after excluding tests and previously Viewed files.

---

📄 **[src/editor/labels.dart](http://127.0.0.1:47821/diff?example=labels)** · `+1 / −0`

**M1** · **Share the existing draft label**

> ⏪ The [draft list](https://example.test/repo/blob/0123456/src/editor/draft_list.dart) uses this file's existing default label for unnamed drafts, and the formatter is private to this file.
>
> ⏩ The file adds a public `draftLabel` function backed by the same formatter, so the [message after saving](http://127.0.0.1:47821/diff?example=complete-report) can use the label people already see in the list.

---

📄 **[src/editor/save_controller.dart](http://127.0.0.1:47821/diff?example=complete-report)** · `+5 / −3`

**M2** · **Name the draft in the save result**

> ⏪ The message after saving only says the save succeeded, so the user has to remember which draft was saved.
>
> ⏩ The message includes the draft name, using the [shared label formatter](http://127.0.0.1:47821/diff?example=labels).

**M3** · **Move cleanup into outcome branches**

> ⏪ One completion block clears the save-in-progress flag after every attempt. A reader tracing success or failure has to look at that block to see how the editor becomes available again.
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
> ⏩ The new code puts each reset next to the success or failure it handles, aiming to make each outcome easier to follow.
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
>
> ❌ ⚖️ **Unreasonable** · **P2** · Close the prompt before saving, then try to save again. The cancellation exits before either reset, so the editor still thinks a save is running and ignores the next attempt.
>
> 💡 Restore one completion block that clears the flag on every exit after it is set, including cancellation.

**O1** · **Use the existing draft-ordering policy**

> 🎨 **Optional improvement** · The `recentDrafts` and `pinnedDrafts` getters repeat the sort order from the [draft list](https://example.test/repo/blob/0123456/src/editor/draft_list.dart). Both getters and their callers match in the pinned base and head. The save and prompt paths do not use either getter.
>
> 💡 Reuse the draft list's comparator to preserve the current order and keep future ordering changes in one place.

---

📄 **[src/editor/draft_menu.dart](https://example.test/repo/blob/0123456/src/editor/draft_menu.dart#L25)**

**O2** · **Use the existing unnamed-draft label**

> 🎨 **Optional improvement** · The `renameAction` and `copyAction` each supply their own fallback for an unnamed draft. Both actions and the [label formatter's fallback](http://127.0.0.1:47821/diff?example=labels) match in the pinned base and head. The [message after saving](http://127.0.0.1:47821/diff?example=complete-report) is the new caller of the shared label function.
>
> 💡 Use the same formatter in both menu actions so the unnamed-draft label has one owner.

---

M3 remains unreasonable at P2 because cancelling a save can disable the next save. O1 and O2 are optional improvements to reuse the comparator and formatter so each policy has one owner.

The pre-save prompt returns `false` when dismissed. Source inspection traces that result through the early exit and the next save's guard. No repair checks have run.

📊 **Reviewed 2 / 2 files, with 3 modifications.**

- A. **Fix** (recommended): Restore M3's shared cleanup, run required checks, and show its dedicated re-review.
- B. **Optimize**: Apply O1 and O2 to reuse the comparator and label formatter, then check and re-review those changes.
- C. **Ignore**: Accept that cancellation can disable the next save under M3.

## Selecting Optimize while M3 is pending

Choosing B authorizes work on the two named observations. After their checks and re-review, M3 remains pending and main progress remains 2 / 2 files with 3 modifications.
