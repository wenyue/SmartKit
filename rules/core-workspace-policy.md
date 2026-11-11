# Workspace Policy

Choose a workspace that lets the task proceed while preserving existing work. Carrying changes into a linked worktree does not transfer their ownership to the current task.

## Preserve work before choosing a workspace

Preserve pre-existing staged, unstaged, and untracked changes in the current checkout and every linked worktree. Use a non-destructive path; if none exists, stop and request direction.

Task edits may share a file with existing work when the changes can be distinguished and the result is verified to preserve that work. If they are inseparable, stop and request direction.

Before editing project Agent configuration in a linked worktree or removing a worktree, follow [Worktree configuration](../skills/create-worktree/references/configuration.md) to preserve shared sources and keep copied edits in both workspaces.

Decide whether isolation is needed before creating a worktree. Read-only inspection and remote-only PR operations normally need no new checkout. Use the current checkout when existing state can be preserved and the user, Harness, applicable Skills, and parallel work do not require isolation.

When isolation is needed, prefer a compatible existing task worktree to a new one. Weigh the benefit against dependency restoration and generation costs before choosing a new checkout. Use `create-worktree` to select or create the isolated workspace and establish readiness; its required preparation still applies.

Before creating a worktree or branch, switching branches in a checkout, or performing task analysis or edits in another worktree, explain the planned operations, concrete target path and branch as applicable, and effects on existing work; obtain the user's explicit agreement before proceeding. Branch creation requires this agreement even without a new worktree or a branch switch.

Reuse agreement already present in the conversation when it covers the planned operations and target. Direct instructions and workspace or branch choices made through another Skill count; one choice may cover both a worktree and its branch. General permission to implement does not by itself authorize these operations.

## Keep commit authority scoped

Commit task changes only when an applicable Skill, Rule, or conversation instruction explicitly requires or permits it, within that instruction's scope and conditions. Otherwise leave them uncommitted.

After receiving and rechecking a ready `create-worktree` result, the owning workflow may make scope-only Checkpoint Commits in that exact worktree through normal repository commit hooks without separate authorization. A ready worktree may include inherited source changes. Account for them under their original ownership; checkpoint authority covers only the task's scope, not everything carried into the worktree.

A later Agent may continue that authority only when the accepted workflow identifies the exact worktree and base, and current Git evidence establishes that every intervening commit and local change belongs to the same scope. Ambiguity stops new commits.

## Require explicit authority for remote writes

Change Git remote state only when the user explicitly requests that outcome. Local commit authority does not authorize a remote write.

Read-only Git remote queries remain subject to ordinary tool and network authorization; this Rule adds no explicit-request condition for them.
