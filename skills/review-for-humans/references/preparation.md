# Preparation

Read for PR or remote-aligned branch review, before choosing a workspace or preparing its links. This guide owns source/version evidence, PR Viewed filtering, workspace routes, and verified display context. The Skill entry owns ordinary review and user decisions; common local comparison and link generation do not require this guide.

## Establish repository, branch, and version

Use current authoritative PR metadata for owning repository, source repository/fork, source branch, and target commit. A selected historical version remains the target; local tracking cannot establish current PR head.

To apply the Viewed filter, obtain complete file states for the authenticated viewer with unchanged base/head across all pages. For a current `github.com` PR, run `snapshot` from the loaded Skill with a new private evidence directory outside the worktree.

```text
python "<skill-root>/scripts/complete_review.py" snapshot --pull-request owner/repo --number 123 --state "/private/viewed-snapshot"
```

Select `UNVIEWED` and `DISMISSED` paths from evidence for the selected version, including for historical comparisons. With `snapshot.json`, match its viewer and base/head to the intended review before using `candidate_paths`. Approval, comments, and earlier chat display cannot establish file states.

If the user asks to include viewed files, select all paths from the verified comparison. A matching current `snapshot.json` supplies these paths in the full `files` map. Apply the project's test-file exclusions with or without the Viewed filter.

If complete Viewed filtering remains unavailable after authorized acquisition, first ask directly for any genuinely needed user fact. Otherwise, when fixed comparison evidence is ready, ask directly whether the user wants to review all otherwise eligible files without the Viewed filter. Proceed with that broader scope only after an explicit choice; never fabricate historical or current Viewed states.

Inspect even an apparently matching checkout. Resolve `local_web` from loaded SmartKit resources:

```text
python "<local_web>" --help
python "<local_web>" diff --inspect --input "<context.json>"
```

Supply verified PR context. Read `current` and `worktrees`; no alternatives says nothing about current repository identity. Interpret `repository_status`, `branch_status`, and version `status` independently. Equal commits do not establish branch identity; related repositories do not establish source-branch identity. Inspection does not fetch, check out, or synchronize.

Retain path, repository relationship, branch, commit, and all staged/unstaged/untracked/conflicted `changes`, including partial staging and rename sources. Inspect existing workspaces before proposing Use. An inventory is not a recovery snapshot or proof of safety; unknown is not clean/current. Explain relevant paths and preservation effects to the user rather than reciting status-field names.

1. Establish whether the checkout belongs to the PR owner or verified source repository. Preserve unrelated workspaces.
2. Verify source repository and branch. A verified tracking alias may qualify; disclose it. A different branch or detached HEAD needs a choice even at the target commit. Finding a matching worktree does not select it; never force a second checkout of a branch owned elsewhere.
3. Compare the selected corresponding branch/workspace HEAD with target. A match needs no synchronization question; disclose dirty live contents. For ahead/diverged plans identify local and distinct target commits and preserve work/history.

Separate comparison evidence from local evidence. An independently verified fixed PR comparison can be reviewed even when local identity/version or a safe alignment plan is unavailable. It needs verified scope, PR identity/target, and before/after content; it changes no local work. Once selected, skip irrelevant local alignment and resolve only required filtering/evidence. Differing live links require verified fixed evidence and explicit disclosure; they do not change assessed commits or Viewed eligibility.

## Choose a workspace route for the actual task

If repository, branch, and version already match, proceed without another alignment choice. An explicitly selected fixed comparison also needs no local alignment. Preserve earlier workspace and view choices; only changed facts or a new task requirement reopen their affected parts.

Otherwise inspect the available routes before offering them. These actions prepare a workspace or comparison; none delivers changes or advances a review group.

| Action | Applicable route and required disclosure |
| --- | --- |
| **Switch** | Change the current related checkout to the verified source branch using an established preservation plan. Name affected state and commits. A combined synchronization is included only when its exact method and safety are already verified and disclosed. |
| **Sync** | Align a selected corresponding branch/workspace to the exact target using a verified preservation plan. Disclose affected local/target commits and preserved index, worktree, untracked content, and history. |
| **Use** | Select a verified existing workspace. Give its path, repository/source-branch mapping, commit, and preserved changes. A differing live workspace requires independent fixed comparison evidence and explicit disclosure of the version difference. |
| **Create** | Create a clean isolated workspace at the verified immutable target. Name the path, branch or alias, target, and environment assessment; preserve current workspaces. Include this route unless a known blocker prevents it. |
| **Snapshot** | For a PR with independently verified before/after evidence, review that fixed comparison without changing local work. It does not provide a matching checkout for edits or local execution. Branch-only review has no PR snapshot fallback. |

Honor an explicitly selected viable route first. Otherwise use the entry's decision principles and the common PR situations below. A current-workspace route means a safe, useful Switch or Sync; name that concrete action in the menu. A route is useful only when it establishes the workspace or evidence needed for the task. Snapshot cannot replace required local editing or execution. Preserve source-branch ownership and existing work when judging viability.

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| The current workspace matches, or a viable route is already selected | Begin the review | No new choice; complete the selected route's verification |
| A safe current-workspace route and a verified existing workspace are available | **Switch** or **Sync** current workspace | **Switch** or **Sync**; **Use**; **Create**; **Snapshot** |
| A safe current-workspace route is available; no existing workspace qualifies | **Switch** or **Sync** current workspace | **Switch** or **Sync**; **Create**; **Snapshot** |
| The current workspace is unsuitable; a verified existing workspace is available | **Use** existing workspace | **Use**; **Create**; **Snapshot** |
| Neither the current workspace nor an existing workspace qualifies | **Create** workspace | **Create**; **Snapshot** |

These choice rows assume Create and fixed PR Snapshot are viable; for other situations apply the same priorities to the established routes. Present every viable route once in order, using consecutive letters with the first recommended. If Switch includes a fully verified Sync, describe that combination once. A verified existing workspace needing alignment may be offered as Use with its concrete Sync plan. Unknown facts are investigation work, not proof that an option is unavailable; establish them before excluding a potentially useful route. Explain known missing prerequisites where they remove an otherwise relevant choice.

When several workspaces qualify for Use, list their concrete paths while retaining the other routes. Ask for a path only after Use is selected and the path remains ambiguous; that question must not select Use for the user. Offer no Stop or Cancel choice, and do not select a route merely because it is recommended or the only one available. If no useful route is verified, ask the specific user-owned fact that could establish one or report the actual limitation without a fabricated menu. Independently verified PR evidence may still provide Snapshot when local identity or alignment is unresolved.

After Create is selected, use [create-worktree](../../create-worktree/SKILL.md) for creation checks, authorized creation, and environment assessment with the user's clean choice and immutable base. Reuse existing choices and resolve only outstanding decisions. No route authorizes unstated synchronization, history rewriting, or publication.

## Verify before reviewing

After alignment rerun inspection on the exact path. Verify branch mapping, target commit, and preserved work. Refresh PR base/head and Viewed evidence and reassess changed targets before review/links. After interruption inspect actual results before retrying. Dependent review stays pending until verification, explicit fixed-comparison selection, or stop.

Retain workspace, source-branch mapping, target, and snapshot/live mode. For historical PRs, selected fixed comparisons, or unavailable source identity, use `view="snapshot"` with verified fixed evidence. For PR live links use `view="worktree"` and bind `repo` to the exact workspace verified here, including a verified local alias.

For branch-only review use read-only Git for checkout/worktrees and an explicit or reliably established authoritative remote; never invent an upstream. PR inspection requires PR context. Without a display workspace resolve a verified workspace/creation or another scope. Deliberately local branch and local unstaged reviews need no remote synchronization.
