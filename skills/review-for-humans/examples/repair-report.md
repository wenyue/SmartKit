# A Repair that Changes the Lookup and Its Callers

In this fictional PR review, the user selected Fix M2 without delivery in `/work/catalog`. Main progress was 4 / 9 files with M1–M10 displayed.

M2 replaces translated names with stable IDs in the category-list lookup. M11 and M12 update its two callers as part of the same repair.

---

📄 **[src/catalog/category_index.ts](http://127.0.0.1:47821/diff?example=repair-index)**

**M2** · **Find category lists by stable identity**

> ⚖️ **Reasonable** · Changing a category's translated name keeps its existing list reachable through the stored category ID.\
> 🎨 **Elegant** · One lookup owner uses the existing identity contract for both callers, with no name-based fallback or second index.
>
> ⏪ The lookup matches the display name supplied by the caller.
>
> ```typescript
> function itemsFor(name: string) {
>   return lists.find(list => list.name === name)?.items ?? [];
> }
> ```
>
> ⏩ The repaired lookup matches the stable ID already stored on each list.
>
> ```typescript
> function itemsFor(categoryId: string) {
>   return lists.find(list => list.categoryId === categoryId)?.items ?? [];
> }
> ```

---

📄 **[src/catalog/editor_controller.ts](http://127.0.0.1:47821/diff?example=repair-editor)**

M11 · Category selection passes the category ID to the lookup so editing the display name keeps the same list selected.

---

📄 **[src/catalog/gallery_controller.ts](http://127.0.0.1:47821/diff?example=repair-gallery)**

M12 · Initialization and service updates use the category ID so a translated-name change still finds the original list.

---

M2's repair is complete, with no new findings or outstanding optional improvements. M11 and M12 are reasonable and elegant: both callers use the confirmed identity contract directly.

Required project checks passed on the repaired contents. Independent re-review covered all three changed non-test files and the affected previously reviewed category-selection paths. The changed `tests/catalog/category_lookup.test.ts` supplies evidence for renamed and missing categories. [Verification evidence](http://127.0.0.1:47821/evidence?example=repair-checks) records the procedures, results, and available logs.

Repair coverage is three non-test files; main progress remains 4 / 9 files with 10 modifications. Commit, publication, and Viewed recording have not occurred.

- A. **Pass** (recommended): Prepare and commit outstanding changes in `/work/catalog`, publish the complete outgoing scope to the PR source, and record eligible Viewed paths. Once only Viewed remains, review the next group read-only under the delivery guide.
- B. **Continue**: Review the next group without delivery, keeping the local repair.

## A required check cannot run

If all three files were re-reviewed but the required application check could not run, keep the three file blocks and report M2 as incomplete. Name the missing check and the unavailable runner in the evidence paragraph. With no selectable workaround, close by explaining that the runner must be restored to finish the repair.

## The selected item was an independent observation

If Optimize O1 updates `draft_menu.ts`, `draft_toolbar.ts`, and a label test, show O1 once under the menu file and describe the supporting change in the toolbar file's overview. Report the test with the verification evidence and keep main counts unchanged.
