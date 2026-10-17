---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand a PR, branch, or local change: what changed, whether it is reasonable, whether its implementation is elegant and tasteful, and where their attention is needed. Use this Skill only when the user requests it, loading the necessary Skills and Rules for the work.

Review the selected scope read-only, then carry out only the effects authorized by the user's selected actions under the scope and verification requirements below. Read-only review permits capturing the comparison, resolving existing Git objects, and running the shared diff-link command; keep the reviewed files and Git index unchanged until an authorized action.

## Establish the review scope

### Choose the comparison

Identify the task's intended outcome and select the comparison below. Obtain its before-and-after evidence through available read-only Git or GitHub interfaces, such as a CLI, connector, or authenticated GitHub UI.

| Requested scope | Comparison |
| --- | --- |
| A pull request | Obtain the PR's changed files and comparison evidence, recording its base and head commit IDs. Review that fixed PR version, applying the file-level viewed-state filter below. |
| A branch, with or without an explicit base | Resolve the reviewed branch tip and a reliable comparison base; compare their merge-base with that tip, pinning both commit IDs. If the base cannot be established reliably, ask the user rather than assuming `main`. |
| Local changes, or no explicit scope | Compare the index with the current worktree, using `git diff` or equivalent evidence. |
| Selected files | Filter the applicable comparison to those files; count and report the selection rather than the full PR or branch. |

An explicit PR or branch comparison does not include local uncommitted changes unless the user requests them.

### Review local changes

The local default reviews only unstaged changes, using the index as the before version. Skip staged-only edits; for a partially staged file, review only its unstaged portion. If a staged edit is subsequently reverted in the worktree, that reversal relative to the index is an unstaged change to review.

An explicit request to include staged changes or use another local comparison overrides this default. An empty comparison remains empty: do not include earlier commits or fall back to staged changes or the last commit. Exclude untracked files unless the user explicitly includes them; when included, review them as additions.

### Filter PR files

For a PR, default to skipping files marked viewed by the current authenticated GitHub viewer. Obtain the complete file-level states through an available authenticated read-only GitHub interface; GitHub GraphQL exposes them as [`PullRequestChangedFile.viewerViewedState`](https://docs.github.com/en/graphql/reference/pulls#pullrequestchangedfile). Exclude `VIEWED`; include `UNVIEWED` and `DISMISSED`, which means the file changed since it was last viewed.

Complete pagination and check that the PR's base and head remain unchanged while obtaining the file list and states, so the filter belongs to the pinned version. Current viewed states cannot establish a filter for an older PR snapshot. A PR approval, comments, or files displayed in an earlier chat are not evidence of a file's viewed state.

The user can explicitly include reviewed files, overriding that exclusion. If required viewed-state evidence is unavailable, name the missing prerequisite and pause the dependent review; ask for access to that evidence or whether to include all otherwise eligible files without the filter. Treat missing state as unknown rather than `UNVIEWED`.

### Keep a fixed snapshot and file list

Preserve this Skill's selected comparison when loading other review guidance with different scope defaults. Keep a fixed review snapshot containing:

- The comparison commit IDs for PRs and branches.
- The local comparison's before-and-after content and index baseline. Retain that index baseline even when an explicitly selected comparison uses another before version, so later completion can account for existing staged work and preserve its recovery evidence.
- The viewer identity and file-level states used for PR filtering.

Keep an ordered file list matching GitHub's Files changed directory tree for every scope: at each directory, recursively list each subdirectory's changed files before the files directly in that directory. Use the PR's actual tree sibling order when accessible; otherwise sort sibling directories and direct files by name. For example, `src/z/api.dart` precedes `src/a.dart`; sorting complete paths from `git diff` does not establish that order.

Skip test files in the human review: do not give them file reports or count them toward progress or modifications. Apply the scope filters before counting; skipped viewed PR files and staged-only local files likewise receive no file reports, progress credit, or modifications. These display filters do not exclude changes from a later branch commit or its required checks. Count the remaining files before displaying the first group. Briefly identify the scope and exclusions so the reader can interpret the total. If no files require review, say so and finish without manufacturing a report or a progress fraction.

When scope, required guidance, or source evidence is unavailable—including a usable `HEAD`, requested refs or PR evidence, or a required interface—name the missing prerequisite and its effect, then pause the dependent review. Keep a known file with incomplete evidence in the total, explain the gap in its report, and use an insufficient-evidence evaluation where necessary; unavailable evidence does not justify invented facts, totals, or a completed assessment.

Assess the selected comparison and its effects, using relevant context as needed while preserving the file filters and test exclusions. A defect introduced, triggered, or aggravated by the selected change belongs in that modification's formal assessment even when evidenced in unchanged code. Treat unrelated pre-existing issues under the incidental-observation guidance below.

## Prepare live diff links

### Prepare inputs

Every reviewed filename links to the unified localhost diff entry for that path. Keep the fixed evidence for the report and later actions independently of the display link: a local comparison uses the review's fixed before content and the path's current on-disk worktree state, which may change after the judged snapshot. Supply the selected comparison's actual before commit, an already-known before blob, or genuine absence; do not substitute the latest index, `HEAD`, or a mutable branch name.

Use the unified `local_web` tool supplied in `SmartKit plugin resources`, independently of the reviewed repository or cwd. Read its help for the batch schema and output contract:

```text
python "<local_web>" --help
python "<local_web>" diff --input "<batch.json>"
```

Submit one batch per repository and PR, with the worktree root as `repo`, an optional default `base`, optional `pr` context, and a nonempty `files` list. Each file supplies a unique `id` and its current `path`; `title` defaults to that path. A file's explicit `base` overrides the batch default; otherwise the batch must supply one. The CLI help owns the exact schema; `local_web` owns validation, baseline resolution, GitHub address construction, and URL encoding.

For the local default, prepare links alongside the review snapshot using index mode, so the tool fixes the same index baseline used for the review, including partially staged files. Branch and PR comparisons use their actual fixed before commit or an already-known blob; a PR cannot use the mutable index.

For every PR review, supply batch-level `pr.repository`, `pr.number`, and the full pinned reviewed `pr.head` from the obtained PR metadata. `repository` identifies the GitHub repository that owns the PR, not its source fork or an inferred local remote. Non-PR reviews omit `pr`. If required PR context is unavailable, identify the missing prerequisite and pause the dependent report. GitHub is an accepted display exception and may show the remote PR version rather than local edits.

### Locate files and worktrees

Supply a rename's old path as `base_path` when resolving an index or commit baseline; the current `path` remains the GitHub file target.

The tool constructs a GitHub Files changed URL targeting each file, deriving its default file anchor from the current `path`. The Agent supplies neither a complete GitHub URL nor a computed anchor. A file's optional `github_anchor` overrides that default with an already-observed fragment without the leading `#`; omit it when unavailable and let the tool derive the anchor. No separate GitHub visit or network lookup is needed to prepare file links.

Use that same command even when no PR checkout is known. `local_web` searches and validates the current checkout and its existing linked worktrees against the supplied PR head, binds a single match automatically, offers a page to choose among multiple matches, and routes to the generated GitHub URL when no match or usable local comparison exists. The Agent supplies context rather than enumerating, verifying, or selecting worktrees. Link preparation and display use existing Git data only; they do not fetch, clone, write Git objects, switch checkouts, create worktrees, or persist arbitrary before bytes.

### Use and open links

Match each returned `id` and `title` to its file and use the returned `markdown` for the filename link. The returned `url` and `markdown` point to the same localhost diff entry; `local_web` owns viewer selection and fallback dispatch.

The self-contained URL carries its comparison context without a signature, registration record, or link expiry. Once bound, it keeps that worktree and fixed baseline; later edits or commits do not trigger PR-head matching or rerouting. Missing Git objects or an unavailable repository are errors: the link provides no baseline backup and permits neither empty-content fallback nor baseline substitution. Deletion in an existing worktree is an absent current side; a rename needs a link for the new path.

When a local comparison is available, `local_web` tries VS Code first. Explicit unavailability or launch failure goes to the generated GitHub address for a PR, otherwise to HTML computed from the current local comparison. GitHub navigation stays in the current tab for automatic fallback and manual links. After an editor request is dispatched, the page attempts to close itself; if browser policy blocks closing, it keeps the status and manual fallback controls. The manual HTML control displays the local comparison without attempting the editor. A normal CLI return does not prove the diff was displayed.

Diff URLs remain usable after service restart while the referenced worktree and Git object exist; ordinary preview artifact retention remains separate. Filename links need no fixed after snapshot, but report examples and review-action verification still do.

### Handle unavailable links

If required link generation is unavailable, preserve diagnostics and pause the dependent report under the shared resource's unavailable-resource policy; leave dependent links incomplete rather than substituting old tools or hand-written addresses. Use the unified tool's help for service recovery; report observed navigation restrictions and claim successful opening only when observed. Do not publish repository changes merely to obtain a link.

## Explain each file through the problem it solves

Use [report examples](references/report-examples.md) when calibrating a compact or expanded explanation, incidental observation, or closing menu. They illustrate the formats below without adding review requirements.

Keep all report emoji outside bold spans, preserving emphasis on their accompanying text. When emphasizing a word, phrase, identifier, or label, keep surrounding separators and terminal punctuation outside bold; deliberately emphasized complete sentences may retain their sentence punctuation. Preserve punctuation intrinsic to code, identifiers, and paths.

Begin each file in the form `📄 **[path](diff-destination)**`, using the returned live diff Markdown, and a short overview of its responsibility and overall change. Source links and relevant line references may supplement this required filename link. Explain in ordinary language what the change means for users or callers, retaining technical detail that affects the judgment.

Divide the explanation into modifications by business problem or human-understood scenario. Start by keeping related changes together. Split only when they are logically independent or cannot be explained jointly with one simple example. Methods, diff hunks, and individual implementation steps do not by themselves justify separate modifications. For example, tracking pending work, refusing new work, and waiting before closing a resource can be one modification about safely finishing work on shutdown.

Small accompanying edits, such as a comment typo, can be mentioned in the overview or omitted. Explain each localization translation file as one modification for the whole file, rather than separating its strings into several modifications.

Label modifications in the exact format `🔧 **M1** - **<modification title>**`, then M2, M3, and so on, with continuous numbering across all files and groups. Reuse those M-prefixed IDs in finding lists, suggestion lists, selections, and re-reviews.

### Assess every modification on two independent dimensions

Use the same reasoning coverage for every modification: establish what changed from before to after, its effects and supporting evidence, then judge reasonableness and elegance independently. Apply both dimensions to all kinds of changes, including fixes, features, refactors, documentation, and translations. For prose, elegance concerns clear expression and organization; for code, it concerns the mechanism and structure. Adjust the expression's length, not the assessment's coverage.

Use the fixed emoji ⚖️ for reasonableness and 🎨 for elegance in every modification, including compact modifications. Put each judgment in its own paragraph, with its emoji followed directly by the conclusion, without repeating the dimension's name. Give each dimension an explicit conclusion and a reason; the emoji identifies the dimension, not whether the judgment is favorable.

- ⚖️ **Reasonable**. The change serves the intended task; its behavior is correct and safe, its scope fits the task, and its costs are justified by the available evidence.
- ⚖️ **Unreasonable** (P1): A material defect, unnecessary scope expansion, or unjustified cost makes the change a poor choice under the task's requirements. Substitute the actual P0–P3 severity, explain the evidenced impact, and give a concrete recommendation with its advantage under the same requirements. Bold only the judgment word; keep the severity plain in ASCII parentheses followed by an ASCII colon. A more elegant alternative, small optimization, or style preference alone does not meet this threshold.
- 🎨 **Elegant**. The change addresses the underlying problem at the appropriate responsibility or location, with clear structure and little unnecessary state, branching, or repetition. Explain which choices make it easy to understand and maintain.
- 🎨 **Can improve**. The behavior may be reasonable while its mechanism or expression creates avoidable complexity or repetition. Point to the concrete structure that could improve, suggest a simpler approach where supported, and explain the maintenance or clarity benefit. Distinguish that benefit from personal style preferences.
- ⚖️ **Insufficient evidence**. or 🎨 **Insufficient evidence**. Name what prevents a sound judgment on that dimension and what evidence would resolve it. Keep established facts and assumptions distinct. One dimension can have a supported conclusion while the other lacks evidence.

A reasonable change can be inelegant. An elegance concern alone is an optional improvement suggestion and does not trigger the mandatory fix-or-ignore pause. If the same structure also causes an evidenced material defect, risk, or unjustified cost, report that impact independently under reasonableness as well; that unreasonable finding follows the normal pause and repair procedure.

Assign P0–P3 only to unreasonable findings, never to a pure elegance suggestion or style preference. Use P0 for critical problems requiring immediate intervention, P1 for serious problems needing prompt correction, P2 for normal-priority problems, and P3 for lower-impact problems worth correcting. Base severity on evidenced consequences and affected conditions, not on how much code changed.

Carry the underlying review's material findings and qualifications into the relevant modifications, including the basis of a standards or task-scope concern when that distinction matters. A readable explanation must retain limitations that could change the human reviewer's decision. Report checks actually performed and distinguish them from results merely supplied by the author.

### Choose how much to show

Choose the form by what the reader needs to understand, not the diff's line count: one changed line can affect exception handling or persistence. Both forms retain the two separate, reasoned judgments above.

- **Compact**: Use when the behavior change is straightforward, its scope is clear, and no material risk or trade-off needs elaboration. Give the before-and-after behavior in one short prose paragraph without an emoji prefix, examples, code snippets, illustrative scenarios, or fixed Before and After labels. Follow it with the ⚖️ judgment paragraph, then the 🎨 judgment paragraph.
- **Expanded**: Use for complex mechanisms, important contracts, material risks or findings, consequential trade-offs, or key evidence gaps. Explain the behavior under ⏪ **Before**, then ⏩ **After**, followed by the ⚖️ judgment paragraph, then the 🎨 judgment paragraph. A separate "consequence of not changing" field is unnecessary.

For expanded code changes, show concise before-and-after code in the project's language from the retained review snapshot. Keep the conditions, state changes, or call order that explain the mechanism, including the relevant error or lifecycle branch when it matters to the judgment. Explain in plain language how the old code produces the original behavior and how the new code changes it; naming a benefit or paraphrasing the diff alone does not explain that causal connection. A simplified example must be recognizable as an illustration, preserve the behavior being compared, and be distinguishable from a verbatim source excerpt. Omit code when it adds no understanding, such as for prose organization.

Use the smallest useful comparison. Add another concise example only when a distinct behavior or finding needs its own explanation; repeated variations of the same mechanism add length without helping the reader. Preserve relevant qualifications and both judgments while keeping each example focused on the decision it supports.

## Display a group and offer actions

### Group files

Separate file blocks with `---` and display complete files in their established order. Finish the group after the file that brings its modification count to at least 10. Never split a file, even if it alone exceeds 10 modifications. For example, files with 3 and 8 modifications form one group of 11 modifications; the next file starts the next reply. Display the final shorter group when the scope ends.

End each group with `---` and 📊 **Progress**: **displayed files / files requiring review**, explicitly saying that the files have been displayed. Count displayed files, not modifications or conclusive judgments.

Across replies, retain the snapshot, ordered file list, every displayed group's files and reviewed changes, next-unreviewed position, next modification ID, judgments, finding statuses, and outstanding elegance suggestions. Keep each group's recording status and verified operation results so final completion can account for earlier groups, including those advanced without recording.

A full branch commit can include undisplayed groups and make a local worktree clean. Preserve the fixed before-and-after evidence for those groups and continue from the saved list; do not rebuild the remaining review from the new index or remove files because their changes are now committed. Reassess any content or effects that changed, while keeping previously undisplayed files distinct from completed review.

### Report incidental observations

During necessary reading for the selected review, report an unrelated pre-existing issue only when the available evidence establishes both the issue and its independence from the selected change. This advisory channel does not authorize a broader audit or bypass the file filters and test exclusions. Keep unsupported suspicions out of the observation list.

Initially report observations only in the group closing, under `📌 **Incidental observations (outside this review's scope)**`, outside file blocks and modification assessments. Follow the closing-section order below and omit the section when empty. Assign independent **O1**, **O2**, and subsequent IDs continuously across the report; retain their identity and status across groups and dedicated repair re-reviews rather than duplicating or renumbering them.

For each observation, give a short title, source location with a source link when available, supporting evidence and impact, its relationship to the selected change, and a concrete recommendation with its benefit. Establish that the issue existed before and was neither introduced, triggered, nor aggravated by this change. An initial observation's source references do not create reviewed-file blocks or require diff links for additional files.

Observations add no reviewed files, modifications, or progress, and remain separate from **Pending findings** and **Optional improvements**. An observation left as advice neither blocks advancement or completion nor authorizes repairs or enlarges the Viewed set. Unqualified **fix**, **optimize**, and **ignore all** exclude O items.

Explicitly selecting an O item for handling requires a separately established outcome, authorization, evidence, and checks. Route its repair through the dedicated O re-review below before marking it repaired or including its follow-up changes in completion. That follow-up remains separate from the main review unless its scope is explicitly expanded; if present on the target branch, it is accounted for in the full branch commit under the same disclosure and verification requirements as other changes.

### Choose an action

Use the conversation's language for human-facing labels, summaries, action names, and input prompts. Localize action names and their descriptions consistently in that language, without pairing them with names in another language. Interpret natural-language selections by meaning, rather than requiring command syntax.

Modification IDs select their relevant findings or suggestions. Unqualified **fix**, **optimize**, and explicit **ignore all** cover this report's already displayed, outstanding items in the chosen dimension, including earlier groups. A subset affects only that subset. Explain the applicable scope and count in the menu. Advancing displays the next group at the saved position or finishes an exhausted scope.

| Action | Effect and selection |
| --- | --- |
| **fix** | Repair pending unreasonable findings: all when unqualified, otherwise only those selected. |
| **ignore** | Record only the selected findings as ignored, retaining their severity and impact. A lone clearly identified finding needs no repeated ID; otherwise ask which findings, unless the user explicitly chooses all. Other findings stay pending. |
| **optimize** | Implement supported outstanding 🎨 **Can improve** suggestions: all when unqualified, otherwise only those selected. This leaves separately pending findings unchanged. |
| **pass and continue** | Commit all outstanding changes on the target branch after the disclosure and confirmation below, perform any disclosed PR publication and Viewed recording, verify the results, then advance. |
| **continue** | Advance without staging, committing, pushing, or marking Viewed. Retain unpublished modifications and unimplemented suggestions. |

**pass and continue** and **continue** are peer actions sharing the advancement gate below; completion adds the branch commit and any applicable PR effects. Keep three scopes distinct: the selected files and deltas determine the human review and progress; all outstanding changes on the target branch determine the commit; only eligible paths actually reviewed and displayed determine Viewed recording. The commit therefore includes staged, unstaged, and untracked changes, including tests, supporting files, and changes in files or groups not displayed. Commit inclusion is not evidence that those changes were reviewed. Apply the preparation and confirmation requirements below before including them.

Intermediate Viewed recording covers the whole current group, including its latest displayed re-review, and any eligible earlier displayed paths explicitly included in the selection. Clarify selections of individual modifications rather than treating them as whole-group completion or continuation. When all files have been displayed, name these actions **pass and finish** and **finish**. **pass and finish** has the same full branch commit scope and completes Viewed recording for ALL displayed, reviewed groups, including earlier groups advanced using **continue**. State those scopes in the final menu. Account for every group and reuse verified completed steps; a blocked part makes completion unavailable rather than reducing its scope. **finish** retains the non-recording semantics of **continue**.

A completion selection authorizes only the actual effects and scope disclosed before that selection. A local or branch review permits the disclosed local commit without requiring a PR; it supplies no push authority. For a verified PR, disclose the entire publication delta separately from the Viewed set and obtain authorization for that push. Neither completion nor continuation formally approves or merges a PR. Ignored findings remain ignored, not repaired or approved.

### Generate the closing menu

Use the table below for completion availability and effects in every closing: ordinary groups, dedicated re-reviews, menus after fixing, ignoring, or optimizing, final groups, and interrupted-operation recovery. Apply the completion scope above and the final labels when exhausted. Before closing, complete derivable, authorized read-only checks needed to establish the state; the user should choose effects, not diagnose whether publication is needed.

Both actions require the same advancement gate: every displayed unreasonable finding is repaired or explicitly ignored, required correctness and version evidence for the review is available, required review checks and affected re-reviews are complete, and any previously selected completion operation is verified. An optional improvement or lack of elegance evidence alone does not block advancement. Operation-specific completion prerequisites, including checks for additional branch content that does not affect the reviewed changes, can block **pass and continue** without blocking **continue**; an already-selected unfinished operation blocks both from advancing until its recovery is verified.

| State, in priority order | Completion status, effects, and available choices |
| --- | --- |
| Pending unreasonable findings, including after subset fixes or ignores | Completion and continuation are unavailable: name the pending IDs and required fix or explicit ignore. Offer **fix**, **ignore**, and **optimize** if supported suggestions remain. |
| Missing review correctness/version evidence, incomplete or failed required review checks, or stale affected review | Completion and continuation are unavailable: name the missing evidence, check, or re-review and its remedy. Complete authorized work before regenerating the menu. |
| A selected commit, Viewed, or publication operation is unfinished | Report its confirmed, failed, and unknown steps. Resolve the blocker, then offer the same completion action as a resumption of only the remaining steps. Ordinary **continue** remains unavailable; follow recovery below. |
| Advancement ready, but a required completion target, interface, check, or safe scope cannot be established | Completion is unavailable: name the concrete prerequisite and remedy, including a verified GitHub PR review target when GitHub recording or publication is required. **continue** is independently available. |
| Additional content is not confirmed for inclusion | Explain the concrete changes made outside this conversation or with unknown origin, including existing unpushed commits when publication is proposed. Obtain explicit inclusion confirmation before committing or pushing; a combined **confirm inclusion and pass and continue** choice may supply it when its text names the disclosed extra content and all other prerequisites are ready. **continue** remains independently available. |
| Ready completion with no remaining commit, publication, or Viewed writes | Say which branch state and recording results are verified. Offer **pass and continue** to reuse those results and advance without repeating writes, alongside **continue**. A clean branch needs no empty commit. |
| Ready local or branch review with outstanding changes | **pass and continue** stages and commits all disclosed branch changes through normal hooks, verifies the commit and remaining state, then advances. **continue** advances without committing. A PR and push are not required. |
| Ready PR with no unpublished branch changes | **pass and continue** verifies the pinned PR version and viewer, marks the selected scope's eligible reviewed paths Viewed, verifies every readback, and advances; **continue** advances without marking. Apply the PR recording safeguards below. |
| Ready PR with branch changes awaiting publication | **pass and continue** commits all disclosed outstanding changes if needed, pushes the full disclosed and authorized branch delta, verifies the resulting PR version, marks only the disclosed eligible reviewed paths Viewed, verifies every readback, and advances. **continue** retains local changes without publication or marking. Establish the publication and recording prerequisites below before offering completion. |

Reuse verified completed steps in partially recorded scopes; only remaining work needs writes. Add **optimize** to ready-state menus whenever supported outstanding suggestions remain. This Skill's PR publication procedure requires a known, verified PR; an ordinary branch or local comparison supplies no remote-write target. Already committed changes are reused, and a PR already containing the complete intended branch state needs no unnecessary push.

Every closing explicitly accounts for completion, including when only continuation is available after a successful repair. Offer its concrete effects and scope when ready, state what recording is already complete when applicable, or explain why **pass and continue** is unavailable or not applicable and give the next remedy. For an exhausted scope, use **pass and finish** in that status. Keep unavailable or inapplicable status outside **Available actions**: it is explanatory status, not an executable choice.

After progress, use these Markdown sections in order, omitting empty sections:

1. **Pending findings**: Include outstanding findings from earlier groups. Use the exact format `**M1** (P1): <impact summary>` with the actual ID and severity; bold only the ID and keep the ASCII parentheses and colon plain.
2. **Optional improvements**: Include outstanding supported suggestions from earlier groups, each with its ID, proposed improvement, and benefit.
3. 📌 **Incidental observations (outside this review's scope)**: Use the separate O items defined above.
4. **Available actions**: Number every executable choice consecutively from 1 in an ordered list, including a sole continuation or resumption choice. Use short descriptions of actual effects rather than execution recipes, naming the full branch commit scope, any extra-content confirmation, and the publication delta and eligible Viewed set when needed. Regenerate the numbering for each menu; these numbers identify its choices, while M and O IDs retain their item identities across the report.

End with one concise instruction to enter an operation number, such as “Enter an operation number.” When no choice remains, close without an input prompt. Consult [example closings](references/report-examples.md#example-closings-for-different-results) when the presentation of a particular state needs clarification.

An incoming “continue” finishes an exhausted scope only when the gate is satisfied. An explicit stop or pause is always allowed: report the displayed progress, unresolved or ignored findings, evidence gaps, uncommitted or unpublished modifications, and unfinished operations as applicable, without claiming successful completion. Completed display does not mean all findings were repaired or all modifications were committed or published.

## Carry out the selected action

### Interpret replies

Resolve operation numbers against the latest displayed menu, then apply the selected action's existing scope and authorization requirements. M-prefixed modification IDs and O-prefixed observation IDs select items rather than menu actions. Keep natural-language selections supported, including a meaning absent from the menu when its prerequisites and authority hold.

If required effects were not disclosed or explicitly authorized, explain them and obtain the selection before writing; a historical “pass” disclosed as staging or marking Viewed supplies no commit or push authority. If the user requests advancement while blocked, refuse it briefly, name the blockers, and regenerate the numbered menu for the relevant fix, ignore, or remedy; “continue” never means “ignore.” Clarify ambiguous scopes or menu references, invalid operation numbers or item IDs, conflicting directions, or a bare agreement following an ambiguous menu; “yes” authorizes an action only when the preceding question specifies it unambiguously. Reassess disputed findings from the supplied evidence rather than treating disagreement as ignoring. Answer questions without interpreting them as authorization for edits or advancement.

### Repair or optimize, then re-review

For authorized repairs or optimizations, including separately selected O repairs, load the necessary guidance, limit edits to the selected findings, suggestions, or observations and their necessary supporting changes, and run required checks. Optimization preserves supported behavior and contracts. Whenever reviewed content changes or an O item is repaired:

1. Complete required checks successfully, refresh the relevant before-and-after snapshot, and regenerate or revalidate its diff links. Retain an O repair's evidence separately from the main review snapshot. For unpublished PR changes, retain both the pinned remote version and the checked local content expected to be published.
2. Independently re-review every changed or affected previously reviewed part, including unexpected changes. Show complete file blocks with updated explanations and both judgments in dedicated replies separate from unseen files. For an O repair, independently assess the repaired behavior and affected dependencies even though the original observation was outside the main review. Show a dedicated O re-review with its source location, before-and-after explanation, and separate reasoned ⚖️ and 🎨 judgments; retain its O ID rather than assigning an M ID.
3. Retain modification IDs and original group membership, count each displayed main-review file once, and explain the version transition. An O re-review adds no main-review file, modification, progress, or Viewed eligibility unless the user explicitly expands that scope. Update the main file list and total only for actual scope changes. Mark findings or O items repaired, and suggestions completed, only after required checks and re-review confirm the result; otherwise retain the unresolved status and explain what remains.

A single **fix**, **ignore**, or **optimize** ends with the regenerated menu and completion status, not automatic advancement. An explicit compound request authorizes its ordered steps: for example, fix, check, display the dedicated re-review, complete the disclosed branch commit and PR publication, mark eligible files Viewed, then advance. Continue already authorized steps without routine reconfirmation; newly discovered extra content still requires its explicit inclusion confirmation. A new finding, failed check, or material change pauses dependent steps and regenerates the menu. An independently authorized optimization can still proceed while findings are pending, but does not open the advancing gate.

### Prepare the full branch commit

Before offering completion, identify the exact repository, branch, and worktree whose changes will be committed. A different current checkout is not a substitute for the reviewed branch. Use available read-only Git evidence to inventory its complete staged, unstaged, and untracked changes and any commits that a proposed push would publish. Retain the branch tip, index entries, worktree contents, and applicable untracked contents as the operation baseline alongside the fixed review snapshots. Existing commits remain commits; do not recreate them merely to make completion perform a write.

The commit includes all outstanding branch changes, not just the current group, this conversation's edits, or the report's eligible paths. Account for tests, necessary supporting and generated files, selected-file exclusions, staged-only edits, and untracked source files. Honor repository restrictions on ignored, sensitive, or disposable files; if a candidate change cannot safely be included, explain the obstacle and resolve the intended scope with the user rather than silently omitting it or using a scope-only commit. For partially staged files, compare both deltas and establish the coherent final worktree content to commit; retain the original index version for recovery and explain any staged content superseded by the worktree. Unresolved final-content conflicts block completion.

Determine provenance from the current conversation's recorded actions and baseline evidence, not author names, timestamps, the branch name, or a clean-looking diff. Separate changes introduced in this conversation from changes made elsewhere and changes whose origin cannot be established, including mixed-origin hunks in the same file. Before including either of the latter categories, explain the affected paths or commits, what the extra changes do, and any material consequences. Ask for explicit confirmation to include that concrete extra content in the commit and, when applicable, publication. A prior confirmation remains valid for the same content and effects; generic approval of the reviewed group does not confirm undisclosed extras. If confirmation is absent or declined, preserve the changes and leave full-branch completion pending. Offer ordinary continuation or ask for a revised scope; do not silently fall back to committing only this conversation's changes.

Show how the full commit and any push differ from the displayed review. Same-conversation changes outside the human review need accounting and applicable checks even though they need no extra provenance confirmation. Run required checks for the whole intended commit and publication delta, including supporting and test changes, and reassess effects on previously reviewed content. Complete the dedicated re-review for every authorized O repair included in that delta; an unfinished or failed O repair check or re-review blocks dependent completion. Display an affected main re-review when those effects change; keep undisplayed and excluded files outside progress and the Viewed set. Additional content confirmation authorizes inclusion, not a claim of completed review or a waiver of required checks or O re-review.

### Commit the branch changes

Execute only after the full inventory, required checks, affected re-reviews, disclosure, and any extra-content confirmation are complete. Retain the selected operation and its baseline through verification and any retry.

1. Revalidate the target branch tip, index, and worktree against the prepared inventory and fixed review evidence. Resolve drift before writing: refresh the inventory and checks, re-review affected displayed content, and obtain renewed confirmation for changed or newly discovered extra content or effects.
2. Stage the full disclosed final content, including applicable additions and deletions, and verify that the complete index represents that intended tree. Preserve recovery evidence for the original staged and unstaged states. If no outstanding delta remains, verify and reuse the existing commit instead of creating an empty one.
3. Create the commit through normal repository hooks. Verify the resulting commit, its parent, and its complete tree against the intended result, then inspect the index and worktree for remaining changes. Hook changes require applicable checks and affected re-review; changes beyond the confirmed content also require updated disclosure and confirmation before dependent writes or advancement. A successful command alone does not prove full completion.
4. Record the verified commit and remaining state. Completion requires all intended branch changes to be committed, with no unexplained residue. A local or branch review can then advance without a PR or push; a PR operation proceeds through its separately authorized publication and recording steps below.

### Record reviewed PR files

Before offering PR completion, establish the verified GitHub PR review target and an authenticated interface for the required viewer, version, and per-path readbacks. When marking remains, the interface must also be capable of marking files Viewed. The checked, reviewed version must be present on the PR; first use the publication procedure below when necessary.

Viewed applies to a whole file at a PR version. For every path in the selected Viewed set, compare its complete delta in the intended published PR comparison with the retained displayed assessments. Every hunk must be covered, including expected extra content that is independent of the previously reviewed changes. Display and assess missing content in a dedicated re-review with both judgments before offering completion that marks the path. Retain applicable M or O identities and original group membership, without counting the file again; an O re-review still creates no Viewed eligibility for a path outside the selected main review. Inclusion confirmation, passing checks, and unchanged effects of earlier hunks do not supply missing review coverage.

If the necessary coverage is unavailable or requires a review-scope decision, leave that path unmarked and explain what review or scope choice is needed. Completion is unavailable, or remains pending if already selected; preserve its Viewed set and displayed progress rather than silently dropping the path. After publication, verify the same coverage against the actual PR version before recording.

1. Verify the viewer identity and pinned base and head immediately before writing, and confirm that every selected path's complete current PR delta matches its displayed review evidence.
2. Mark only the selected completion scope's eligible reviewed paths still awaiting Viewed.
3. Read back every selected path's `viewerViewedState` and the PR version, including paths whose completed marking is being reused. Every selected path must be `VIEWED`, with both commit IDs unchanged during recording, before advancing.

A changed version requires an affected re-review and a new selection; marking a newer version does not establish that it was reviewed.

### Publish branch changes to the reviewed PR

Use available Git and authenticated GitHub read/write interfaces, such as a CLI, connector, or UI. Establish the exact repository, PR, source branch, viewer, write capabilities, remote base and head, and complete outgoing ancestry before offering completion that publishes changes. Prepare the full branch scope above, including existing unpushed commits and all outstanding changes, and disclose the complete delta the push would publish. Explain and obtain explicit confirmation for non-conversation or unknown-origin content in that delta even if already committed locally. The publication scope may exceed the human review and Viewed set; inclusion never establishes review. If the full branch cannot be published by a normal push to the verified source branch, explain the prerequisite rather than implicitly rebasing, force-pushing, or excluding extra commits.

Execute the selected operation in this order:

1. Verify the pinned remote base and head, the reviewed before-and-after content and affected dependencies, and the entire delta and commit ancestry to be published. Confirm that the actual publication delta, extra-content confirmations, and eligible displayed paths match the disclosed selection; verify each path's content and the pinned viewer.
2. Complete and verify the full branch commit procedure above when needed, reusing existing verified commits. Revalidate the complete outgoing delta after hooks and before pushing; unexpected changes need the applicable checks, affected re-review, and updated confirmation.
3. Push normally to the validated PR source branch. Read back the remote head and base, confirming the expected commit and that the complete published delta matches the checked and authorized branch state, with the displayed review still valid for its eligible paths.
4. Apply the PR recording safeguards above to the disclosed eligible displayed paths, including the final accumulated scope when selected. Mark only paths still awaiting Viewed; read back every selected path's state and the PR version. All must be `VIEWED` on the verified base and head.
5. Acknowledge the completed operation and advance from the saved position, or finish an exhausted scope.

The intentional new head needs verification, not a repeat of already covered review. Apply the complete per-path coverage requirement above even to intentionally published extra content. Unexpected changes to content, base, or affected dependencies require re-review of the affected parts; text equality alone does not establish unchanged effects. Refresh the snapshot and obtain a new choice when the result no longer represents the authorized reviewed version. Retain the ordered list, group membership, next position, modification IDs, decisions, and per-group recording results across publication.

### Recover an unfinished operation

If a required interface is unavailable or a write or verification fails, pause without advancing, rolling back automatically, or substituting **continue** or **finish**. Report confirmed, failed, and unknown steps, including the exact commits, publication status, remaining branch changes, and partial staging or Viewed paths, then generate the closing status from the state table.

Retain the full branch inventory and provenance decisions, inclusion confirmations, selected publication and Viewed scopes, group snapshots, PR version, viewer, and resume position. Resuming an intermediate operation does not silently expand its Viewed set to final scope or include new branch content without reassessment. After a lost response, inspect the actual local and remote state before deciding whether a write occurred. Once readiness is restored, resume the same **pass and continue** or **pass and finish** operation, describing only the remaining supported steps, without duplicate commits or repeated successful writes.

A selected operation completes only after all required readbacks succeed. Explicit stopping can leave it incomplete and must report that residual state. Successful completion preserves saved progress and the resume position; amend totals only for real scope changes, and do not reapply unstaged or Viewed filters to remove displayed files.
