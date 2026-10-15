# Workspace Policy

Choose a workspace that lets the task proceed while preserving the work already there. Keep ownership clear: a linked worktree can contain inherited source changes alongside task changes, and carrying those changes leaves their original ownership intact.

## Preserve Existing Work

Preserve pre-existing staged, unstaged, and untracked work in the current checkout and every linked worktree. Choose a non-destructive path; when none is available, stop and request direction.

When existing work and task edits share a file, proceed only when the two can be distinguished and the result is verified to preserve the existing changes. A shared file is acceptable; inseparable changes require a stop and a request for direction.

## Disposable Temporary Artifacts

Use SmartKit's shared artifact cache for disposable temporary files unless the user, project, or applicable Skill specifies their output location or lifecycle. Retention is configurable per artifact and defaults to seven days. An unspecified directory alone does not make an output disposable: preserve source edits, canonical records, and sole copies requiring preservation under their owning contracts. Keep sensitive acquisition material requiring earlier deletion under its owner's private storage and deletion lifecycle.

Resolve the tools from the `artifact_cache` and `web_service` absolute paths in the loaded installation's `SmartKit plugin resources` metadata, independently of the target project's working directory. Before using the cache, read `python "<artifact_cache>" --help`, substituting its supplied path; before HTTP delivery, likewise read `python "<web_service>" --help`. The CLI help owns the operation inputs, commands, and results. The full SmartKit plugin and Python 3.8+ are required.

Cache privately by default; creation alone starts no HTTP service and returns no URL. When web display is appropriate and authorized, explicitly declare the intended public files and publish the retained artifact through the web tool, using its returned current URL. Keep private files undeclared. When a feature tool already returns a captured artifact or URL, reuse that result rather than caching or publishing it again.

If required resource metadata, a tool, or Python capability is unavailable, report the prerequisite gap and leave dependent output incomplete. Do not silently substitute an arbitrary project directory or claim URL delivery.

## Workspace and Commit Authority

### Choose where to work

Use the current checkout when existing state can be preserved and the user, Harness, applicable Skills, and parallel work do not require isolation. Use `create-worktree` when isolation is required or needed to protect existing state. That Skill owns workspace selection and readiness.

### Determine what may be committed

Commit task changes only when an applicable Skill, Rule, or conversation instruction explicitly requires or permits it. Follow that instruction's scope and conditions; otherwise leave the changes uncommitted.

After receiving and rechecking a ready `create-worktree` result, the owning workflow may create scope-only Checkpoint Commits in that exact worktree through normal repository commit hooks, without separate authorization. A ready worktree may still contain inherited source changes; checkpoint authority covers only the task's scope. Account for inherited work under its original ownership rather than treating all worktree contents as task-owned commit content.

A later Agent may continue this checkpoint authority only when the accepted workflow identifies the exact worktree and base, and current Git evidence proves that every intervening commit and local change belongs to the same scope. Ambiguity stops new commits.

## Git Remote Writes

Perform a Git operation that changes remote state only when the user explicitly requests that outcome. Local commit authority does not by itself authorize a remote write.

Read-only Git remote queries remain subject to ordinary tool and network authorization; this Rule adds no explicit-request condition for them.
