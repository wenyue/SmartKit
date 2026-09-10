# Workspace Policy

Strength: `Mandatory`

Scope: Workspace selection, local Git state, commit authority, and remote action authorization.

## Preserve Existing Work

- Preserve pre-existing staged, unstaged, and untracked work in the current checkout and every
  linked worktree. Choose a non-destructive path; when none is available, stop and request direction.
- When pre-existing and task changes share a file, proceed only when they can be distinguished and
  the result is verified to preserve the pre-existing changes; otherwise stop and request direction.

## Workspace and Commit Authority

- Use the current checkout when existing state can be preserved and the user, Harness, applicable
  Skills, and parallel work do not require isolation. Use `create-worktree` when isolation is
  required or needed to protect existing state.
- Leave task changes uncommitted unless the user has authorized a commit or the checkpoint authority
  below applies.
- After receiving and rechecking a ready `create-worktree` result, the owning workflow may create
  scope-only Checkpoint Commits in that worktree through normal repository commit hooks without
  separate authorization. A later Agent may continue this authority only when the accepted workflow
  identifies the exact worktree and base and current Git evidence proves every intervening commit
  and local change belongs to the same scope; ambiguity stops new commits.

## Remote Actions

- Perform each remote action only when the user explicitly requests that outcome.
