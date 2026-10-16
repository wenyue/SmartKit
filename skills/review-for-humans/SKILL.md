---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand a pull request or branch change: what changed, whether it is reasonable, whether its implementation is elegant and tasteful, and where their attention is needed. Use this Skill only when the user requests it. Review the selected scope read-only, then carry out only the effects authorized by the user's selected actions within the scope and verification rules below. Read-only review permits capturing the comparison, resolving existing Git objects, and running the shared diff-link command; keep the reviewed files and Git index unchanged until an authorized action below.

Load the necessary Skills and Rules to perform the review.

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

The local default reviews only unstaged changes, using the index as the before version. Skip staged-only edits; for a partially staged file, review only its unstaged portion. If a staged edit is subsequently reverted in the worktree, that reversal relative to the index is an unstaged change to review. An explicit request to include staged changes or use another local comparison overrides this default. Do not include earlier commits or fall back to staged changes or the last commit when the selected comparison is empty. Exclude untracked files unless the user explicitly includes them; when included, review them as additions.

### Filter PR files

For a PR, default to skipping files marked viewed by the current authenticated GitHub viewer. Obtain the complete file-level states through an available authenticated read-only GitHub interface; GitHub GraphQL exposes them as [`PullRequestChangedFile.viewerViewedState`](https://docs.github.com/en/graphql/reference/pulls#pullrequestchangedfile). Exclude `VIEWED`; include `UNVIEWED` and `DISMISSED`, which means the file changed since it was last viewed. Complete any pagination and check that the PR's base and head remain unchanged while obtaining the file list and states, so the filter belongs to the pinned version. Current viewed states cannot establish a filter for an older PR snapshot. A PR approval, comments, or files displayed in an earlier chat are not evidence of a file's viewed state.

The user can explicitly include reviewed files, overriding that exclusion. If required viewed-state evidence is unavailable, name the missing prerequisite and pause the dependent review; ask for access to that evidence or whether to include all otherwise eligible files without the filter. Treat missing state as unknown rather than `UNVIEWED`.

### Keep a fixed snapshot and file list

Preserve this Skill's selected comparison when loading other review guidance with different scope defaults. When there is no usable `HEAD`, the requested refs or PR evidence are unavailable, or a required interface cannot be used, name the missing prerequisite and pause the dependent review.

Keep a fixed review snapshot and an ordered file list for displaying the report. Record comparison commit IDs for PRs and branches, the local comparison's before-and-after content including the index baseline, and the viewer identity and file-level states used for PR filtering. Retain the local index baseline even when an explicitly selected comparison uses another before version, so later staging can preserve existing staged work. For all review scopes, match GitHub's Files changed directory-tree order: at every directory, recursively list each subdirectory's changed files before the files directly in that directory. Use the pull request's actual tree sibling order when accessible; otherwise sort sibling directories and direct files by name. For example, `src/z/api.dart` precedes `src/a.dart`; sorting complete paths from `git diff` does not establish that order.

Skip test files entirely: do not review them or count them toward progress or modifications. Apply the scope filters before counting; skipped viewed PR files and staged-only local files receive no file reports, progress credit, or modifications. Count the remaining files before displaying the first group. Briefly identify the scope and exclusions so the reader can interpret the total. If no files require review, say so and finish without manufacturing a report or a progress fraction.

When scope, required guidance, or source evidence is unavailable, identify the missing input and its effect. Pause the dependent review rather than inventing facts, totals, or a completed assessment. A known file with incomplete evidence remains in the total; explain the gap in that file's report and use an insufficient-evidence evaluation where necessary.

Assess the selected comparison and its effects, using relevant context as needed while preserving the file filters and test exclusions. A defect introduced, triggered, or aggravated by the selected change belongs in that modification's formal assessment even when evidenced in unchanged code. Treat unrelated pre-existing issues under the incidental-observation guidance below.

## Prepare live diff links

### Prepare inputs

Every reviewed file's report links to the tool's unified localhost diff entry for that path. Keep the fixed review evidence used for the report and later actions independently of what the display link currently shows. A local comparison always uses the actual review's fixed before content and the path's current on-disk worktree state; later edits may therefore differ from the judged snapshot. Supply the selected comparison's actual before commit, an already-known before blob, or genuine absence; do not substitute the latest index, `HEAD`, or a mutable branch name.

Use the unified `local_web` tool supplied in `SmartKit plugin resources`, independently of the reviewed repository or cwd. Read its help for the batch schema and output contract:

```text
python "<local_web>" --help
python "<local_web>" diff --input "<batch.json>"
```

Submit one batch object with shared `repo`, an optional default `base`, optional `pr` context, and a nonempty `files` list. Use the repository worktree root as the `repo` lookup entry. Each file supplies a unique `id` and its current `path`; `title` defaults to that path. A file's explicit `base` overrides the batch default; otherwise the batch must supply one. Separate repositories or PRs need separate batches. The CLI help owns the exact schema; `local_web` owns validation, baseline resolution, GitHub address construction, and URL encoding.

For the local default, prepare links alongside the review snapshot using index mode, so the tool fixes the same index baseline used for the review, including partially staged files. Branch and PR comparisons use their actual fixed before commit or an already-known blob; a PR cannot use the mutable index.

For every PR review, supply batch-level `pr.repository`, `pr.number`, and the full pinned reviewed `pr.head` from the obtained PR metadata. `repository` identifies the GitHub repository that owns the PR, not its source fork or an inferred local remote. Non-PR reviews omit `pr`. If required PR context is unavailable, identify the missing prerequisite and pause the dependent report. GitHub is an accepted display exception and may show the remote PR version rather than local edits.

### Locate files and worktrees

Supply a rename's old path as `base_path` when resolving an index or commit baseline; the current `path` remains the GitHub file target.

The tool constructs a GitHub Files changed URL targeting each file, deriving its default file anchor from the current `path`. The Agent supplies neither a complete GitHub URL nor a computed anchor. A file's optional `github_anchor` overrides that default with an already-observed fragment without the leading `#`; omit it when unavailable and let the tool derive the anchor. No separate GitHub visit or network lookup is needed to prepare file links.

Use that same command even when no PR checkout is known. `local_web` searches and validates the current checkout and its existing linked worktrees against the supplied PR head, binds a single match automatically, offers a page to choose among multiple matches, and routes to the generated GitHub URL when no match or usable local comparison exists. The Agent supplies context rather than enumerating, verifying, or selecting worktrees. Link preparation and display use existing Git data only; they do not fetch, clone, write Git objects, switch checkouts, create worktrees, or persist arbitrary before bytes.

### Use and open links

Match each returned `id` and `title` to its file and use the returned `markdown` for the filename link. The returned `url` and `markdown` point to the same localhost diff entry; `local_web` owns viewer selection and fallback dispatch. The self-contained local URL carries its comparison context without a signature, registration record, or link expiry. Once bound to a worktree, the link always compares its fixed baseline with that worktree's current on-disk path; subsequent edits or commits do not cause PR-head matching or rerouting. It does not back up the baseline: missing Git objects or an unavailable repository are errors, not empty content or permission to substitute a different baseline. Deletion in an existing worktree is an absent current side, and a rename needs a link for the new path.

When a local comparison is available, `local_web` tries VS Code first. Explicit unavailability or launch failure goes to the generated GitHub address for a PR, otherwise to HTML computed from the current local comparison. GitHub navigation stays in the current tab for both automatic fallback and manual links. After an editor request is dispatched, the page attempts to close itself; if browser policy blocks closing, it keeps the status and manual fallback controls. A normal CLI return does not prove the diff was displayed. The page's manual HTML control displays the local comparison without attempting the editor. Current diff URLs remain usable after service restart while the referenced worktree and Git object exist; ordinary preview artifact retention remains separate. Filename links need no fixed after snapshot, but report examples and review-action verification still do.

### Handle unavailable links

If required link generation is unavailable, preserve diagnostics and pause the dependent report under the shared resource's unavailable-resource policy; leave dependent links incomplete rather than substituting old tools or hand-written addresses. Use the unified tool's help for service recovery; report observed navigation restrictions and claim successful opening only when observed. Do not publish repository changes merely to obtain a link.

## Explain each file through the problem it solves

Keep all report emoji outside bold spans, preserving emphasis on their accompanying text. When emphasizing a word, phrase, identifier, or label, keep surrounding separators and terminal punctuation outside bold; deliberately emphasized complete sentences may retain their sentence punctuation. Preserve punctuation intrinsic to code, identifiers, and paths.

Begin each file in the form `📄 **[path](diff-destination)**`, using the returned live diff Markdown, and a short overview of its responsibility and overall change. Source links and relevant line references may supplement this required filename link. Explain in ordinary language what the change means for users or callers, retaining technical detail that affects the judgment.

Divide the explanation into modifications by business problem or human-understood scenario. Start by keeping related changes together. Split only when they are logically independent or cannot be explained jointly with one simple example. Methods, diff hunks, and individual implementation steps do not by themselves justify separate modifications. For example, tracking pending work, refusing new work, and waiting before closing a resource can be one modification about safely finishing work on shutdown.

Small accompanying edits, such as a comment typo, can be mentioned in the overview or omitted. Explain each localization translation file as one modification for the whole file, rather than separating its strings into several modifications.

Label modifications in the exact format `🔧 **M1** - **<modification title>**`, then M2, M3, and so on, with continuous numbering across all files and continuation groups in the same report. Keep the emoji and separator outside the bold spans, and use the same M-prefixed IDs in finding lists, suggestion lists, selections, and re-reviews.

### Assess every modification on two independent dimensions

Use the same reasoning coverage for every modification: establish what changed from before to after, its effects and supporting evidence, then judge reasonableness and elegance independently. Apply both dimensions to all kinds of changes, including fixes, features, refactors, documentation, and translations. For prose, elegance concerns clear expression and organization; for code, it concerns the mechanism and structure. Adjust the expression's length, not the assessment's coverage.

Use the fixed emoji ⚖️ for reasonableness and 🎨 for elegance in every modification, including compact modifications. Put each judgment in its own paragraph, with its emoji followed directly by the conclusion, without repeating the dimension's name. Give each dimension an explicit conclusion and a reason; the emoji identifies the dimension, not whether the judgment is favorable.

- ⚖️ **Reasonable**. The change serves the intended task; its behavior is correct and safe, its scope fits the task, and its costs are justified by the available evidence.
- ⚖️ **Unreasonable** (severity): A material defect, unnecessary scope expansion, or unjustified cost makes the change a poor choice under the task's requirements. Substitute the finding's actual severity from P0 to P3 in this label, explain the evidenced impact, and give a concrete recommendation with its advantage under the same requirements. A more elegant alternative, small optimization, or style preference alone does not meet this threshold.
- 🎨 **Elegant**. The change addresses the underlying problem at the appropriate responsibility or location, with clear structure and little unnecessary state, branching, or repetition. Explain which choices make it easy to understand and maintain.
- 🎨 **Can improve**. The behavior may be reasonable while its mechanism or expression creates avoidable complexity or repetition. Point to the concrete structure that could improve, suggest a simpler approach where supported, and explain the maintenance or clarity benefit. Distinguish that benefit from personal style preferences.
- ⚖️ **Insufficient evidence**. or 🎨 **Insufficient evidence**. Name what prevents a sound judgment on that dimension and what evidence would resolve it. Keep established facts and assumptions distinct. One dimension can have a supported conclusion while the other lacks evidence.

A reasonable change can be inelegant. An elegance concern alone is an optional improvement suggestion and does not trigger the mandatory fix-or-ignore pause. If the same structure also causes an evidenced material defect, risk, or unjustified cost, report that impact independently under reasonableness as well; that unreasonable finding follows the normal pause and repair procedure.

Assign P0–P3 only to unreasonable findings, never to a pure elegance suggestion or style preference. Use P0 for critical problems requiring immediate intervention, P1 for serious problems needing prompt correction, P2 for normal-priority problems, and P3 for lower-impact problems worth correcting. Base severity on evidenced consequences and affected conditions, not on how much code changed. For example, use ⚖️ **Unreasonable** (P1): followed by the impact and recommended repair, substituting the finding's actual severity. Bold only the judgment word; keep the severity plain in ASCII parentheses and place the ASCII colon after them.

Carry the underlying review's material findings and qualifications into the relevant modifications, including the basis of a standards or task-scope concern when that distinction matters. A readable explanation must retain limitations that could change the human reviewer's decision. Report checks actually performed and distinguish them from results merely supplied by the author.

### Choose how much to show

Use a compact explanation when the behavior change is straightforward, the affected scope is clear, and no material risk or trade-off needs elaboration. Compress only the before-and-after behavioral explanation into one short paragraph without an emoji prefix. Keep compact modifications in prose without examples, including code snippets or illustrative scenarios, and omit the fixed Before and After labels. Follow the explanation with a separate ⚖️ judgment paragraph and a separate 🎨 judgment paragraph, each retaining its conclusion and reason. Judge simplicity by what the reader needs to understand, not by the diff's line count: one changed line can affect exception handling or persistence.

Expand modifications involving complex mechanisms, important contracts, material risks or findings, consequential trade-offs, or key evidence gaps. Present ⏪ **Before**, then ⏩ **After**, then a separate ⚖️ reasonableness judgment paragraph, then a separate 🎨 elegance judgment paragraph, using emoji plus conclusion for both judgments. Explain the behavior before and after; a separate "consequence of not changing" field is unnecessary.

For expanded code changes, show concise before-and-after code in the project's language from the retained review snapshot. Keep the conditions, state changes, or call order that explain the mechanism, including the relevant error or lifecycle branch when it matters to the judgment. Explain in plain language how the old code produces the original behavior and how the new code changes it; naming a benefit or paraphrasing the diff alone does not explain that causal connection. A simplified example must be recognizable as an illustration, preserve the behavior being compared, and be distinguishable from a verbatim source excerpt. Omit code when it adds no understanding, such as for prose organization.

Use the smallest useful comparison. Add another concise example only when a distinct behavior or finding needs its own explanation; repeated variations of the same mechanism add length without helping the reader. Preserve relevant qualifications and both judgments while keeping each example focused on the decision it supports.

## Display one group and handle actions

### Group files

Separate file blocks with `---` and display complete files in their established order. Finish the group after the file that brings its modification count to at least 10. Never split a file, even if it alone exceeds 10 modifications. For example, files with 3 and 8 modifications form one group of 11 modifications; the next file starts the next reply. Display the final shorter group when the scope ends.

End each group with `---` and 📊 **Progress**: **displayed files / files requiring review**, explicitly saying that the files have been displayed. Count displayed files, not modifications or conclusive judgments. Across replies, retain the snapshot, ordered file list, every displayed group's files and reviewed changes, next-unreviewed position, next modification ID, judgments, finding statuses, and outstanding elegance suggestions. Retain each group's recording status and verified operation results so final completion can account for earlier groups, including those advanced without recording.

### Report incidental observations

During necessary reading for the selected review, report an unrelated pre-existing issue only when the available evidence establishes both the issue and its independence from the selected change. This advisory channel does not authorize a broader audit or bypass the file filters and test exclusions. Keep unsupported suspicions out of the observation list.

Display observations only in the group closing, under `📌 **Incidental observations (outside this review's scope)**`, after progress and before **Available actions**, outside file blocks and modification assessments. Omit the section when empty. Assign independent **O1**, **O2**, and subsequent IDs continuously across the report; retain their identity and status across groups and re-reviews rather than duplicating or renumbering them.

For each observation, give a short title, source location with a source link when available, supporting evidence and impact, its relationship to the selected change, and a concrete recommendation with its benefit. Establish that the issue existed before and was neither introduced, triggered, nor aggravated by this change. These references do not create reviewed-file blocks or require diff links for additional files.

Observations add no reviewed files, modifications, or progress, and remain separate from **Pending findings** and **Optional improvements**. They do not block advancement or completion, and unqualified **fix**, **optimize**, and **ignore all** exclude them. They do not enlarge staging, Viewed, or publication scope. Explicitly selecting an O item for handling requires a separately established outcome, authorization, evidence, and checks; neither that observation nor its follow-up changes enter the current reviewed scope or its completion operations automatically.

### Choose an action

Use the conversation's language for human-facing labels, summaries, action names, and questions. Localize action names and their descriptions consistently in that language, without pairing them with names in another language. Interpret natural-language selections by meaning, rather than requiring command syntax.

Modification IDs select that modification's relevant findings or suggestions. Unqualified **fix**, **optimize**, and explicit **ignore all** cover only this report's already displayed, outstanding items in the chosen dimension, including earlier groups. A subset affects only that subset. Explain the applicable scope and count in the menu. Advancing displays the next group at the saved position or finishes an exhausted scope.

| Action | Effect and selection |
| --- | --- |
| **fix** | Repair pending unreasonable findings: all when unqualified, otherwise only those selected. |
| **ignore** | Record only the selected findings as ignored, retaining their severity and impact. A lone clearly identified finding needs no repeated ID; otherwise ask which findings, unless the user explicitly chooses all. Other findings stay pending. |
| **optimize** | Implement supported outstanding 🎨 **Can improve** suggestions: all when unqualified, otherwise only those selected. This leaves separately pending findings unchanged. |
| **pass and continue** | Perform the applicable completion steps in the state table below, verify them, then advance. The disclosed effects determine whether this stages local changes, publishes checked PR repairs, or marks reviewed PR files Viewed. |
| **continue** | Advance without staging, committing, pushing, or marking Viewed. Retain unpublished modifications and unimplemented suggestions. |

**pass and continue** and **continue** are peer actions sharing the same advancement gate; completion adds state-recording steps and their prerequisites. Intermediate completion covers the whole current group, including its latest displayed re-review. When PR publication is needed, its disclosed scope may also include this report's eligible previously displayed paths and authorized, checked, re-reviewed decisions. Clarify selections of individual modifications rather than treating them as whole-group completion.

When all files have been displayed, use **pass and finish** and **finish**. These are the same two actions at the end of the report. **pass and finish** covers ALL displayed, reviewed groups in this report, including earlier groups advanced using **continue**, and completes their remaining applicable recording and publication work. State that accumulated scope in the final menu. Reuse verified completed steps, and account for every group; a blocked part makes final completion unavailable rather than silently reducing its scope. **finish** retains the non-recording semantics of **continue**.

A completion selection authorizes only the actual effects and scope disclosed before that selection. Neither completion nor continuation formally approves or merges a PR. Ignored findings remain ignored, not repaired or approved.

### Generate the closing menu

Use this table as the authority for completion availability and effects in every closing: ordinary groups, dedicated re-reviews, menus after fixing, ignoring, or optimizing, final groups, and interrupted-operation recovery. Before closing, complete derivable, authorized read-only checks needed to establish the state; the user should choose effects, not diagnose whether publication is needed. Apply the completion scope defined above, using the final labels when exhausted.

Both actions require the same advancement gate: every displayed unreasonable finding is repaired or explicitly ignored, required correctness and version evidence is available, required checks and affected re-reviews are complete, and any previously selected recording or publication operation is verified. An optional improvement or lack of elegance evidence alone does not block advancement. Operation-specific completion prerequisites can block **pass and continue** without blocking **continue**; an already-selected unfinished operation blocks both from advancing until its recovery is verified.

| State, in priority order | Completion status, effects, and available choices |
| --- | --- |
| Pending unreasonable findings, including after subset fixes or ignores | Completion and continuation are unavailable: name the pending IDs and required fix or explicit ignore. Offer **fix**, **ignore**, and **optimize** if supported suggestions remain. |
| Missing correctness/version evidence, incomplete or failed required checks, or stale affected review | Completion and continuation are unavailable: name the missing evidence, check, or re-review and its remedy. Complete authorized work before regenerating the menu. |
| A selected staging, Viewed, or publication operation is unfinished | Report its confirmed, failed, and unknown steps. Resolve the blocker, then offer the same completion action as a resumption of only the remaining steps. Ordinary **continue** remains unavailable; follow recovery below. |
| Advancement ready, but a required completion target, interface, or safe scope cannot be established | Completion is unavailable: name the concrete prerequisite and remedy, including a verified GitHub PR review target when GitHub recording or publication is required. **continue** is independently available. |
| Ready local or PR completion with no remaining staging, publication, or Viewed writes | Say what is already verified staged or Viewed. Offer **pass and continue** to reuse that verified result and advance without repeating writes, alongside **continue**. Revalidate current state before relying on the result. |
| Ready local review with reviewed deltas remaining to stage | **pass and continue** stages only the selected completion scope's remaining reviewed delta and verifies the index and worktree; **continue** advances without staging. Apply the local recording safeguards below. |
| Ready branch comparison without a PR | Completion is not applicable because this comparison has no recording or publication target. Offer **continue**; invent no remote-write target. |
| Ready PR matching the checked, reviewed version, with no unpublished reviewed changes | **pass and continue** verifies the pinned PR version and viewer, marks the selected scope's eligible reviewed paths Viewed, verifies every readback, and advances; **continue** advances without marking. Apply the PR recording safeguards below. |
| Ready PR with authorized, checked, re-reviewed local changes awaiting publication | **pass and continue** commits and pushes only the disclosed scoped decisions if needed, verifies the resulting PR version, marks the disclosed eligible reviewed paths Viewed, verifies every readback, and advances; **continue** retains local changes without publication or marking. Establish the publication and recording prerequisites below before offering completion. |

Reuse verified completed steps in partially recorded scopes; only remaining work needs writes. Add **optimize** to ready-state menus whenever supported outstanding suggestions remain. Publication requires a known, verified PR; an ordinary branch or local comparison supplies none. When the PR already contains the reviewed version, completion needs no empty commit or unnecessary push.

Every closing explicitly accounts for completion: offer its concrete effects and scope when ready, state that recording is already complete when applicable, or state that **pass and continue** is unavailable or not applicable with the concrete reason and next remedy. Put unavailable or inapplicable status outside **Available actions**; it is explanatory status, not an executable choice. Use **pass and finish** in that status for an exhausted scope. This accounting also applies when only continuation is available after a successful repair.

After progress, separate **Pending findings**, **Optional improvements**, **Incidental observations (outside this review's scope)**, and **Available actions** in that order with Markdown, omitting empty sections. List pending findings using the exact format `**M1** (P1): <impact summary>`, substituting the actual ID and severity; bold only the ID and keep the ASCII parentheses and colon plain. List supported suggestions by ID, proposed improvement, and benefit. Include outstanding findings and suggestions from earlier groups. Describe each available action's actual effects in short bullets without command syntax or numbered recipes, including the exact publication delta and eligible Viewed set when needed. End with one concise question; when no choice remains, close without a question.

An incoming “continue” finishes an exhausted scope only when the gate is satisfied. A ready exhausted branch scope with no suggestions can close without a question after explaining why completion is not applicable. An explicit stop or pause is always allowed: report the displayed progress, unresolved or ignored findings, evidence gaps, unpublished modifications, and unfinished operations as applicable, without claiming successful completion. Completed display does not mean all findings were repaired or all modifications were published.

### Interpret replies and re-review edits

Apply the selected meaning even when it is absent from the menu, provided its prerequisites and authority hold. If required effects were not disclosed or explicitly authorized, explain them and obtain the selection before writing; a historical “pass” disclosed as staging or marking Viewed supplies no commit or push authority. If the user requests advancement while blocked, refuse it briefly, name the blockers, and ask for the relevant fix, ignore, or remedy; “continue” never means “ignore.” Clarify ambiguous scopes, invalid IDs, conflicting directions, or a bare agreement following an ambiguous menu; “yes” authorizes an action only when the preceding question specifies it unambiguously. Reassess disputed findings from the supplied evidence rather than treating disagreement as ignoring. Answer questions without interpreting them as authorization for edits or advancement.

For authorized repairs or optimizations, load the necessary guidance, limit edits to the selected findings or suggestions and their necessary supporting changes, and run required checks. Optimization preserves supported behavior and contracts. Whenever reviewed content changes, complete required checks successfully, refresh the review snapshot and regenerate or revalidate its diff links, and independently re-review every changed or affected previously reviewed part, including unexpected changes. Show complete file blocks with updated explanations and both judgments in dedicated replies separate from unseen files. Retain modification IDs and original group membership, count each displayed file once, explain the version transition, and update the file list and total only for actual scope changes. For unpublished PR changes, retain both the pinned remote version and the checked local content expected to be published. Mark findings repaired or suggestions completed only after re-review confirms the result.

A single **fix**, **ignore**, or **optimize** ends with the regenerated menu and completion status, not automatic advancement. An explicit compound request authorizes its ordered steps: for example, fix, check, display the dedicated re-review, publish the scoped fixes and mark Viewed, then advance. Continue already authorized steps without routine reconfirmation; a new finding, failed check, or material change pauses dependent steps and regenerates the menu. An independently authorized optimization can still proceed while findings are pending, but does not open the advancing gate.

### Record the selected completion scope

For a local review, retain every displayed group's before-and-after content, original index entries, and verified staging results across groups. Before completion, verify current worktree contents and relevant index entries against those snapshots, accounting for earlier verified task staging, and capture the complete current index as the write baseline. Determine the selected scope's reviewed delta still unstaged; final completion includes earlier continued groups. Stage only that remaining delta, using a scoped patch when whole-file staging would include unseen or excluded changes. Preserve existing staged contents outside that delta, including unrelated edits in partially staged files, and leave the worktree unchanged. Verify that the resulting index equals the write baseline plus exactly that delta, all other entries remain unchanged, and the worktree still matches the snapshots. Retain the verified result so later completion can reuse it without reapplying staged changes. If a snapshot is stale or the delta cannot be separated safely, refresh and display the affected review and obtain a new selection before staging. Local completion supplies no commit or push authority.

For a PR review, establish the verified GitHub PR review target and an authenticated interface for the required viewer, version, and per-path readbacks before offering completion; when marking remains, the interface must also be capable of marking files Viewed. The checked, reviewed version must be present on the PR; use the publication procedure below first when necessary. Verify the viewer identity and pinned base and head immediately before writing, mark only the selected completion scope's eligible reviewed paths still awaiting Viewed, then read back every selected path's `viewerViewedState` and the PR version, including paths whose completed marking is being reused. Every selected path must be `VIEWED`, with both commit IDs unchanged during recording, before advancing. A changed version requires an affected re-review and a new selection; marking a newer version does not establish that it was reviewed.

### Publish reviewed PR changes when completion requires it

Use available Git and authenticated GitHub read/write interfaces, such as a CLI, connector, or UI. Establish the exact repository, PR, source branch, viewer, write capabilities, and attributable publication scope before offering completion that publishes changes. Include only this report's explicitly authorized decisions that passed required checks and re-review, with their necessary support, generated, and test changes; tests remain excluded from report counts. Preserve unrelated staged and worktree changes, and exclude unrelated unpushed commits, other unseen edits, and unknown file versions. If the push ancestry or delta cannot be separated safely, explain the prerequisite rather than implicitly rebasing or force-pushing.

Execute the selected operation in this order:

1. Verify the pinned remote base and head, the reviewed before-and-after content and affected dependencies, and the entire delta and commit ancestry to be published. Confirm that the actual publication delta and eligible displayed paths match the disclosed selection; verify each path's content and the pinned viewer.
2. If needed, stage and create a scope-only commit through normal repository hooks, preserving pre-existing staged work outside the authorized delta and the worktree. Verify the resulting commit and remaining local state; hook changes need checks and affected re-review before publication.
3. Push normally to the validated PR source branch. Read back the remote head and base, confirming the expected commit and that its complete comparison and effects match the checked, re-reviewed decisions.
4. Apply the PR recording safeguards above to the disclosed eligible displayed paths, including the final accumulated scope when selected. Mark only paths still awaiting Viewed; read back every selected path's state and the PR version. All must be `VIEWED` on the verified base and head.
5. Acknowledge the completed operation and advance from the saved position, or finish an exhausted scope.

The intentional new head needs verification, not a repeat of the whole review. Unexpected changes to content, base, or affected dependencies require re-review of the affected parts; text equality alone does not establish unchanged effects. Refresh the snapshot and obtain a new choice when the result no longer represents the authorized reviewed version. Retain the ordered list, group membership, next position, modification IDs, decisions, and per-group recording results across publication.

### Recover an unfinished operation

If a required interface is unavailable or a write or verification fails, pause without advancing, rolling back automatically, or substituting **continue** or **finish**. Report confirmed, failed, and unknown steps, including the exact commits, publication status, and partial staging or Viewed paths, then generate the closing status from the state table. Retain the selected completion scope, group snapshots, PR version, viewer, and resume position; resuming an intermediate operation does not silently expand it to final scope. After a lost response, inspect the actual local and remote state before deciding whether a write occurred. Once readiness is restored, resume the same **pass and continue** or **pass and finish** operation, describing only the remaining supported steps, without duplicate commits or repeated successful writes. A selected operation completes only after all its required readbacks succeed; explicit stopping can leave it incomplete and must report that residual state. Successful completion preserves saved progress and the resume position; amend totals only for real scope changes, and do not reapply unstaged or Viewed filters to remove displayed files.

## Reference report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, modifications, both reasoned judgments, and progress; use a vertical comparison only when the modification calls for expansion. These are illustrative files and snippets, not findings about a particular repository. This example is a local unstaged review containing three non-test files. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

The loopback URLs below illustrate filename-link formatting only; they are placeholders rather than generated previews. Actual reports use the shared tool's returned Markdown.

📄 **[l10n/en.json](http://127.0.0.1:47821/diff?repo=%2Fproject&path=l10n%2Fen.json&base=blob%3A1111111111111111111111111111111111111111)**

This file supplies English interface text. The changed label makes clear that the action deletes the account; all translation changes in this file are reviewed together.

🔧 **M1** - **Make the account-deletion label explicit**

The label changes from “Delete” to “Delete account,” naming the affected object.

⚖️ **Reasonable**. The label accurately describes the assumed action.

🎨 **Elegant**. Two plain words communicate the action clearly.

---

📄 **[lib/item_storage.dart](http://127.0.0.1:47821/diff?repo=%2Fproject&path=lib%2Fitem_storage.dart&base=blob%3A1111111111111111111111111111111111111111)**

This file saves and deletes stored items. The change preserves the storage-box reference so deleting an item can still flush the deletion afterward.

🔧 **M2** - **Flush the deletion to the original storage box**

⏪ **Before**

```dart
await item.delete();
await item.box?.flush();
```

After deletion, `item.box` becomes null, so the flush is skipped.

⏩ **After**

```dart
final originalBox = item.box;
await item.delete();
await originalBox?.flush();
```

Saving the box reference first lets the code flush that same box after deleting the item.

⚖️ **Reasonable**. This directly repairs the promised deletion behavior with a small change. Flush failures reach the caller; flushing does not roll back the deletion, so a failed flush must not be described as a restored item.

🎨 **Elegant**. Keeping the original box reference at the deletion site directly handles the detachment mechanism without adding a separate lookup or new state elsewhere.

---

📄 **[ui/save_button.dart](http://127.0.0.1:47821/diff?repo=%2Fproject&path=ui%2Fsave_button.dart&base=blob%3A1111111111111111111111111111111111111111)**

This file handles the Save button. The change prevents repeated clicks from starting duplicate saves.

🔧 **M3** - **Refuse repeated clicks while saving**

Previously, repeated clicks could start duplicate saves; the handler now refuses another save while one is pending, and completion and cancellation both reset the pending flag correctly.

⚖️ **Reasonable**. This prevents duplicate saves within the requested scope.

🎨 **Can improve**. Both branches repeat the same flag reset; a shared completion path would make cleanup easier to maintain.

---

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending.

**Optional improvements**

- **M3**: Use a shared completion path for the flag reset to reduce duplication and make cleanup easier to maintain.

**Available actions**

- **Optimize**: Implement the optional improvement.
- **Pass and finish**: Stage the remaining reviewed changes across all groups in this report and end this review, retaining the improvement as advice.
- **Finish**: End this review without staging remaining changes, retaining the improvement as advice.

🤖 **Would you like to optimize, pass and finish, or finish?**

## Example closings for different results

These illustrative closings follow file reports or dedicated re-reviews; they do not replace the two judgments in each modification. Localize them and use only the options available for the actual state.

### Incidental observation with a ready final group

In this illustrative local review, the selected change only adjusts export-button text. The source location below is illustrative; an actual report uses an available source link.

📊 **Progress**: **3/3 files displayed**. No unreasonable findings are pending.

📌 **Incidental observations (outside this review's scope)**

**O1**: The export button stays disabled after a failed export.

- **Location**: `src/export.ts:68`.
- **Evidence and impact**: The button is disabled before export and restored only on success. When export throws, users must refresh the page to retry.
- **Relationship to this change**: The same failure path exists in the before version; the text change neither triggers nor aggravates it.
- **Recommendation**: Restore the button in a shared completion path so users can retry after success or failure.

O1 remains advice, does not block completion, and is excluded from bulk fixes or optimizations. Handling it requires a separate selection.

**Available actions**

- **Pass and finish**: Stage the remaining reviewed changes across all groups in this report and end this review, retaining O1 as advice.
- **Finish**: End this review without staging remaining changes, retaining O1 as advice.

🤖 **Would you like to pass and finish, or finish?**

### Pending findings and optional improvements

📊 **Progress**: **4/9 files displayed**.

**Pending findings**

- **M2** (P1): Closing the resource can lose unsaved data.
- **M5** (P2): The error path leaves the button disabled.

**Optional improvements**

- **M7**: Share the repeated state-reset logic to reduce maintenance omissions.

**Pass and continue** and **continue** are unavailable until M2 and M5 are repaired or explicitly ignored.

**Available actions**

- **Fix**: Repair both pending findings, or the subset you select.
- **Ignore**: Choose which findings to ignore; other findings remain pending.
- **Optimize**: Implement the optional improvement; the pending findings still need attention.

🤖 **Would you like to fix or ignore the findings, or optimize? The findings must be handled before continuing.**

If the user replies “continue,” respond: “M2 and M5 are still pending, so I cannot show the next group yet. Would you like to fix them or explicitly ignore them?”

### PR repaired locally and ready for completion

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired; required checks and re-review passed. The fixes remain local. The PR target, viewer, write interfaces, and publication scope have been verified.

**Available actions**

- **Pass and continue**: Commit and push the two fixes, verify the PR version, mark the four displayed reviewed files Viewed and verify every readback, then show the next group.
- **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

🤖 **Would you like to pass and continue, or continue with the fixes kept local?**

### Publication scope is not safe

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired; required checks and re-review passed.

**Pass and continue** is unavailable: pushing the current ancestry would also publish an unrelated unpushed commit. Completion first needs a separable publication scope containing only this report's authorized, checked fixes.

**Available actions**

- **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

🤖 **Would you like to continue with the fixes kept local?**

### Resume partially completed PR recording

📊 **Progress**: **4/9 files displayed**. The selected completion's commit and push are verified. After access was restored, readback confirmed the expected PR version and viewer: two selected files are Viewed and two remain unviewed.

The selected **pass and continue** is unfinished. Ordinary **continue** is unavailable until the remaining recording and readbacks complete.

**Available actions**

- **Pass and continue**: Resume by marking the two remaining selected files Viewed, verify all four selected files and the PR version, then show the next group. The verified commit, push, and completed marking will be reused.

🤖 **Would you like to resume pass and continue?**

### Final group of a PR review

📊 **Progress**: **9/9 files displayed**. No pending findings or unpublished reviewed changes remain; the PR matches the reviewed version. Four files from earlier groups are verified Viewed; five reviewed files across the report, including files from groups advanced using continue, still await Viewed.

**Optional improvements**

- **M7**: Share the state-reset logic to reduce duplication and maintenance omissions.

**Available actions**

- **Optimize**: Implement the optional improvement.
- **Pass and finish**: Complete recording for all nine reviewed files across every group: mark the five remaining files Viewed, verify all nine files and the PR version, then end this review, retaining the improvement as advice.
- **Finish**: End this review without marking the remaining files Viewed, retaining the improvement as advice.

🤖 **Would you like to optimize, pass and finish, or finish?**
