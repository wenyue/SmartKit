# Preparing a PR Review

## Verify the selected workspace

In this fictional PR review, `/work/app` is clean on `main`. The verified local `feature/export` branch is free to check out and can fast-forward from `b1ce402` to the pinned head `38bf06d`. No existing task worktree qualifies.

- A. **Switch** (recommended): Switch `/work/app` to `feature/export` and fast-forward it to `38bf06d`, preserving the clean state and the `main` tip.
- B. **Create**: Create `/work/app/.worktrees/export-review` on `codex/export-review` at `38bf06d`, check its environment, and preserve `/work/app`.
- C. **Snapshot**: Review the verified fixed PR comparison without changing local work.

The user chooses Create. Verify the resulting path, branch mapping, commit, environment, and preserved work. Refresh the PR comparison and Viewed evidence before beginning the review.

## When the Viewed filter is unavailable

The fixed comparison is available, but authorized acquisition cannot establish complete Viewed states and needs no further user facts. Ask whether to review all otherwise eligible non-test files. If the user keeps the filter, preserve the fixed comparison and leave the filtered review pending until complete Viewed evidence is available.
