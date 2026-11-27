# Preparing a PR Review

## Verify the selected workspace

In this fictional PR review, `/work/app` is clean on `main`. The `contributor` remote points to the verified source fork. The local `feature/export` branch tracks `contributor/feature/export`, is free to check out, and can fast-forward from `b1ce402` to the pinned head `38bf06d` at that remote-tracking ref. No existing task worktree qualifies.

- A. **Create** (recommended): Create `/work/app/.worktrees/export-review` on `codex/export-review` at `38bf06d`, configure that new branch to track `contributor/feature/export`, and check readiness, keeping `/work/app` on `main`.
- B. **Switch**: Switch `/work/app` to `feature/export` and fast-forward it to `38bf06d`, preserving the clean state and the `main` tip.
- C. **Snapshot**: Review the verified fixed PR comparison without changing local work.

The user chooses Create. After creation returns `ready`, verify the pinned commit and original checkout. Apply the selected tracking change, then confirm the new branch's upstream remote and merge ref map to the verified source fork and `feature/export`. Refresh the PR comparison and Viewed evidence before live review.

## When the Viewed filter is unavailable

The fixed comparison is available, but authorized acquisition cannot establish complete Viewed states and needs no further user facts. Ask whether to review all otherwise eligible non-test files. If the user keeps the filter, preserve the fixed comparison and leave the filtered review pending until complete Viewed evidence is available.
