# Preparing a Review when the Workspace or Comparison Is Unsettled

In this fictional PR review, the related checkout is clean on `main`. The verified PR source is `feature/export`; the checkout can switch there and fast-forward to the pinned head without losing work. No existing task worktree qualifies, while both a new worktree and fixed-snapshot review are viable.

## Choose the display workspace

**Agent:** The checkout is on main; the PR uses feature/export. These routes preserve the current clean state:

- A. **Switch current workspace** (recommended): Switch /work/app to feature/export, fast-forward to the verified target, and verify preservation.
- B. **Create workspace**: Create /work/app/.worktrees/export-review at the fixed target on review/export, assess its environment, and preserve the current checkout.
- C. **Snapshot review**: Review fixed PR contents without changing this workspace.

**User:** Create.

**Agent:** The selected worktree, branch mapping, target, and environment are verified. Review will use /work/app/.worktrees/export-review.

The user's choice establishes the concrete workspace and branch operation. The Agent then verifies the created workspace rather than treating the proposed path as evidence that it is ready.

## The Viewed filter cannot be established

In another PR review, fixed source versions are available, but authorized acquisition cannot obtain the authenticated viewer's complete file statuses. No missing user fact would repair that acquisition failure.

**Agent:** I have the fixed PR contents, but cannot determine which files you already marked Viewed. May I review all otherwise eligible non-test files without that filter?

**User:** No, keep the Viewed filter.

The broader scope remains unselected. The Agent preserves the pinned comparison and reports that the filtered review cannot proceed until complete Viewed evidence is available. It neither silently includes all files nor describes unseen files as clean.

## A branch comparison has no established base

A user asks to review `feature/export` without naming a base, and the available repository evidence does not settle one.

**Agent:** Which branch should feature/export be compared against?

**User:** release.

The verified merge-base with `release` equals the reviewed branch tip. The Agent reports that this comparison has no changes, with no progress fraction or action menu. The user's answer resolved the comparison; it did not create files to review.
