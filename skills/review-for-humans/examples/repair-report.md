# A Repair that Changes the Lookup and Its Callers

In this fictional PR review, the user selected Fix M2 without delivery in `/work/catalog`. Main progress was 4 / 9 files with M1–M10 displayed.

M2 restores access to a category's saved list when its translated name changes. M11 and M12 update [category selection](http://127.0.0.1:47821/diff?example=repair-editor) and [gallery updates](http://127.0.0.1:47821/diff?example=repair-gallery) to pass the same stable category ID.

---

📄 **[src/catalog/category_index.ts](http://127.0.0.1:47821/diff?example=repair-index)** · `+2 / −2`

**M2** · **Find category lists by stable identity**

> ⏪ The lookup compares names. After a rename, the caller sends the new name while the saved list still carries the old one, so the lookup returns an empty list even though the saved items are still there.
>
> ```typescript
> function itemsFor(name: string) {
>   return lists.find(list => list.name === name)?.items ?? [];
> }
> ```
>
> ⏩ The lookup uses the stable ID already stored on each list. It finds the same items after a name change.
>
> ```typescript
> function itemsFor(categoryId: string) {
>   return lists.find(list => list.categoryId === categoryId)?.items ?? [];
> }
> ```

---

📄 **[src/catalog/editor_controller.ts](http://127.0.0.1:47821/diff?example=repair-editor)** · `+1 / −1`

**M11** · **Keep the selected list when its name changes**

> ⏪ The editor passes the name to the [lookup](http://127.0.0.1:47821/diff?example=repair-index), so changing the name can lose the selected list.
>
> ⏩ The editor passes the category ID so selection continues to find the same list.

---

📄 **[src/catalog/gallery_controller.ts](http://127.0.0.1:47821/diff?example=repair-gallery)** · `+2 / −2`

**M12** · **Find the same list when opening or refreshing the gallery**

> ⏪ Opening and refreshing the gallery send the translated name to the [lookup](http://127.0.0.1:47821/diff?example=repair-index), so a translation change can hide existing items.
>
> ⏩ Both operations send the category ID so they keep finding the same items.

---

M2's repair is complete, with no new findings or outstanding optional improvements.

Required project checks passed on the repaired contents. Independent re-review covered all three changed non-test files and the affected previously reviewed category-selection paths. The [category lookup test](https://example.test/repo/blob/0123456/tests/catalog/category_lookup.test.ts) supplies evidence for renamed and missing categories. [Verification evidence](http://127.0.0.1:47821/evidence?example=repair-checks) records the procedures, results, and available logs.

Repair coverage is three non-test files; main progress remains 4 / 9 files with 10 modifications. Commit, publication, and Viewed recording have not occurred.

- A. **Pass** (recommended): Prepare and commit outstanding changes in `/work/catalog`, publish the complete outgoing scope to the PR source, and record eligible Viewed paths. Once only Viewed remains, review the next group read-only under the delivery guide.
- B. **Continue**: Review the next group without delivery, keeping the local repair.

## A required check cannot run

If all three files were re-reviewed but the required application check could not run, keep the three file blocks and report M2 as incomplete. Name the missing check and the unavailable runner in the evidence paragraph. With no selectable workaround, close by explaining that the runner must be restored to finish the repair.

## The selected item was an independent observation

If Optimize O1 updates `draft_menu.ts`, `draft_toolbar.ts`, and a label test, show O1 once under the menu file and describe the supporting change in the toolbar file's overview. Report the test with the verification evidence and keep main counts unchanged.
