---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help a human reviewer understand a pull request or branch change: what changed, whether it is reasonable, whether its implementation is elegant and tasteful, and where their attention is needed. Use this Skill only when the user requests it. Review the selected scope read-only, then carry out only the effects authorized by the user's selected actions within the scope and verification rules below. Apart from the shared runtime's initialization below, read-only review permits only auxiliary snapshot/export writes; keep the reviewed files and Git index unchanged until an authorized action below.

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

### Prepare fixed diff links

Every reported filename must link to a fixed diff snapshot of that file's reviewed before-and-after content. For the local default, export the index version and captured worktree version, preserving only their unstaged comparison even for a partially staged file. For a PR, use the pinned base/head comparison evidence; for a branch, use the pinned merge-base and tip. Honor any explicitly selected comparison. Export from the retained review snapshot rather than current refs or mutable files, so opening the link later shows the version explained in the report.

Use the shared plugin runtime, resolving `<runtime>` as `../../runtime/deep-links/deep_links.py` relative to this loaded Skill's directory. The reviewed repository need not contain it. Read its command help for the current interface; if the runtime is missing, pause the dependent report and request a complete or restored plugin installation.

```text
python "<runtime>" --help
python "<runtime>" ensure --help
python "<runtime>" ensure
python "<runtime>" create --help
python "<runtime>" create --input "<batch.json>" --viewer auto
```

Before generating this report's links, call `ensure` without `--quiet` and require its JSON `status` to be `ready`; a successful session Hook exit does not prove readiness. Automatic preparation initializes absent state on a supported desktop and preserves an explicit disable. This Skill never supplies `--enable`. A `disabled` or `skipped` status, malformed output, or command failure pauses the dependent report: state the actual cause and concrete remedy, such as explicitly re-enabling a disabled installation, using a supported desktop outside CI, restoring the runtime, or resolving the reported foreign-handler or damaged-record conflict. Preserve those conflicts for their owner to resolve. Do not claim readiness, fabricate a URL, or replace the required diff link with a source link.

Build a JSON batch with one unique `id` per file/version, `action: "diff"`, the real reported path as `title`, and `before`/`after` paths to UTF-8 exports. Input paths resolve relative to the batch file. Use `null` for the absent side of an addition or deletion. `create` copies both sides into fixed snapshots; use the automatic viewer to prefer an existing VS Code window and fall back to the HTML comparison. Match each returned `id` and `action` to its real filename and preserve the returned `url`, `web_url`, and `markdown`. Use its actual Markdown or URL in the filename header; task IDs are not native URL tokens. The emitted native URL has the form `smartkit://diff/<token>`.

Retain the link mapping with the review snapshot. Every new reviewed version needs newly generated links; preserve earlier snapshots so earlier reports still open their original comparison. Handler readiness, client acceptance of the scheme, and an opened editor are separate facts. When client support has not been tested, report it as unverified. If the client blocks the scheme, pause the dependent report and state the observed restriction and concrete client remedy; the emitted `web_url` can additionally expose the same fixed comparison. Claim a successful click or an opened VS Code Diff only when observed; generating a link or receiving a successful CLI exit does not establish either result.

## Explain each file through the problem it solves

Keep all report emoji outside bold spans, preserving emphasis on their accompanying text. When emphasizing a word, phrase, identifier, or label, keep surrounding separators and terminal punctuation outside bold; deliberately emphasized complete sentences may retain their sentence punctuation. Preserve punctuation intrinsic to code, identifiers, and paths.

Begin each file in the form `📄 **[path](diff-url)**`, using the actual generated diff link, and a short overview of its responsibility and overall change. Source links and relevant line references may supplement this required filename link. Explain in ordinary language what the change means for users or callers, retaining technical detail that affects the judgment.

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

End each group with `---` and 📊 **Progress**: **displayed files / files requiring review**, explicitly saying that the files have been displayed. Count displayed files, not modifications or conclusive judgments. Across replies, retain the snapshot, ordered file list, current displayed group's files and reviewed changes, next-unreviewed position, next modification ID, judgments, finding statuses, and outstanding elegance suggestions.

### Choose an action

Use the conversation's language for human-facing labels, summaries, action names, and questions. Localize action names and their descriptions consistently in that language, without pairing them with names in another language. Interpret natural-language selections by meaning, rather than requiring command syntax.

Modification IDs select that modification's relevant findings or suggestions. Unqualified **fix**, **optimize**, and explicit **ignore all** cover only this report's already displayed, outstanding items in the chosen dimension, including earlier groups. A subset affects only that subset. Explain the applicable scope and count in the menu. Advancing displays the next group at the saved position or finishes an exhausted scope.

| Action | Effect and selection |
| --- | --- |
| **fix** | Repair pending unreasonable findings: all when unqualified, otherwise only those selected. |
| **ignore** | Record only the selected findings as ignored, retaining their severity and impact. A lone clearly identified finding needs no repeated ID; otherwise ask which findings, unless the user explicitly chooses all. Other findings stay pending. |
| **optimize** | Implement supported outstanding 🎨 **Can improve** suggestions: all when unqualified, otherwise only those selected. This leaves separately pending findings unchanged. |
| **pass** | Local review: stage this group's reviewed delta. PR review: mark this group's reviewed files Viewed. Verify the operation, then advance. It authorizes neither commit nor push. |
| **continue** | Advance without staging, committing, pushing, or marking Viewed. Retain unpublished modifications and unimplemented suggestions. |
| **sync and continue** | For a verified PR target, commit and push this report's authorized, checked and re-reviewed decisions; mark eligible displayed files Viewed, then advance. It expressly authorizes the scoped publication and marking, including earlier displayed files awaiting Viewed. |

**pass** and **continue** select the whole current group; clarify selections of individual modifications. For **sync and continue**, identify the actual publication delta and eligible Viewed set before writing. Neither **pass** nor **sync and continue** formally approves or merges a PR. Ignored findings remain ignored, not repaired or approved.

### Generate the closing menu

Use the same state table after ordinary reviews and re-reviews. Advancing requires every displayed unreasonable finding to be repaired or explicitly ignored, required correctness and version evidence to be available, required checks and affected re-reviews to be complete, and any selected recording or synchronization operation to be verified. An optional improvement or lack of elegance evidence alone does not block advancing.

| State, in priority order | Available choices or next step |
| --- | --- |
| Pending unreasonable findings, including after subset fixes or ignores | **fix**, **ignore**, and **optimize** if supported suggestions remain. Refuse **pass**, **sync and continue**, and **continue** until the findings are handled. |
| Missing correctness/version evidence, incomplete or failed required checks, or stale affected review | Complete authorized checks or re-review; otherwise offer the concrete prerequisite or remedy. Keep advancing unavailable. |
| A selected staging, Viewed, or synchronization operation is unfinished | Resolve its blocker and complete the remaining verified steps; offer **complete sync and continue** for synchronization. Keep ordinary **continue** unavailable. |
| Ready local review | **pass**, **continue**. Omit **pass** when this group's reviewed delta is already staged. |
| Ready branch comparison without a PR | **continue**; no state-recording or synchronization target is implied. |
| Ready PR matching the reviewed version, with no unpublished reviewed changes | **pass**, **continue**. Omit **pass** when this group's files are already Viewed. |
| Ready PR with authorized, checked, re-reviewed local changes awaiting publication | **sync and continue**, **continue**, if the publication and marking prerequisites below are established. Explain that ordinary **pass** requires the reviewed version on the PR; **continue** retains the local changes without publishing. |
| Required write target, interface, or safe scope cannot be established | Name the concrete prerequisite; omit the unavailable write action. **continue** remains available only if the advancing gate is satisfied and no selected operation is unfinished. |

Add **optimize** to ready-state menus whenever supported outstanding suggestions remain. Do not offer redundant synchronization when no publication is needed; if the user nevertheless requests it, perform only the required marking and advancement, without an empty commit or unnecessary push. A known, verified PR is required for synchronization; an ordinary branch or local comparison supplies none.

After progress, separate **Pending findings**, **Optional improvements**, and **Available actions** with Markdown, omitting empty sections. List pending findings using the exact format `**M1** (P1): <impact summary>`, substituting the actual ID and severity; bold only the ID and keep the ASCII parentheses and colon plain. List supported suggestions by ID, proposed improvement, and benefit. Include outstanding items from earlier groups. Describe only the actual operation for each available action, using short bullets without command syntax or numbered recipes. End with one concise question; when no choice remains, close without a question.

In the final group, label **pass** as **pass and finish**, **sync and continue** as **sync and finish**, and **continue** as **finish review**; these are closing wordings of the same actions. An incoming “continue” finishes an exhausted scope only when the gate is satisfied. A ready exhausted branch scope with no suggestions can close without a prompt. An explicit stop or pause is always allowed: report the displayed progress, unresolved or ignored findings, evidence gaps, unpublished modifications, and unfinished operations as applicable, without claiming successful completion. Completed display does not mean all findings were repaired or all modifications were published.

### Interpret replies and re-review edits

Apply the selected meaning even when it is absent from the menu, provided its prerequisites hold. If the user requests advancement while blocked, refuse it briefly, name the blockers, and ask for the relevant fix, ignore, or remedy; “continue” never means “ignore.” Never upgrade **pass** to a commit or push. Clarify ambiguous scopes, invalid IDs, conflicting directions, or a bare agreement following an ambiguous menu; “yes” authorizes an action only when the preceding question specifies it unambiguously. Reassess disputed findings from the supplied evidence rather than treating disagreement as ignoring. Answer questions without interpreting them as authorization for edits or advancement.

For authorized repairs or optimizations, load the necessary guidance, limit edits to the selected findings or suggestions and their necessary supporting changes, and run required checks. Optimization preserves supported behavior and contracts. Whenever reviewed content changes, complete required checks successfully, refresh the snapshot and its diff links, and independently re-review every changed or affected previously reviewed part, including unexpected changes. Show complete file blocks with updated explanations and both judgments in dedicated replies separate from unseen files. Retain modification IDs and original group membership, count each displayed file once, explain the version transition, and update the file list and total only for actual scope changes. For unpublished PR changes, retain both the pinned remote version and the checked local content expected to be published. Mark findings repaired or suggestions completed only after re-review confirms the result.

A single **fix**, **ignore**, or **optimize** ends with the regenerated menu, not automatic advancement. An explicit compound request authorizes its ordered steps: for example, fix, check, display the dedicated re-review, synchronize, then advance. Continue already authorized steps without routine reconfirmation; a new finding, failed check, or material change pauses dependent steps and regenerates the menu. An independently authorized optimization can still proceed while findings are pending, but does not open the advancing gate.

### Record a passed group

**pass** covers only the current group's reviewed delta or file paths, including its latest displayed re-review. For a local review, verify the current worktree contents and relevant index entries against the retained snapshot and capture the complete current index as the write baseline. Stage only the reviewed delta not already staged, using a scoped patch when whole-file staging would include unseen or excluded changes. Preserve existing staged contents outside that delta, including unrelated edits in partially staged files, and leave the worktree unchanged. Verify that the resulting index equals the write baseline plus exactly that delta, all other entries remain unchanged, and the worktree still matches the snapshot. If the snapshot is stale or the delta cannot be separated safely, refresh and display the affected review and obtain a new selection before staging.

For a PR review, obtain an available authenticated interface capable of marking files Viewed. Verify the viewer identity and pinned base and head immediately before writing, mark only this group's reviewed paths, then read back every selected path's `viewerViewedState` and the PR version. Every selected path must be `VIEWED`, with both commit IDs unchanged, before advancing. A changed version requires an affected re-review and a new selection; marking a newer version does not establish that it was reviewed.

### Synchronize a reviewed PR

Use available Git and authenticated GitHub read/write interfaces, such as a CLI, connector, or UI. Establish the exact repository, PR, source branch, viewer, write capabilities, and attributable publication scope before offering synchronization. Include only this report's explicitly authorized decisions that passed required checks and re-review, with their necessary support, generated, and test changes; tests remain excluded from report counts. Preserve unrelated staged and worktree changes, and exclude unrelated unpushed commits, other unseen edits, and unknown file versions. If the push ancestry or delta cannot be separated safely, explain the prerequisite rather than implicitly rebasing or force-pushing.

Execute the selected operation in this order:

1. Verify the pinned remote base and head, the reviewed before-and-after content and affected dependencies, and the entire delta and commit ancestry to be published. Announce the actual publication delta and eligible displayed paths awaiting Viewed; verify each path's content and the pinned viewer.
2. If needed, stage and create a scope-only commit through normal repository hooks, preserving pre-existing staged work outside the authorized delta and the worktree. Verify the resulting commit and remaining local state; hook changes need checks and affected re-review before publication.
3. Push normally to the validated PR source branch. Read back the remote head and base, confirming the expected commit and that its complete comparison and effects match the checked, re-reviewed decisions.
4. Mark only eligible displayed paths Viewed for the pinned viewer. Read back every selected path's state and the PR version; all must be `VIEWED` on the verified base and head.
5. Acknowledge the completed operation and advance from the saved position, or finish an exhausted scope.

The intentional new head needs verification, not a repeat of the whole review. Unexpected changes to content, base, or affected dependencies require re-review of the affected parts; text equality alone does not establish unchanged effects. Refresh the snapshot and obtain a new choice when the result no longer represents the authorized reviewed version. Retain the ordered list, group membership, next position, modification IDs, and decisions across synchronization.

### Recover an unfinished operation

If a required interface is unavailable or a write or verification fails, pause without advancing, rolling back automatically, or substituting **continue**. Report confirmed, failed, and unknown steps, including the exact commits, publication status, and partial staging or Viewed paths. After a lost response, inspect the actual local and remote state before deciding whether a write occurred. Once readiness is restored, resume only the remaining supported steps, without duplicate commits or repeated successful writes. A selected operation completes only after all its required readbacks succeed; explicit stopping can leave it incomplete and must report that residual state. Successful recording and synchronization preserve saved progress and the resume position; amend totals only for real scope changes, and do not reapply unstaged or Viewed filters to remove displayed files.

## Reference report

Use these examples as a guide, adapting the detail to the reader. Preserve the file overview, modifications, both reasoned judgments, and progress; use a vertical comparison only when the modification calls for expansion. These are illustrative files and snippets, not findings about a particular repository. This example is a local unstaged review containing three non-test files. Assume that deleting an item detaches it from its storage box, that the task promises to flush the deletion, and that flush errors propagate to the caller. That persistence contract and detachment mechanism warrant an expanded explanation.

The `smartkit://diff/TOKEN_PLACEHOLDER_*` destinations below illustrate filename-link formatting only. Their token segments are placeholders, so these are not generated or usable links. Actual reports use the runtime's returned links.

📄 **[l10n/en.json](smartkit://diff/TOKEN_PLACEHOLDER_1)**

This file supplies English interface text. The changed label makes clear that the action deletes the account; all translation changes in this file are reviewed together.

🔧 **M1** - **Make the account-deletion label explicit**

The label changes from “Delete” to “Delete account,” naming the affected object.

⚖️ **Reasonable**. The label accurately describes the assumed action.

🎨 **Elegant**. Two plain words communicate the action clearly.

---

📄 **[lib/item_storage.dart](smartkit://diff/TOKEN_PLACEHOLDER_2)**

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

📄 **[ui/save_button.dart](smartkit://diff/TOKEN_PLACEHOLDER_3)**

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
- **Pass and finish**: Stage this group's reviewed changes and end this review, retaining the improvement as advice.
- **Finish review**: End this review, retaining the improvement as advice.

🤖 **Would you like to optimize, pass and finish, or finish review?**

## Example closings for different results

These illustrative closings follow file reports or dedicated re-reviews; they do not replace the two judgments in each modification. Localize them and use only the options available for the actual state.

### Pending findings and optional improvements

📊 **Progress**: **4/9 files displayed**.

**Pending findings**

- **M2** (P1): Closing the resource can lose unsaved data.
- **M5** (P2): The error path leaves the button disabled.

**Optional improvements**

- **M7**: Share the repeated state-reset logic to reduce maintenance omissions.

**Available actions**

- **Fix**: Repair both pending findings, or the subset you select.
- **Ignore**: Choose which findings to ignore; other findings remain pending.
- **Optimize**: Implement the optional improvement; the pending findings still need attention.

🤖 **Would you like to fix or ignore the findings, or optimize? The findings must be handled before continuing.**

If the user replies “continue,” respond: “M2 and M5 are still pending, so I cannot show the next group yet. Would you like to fix them or explicitly ignore them?”

### PR repaired locally and ready to synchronize

📊 **Progress**: **4/9 files displayed**. M2 and M5 are repaired; required checks and re-review passed. The fixes remain local, so ordinary pass is unavailable until the PR contains this reviewed version.

**Available actions**

- **Sync and continue**: Commit and push the two fixes, verify the PR version, mark the four displayed files Viewed, then show the next group.
- **Continue**: Show the next group, retaining the local fixes without publishing or marking Viewed.

🤖 **Would you like to sync and continue, or continue with the fixes kept local?**

### Final group of a PR review

📊 **Progress**: **9/9 files displayed**. No pending findings or unpublished reviewed changes remain; the PR matches the reviewed version.

**Optional improvements**

- **M7**: Share the state-reset logic to reduce duplication and maintenance omissions.

**Available actions**

- **Optimize**: Implement the optional improvement.
- **Pass and finish**: Mark this group's reviewed files Viewed and end this review, retaining the improvement as advice.
- **Finish review**: End this review without marking Viewed, retaining the improvement as advice.

🤖 **Would you like to optimize, pass and finish, or finish review?**
