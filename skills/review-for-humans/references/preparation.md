# Preparation

Read for PR or remote-aligned branch review and for local branch review that needs a display-workspace choice. This guide owns source and version evidence, PR Viewed filtering, workspace routes, and verified display context. The Skill entry owns ordinary review and user decisions.

## Establish the comparison

### Branch without a PR

Use read-only Git to establish repository identity, branch, tip, comparison base, and checkout/worktree state. For remote alignment, verify the authoritative remote and ref from an explicit choice or reliable repository evidence. Ask for the specific user-owned fact if the required remote, ref, or base remains ambiguous. Use the workspace inspection and choice guidance below for any required alignment or display workspace. Keep the branch scope unless the user explicitly selects a different comparison.

### Pull request

Verify the PR host, owning repository and number, source repository/fork and branch, and base/head from authoritative PR evidence. Preserve any selected historical version. Local tracking establishes a workspace relationship, while the PR metadata establishes the current PR version.

To apply the Viewed filter, obtain complete file states for the authenticated viewer with unchanged base/head across all pages. For a current `github.com` PR, run `snapshot` from the loaded Skill with a new private evidence directory outside the worktree. The bundled route uses authenticated GitHub access. Use another authorized interface only when it can establish the required PR and file-state evidence for the selected host and version.

```text
python "<skill-root>/scripts/complete_review.py" snapshot --pull-request owner/repo --number 123 --state "/private/viewed-snapshot"
```

Select `UNVIEWED` and `DISMISSED` paths from evidence for the selected version, including for historical comparisons. With `snapshot.json`, match its viewer and base/head to the intended review before using `candidate_paths`. Approval, comments, and earlier chat display cannot establish file states.

If the user asks to include viewed files, select all paths from the verified comparison. A matching current `snapshot.json` supplies these paths in the full `files` map. Apply the project's test-file exclusions with or without the Viewed filter.

If complete Viewed filtering remains unavailable after authorized acquisition, first ask directly for any genuinely needed user fact. Otherwise, when fixed comparison evidence is ready, ask directly whether the user wants to review all otherwise eligible files without the Viewed filter. Proceed with that broader scope only after an explicit choice; never fabricate historical or current Viewed states.

An independently verified fixed PR comparison needs the PR identity, selected base/head and scope, and complete before/after content. Once the user selects that comparison, resolve any remaining filter and content evidence and skip irrelevant alignment. Local display has its own requirements. For `local_web` Snapshot display, verify the exact Git worktree root and the pinned objects needed to reconstruct both sides, including renamed paths and genuine absences. Request `view="snapshot"` and check that it displays the fixed diff. Even a successful command can return a URL to a diagnostic page. Preserve the fixed evidence and follow the entry's display procedure when the local comparison cannot be rendered.

## Inspect workspaces for the selected task

For work that depends on a checkout, inspect even an apparently matching one. Use the branch-only Git route above or, for a supported `github.com` PR, resolve `local_web` from loaded SmartKit resources:

```text
python "<local_web>" --help
python "<local_web>" diff --inspect --input "<context.json>"
```

Supply verified PR context to `local_web`. Read `current` and `worktrees` and interpret `repository_status`, `branch_status`, and version `status` independently. Check current repository identity even when no alternatives are listed. Equal commits do not establish branch identity; related repositories do not establish source-branch identity. Inspection does not fetch, check out, or synchronize. Where the bundled inspection is unavailable, use read-only evidence from Git and the verified PR source to establish the same facts before offering a dependent route.

Retain path, repository relationship, branch, commit, and all staged/unstaged/untracked/conflicted `changes`, including partial staging and rename sources. Inspect existing workspaces before proposing Use. An inventory is not a recovery snapshot or proof of safety; unknown is not clean/current. Explain relevant paths and preservation effects to the user rather than reciting status-field names.

1. Establish whether the checkout belongs to the selected repository. For PRs, check its relationship to the PR owner and verified source repository. Preserve unrelated workspaces.
2. Verify the selected branch and its source. For a PR tracking alias, confirm its actual tracking remote resolves to the source repository and its merge ref to the source branch. Disclose the verified alias. A different branch or detached HEAD needs a choice even at the target commit. Finding a matching worktree does not select it; never force a second checkout of a branch owned elsewhere.
3. Compare the selected corresponding branch/workspace HEAD with target. A match needs no synchronization question; disclose dirty live contents. For ahead/diverged plans identify local and distinct target commits and preserve work/history.

Differing live links require verified fixed evidence and explicit disclosure. The pinned comparison still governs assessment and Viewed eligibility.

## Choose a workspace route for the actual task

If repository, branch, and version already match, proceed without another alignment choice. An explicitly selected fixed comparison also needs no local alignment. Preserve earlier workspace and view choices; only changed facts or a new task requirement reopen their affected parts.

Otherwise inspect the available routes before offering them. These actions prepare a workspace or comparison; none delivers changes or advances a review group.

| Action | Applicable route and required disclosure |
| --- | --- |
| **Switch** | Change the current related checkout to the verified source branch using an established preservation plan. Name affected state and commits. A combined synchronization is included only when its exact method and safety are already verified and disclosed. |
| **Sync** | Align a selected corresponding branch/workspace to the exact target using a verified preservation plan. Disclose affected local/target commits and preserved index, worktree, untracked content, and history. |
| **Use** | Select a verified existing workspace. Give its path, repository/source-branch mapping, commit, and preserved changes. A differing live workspace requires independent fixed comparison evidence and explicit disclosure of the version difference. |
| **Create** | Create a clean isolated workspace at the verified immutable target. Name the path, branch, target, and readiness checks. Preserve current workspaces. When the task needs live PR source mapping, establish a feasible plan before offering Create. Use a same-name branch where it will identify the verified source, or disclose the tracking configuration needed to map an alias to that source. |
| **Snapshot** | For a PR with independently verified before/after evidence, review that fixed comparison without changing local work. Editing and local execution need their own ready workspace. |

Honor an explicitly selected viable route first. Otherwise use the entry's decision principles and the common PR situations below. A current-workspace route means a safe, useful Switch or Sync; name that concrete action in the menu. A route is useful only when it establishes the workspace or evidence needed for the task. Snapshot cannot replace required local editing or execution. Preserve source-branch ownership and existing work when judging viability.

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| The current workspace matches, or a viable route is already selected | Begin the review | No new choice; complete the selected route's verification |
| A safe current-workspace route and a verified existing workspace are available | **Switch** or **Sync** current workspace | **Switch** or **Sync**; **Use**; **Create**; **Snapshot** |
| A safe current-workspace route is available; no existing workspace qualifies | **Create** workspace | **Create**; **Switch** or **Sync**; **Snapshot** |
| The current workspace is unsuitable; a verified existing workspace is available | **Use** existing workspace | **Use**; **Create**; **Snapshot** |
| Neither the current workspace nor an existing workspace qualifies | **Create** workspace | **Create**; **Snapshot** |

These PR examples assume Create and fixed PR Snapshot are viable. For branch-only review or other situations, apply the same priorities to the established routes. Present every viable route once in order, using consecutive letters with the first recommended. If Switch includes a fully verified Sync, describe that combination once. A verified existing workspace needing alignment may be offered as Use with its concrete Sync plan. Investigate unknown facts before excluding a potentially useful route. Explain known missing prerequisites where they remove an otherwise relevant choice.

When several workspaces qualify for Use, list their concrete paths while retaining the other routes. Ask for a path only after Use is selected and the path remains ambiguous; that question must not select Use for the user. Offer no Stop or Cancel choice, and do not select a route merely because it is recommended or the only one available. If no useful route is verified, ask the specific user-owned fact that could establish one or report the actual limitation without a fabricated menu. Independently verified PR evidence may still provide Snapshot when local identity or alignment is unresolved.

After Create is selected, use [create-worktree](../../create-worktree/SKILL.md) with the user's clean choice and immutable base. Use its `ready` or `non-ready` result for creation and environment readiness. On `ready`, apply any tracking change authorized by the selected plan and verify the actual mapping along with the other requirements below. Reuse existing choices and resolve only outstanding decisions. No route authorizes unstated synchronization, history rewriting, or publication.

## Verify before reviewing

After alignment rerun inspection on the exact path. Verify branch mapping, target commit, and preserved work. For a PR, refresh base/head and applicable Viewed evidence and reassess changed targets before review or links. After interruption inspect actual results before retrying. If a workspace is non-ready or its mapping is unresolved, report the blocker and retain the chosen route and partial state. Pause work that depends on readiness or mapping, including affected edits or local execution. Continue read-only assessment where the selected scope and independently verified evidence support it.

Retain the selected workspace, its verified mapping, the target, and the selected display mode as applicable. Use fixed display for historical PRs and selected fixed comparisons. For PR live links use `view="worktree"` and bind `repo` to the exact workspace verified here, including a verified local alias. If source identity cannot be verified, resolve a viable route through the user's existing choice or an explicit selection.
