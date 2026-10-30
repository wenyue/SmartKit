# Completion

Read before preparing/offering completion effects, executing them, or recovering unfinished effects. The Skill entry owns ordinary conversation, group choices, and repairs/re-review. This guide owns concrete commit/publication/Viewed preparation and its conditional consent or recovery decisions.

## Keep three scopes separate

| Scope | Coverage |
| --- | --- |
| Review/progress | Selected eligible deltas displayed and assessed. |
| Commit/publication | Full outstanding branch state and all outgoing ancestry, after checks and inclusion consent. |
| Viewed | Whole-file PR deltas at a verified version: current displayed group plus earlier groups explicitly included; final Pass covers all displayed reviewed groups. |

Commit/push is not review. Local/branch completion creates no PR or push authority. PR publication requires a verified PR and authorization for its disclosed delta; neither approval nor merging is included.

A PR with no unpublished review work or unfinished selected commit/publication can record Viewed without committing/pushing. Establish read-only that unrelated local differences, including submodule checkout differences, preserve the fixed delta, dependencies, and whole-file coverage. Preserve them; their presence alone requires neither publication nor inclusion consent. Review repairs/optimizations must reach the verified PR version before Viewed.

## Prepare a complete action

For commit/push identify exact repository, worktree, and branch; inventory staged/unstaged/untracked content and, for publication, every outgoing commit. Retain tip, original index, worktree, and applicable untracked recovery evidence. Commit includes the full outstanding branch state: tests, generated/supporting files, staged-only and undisplayed/excluded files. Resolve sensitive/ignored/disposable inclusion restrictions explicitly rather than silently narrowing the commit. Content conflicts block completion.

For partial staging establish coherent final worktree content, disclose superseded staged content, and retain original index. Establish provenance from conversation actions and baseline, including mixed-origin hunks. Disclose other/unknown-origin paths or commits, behavior, and material effects; obtain explicit inclusion confirmation. Prior consent covers unchanged content/effects; group approval does not cover undisclosed extras. Without consent preserve content and full-branch scope: no automatic smaller commit, cherry-pick, history rewrite, or publication.

Same-conversation extras require inventory/checks but no extra provenance consent. Check the entire proposed commit/publication, assess displayed review's validity, and complete affected dedicated re-review, including every selected O repair. Inclusion consent replaces neither checks nor review.

For PR effects verify owning/source repositories, source branch/remote, viewer, base/head, and usable write/readback interfaces. Disclose publication's whole outgoing ancestry/delta separately from Viewed. Except for the recorded amendment route below, publication uses normal push; completion authorizes no rebase or exclusion of commits.

Compare each selected Viewed path's complete intended PR delta against displayed assessments. Re-review uncovered hunks in a dedicated reply with both judgments, even if approved independent extra content. Preserve IDs/groups/progress; O re-review grants no main eligibility. Missing coverage/evidence/scope leaves the path unmarked and completion pending: never drop selected paths to finish. Unchanged earlier hunks, passing checks, and inclusion consent cannot supply coverage.

Perform derivable read-only preparation before asking for a decision. Disclose actual remaining writes, full commit/publication contents, Viewed set, inclusion question, checks/limits, and verified effects to reuse. Extra branch checks block continuation only if they affect review. No empty commit or unnecessary push is needed.

## Explain the actual choice

Before a normal Pass option, give the entry's group menu the exact remaining effects: which branch content will be committed, whether and where it will be pushed, which files will be marked Viewed, and whether the next step is another group or the end. Omit completed effects rather than hiding needed writes behind “Pass.”

If extra-content consent is undecided and every other prerequisite is ready, use A **Continue** (recommended), or **Finish** for the final group: proceed/end without committing/publishing/recording; B **Pass**: explicitly confirm the named extra content and perform the full disclosed completion; C **Optimize** only if optional suggestions remain. Explain the extra paths/commits and concrete impact first. Declined inclusion is not silently re-asked: preserve content and full-branch scope, allow review continuation where valid, and change the completion outcome only through a new explicit request.

If a user-owned fact is missing, ask it directly. Do available checks and covered-scope dedicated review without another choice. Whole-file coverage gaps are not permission questions when the fixed hunk is already available within authorized review scope.

## Execute and verify

Read [Completion Helper](completion-helper.md) and its help before using supported PR operations. The helper owns mechanical freeze/execute/resume and logs; the Agent owns review, successful checks, provenance consent, coverage, and authorization. Supported preparation may retain private evidence/Git objects while preserving real index, branch, and files. Helper unavailability waives no prerequisite.

Use this manual workflow for local/branch completion or unsupported helper cases. It also states required helper outcomes, not a second implementation to run after the helper.

1. Revalidate evidence, tip/index/worktree, affected dependencies, and relevant PR base/head and outgoing ancestry when publication is involved. Drift needs inventory, checks, affected re-review, and renewed extra-content consent for changed effects. An expected new head needs version/content verification, not repeated covered review; equal text alone does not prove equal effects.
2. When a commit is needed, stage full disclosed final content and verify the intended index tree. Use `git commit --amend` when recorded actions establish HEAD as this review's fix/optimization commit and both current branch and any push target are neither `master` nor `main`; otherwise create a new commit. Run normal hooks; verify commit, parent, full tree, index, and remaining worktree. Hook changes require checks/re-review; effects beyond consent require updated consent. Leave no unexplained residue. Local/branch completion can now advance or finish; steps 3–4 apply only to PR completion.
3. When PR publication is authorized and needed, revalidate outgoing ancestry after hooks. Replacing an already-published review commit uses `--force-with-lease=<ref>:<verified-old-remote-SHA>` to the verified source ref; otherwise push normally. Stop on drift/rejection. Read back base/head and complete published delta; confirm expected commit, checked content, and valid assessments.
4. For PR Viewed recording, on the actual PR version verify viewer, both commit IDs, and whole-file coverage for the selected set. Mark only eligible selected paths still awaiting Viewed. Read back every selected path, including reused markings, and base/head. All paths must be `VIEWED`, with unchanged base/head throughout recording.
5. After every selected effect/readback succeeds, acknowledge them and advance from the saved position or finish. Final completion covers all displayed groups, including groups advanced without recording.

## Recover the selected operation without restarting the conversation

On write/interface/verification failure preserve confirmed, failed, and unknown effects: commits, push state, partial staging, remaining files, and Viewed paths. Do not advance, roll back automatically, or substitute Continue/Finish.

Retain inventory, provenance decisions, fixed evidence, publication/Viewed sets, viewer/version, group status, recovery state, and next position. After interruption/lost response inspect actual local/remote state before retrying. Reuse verified effects and resume missing steps when ready. New facts can require checks/re-review or consent for changed effects, not repeated successful writes or silently narrower scope.

Every required readback must succeed. Once unchanged authorized effects are ready, resume missing steps without another Pass question. If access/readback is externally unavailable and the user has no remedy, report completed, unknown, and pending effects and retain the operation. Do not offer Wait/Resolve choices, promise a monitor, or start polling. At a supported later opportunity, inspect actual state and resume only missing effects under the original authority.

Ask directly for a missing user fact. If verified changed effects require new consent, disclose the revised scope and use A **Stop** (recommended): stop with residual effects reported, or B **Pass**: explicitly approve the revised effects and resume the same operation. New review findings use the entry's necessary-issue choices while the selected completion remains pending; Continue/Finish cannot bypass it. No extra content, checks, coverage, or permission is inferred from the old selection.

An explicit stop reports residual work as incomplete. Preserve progress and do not reapply filters to remove displayed files.
