# Workspace

Read before workspace preparation or links for PR and remote-aligned branch review. Establish the facts needed to choose an alignment route before asking about effects. Ordinary facts and clarification follow the Skill entry; this guide owns workspace choices.

## Establish repository, branch, and version

Use current authoritative PR metadata for owning repository, source repository/fork, source branch, and target commit. A selected historical version remains the target; local tracking cannot establish current PR head.

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

## Ask about concrete alignment, not internal states

Establish facts that materially affect the choice. For current-workspace alignment, disclose workspace, target branch/commit, method, affected commits, and preservation of index/worktree/untracked content and local commits. With a fully verified safe plan, one choice may explicitly combine checkout and exact-target synchronization. If the later step still depends on unknown facts, offer only the verified earlier step, then inspect and resolve its dependency before proposing the rest. Checkout alone never authorizes unstated synchronization.

Use the first applicable situation below after inspection. Present all applicable choices in the stated order, label consecutively, and make the first option A/recommended. Each option uses the short action word followed by its exact effects. Create proposes a clean isolated workspace at the verified target; include it unless a known blocker prevents it.

| Situation | Ordered real choices |
| --- | --- |
| Related repository, wrong branch, safe current alignment plan, source branch not owned elsewhere | **Switch** to the source branch, including synchronization only when explicitly in the fully verified plan; **Snapshot** if available; **Use** another verified workspace if available; **Create** isolated workspace; **Stop**. |
| Corresponding branch/workspace behind target, safe exact-target synchronization | **Sync** to the exact target; **Snapshot** if available; **Use** another verified workspace if available; **Create** isolated workspace; **Stop**. |
| Corresponding branch/workspace ahead/diverged with fixed review evidence | **Snapshot** if available; **Keep** the verified differing live workspace if available, with its version difference disclosed; **Sync** only with a verified preservation plan; **Use** another verified workspace if available; **Create** isolated workspace; **Stop**. |
| Current route unknown/unrelated/unusable/owned elsewhere, or checkout/synchronization known unsafe or unavailable | **Use** a verified alternative workspace; **Snapshot** if available; **Create**; **Stop**. |
| Repository/branch/version match, or a fixed comparison was selected | Proceed without another alignment choice. |

A menu needs a viable non-stop route. If none exists, ask the specific user-owned fact that could establish one, or report the concrete limitation; do not invent “get evidence” or Stop-only menus. When several existing workspaces qualify, list their concrete paths under Use while retaining Snapshot, Create, and other feasible routes. Ask which path directly only after the user selects Use and the path remains unresolved; a path question must not select that route for them. Unknown local facts do not invalidate independent verified alternatives. Branch-only review has no PR snapshot fallback.

After Create is selected, use [create-worktree](../../create-worktree/SKILL.md) for creation checks, authorized creation, and environment assessment with the user's clean choice and verified immutable base. Reuse existing choices; resolve only outstanding decisions. No alignment choice authorizes unspecified history changes or publication.

## Verify before reviewing

After alignment rerun inspection on the exact path. Verify branch mapping, target commit, and preserved work. Refresh PR base/head and Viewed evidence and reassess changed targets before review/links. After interruption inspect actual results before retrying. Dependent review stays pending until verification, explicit fixed-comparison selection, or stop.

Retain workspace, source-branch mapping, target, and snapshot/live mode. Historical/fixed PR review or unavailable source identity uses snapshot mode; live PR links bind the exact verified path, not automatic discovery.

For branch-only review use read-only Git for checkout/worktrees and an explicit or reliably established authoritative remote; never invent an upstream. PR inspection requires PR context. Without a display workspace resolve a verified workspace/creation or another scope. Deliberately local branch and local unstaged reviews need no remote synchronization.
