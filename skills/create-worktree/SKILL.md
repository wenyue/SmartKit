---
name: create-worktree
description: Use when state-changing repository work requires an isolated linked Git worktree for parallel execution, workflow isolation, or protection of the current checkout.
---

# Create Worktree

This Procedure-led Skill creates or reuses one named linked Git worktree and prepares it for its
owning implementation scope while preserving the base branch, index, and pre-existing local state.
It owns worktree selection, creation, validation, readiness, and the mechanical ownership handoff.
It does not classify the scope as a task, ticket, or batch. Business implementation, completed-change
integration, tracker state, and cleanup remain with their owners.

## Establish the Preparation Contract

1. Record the accepted implementation scope, caller-supplied `scope_owner`, intended path or
   lowercase hyphenated slug, named branch, exact base commit, later `integration_owner` and
   `cleanup_owner`, whether the host has already created the intended worktree, and, when it has,
   the caller-supplied `creation_owner`.
2. Resolve one base checkout and named base branch against the caller-supplied exact base commit.
   Inspect the current branch and `HEAD`, the Git common directory, and
   `git worktree list --porcelain`; stop when the intended base is detached or ambiguous, or when
   resolution differs from the supplied commit. Never substitute the current branch tip for it.
3. Before mutation, snapshot the base checkout's branch, `HEAD`, commit tree, index tree, staged,
   unstaged, and untracked state, plus all registered worktrees and local branches. This snapshot is
   the preservation boundary and the accepted base for readiness.

## Select and Validate the Worktree

1. Reuse the current worktree only when the owning workflow selected that linked worktree for the
   exact implementation scope. Require its named branch, `HEAD`, commit tree, and local-state
   ownership to match the preparation contract; otherwise stop without readiness.
2. For a new worktree, select `<base-root>/.worktrees/<slug>` and follow a verified repository
   branch convention, falling back to `worktree/<slug>`. Validate the branch name and require both
   the path and branch to be absent from the filesystem, registered worktrees, and local branches.
3. For every selected path under `<base-root>/.worktrees/`, whether reused or new, require the root
   `.gitignore` to contain an effective repository-relative `.worktrees/` entry. If the entry is
   absent or ineffective, append `.worktrees/` as the smallest effective repair only when
   `.gitignore` is project-owned and the edit can preserve and distinguish all existing content and
   local state; record it as an intentional project-owned change. Stop when the file is generated,
   read-only, ambiguously owned, or the edit would overlap indistinguishable local work.
4. Use `git check-ignore -v` to prove every selected repository-relative `.worktrees/` path is
   ignored by the root `.gitignore` after any repair; a global exclude or `.git/info/exclude` is
   insufficient. For a new worktree, obtain any permission required for the exact selected
   directory and worktree. That permission authorizes no unrelated Git or filesystem change.

## Create and Verify

1. Immediately before creation, recheck the base branch, `HEAD`, commit tree, path, and branch
   against the recorded contract. If any value moved or appeared, stop before creation and report
   the recorded and current values with the preserved snapshot.
2. When the host's native worktree creation capability is available, use it and record its concrete
   lifecycle owner as `creation_owner`. Only when that capability is unavailable, use the Git
   fallback and record the concrete Agent executing
   `git -C <base-root> worktree add -b <branch> <worktree-path> <base-commit>` as
   `creation_owner`.
3. Verify with `git worktree list --porcelain` that the path, branch, and `HEAD` equal the selected
   values. Recheck that the base checkout's `HEAD`, commit tree, index tree, and pre-existing local
   state match the snapshot; allow only the recorded `.worktrees/` `.gitignore` addition.
4. On creation failure, inspect both Git worktree metadata and the selected path. Remove only an
   incomplete artifact proven to have been created by this attempt and to contain no user work.
   When that proof fails, retain the evidence and stop with the exact recovery owner and action.
   After safe removal, repeat the pre-creation checks and retry once. A second failure retains all
   remaining evidence and stops.

## Prepare and Establish Readiness

1. Continue inside the selected worktree. When the target repository provides
   `worktree-environment-setup`, apply it before baseline verification.
2. Run the repository-declared baseline verification after environment preparation. A failing
   baseline is pre-existing evidence: stop before implementation unless the user explicitly accepts
   it for this worktree. When no baseline is declared, stop without readiness unless the owning
   workflow or user explicitly accepts the unavailable baseline. Do not substitute completed-change
   verification or invent a command.
3. Report the worktree ready only when it has one named branch; its `HEAD` and commit tree equal the
   accepted base; its baseline passes or is explicitly accepted; and every local path belongs
   exclusively to the accepted implementation scope.
4. Retain every failed worktree for diagnosis rather than discarding evidence automatically.

## Result

Return one preparation handoff containing `status`; accepted implementation scope; selected
`worktree`, `branch`, exact `head`, and exact `tree`; base checkout, branch, exact commit and tree,
and preserved local state;
`scope_owner`, `creation_owner`, `integration_owner`, and `cleanup_owner`; intended path or slug,
`.gitignore` result, and allowed local-state scope; environment setup and baseline commands,
results, and accepted failures; readiness result and reason; and, when not ready, retained
state, failed phase, and next owner. The caller rechecks the handoff before implementation or
finalization. The handoff grants no authority beyond its recorded values.
