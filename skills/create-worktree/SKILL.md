---
name: create-worktree
description: Use when state-changing repository work requires an isolated linked Git worktree for parallel execution, workflow isolation, or protection of the current checkout.
---

# Create Worktree

Use this Procedure-led Skill when state-changing repository work needs an isolated linked Git
worktree. It selects or creates the worktree, verifies its identity and preservation boundaries,
prepares its environment, establishes baseline readiness, and returns a mechanical handoff.

The caller or owning workflow supplies the accepted scope and decision authority. The Controller—the
Agent running this Skill—performs the procedure. The host creates the worktree when it has a native
capability; Git is the fallback creator. `scope_owner` owns the implementation scope,
`creation_owner` identifies the concrete creator and lifecycle owner, `integration_owner` owns later
integration, and `cleanup_owner` owns later cleanup. This Skill does not take over business
implementation, commits, completed-change verification, integration, tracker state, or cleanup.

## Stage 1: Fix the Inputs and Preservation Boundary

1. Obtain the accepted implementation scope and record:
   - caller-supplied `scope_owner`;
   - for reuse, the exact path and identity of the Controller's current linked worktree, or, for
     creation, a lowercase hyphenated slug;
   - named worktree branch;
   - exact base commit;
   - `integration_owner` and `cleanup_owner`;
   - whether the host already created the intended worktree; and
   - for reuse, the concrete `creation_owner`, proved by caller-supplied evidence or an existing
     handoff, regardless of whether the host or Git created the worktree.
2. Resolve exactly one named base branch and its checkout against the supplied base commit. Inspect
   the current branch and `HEAD`, the Git common directory, and `git worktree list --porcelain`.
   Stop if the intended base is detached or ambiguous, or if the resolved commit differs from the
   supplied commit. The current branch tip never replaces the supplied commit.
3. Before any mutation, snapshot the base checkout's branch, `HEAD`, commit tree, index tree,
   staged, unstaged, and untracked state. Also snapshot every registered worktree and local branch.
4. For reuse, also snapshot the Controller's current linked worktree: exact path, named branch,
   `HEAD`, commit tree, index tree, and staged, unstaged, and untracked state. Record the owner of
   every local-state item and the allowed local-state scope. Stop when any item has ambiguous
   ownership or falls outside the accepted implementation scope.

Continue only with one exact base checkout, named base branch, supplied base commit, and complete
pre-mutation snapshot. For reuse, also require a complete current-worktree snapshot, ownership map,
and allowed local-state scope. These snapshots are the preservation boundary and accepted base for
readiness.

## Stage 2: Select Reuse or Creation

Choose one path:

- **Reuse:** Reuse only the Controller's current linked worktree, and only when the owning workflow
  selected that exact worktree for this exact scope. Stop if its exact path and identity were not
  supplied or the Controller is not currently in that worktree. Require one proven, unambiguous
  `creation_owner`, and require its path, named branch, `HEAD`, commit tree, index tree, staged,
  unstaged, and untracked state and per-item ownership to match the Stage 1 snapshot and allowed
  local-state scope. Stop when `creation_owner` is missing or ambiguous, or on any identity, state,
  scope, or ownership mismatch.
- **Create:** Require the supplied lowercase hyphenated slug, then select
  `<base-root>/.worktrees/<slug>`; stop when the slug is absent or invalid. Use a verified repository
  branch convention; when none is verified, use `worktree/<slug>`. Validate the branch name, then
  prove that the path is absent from both the filesystem and registered worktrees, and that the
  branch is absent from both registered worktrees and local branches. Stop on any conflict.

At this stage's exit, record the selected path and branch, whether the worktree will be reused or
created, and the local-state scope allowed for this implementation.

## Stage 3: Establish the `.worktrees/` Guard

For every selected path under `<base-root>/.worktrees/`:

1. Require the root `.gitignore` to contain an effective repository-relative `.worktrees/` entry.
2. If that entry is absent or ineffective, append `.worktrees/` as the smallest effective repair
   only when `.gitignore` is project-owned and the edit can preserve and distinguish all existing
   content and local state. Record the addition as an intentional project-owned change. Stop when
   the file is generated, read-only, ambiguously owned, or overlaps indistinguishable local work.
3. Run `git check-ignore -v` on the selected repository-relative path. Continue only when its output
   proves that the root `.gitignore` entry is effective; a global exclude or `.git/info/exclude`
   does not satisfy this gate.
4. For creation, obtain any required permission for the exact selected directory and worktree. The
   permission covers only that directory and worktree and authorizes no unrelated Git or filesystem
   change.

## Stage 4: Create and Verify the Worktree

For reuse, proceed directly to the verification gate below. For creation:

1. Immediately recheck the base branch, `HEAD`, commit tree, selected path, and selected branch
   against the recorded inputs and snapshot. Recheck the complete base index tree, staged,
   unstaged, and untracked state as well, allowing only the recorded, distinguishable `.gitignore`
   repair. If any other value moved or appeared, stop before creation and report the complete
   recorded and current state.
2. Prefer the host's native worktree capability when it is available, and record its concrete
   lifecycle owner as `creation_owner`. Only when no native capability exists, run exactly:

   ```text
   git -C <base-root> worktree add -b <branch> <worktree-path> <base-commit>
   ```

   Record the concrete Agent that ran the fallback as `creation_owner`.
3. If creation fails, inspect the selected path and Git's worktree metadata. Remove an incomplete
   artifact only when evidence proves this attempt created it and it contains no user work. If that
   proof is unavailable, retain the artifact and evidence, identify the exact recovery owner and
   action, and stop. After a safe removal, repeat the complete pre-creation check in step 1,
   including the full base snapshot, and retry once. On a second failure, retain all remaining
   evidence and stop.

Verification gate:

1. Use `git worktree list --porcelain` to prove that the selected path, named branch, and `HEAD`
   equal the recorded values.
2. Prove that the base checkout's `HEAD`, commit tree, index tree, and pre-existing staged,
   unstaged, and untracked state still match the snapshot. The only permitted difference is the
   recorded `.worktrees/` addition to `.gitignore`.

Continue only with the selected worktree identity proven and the base preservation boundary intact.

## Stage 5: Prepare and Decide Readiness

1. Work inside the selected worktree. If the target repository provides its own
   `worktree-environment-setup`, run it before baseline verification and record its commands and
   results. Continue to baseline verification only when that setup returns a successful, ready
   result. If the setup is unavailable, stops, fails, or returns a non-ready result, end readiness
   immediately, retain the worktree, and record the failed step, result, exact next owner, and
   exact next action for the handoff.
2. Run the repository-declared baseline after environment setup. Record the exact commands and
   results. A failing baseline stops readiness unless the user explicitly accepts the failure. The
   absence of a declared baseline stops readiness unless the owning workflow or user explicitly
   accepts the absence. Record the accepted failure or absence; do not invent a command or
   substitute completed-change verification.
3. Mark the result ready only when all of these are true:
   - the worktree has one named branch;
   - its `HEAD` and commit tree equal the accepted base;
   - target-owned `worktree-environment-setup` is absent, or it completed successfully with a ready
     result;
   - the baseline passed, its failure was explicitly accepted by the user, or its declared absence
     was explicitly accepted by the owning workflow or user; and
   - every local path belongs exclusively to the accepted implementation scope.

Retain every failed worktree for diagnostic evidence. Preserve any other non-ready worktree unless
its owning workflow supplies separate disposition authority; this Skill grants no deletion
authority for it. End this stage with an observable readiness result and reason, identifying any
stop or failure precisely.

## Stage 6: Return the Mechanical Handoff

Every terminal exit returns one handoff. Set `status` to `ready` only when the complete Stage 5 ready
predicate passes; set it to `non-ready` for every earlier stop or failure. `failed_phase`, the
observable reason, and the exact next action distinguish non-ready outcomes.

Populate every handoff field according to the completed boundary. Preserve every observed value and
its exact failure reason; use a literal marker instead of inferring anything not established,
verified, or run:

- Before Stage 2 selects a worktree, set selected worktree, branch, `head`, and `tree` to
  `not-selected`.
- After the Create branch selects its path and branch but before it creates a worktree, report the
  exact selected path and branch and set `head` and `tree` to `not-created`.
- After a creation attempt, or after Reuse selection but before the verification gate passes,
  report the selected path and branch plus observed `head` and `tree` when available, and mark the
  identity unverified. Report an unavailable observed value as `unavailable`; never infer it.
- After the verification gate passes, including during setup or baseline, report the exact verified
  selected path, named branch, `head`, and `tree`.
- For accepted scope, base checkout, base branch, base commit and tree, each owner, reuse path or
  creation slug, and allowed local-state scope, use `unavailable` until established. Preserve an
  observed value and label it `unverified` until its applicable gate passes; afterward report the
  exact verified value.
- For the `.gitignore` gate, report `not-run` before Stage 3. Preserve any observed rule or repair
  result and label it `unverified` until `git check-ignore -v` proves the required root rule;
  afterward report the exact verified result.
- For environment setup and baseline, report their commands, results, and acceptance fields as
  `not-run` until the applicable step runs. Once run, preserve the exact command and result and
  label any still-unverified outcome `unverified`. If target evidence proves a step absent, report
  that exact absence and its required acceptance instead of `not-run`.
- For readiness, report `non-ready` with the exact failed phase and reason until every Stage 5
  predicate passes. A `ready` handoff contains no boundary marker: every mandatory field is exact
  and verified, and every applicable setup and baseline step has an exact result.

The handoff contains:

- `status` and the accepted implementation scope;
- worktree identity populated under the completed-boundary rules above;
- base checkout, named base branch, exact commit and tree, and preserved local state;
- `scope_owner`, `creation_owner`, `integration_owner`, and `cleanup_owner`;
- exact reuse path or creation slug, `.gitignore` result, and allowed local-state scope;
- environment-setup and baseline commands, results, and explicitly accepted failures or absence;
  and
- readiness result and reason.

For any non-ready result, also return the retained state, failed phase, failed setup step and result
when applicable, next owner, and exact next action. The caller must recheck the handoff before
implementation or finalization. Its recorded values grant no broader authority.
