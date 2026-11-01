# Conversation Examples

The Skill entry owns the ordinary review loop; [Report Format](../references/report-format.md) owns the fixed presentation, and Preparation and Delivery own their conditional branches. These synthetic scenarios stand in for inspection/check evidence. The complete report uses a placeholder returned link and illustrative source; it is not an execution record or evidence of general model reliability.

## One complete report

Scenario: this final PR group has one eligible production file. Inspection covered its whole diff and necessary context, including a cleanup edit omitted from the author's summary. The source shown below is the synthetic fixed comparison.

**Agent:** The fixed PR comparison is ready. This group contains the remaining non-test file; tests are excluded from the report.

---

📄 **[src/editor/save_controller.dart](http://127.0.0.1:47821/diff?example=complete-report)**

This controller saves drafts and reports progress. The change names the saved draft and moves pending-state cleanup.

⚖️ **Unreasonable** — M1 clarifies which draft was saved. M2 is P2: cancellation now skips the pending-state reset, so the next save stays disabled. Restore cleanup on that exit. The author's summary omitted this edit, but its defect still needs an explicit item.

🎨 **Needs improvement** — M2 requires optimization: success and failure branches duplicate one cleanup responsibility and miss cancellation. A shared completion block covers every exit and removes repeated maintenance. M1 needs no new boundary.

**M1 — Identify the saved draft**

> ⏪ The status names only the action: `status = 'Saved';`.
>
> ⏩ The status includes the available draft name: `status = 'Saved ${draft.name}';`.

**M2 — Move cleanup into outcome branches (P2)**

> ⏪ One completion block clears pending state after the save attempt.
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
> ⏩ Success and failure each clear state after the cancellation check.
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

---

**1/1 main files displayed.** Source and control-flow inspection support M2's P2 cancellation defect and repeated-cleanup burden; no repair checks have run yet. One shared cleanup owner addresses both.

- A. **Fix and optimize** (recommended): Restore M2's shared cleanup, run required checks, then show the file's dedicated re-review.
- B. **Ignore**: Leave M2 unchanged, explicitly accepting the disabled-next-save risk and repeated-cleanup burden.

## Choices and transitions without repeated report bodies

The following independent scenarios are abbreviated notes, not complete review responses. They omit repeated file blocks to focus on decisions. Actual supplementary, main repair, and selected-O re-reviews still show the complete fixed layout before dependent action resumes.

| Situation | Choice and follow-through |
| --- | --- |
| A new early return triggers a defect in an unchanged caller. | If the caller closes storage after awaiting the controller, returning before its write finishes can lose the draft. Report the responsible M item's severity, trigger, impact, and correction in the leading judgment; restore the await and failure propagation. This is a main finding. An unrelated pre-existing formatter burden found during necessary reading is O instead. |
| At 4/9 files, only M8's optional named-parameter rename to expose milliseconds remains; coverage and checks are ready, with no commit or push pending. | Offer A **Optimize**, B **Pass** accepting M8's disclosed unit-lookup cost and recording all four eligible files Viewed before advancing, C **Continue** leaving the suggestion outstanding. After Optimize, check the rename and show its dedicated report without increasing 4/9. A subsequent Pass includes the new commit/push; Continue leaves that change unpublished. |
| Local review contains one label edit, and delivery inventory finds nothing else; coverage and checks are ready, and no push was requested. | **Pass** commits, verifies, and finishes. **Finish** ends with the edit uncommitted. No push, PR creation, or Viewed effect is implied. |
| Only-deliver is pending at 4/9; inventory adds an unpublished commit, staged production changes, and tests from another conversation. | Include all of them in commit/publication inventory and checks; supplement current-conversation review of every uncovered non-test change. Tests are excluded from semantic review and gain no Viewed eligibility from passing checks. A new M11 defect or improvement pauses delivery for its remedy or explicit **Ignore**, not another Pass. After required checks and complete affected re-review, resume only-deliver and stay at 4/9. |
| M2 can lose a promised flush and M7 duplicates cleanup; the user says “Only optimize M7 first,” with no delivery pending. | Optimize, check, and show M7's dedicated re-review. M2 remains unresolved: offer **Fix** or explicit **Ignore** for its disclosed risk. The subset selection grants no delivery or advancement. |
| Nine main files are displayed; four were advanced with Continue. A supplementary production file also has full PR-delta coverage. Checks are ready and only Viewed recording remains. | Prepare Viewed for all ten current, fully reviewed eligible paths, including the earlier four; supplementary coverage does not change 9/9. Unreviewed tests and files with only a repaired fragment reviewed stay out. A selected Pass records and reads back all ten plus the unchanged PR version, then finishes. |
| Pass committed and pushed successfully, but the interface failed after confirming only two of four Viewed paths. | Report confirmed, unknown, and pending effects without a fabricated waiting menu. On a supported resume, verify the viewer/version and actual markings, reuse completed effects, record only the missing paths, and read back the full set and version. Then resume Pass's saved next group; do not repeat commit/push. |
| No M issue remains; unrelated O1 has a supported normalization simplification. Delivery is prepared but unselected. | Offer A **Optimize O1**, B **Pass** leaving O1 unchanged, C **Continue**. An unambiguous “Optimize” selects that explicit O1 scope. After checks, show a separate O1 report with the fixed layout, no M ID or main-progress increase. Its changes enter full delivery review/check scope; Viewed still needs complete PR-file coverage. With a necessary main issue, recommend its remedy and show O1 optimization after **Ignore**, disclosing the unresolved main issue. Unselected O advice does not block delivery; already authorized ready delivery proceeds without a new menu. |

## Workspace alternatives remain visible

Scenario: the current related checkout is clean on main; it can safely switch to the PR source and fast-forward to the fixed target. No other existing workspace qualifies. Creation and fixed-snapshot review are both available.

**Agent:** This checkout is on main; the PR uses feature/export.

- A. **Switch current workspace** (recommended): Switch /work/app to feature/export, fast-forward to the verified target, and verify preservation. No push.
- B. **Create workspace**: Create /work/app/.worktrees/export-review at the fixed target on review/export, assess its environment, and preserve the current checkout.
- C. **Snapshot review**: Review the fixed PR contents without changing this workspace.

**User:** Create.

**Agent:** The selected worktree, branch mapping, target, and environment are verified. I will review from that path.

## A missing filter needs consent, not an automatic expansion

Scenario: fixed PR evidence is ready, but authorized acquisition could not obtain complete Viewed states and no user-owned fact can resolve that limitation.

**Agent:** The complete Viewed filter is unavailable. Would you like me to review all otherwise eligible non-test files at the pinned version without that filter?

**User:** No, stop here.

**Agent:** Stopped. The comparison evidence is preserved; no files were reviewed and the broader scope was not selected.

## Ask directly for missing facts

For a branch review with no established comparison base, ask “Which branch should I compare against?” After the user chooses release, derive its verified merge-base. If that equals the reviewed tip, report no changes without a progress fraction or invented action menu.
