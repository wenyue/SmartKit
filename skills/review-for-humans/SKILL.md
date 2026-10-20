---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help the human understand what each change does, whether it is reasonable, and whether its implementation is elegant. Review the selected comparison read-only, then carry out the actions the user selects. Capturing evidence and preparing diff links are part of review; changes to reviewed files or Git state need the applicable action's authorization.

For every question, offer a list of concrete choices consecutively labeled **A**, **B**, **C**, and so on, including scope questions, workspace creation or synchronization, remedies, and closing menus. Describe the effects in the conversation's language and ask for a letter. Interpret letters case-insensitively against the latest menu; accept unambiguous natural-language selections, including agreement to a clearly specified action. M and O IDs select items, not actions. Clarify ambiguous replies; questions and disagreements do not authorize actions.

## Establish the comparison

| Requested scope | Review evidence |
| --- | --- |
| PR | Identify the PR and its source repository and branch. Complete the workspace check, then pin the PR base and head and apply the Viewed filter below. |
| Branch | Pin its tip and its merge-base with a reliably established comparison base. Ask when the base is uncertain; do not assume `main`. |
| Local changes, or no explicit scope | Compare the index with the worktree: unstaged changes only. |
| Selected files | Filter the applicable comparison to those files. |

An explicit PR or branch comparison excludes local uncommitted changes unless requested. Honor an explicitly selected historical version. Preserve the selected scope when applying other review guidance with different defaults.

For the local default, skip staged-only edits and review only the unstaged portion of a partially staged file. Reverting a staged edit in the worktree is an unstaged change relative to the index. Include untracked files as additions only when explicitly requested. Another explicitly selected local comparison overrides these defaults. An empty comparison stays empty.

### Check the review workspace

Before every PR review, run the shared read-only workspace inspection, including when the current checkout already uses the PR branch. Resolve `local_web` from the loaded SmartKit resources and follow its help for inputs and results:

```text
python "<local_web>" --help
python "<local_web>" diff --inspect --input "<context.json>"
```

Supply current authoritative PR metadata, distinguishing the PR-owning repository from its source fork. Use the returned workspace matches and freshness results for the decisions below; stale local tracking data cannot establish the PR's current head.

The inspection command requires PR context. For a branch-only review, inspect the current checkout and registered linked worktrees through read-only Git. Check against its authoritative remote when specified or reliably established; ask for a missing target rather than inventing an upstream. A deliberately local branch or local unstaged review needs no remote synchronization. Keep an explicitly selected historical version as the review target.

For a selected workspace, use read-only Git to inventory staged, unstaged, and untracked work; the PR inspection reports these only as a dirty indicator. Report its path, branch, commit, local changes, and relationship to the target. Unknown evidence is not clean or current. Resolve the applicable decision before filtering or displaying files; fixed-snapshot alternatives below are PR-only and require the fixed comparison's evidence.

| Workspace state | Choices |
| --- | --- |
| No verified match | Create a clean worktree at the verified target; review the fixed PR comparison without creation; or cancel. |
| Same commit | Continue without a sync question. Disclose local changes when live links will show them. |
| Behind | Synchronize using a concrete safe plan; review the fixed PR comparison without syncing; or cancel. |
| Ahead or diverged | Explain the local commits and, for divergence, the distinct remote commits. Offer to keep them and use live links for the fixed review, use fixed PR snapshot links, or prepare a synchronization plan for a separate decision. |
| Unknown | Explain the missing evidence. Offer an available way to obtain it, an already verified fixed PR comparison, or cancellation. |

For a branch-only review without a usable display workspace, offer authorized creation, another scope, or cancellation.

Use [create-worktree](../create-worktree/SKILL.md) for authorized creation, with the user's clean choice and verified immutable base. Before a sync, disclose its workspace, target, method, affected commits, and preservation of staged, unstaged, and untracked work. Obtain authorization for those concrete effects; “sync” does not authorize an unspecified history change or publication.

Verify creation or synchronization and preservation of local work before reviewing, then refresh PR base/head and Viewed evidence and reassess changed targets. After interruption, inspect the actual result before retrying; keep review pending until verification or an explicit change to supported fixed review or cancellation. Retain the verified workspace and selected link mode.

### Filter files and retain the snapshot

For PRs, obtain complete file-level Viewed states for the current authenticated GitHub viewer. Exclude `VIEWED`; include `UNVIEWED` and `DISMISSED`. Complete pagination and verify that base and head remain unchanged during acquisition. Approval, comments, and prior chat display do not establish Viewed state, and current states do not establish the filter for a historical snapshot. An explicit request to include viewed files overrides the filter. If required states are unavailable, pause and offer to obtain them or review all otherwise eligible files without filtering.

Exclude test files from file reports, modification counts, and progress. Apply selected-file, Viewed, and local-scope filters before counting. These report filters do not exclude changes from a later full-branch commit or its checks. Order files like GitHub's Files changed directory tree: recursively list changed files in subdirectories before direct files; use observed sibling order when available, otherwise sort sibling directories and direct files by name. Thus `src/z/api.dart` precedes `src/a.dart`.

Retain fixed before-and-after evidence, pinned comparison commits, the ordered file list, and PR viewer/filter evidence. For local comparisons, also retain the original index baseline, even when the user chose another before version, so completion can account for existing staged work. State the scope and exclusions before the first group. If no files remain, report that and finish without a fabricated report or progress fraction.

When required scope or source evidence is unavailable, identify the gap and pause dependent review. Keep a known file with incomplete evidence in the total and report insufficient evidence for the affected judgment. Assess defects introduced, triggered, or aggravated by the selected change within its modifications, including when the evidence is in unchanged code. Unrelated pre-existing issues use O observations below.

## Prepare filename links

Use the shared tool for every reviewed filename link, following its help for inputs:

```text
python "<local_web>" diff --input "<batch.json>"
```

Prepare links from the retained comparison: capture local index-based links alongside the review snapshot; use the fixed before commit, existing blob, or genuine absence for branch and PR comparisons. Supply the pinned reviewed PR head and other PR metadata, and rename paths, as the help requires.

For PRs, set `view="snapshot"` for an explicitly historical target, a selected fixed comparison, or unavailable source identity, with the required fixed evidence. Use `view="worktree"` and the verified path for an explicitly selected or newly prepared workspace, including a local alias; otherwise use the default selection. A branch-only review supplies its verified display workspace without PR context.

Use returned IDs to associate the returned Markdown with files. Keep review evidence and Viewed eligibility tied to the fixed assessed version, even if live links or GitHub show newer contents.

If link preparation fails, report the diagnostic and pause the dependent report; preserve the selected comparison and mode when resolving it. Link generation alone does not prove editor display.

## Explain each file

Use [report examples](references/report-examples.md) to calibrate explanations, observations, and menus. Begin each complete file block with `📄 **[path](diff-destination)**` and a short overview of the file's responsibility and overall change. Explain user or caller effects in ordinary language, retaining technical details that affect the judgment.

Group modifications by the problem or scenario they address. Keep related implementation steps together; split when changes are independent or cannot share one simple explanation. A localization file is one modification. Minor accompanying edits can appear in the overview or be omitted.

Label modifications `🔧 **M1** - **<title>**`, numbering continuously across files and groups. Retain M IDs for findings, suggestions, selections, and re-reviews. Keep emoji and surrounding punctuation outside bold; preserve punctuation intrinsic to code and paths.

### Give two independent judgments

Every modification gets both judgments, each in its own paragraph with an explicit conclusion and reason. Apply them to code, prose, and translations alike. Use ⚖️ for reasonableness and 🎨 for elegance, without repeating the dimension's name after the emoji.

| Judgment | Basis |
| --- | --- |
| ⚖️ **Reasonable**. | The change serves the task, is correct and safe, fits its scope, and has justified costs. |
| ⚖️ **Unreasonable** (P1): | Evidence establishes a material defect, unnecessary scope, or unjustified cost. Explain its impact and recommend a concrete correction with its benefit. Use the actual P0–P3 severity. |
| 🎨 **Elegant**. | The change addresses the problem at the appropriate responsibility, with clear structure and little unnecessary state, branching, or repetition. |
| 🎨 **Can improve**. | Identify avoidable complexity or repetition and a supported simpler approach, explaining its clarity or maintenance benefit. A style preference alone is insufficient. |
| ⚖️ **Insufficient evidence**. or 🎨 **Insufficient evidence**. | Name the missing evidence for that dimension and how to resolve it. The other dimension may still have a supported judgment. |

A reasonable change can be inelegant. Elegance concerns are optional improvements; only a separately evidenced reasonableness defect creates a fix-or-ignore gate. Assign severity only to unreasonable findings: P0 critical/immediate, P1 serious/prompt correction, P2 normal priority, P3 lower-impact but worth correcting. Base it on consequences and affected conditions.

Retain material findings and qualifications from the underlying review, including task and standards concerns. Distinguish checks actually performed from author-reported results.

### Choose the explanation's depth

Use a **compact** explanation for straightforward behavior with clear scope and no material risk or trade-off: one short before-and-after paragraph, then the separate ⚖️ and 🎨 paragraphs. It uses no examples, snippets, emoji prefix, or Before/After labels.

Use an **expanded** explanation for complex mechanisms, important contracts, material findings or trade-offs, or key evidence gaps: ⏪ **Before**, ⏩ **After**, then the two judgments. For code, show the smallest useful before-and-after snippets from the retained evidence and explain how they cause the compared behavior. Keep relevant error, state, or lifecycle conditions. Clearly label illustrative simplifications and preserve their behavior; omit code when it adds no understanding. A one-line diff can still need expansion.

## Display groups and maintain progress

Separate complete file blocks with `---`. End a group after the file that brings it to at least 10 modifications; never split a file. Display the final shorter group when the scope ends. End with `---` and `📊 **Progress**: **displayed files / files requiring review**`, explicitly describing the count as displayed files.

Across replies, retain group membership, reviewed changes, next position and M ID, judgments, finding decisions, outstanding suggestions, and each group's verified completion results. Count each main-review file once. A full-branch commit can clean the worktree before all files are displayed; continue unseen groups from retained evidence rather than rebuilding the scope from the new index. Update totals only for actual scope changes.

### Keep incidental observations separate

During necessary reading, report an unrelated pre-existing issue only when evidence establishes both the issue and that the selected change neither introduced, triggered, nor aggravated it. This does not authorize a broader audit.

Give observations continuous **O1**, **O2**, and subsequent IDs. Initially show them only in the group closing, under `📌 **Incidental observations (outside this review's scope)**`, with a title, source location/link, evidence and impact, independence from the selected change, and a recommendation with its benefit.

O items add no main-review files, modifications, progress, or Viewed eligibility. Advice alone does not block advancement or authorize repair. Unqualified fix, optimize, and ignore-all actions exclude them. A selected O repair needs its own outcome, authorization, checks, and dedicated re-review; it remains separate unless the user explicitly expands the main scope.

## Offer actions

| Action | Effect |
| --- | --- |
| **fix** | Repair selected pending unreasonable findings; unqualified fix selects all displayed outstanding findings, including earlier groups. |
| **ignore** | Mark only selected findings ignored, retaining severity and impact. If several are possible, clarify the selection unless the user explicitly chose all. |
| **optimize** | Implement selected supported 🎨 suggestions; unqualified optimize selects all displayed outstanding suggestions. Pending unreasonable findings remain pending. |
| **pass and continue** | Commit the full disclosed branch scope, perform disclosed PR publication and Viewed recording when applicable, verify completion, then advance. |
| **continue** | Advance without staging, committing, pushing, or marking Viewed. Retain modifications and suggestions. |

Localize action names and descriptions to the conversation's language. M IDs narrow an action to items; they do not select whole-group completion. Advance to the saved next group, or use **pass and finish** and **finish** when all files are displayed.

Keep these scopes distinct:

- **Review and progress:** the selected, eligible files and deltas actually displayed.
- **Commit and publication:** all outstanding branch changes and, for a push, the full outgoing ancestry, subject to the preparation and confirmation below.
- **Viewed:** eligible reviewed files in the current group, plus earlier files explicitly included in an intermediate completion. Final **pass and finish** covers every displayed reviewed group, including those advanced with **continue**.

Inclusion in a commit or push is not review. A local or branch review needs no PR and grants no push authority. PR completion requires a verified PR and explicit authorization for the disclosed publication delta. Neither action approves or merges the PR; ignored findings remain ignored.

### Decide which actions are ready

Both advancing actions require all displayed unreasonable findings repaired or explicitly ignored, available correctness/version evidence, successful required review checks, completed affected re-reviews, and any previously selected completion operation fully verified. Optional improvements and missing elegance evidence alone do not block advancement.

Before offering completion, perform derivable read-only preparation for its actual effects. Use the following priorities:

| State | Menu |
| --- | --- |
| Pending unreasonable findings | Offer fix and ignore, plus supported optimize. Explain why both advancing actions are unavailable. |
| Missing correctness/version evidence, failed or incomplete review checks, or stale review | Explain the gap and its remedy; complete authorized work before offering advancement. |
| Selected commit, push, or Viewed operation unfinished | Preserve that selection. Once ready, offer its remaining steps as the same completion action; ordinary continue cannot bypass it. |
| Advancement ready but completion's target, interface, checks, or safe scope unavailable | Explain the concrete prerequisite. Continue remains available. Checks for extra branch content block continuation only when they affect the review. |
| Extra content needs inclusion confirmation | Disclose it and offer a combined confirmation-and-completion choice when all other prerequisites are ready, alongside continue. |
| Completion ready | Offer its actual remaining commit, push, and Viewed effects, alongside continue. Reuse verified completed work; no empty commit or unnecessary push. |

For a ready local/branch review, completion commits outstanding changes and verifies them. For a ready PR, it also publishes unpublished changes when authorized and records eligible files Viewed. If there are no writes left, state the verified results it will reuse. Add optimize whenever supported suggestions remain.

Every closing accounts for completion readiness, including after a repair or in a dedicated re-review. Put unavailable-action explanations outside the executable menu. After progress, use these sections in order, omitting empty ones:

1. **Pending findings**, including earlier groups: `**M1** (P1): <impact summary>`.
2. **Optional improvements**, including earlier groups: ID, proposed improvement, and benefit.
3. 📌 **Incidental observations (outside this review's scope)**.
4. **Available actions**, using the lettered choices and concrete effects described above. Name the full commit scope, any extra-content confirmation, publication delta, and Viewed set when applicable.

End with one short instruction to enter a letter; omit it if no choice remains. [Example closings](references/report-examples.md#example-closings-for-different-results) show the presentation of these states.

If the user asks to advance while blocked, explain the pending IDs or prerequisites and regenerate the available menu; continue never means ignore. Questions and disputed findings call for answers or reassessment, not automatic advancement. An explicit stop or pause is always allowed: report displayed progress and unresolved findings, evidence, modifications, publication, or operations without claiming completed work.

## Repair and re-review

Limit an authorized fix or optimization to selected items and necessary supporting changes; optimization preserves supported behavior and contracts. After reviewed content changes, or after any O repair:

1. Run required checks successfully and refresh before-and-after evidence and links. For unpublished PR changes, keep both the pinned remote version and the checked local content intended for publication; keep O evidence separately.
2. Independently re-review changed or affected previously reviewed parts, including unexpected changes. Display complete updated file blocks with both judgments in a dedicated reply separate from unseen files. For an O repair, assess the behavior and affected dependencies in a dedicated O re-review with its source location, before-and-after explanation, and both reasoned judgments.
3. Retain original M/O IDs and group membership; do not count a file again. O re-review creates no main progress or Viewed eligibility. Mark repairs or suggestions complete only when checks and re-review confirm them.

A single fix, ignore, or optimize ends with an updated menu, without advancement. An explicit compound request authorizes its ordered effects, including dedicated re-review before completion and advancement; continue those authorized steps without routine reconfirmation. New findings, failed checks, changed effects, or newly discovered extra content pause the dependent step. Independently authorized optimization can proceed while findings remain, but cannot open the advancement gate.

## Prepare completion

### Account for the whole branch

Identify the exact repository, branch, and worktree to commit. Inventory all staged, unstaged, and untracked changes, plus every existing commit a proposed push would publish. Retain the branch tip, index, worktree and applicable untracked content as recovery evidence.

Completion commits the full outstanding branch state, including tests, supporting/generated files, staged-only changes, and undisplayed or excluded files. Honor repository restrictions on sensitive, ignored, or disposable files; resolve any unsafe inclusion with the user instead of silently narrowing the commit. For partial staging, establish the coherent final worktree content, explain any staged content it supersedes, and retain the original index. Unresolved content conflicts block completion.

Establish provenance from this conversation's recorded actions and baseline, including mixed-origin hunks. For changes made elsewhere or of unknown origin, disclose the concrete paths or commits, behavior, and material effects, and obtain explicit inclusion confirmation before committing or publishing them. A prior confirmation covers the same content and effects; generic approval of a reviewed group does not cover undisclosed extras. If confirmation is declined or absent, preserve the changes and leave full-branch completion pending; offer continuation or a revised scope, not an automatic smaller commit.

Explain how the commit and push scope differ from displayed review and Viewed scope. Same-conversation extras need accounting and checks, though no additional provenance consent. Run required checks for the whole intended commit/publication, assess effects on displayed review, and complete dedicated re-reviews where needed, including every selected O repair. Inclusion consent cannot replace review or checks.

### Prepare PR publication and Viewed recording

Before offering PR completion, verify the PR-owning repository, source branch/remote, viewer, current base/head, outgoing ancestry, and available interfaces for its writes and readbacks. Disclose the entire push delta separately from the Viewed set, including existing unpushed commits. If publication cannot use a normal push to the verified source branch, explain the missing prerequisite; this action does not implicitly authorize rebasing, force-pushing, or excluding commits.

Viewed covers a whole file at a PR version. Before offering to mark a path, compare its complete intended PR delta with the retained displayed assessments. Show every uncovered hunk in a dedicated re-review with both judgments, even when it is independent extra content already approved for inclusion. Preserve IDs, original group membership, and progress. An O re-review does not make an otherwise ineligible path eligible.

If coverage needs missing evidence or a scope decision, leave the path unmarked and completion unavailable or pending. Preserve the selected Viewed set rather than dropping a path to finish. Passing checks, inclusion consent, and unchanged earlier hunks do not supply missing coverage.

## Execute completion and verify it

Execute only the effects disclosed and authorized by the selected action. Reuse verified commits, pushes, and Viewed results instead of repeating writes.

1. **Revalidate.** Compare the branch tip, index, worktree, review evidence, and any remote base/head and outgoing ancestry with the prepared state. Resolve drift with refreshed inventory, applicable checks and affected re-review; changed or new extra content needs renewed inclusion confirmation.
2. **Commit when needed.** Stage the full disclosed final content and verify the index against the intended tree. Commit through normal hooks, then verify the commit, parent, full tree, index, and remaining worktree state. Hook changes need applicable checks and affected re-review; changes beyond confirmed content also need updated consent. All intended changes must be committed without unexplained residue. A local/branch completion can now advance.
3. **Publish when authorized and needed.** Revalidate the full outgoing delta after hooks, push normally to the verified PR source branch, and read back base/head and the complete published delta. Confirm the expected commit, checked content, and valid displayed assessments.
4. **Record Viewed.** On the actual PR version, verify the viewer and both commit IDs and confirm complete per-path coverage for the selected set. Mark only eligible selected paths still awaiting Viewed. Read back every selected path, including reused results, and the PR version. All must be `VIEWED`, with base/head unchanged during recording.
5. **Advance or finish.** Acknowledge the verified result and resume from the saved position. Final completion accounts for all displayed groups, including earlier groups advanced without recording.

An intended new head needs verification, not repetition of already covered review. Unexpected changes to content, base, or affected dependencies require affected re-review; text equality alone cannot prove unchanged effects. Refresh evidence and obtain a new selection when the result no longer represents the authorized reviewed version. Marking a newer version does not prove it was reviewed.

### Recover an unfinished operation

When a write, interface, or verification fails, pause without advancing, automatic rollback, or substitution of continue/finish. Report confirmed, failed, and unknown effects, including commits, push state, remaining changes, partial staging, and Viewed paths.

Keep the inventory, provenance confirmations, fixed evidence, selected publication and Viewed scopes, viewer/version, group status, and resume position. After a lost response, inspect actual local and remote state before retrying. Once ready, resume only the missing steps of the same completion operation; do not silently add content, enlarge an intermediate Viewed set, or repeat successful writes.

Completion requires every required readback. An explicit stop may leave residual work, which must be reported. Preserve progress after successful recovery; do not reapply filters to remove files already displayed.
