# Workspace Policy

Choose a workspace that lets the task proceed while preserving the work already there. Keep
ownership clear: a linked worktree can contain inherited source changes alongside task changes,
and carrying those changes leaves their original ownership intact.

## Preserve Existing Work

Preserve pre-existing staged, unstaged, and untracked work in the current checkout and every linked
worktree. Choose a non-destructive path; when none is available, stop and request direction.

When existing work and task edits share a file, proceed only when the two can be distinguished and
the result is verified to preserve the existing changes. A shared file is acceptable; inseparable
changes require a stop and a request for direction.

## Workspace and Commit Authority

### Choose where to work

Use the current checkout when existing state can be preserved and the user, Harness, applicable
Skills, and parallel work do not require isolation. Use `create-worktree` when isolation is
required or needed to protect existing state. That Skill owns workspace selection and readiness.

### Determine what may be committed

Leave task changes uncommitted unless the user has authorized a commit or the checkpoint authority
below applies.

After receiving and rechecking a ready `create-worktree` result, the owning workflow may create
scope-only Checkpoint Commits in that exact worktree through normal repository commit hooks,
without separate authorization. A ready worktree may still contain inherited source changes;
checkpoint authority covers only the task's scope. Account for inherited work under its original
ownership rather than treating all worktree contents as task-owned commit content.

A later Agent may continue this checkpoint authority only when the accepted workflow identifies
the exact worktree and base, and current Git evidence proves that every intervening commit and
local change belongs to the same scope. Ambiguity stops new commits.

## Git Remote Writes

Perform a Git operation that changes remote state only when the user explicitly requests that
outcome. Local commit authority does not by itself authorize a remote write.

Read-only Git remote queries remain subject to ordinary tool and network authorization; this Rule
adds no explicit-request condition for them.
