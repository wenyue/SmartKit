# A Repair that Changes the Lookup and Its Callers

In this fictional review, M1–M10 have been assigned and main progress is 4 / 9 files with 10 modifications. M2 found that category-list lookup uses a translated name even though stored lists and callers already have stable IDs. The user selected Fix M2 without delivery. The repair changes the lookup and both callers, plus a test file.

M2 is repaired across the lookup and its two callers. M11 and M12 describe supporting caller changes; all three belong to this repair of M2.

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

- A. **Pass** (recommended): Prepare and deliver the selected workspace's outstanding changes, publish the complete outgoing scope to the PR source, and review the next group read-only while eligible Viewed paths are recorded.
- B. **Continue**: Review the next group without delivery, keeping the local repair.

## A required check cannot run

In this variation, all three files were re-reviewed, but the project-required application check cannot run because its runner is unavailable. The source evidence still supports the lookup change; it does not replace that check.

The report keeps the same three file blocks, names the missing check in its evidence paragraph, and describes M2's repair as incomplete. It offers neither Pass nor Continue. The next useful step is to restore the required runner; no selectable in-scope workaround has been established, so the Agent does not manufacture a Wait option.

## The selected item was an independent observation

In a separate review, the user selected Optimize O1 to use an existing label formatter in `draft_menu.ts` and `draft_toolbar.ts`. Both files change, and the relevant label test is updated. The repair report explains O1 once under the menu file, describes the toolbar change in that file's overview, and reports the test with verification evidence.

Here O1 remains the selected incidental observation; the supporting toolbar edit does not create a new M or O item. The report covers both changed non-test files and affected callers while keeping that review's main counts unchanged.
