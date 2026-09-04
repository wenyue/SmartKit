# Workspace Policy

Strength: `Mandatory`

Scope: Workspace selection, local Git state, commit authority, and remote action authorization.

## All Checkouts

- Apply this section to the current checkout and every linked worktree.
- Preserve all pre-existing staged, unstaged, and untracked work while implementing and reviewing
  the accepted task.
- Choose a non-destructive path when a task operation would overwrite, stash, reset, clean, or
  discard that state; request direction when no such path is available.
- When a file contains both pre-existing and task changes, continue when they can be distinguished
  and the result is verified to preserve the pre-existing changes; otherwise stop and request
  direction.
- Leave task changes uncommitted unless the user separately authorizes a commit or the worktree has
  received the specific commit authority below.

## Worktree Selection and Commit Authority

- Use the current checkout when the user, Harness, and applicable Skills do not require isolation,
  parallel work does not need separate state, and existing checkout state can be preserved in place.
- Apply `create-worktree` when the user, Harness, or an applicable Skill requires isolation,
  parallel work needs separate state, or isolation is needed to protect existing checkout state.
  It owns linked-worktree selection, creation, validation, and the current readiness result used by
  its caller.
- After the caller receives and rechecks a ready `create-worktree` result, the owning workflow may
  create scope-only Checkpoint Commits in that worktree through the repository's normal commit
  hooks without separate authorization. A later Agent may continue that authority only when the
  accepted workflow identifies the exact worktree and base and current Git evidence proves that
  every intervening commit and local change belongs to the same scope; ambiguity stops new commits.
- Apply `finish-worktree` to a reviewed isolated linked worktree when an implementation workflow is
  ready to consolidate or deliver. The implementation workflow owns formal review.
  `finish-worktree` independently proves the current worktree, head and tree, delivery target,
  authority for every requested effect, and that the same head and tree passed verification and
  formal review with no blocking finding.
- Synchronization that changes reviewed content returns it to the implementation workflow for
  verification and formal review before delivery.

## Remote Actions

- Perform each remote action only when the user explicitly requests that outcome.
