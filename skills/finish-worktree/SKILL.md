---
name: finish-worktree
description: Finish an isolated linked Git worktree by keeping it for later, publishing a pull request, merging locally, transferring its changes back to a checkout, or explicitly discarding it.
---

# Finish Worktree

Choose where the work should go, verify that result, and leave any remaining work easy to resume. The implementation workflow owns content, checks and review; the issue tracker's owner decides when to close its records. A PR or a transfer is a handoff, not proof that the result was integrated.

## Choose the outcome

Confirm the source's physical path, Git worktree registration, repository, branch and HEAD against the intended task. Establish its scope, local changes and any unfinished earlier operation. Reuse an existing choice and authorization; ask when the destination or a consequential choice is missing. Read the selected route before changing state:

| Outcome | When to use it |
| --- | --- |
| Keep for later | Leave the work available, including dirty or unfinished work. Follow the guidance below. |
| [Create a pull request](references/create-pull-request.md) | Publish the accepted commits and hand them off for review. |
| [Merge locally](references/merge-local.md) | Deliver to an authorized local branch by fast-forward. |
| [Return for review](references/return-for-review.md) | Combine task changes with a checkout's working files while preserving its HEAD and complete index. |
| [Explicit discard](references/discard.md) | Remove work whose actual loss the user has authorized. |

A blocked route does not authorize a different outcome. Preserve commits unless consolidation is explicitly requested or required by project policy. Publication, local integration and requested consolidation require [History Preparation](references/history.md); keeping, transferring and discarding do not otherwise require formal review. Independent project and caller requirements still apply.

To **keep for later**, leave files, indexes and refs untouched. Report the worktree, branch, HEAD, unfinished work, pending checks or operations, and who will continue with what next action. Refresh that account if concurrent work changes it. There is no need to clean or review work merely to keep it. Retaining the residue of an earlier failed operation does not make that operation successful.

## Handle changes and interrupted operations

Immediately before a write, refresh the identities, refs, files or host state it depends on. Coordinate writers and stop the affected operation when those facts change. Reuse immutable evidence and valid checks; changes to previously accepted content go back to the implementation workflow for the applicable checks and review. If an essential capability is unavailable, retain the work and report what is needed to continue.

After a failure or missing response, inspect what the original operation actually did before retrying. Continue only the unfinished work whose preconditions and authorization still hold. For example, a successful push followed by failed PR creation needs PR recovery; delivered work followed by failed cleanup needs cleanup alone. If the effect cannot be established, keep the uncertainty visible and retain the state needed to resolve it. For an interrupted file transfer, keep the source and external backups while inspecting the partial result under its route.

## Clean up and report

Remove only identified, task-owned items that are no longer needed and whose removal is authorized. Retain dirty worktrees, uncertain ownership and anything needed for review, continuation or recovery. Inventory ignored contents before removal could reach them; ordinary cleanup does not authorize losing them. Use the creating host's removal interface for host-created worktrees.

Before deleting a branch, establish that no worktree uses it. Delete owned branch and recovery refs with their expected old OIDs. Observe each removal before proceeding; partial cleanup does not undo a verified handoff or delivery. Keeping an item is a valid finish when its location, next owner and condition for later removal are clear. Transfer backups and sources have the stricter acceptance condition in their route.

Report the selected outcome and what was verified: relevant paths, branches/commits or PR URL, checks, retained work and the next action. Distinguish completed actions from failures or uncertainty; for example, “delivered to main; source cleanup failed” must not prompt another integration. Finish when the selected result is verified and remaining items are either safely removed or deliberately retained with enough information to continue.
