---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，判断合理性与优雅性，协助用户选择后续行动。
disable-model-invocation: true
---

# Review for Humans

Help the reader decide whether a change solves the right problem, whether its implementation earns its cost, and what to do next. Pin the evidence, explain one complete group of files, then act on the user's choice. The review request authorizes evidence capture and link preparation. Repairs, delivery, and advancement take their authority from the selected action.

## Fix the comparison and reading order

For a PR or remote-aligned branch, read [Preparation](references/preparation.md) before selecting a workspace or gathering version evidence. It owns workspace choices, source alignment, and the authenticated viewer's file filter. For a deliberately local branch, use the comparison below and read Preparation if you need to choose a workspace to display it. For unstaged work, use the local comparison below. If a required guide is unavailable, report the gap and leave its dependent work incomplete.

| Request | Comparison and initial evidence |
| --- | --- |
| PR | Preparation verifies PR identity, pins base/head, and obtains the authenticated viewer's complete file-level Viewed filter when it applies. It verifies a worktree when the selected route needs one. |
| Branch | Pin the tip and merge-base with a reliably established comparison base. Ask for an unknown base instead of assuming `main`. |
| Local changes or no stated scope | Compare index to worktree: unstaged changes only. |
| Selected files | Restrict the applicable comparison to those paths. |

Honor explicit alternative comparisons and historical versions. PR and branch comparisons exclude local uncommitted changes unless requested. For local review, exclude staged-only files, assess only the unstaged part of partially staged files, and recognize a worktree reversal of staged content as an unstaged change. Include untracked additions only when explicitly requested. These defaults prevail over different defaults in other review guidance.

Use the repository's test classification to skip semantic review of test code, including unit, integration, and end-to-end tests, in main review, supplementary review, and repair re-review. Consult relevant tests as evidence. Apply the test exclusion and the selected-file, Viewed, and local filters before counting files, change items, or progress. The delivery guide separately accounts for the complete submitted and outgoing scope. Review filters never narrow a commit or its required checks.

Use source, test definitions, and existing valid results for read-only review and Viewed-only recording. Run unit tests or complete change-set verification when the user requests them or applicable project requirements call for them. Edits follow the repair procedure below. When execution evidence is missing, identify the affected judgments and continue independently supported assessment.

Order files like GitHub's directory tree: recursively list changed files in subdirectories before direct files, preserving observed sibling order or otherwise sorting sibling directories and direct files by name. Thus `src/z/api.dart` precedes `src/a.dart`. Retain the ordered eligible list, pinned commits, complete before/after content, and PR viewer/filter evidence. For local review retain the original index baseline even when another before version is selected.

State the comparison and exclusions before the first group. Empty scope ends without a progress fraction. Known files with incomplete evidence remain in the total; identify what is missing and pause the affected assessment instead of treating unseen content as clean.

### Provide links to the assessed version

For local display, resolve `local_web` from loaded SmartKit resources and read its supported interface:

```text
python "<local_web>" --help
python "<local_web>" diff --input "<batch.json>"
```

When using `local_web`, supply each file's full repository-relative `path` with forward slashes and omit `title`. Associate the returned Markdown by ID and use it unchanged as the filename link, preserving its full label, escaping, and URL binding. Capture index-based local links with the snapshot. Fixed comparisons supply the verified before commit, existing blob, or genuine absence and rename paths.

Use the verified display mode from Preparation for PR reviews. Bind branch-only and local links to the exact verified display workspace without PR context. Disclose dirty or differing live contents while preserving the assessment and Viewed eligibility. Verify that the link serves the intended comparison. For a PR Snapshot with unavailable local display, disclose the limitation and use a display route verified to show the same file and fixed versions if one is available. When a required link is unavailable, keep the chosen mode, fixed evidence, and supported assessment, and leave any report that requires the link pending.

## Judge the need and what changed for callers

Read the whole scoped change and the context needed to judge it, including callers, comparable implementations, contracts, owners, and lifetimes. Assess every eligible change on both reasonableness and elegance, including documentation, translations, and minor edits that need no separate explanation. Apply project rules and accepted user decisions. Retain material task and standards findings, distinguishing evidence you verified from author-reported results. A passing test demonstrates behavior under the conditions and assumptions it exercised.

Establish the purpose before evaluating the design. What does the caller need, what did the original provide, and what does the proposed change add or remove? Compare a simpler implementation under the same requirements. To endorse extra complexity, show what that alternative would lose and why it matters. A proposal to change supported behavior needs a scope decision.

Spend more effort on elegance than reasonableness. Trace the purpose of each added file and each new or changed function, type, member, or piece of state, including private members. For a changed boundary or contract, establish who held the responsibility before, who depends on it now and for how long, and whether direct calls or an existing owner could serve those callers. Explain the consequential trade-off.

For derived state, start with the owner of each input. Use source references to find every relevant production entry point that updates, removes, or resets the input or its source entity, including outside the diff. For each such entry point, keep an internal, source-backed account of what each owner writes, clears, or retains and what reaches the consumer before and after the change. Include the case where one input clears or updates while another retains its value. For derived state or asynchronous feedback, trace permitted orders from availability to delivery, including intervening writes, clears, handling, interruption, or dismissal. Check the relevant production entry points that write or clear the state or mark it as handled, including other owners of its inputs. Carry material gaps as uncertainty. A test establishes the order it exercised.

If a helper is shared or a side effect moves, trace each affected production entry point and input path. Could a new operation fail where that caller previously succeeded? Establish what is saved, what reaches the caller, and whether that outcome is supported. For any defect, connect a reachable trigger to the affected obligation or user experience using source, a supported call sequence, an applicable contract, or a representative reproduction.

### Decide each axis independently

Judge each change on both axes. A definitive verdict, positive or negative, requires high confidence grounded in relevant evidence. Finding no defect or lacking the original conversation settles neither axis by itself.

| Judgment | Basis |
| --- | --- |
| ⚖️ **Reasonable** | Required outcomes, accepted scope, supported behavior/contracts, and justified operating costs and risks. |
| ⚖️ **Unreasonable** | A material task, behavior, or contract defect, including a violated structural obligation, unnecessary scope, or unjustified operating cost or risk. Identify severity, affected conditions, impact, and correction. |
| 🎨 **Elegant** | Responsibilities, boundaries, and interfaces earn their understanding and maintenance cost. Expression is readable; abstraction, state, branching, repetition, and defense have concrete benefits. Comparable patterns and interfaces are consistent, with justified departures. |
| 🎨 **Needs improvement** | A structural defect violates a supported obligation. Explain the obligation, concrete consequence, and necessary correction. Record the same item as an unreasonable finding. |
| 🎨 **Optional improvement** | The structure meets supported obligations, but a simpler or more consistent behavior-preserving alternative offers enough benefit for its change cost. Explain the burden, remedy, and benefit; optimization remains optional. |
| **Uncertain** on either axis | State the established facts, the material uncertainty, and what would resolve it. Keep any supported judgment on the other axis. |

Give every supported defect and worthwhile optional improvement an actionable M item. Attach it to the responsible change, with the trigger, consequence, and remedy or benefit. Include defects in unchanged code that this change introduces, triggers, or aggravates. One good change cannot offset another's defect or burden. Omit low-benefit polish and personal preference.

A behavioral defect alone establishes no structural defect. A violated structural obligation is both unreasonable and **Needs improvement**. Give it one ID, one explanation and one remedy. It requires Fix or explicit retention before advancement or delivery, including Viewed-only delivery. Assign severity only to unreasonable findings: P0 critical/immediate, P1 serious/prompt correction, P2 normal priority, and P3 lower-impact but worth correcting. An optional optimization preserves supported behavior.

Functional correctness and user approval do not establish elegance. Separate a demonstrated burden from its justification and the user's acceptance. When missing rationale or requirements leave the necessity of complexity or the safety of its removal unresolved, mark the affected axis **Uncertain**. Keep uncertainty under its M ID, summarize it as a warning, and identify evidence that would settle it. It creates no O item, Fix scope, Optimize scope, or Optimize choice. Preserve independently supported judgments and remedies on that change.

## Explain one complete group

Read [Report Format](references/report-format.md) in full before the first report or action menu. Apply it to ordinary, supplementary, repair, and selected-O reports. Reuse its complete current content, restore it when missing, including after compaction, and reload it when it changes. It owns the opening change overview, file blocks, change labels and explanation depth, closing disclosures, and menu rendering.

Give displayed changes continuous M IDs across files and groups. Combine steps that solve one problem, including removing an old implementation as part of a replacement or extraction across files. Separate changes with independent effects, such as retiring an entry point callers could use directly. One localization file still counts as one change item. Minor accompanying edits without findings may stay in the overview or be omitted from explanation while remaining assessed. Present each item once in a report. Preserve its ID through supplementary review and repair. Separately explained supporting changes take the next unused M IDs and retain their relationship to the original.

Size main groups internally. A straightforward change needing a short explanation counts as 1 unit, one needing more detail counts as 2. Finish the complete file that brings the group to at least 20 units, reset the count for the next group, and show the shorter remainder at scope end. A request to expand an explanation does not resize the group.

Report the cumulative displayed main files out of eligible files, counting each once, and the actual cumulative number of displayed main change items. Supplementary items, repair items, and incidental observations add no main units or progress. Keep the fixed evidence, group membership, judgments, findings, decisions, next position, and next M ID across replies. Totals change only with scope. A newly clean worktree cannot erase eligible undisplayed changes, and review progress alone establishes neither delivery nor Viewed status.

### Report a genuinely independent observation

When necessary reading reveals a pre-existing issue, establish evidence that the change neither introduced, triggered, nor aggravated it. Give it a separate continuous O ID, title, source link or location, evidence, impact, independence, and recommendation or benefit. Place it with its source file where attributable under Report Format. Keep the search within the task's necessary context.

An O item adds no main file, change item, progress, or automatic Viewed eligibility. Bulk Fix, Optimize, Ignore, or acceptance excludes O items unless explicitly selected or brought into scope. Unselected O advice creates no review or delivery gate. Once selected, an O repair needs its own evidence, checks, and two-axis re-review of the change and affected context. Keep O identities and main progress. The changes enter delivery coverage, where new findings or failed checks can block delivery.

## Offer the decision the group supports

After displaying the complete group, include unresolved items from earlier groups. Close with conclusions, actual checks and limitations, pending unreasonable IDs with severity and impact, accepted trade-offs, and optional remedies and benefits. A completed, checked and re-reviewed repair uses the same decision here unless delivery or another compound action is already pending.

Pass and Continue/Finish both need current version and correctness evidence, successful applicable repair or explicitly requested verification checks, completed affected re-review, and resolution or explicit retention of pending unreasonable findings. Elegance uncertainty alone can travel as a warning. Optional improvements and unselected O advice remain optional. Investigate derivable facts first. Ask directly for a genuinely user-owned missing fact or scope decision. Explain a verified blocker without a supported remedy instead of inventing an action.

When delivery effects remain, read [Delivery](references/delivery.md) and proactively offer Pass alongside Continue/Finish wherever advancement is available. Describe the selected workspace, applicable full-workspace commit, outgoing publication, Viewed effects, and subsequent advancement. Outstanding staged or local work, uncovered outgoing commits, and remaining delivery checks can be part of what Pass starts. Prior delivery selection or completed preparation is unnecessary. Offer only effects supported by known conditions and resolved scope.

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| Unreasonable findings remain; no optional improvement is offered | **Fix** | **Fix**; **Ignore** |
| Unreasonable findings remain; optional improvements are also offered | **Fix** | **Fix**; **Optimize**; **Ignore** |
| Only optional improvements are offered | **Optimize** | **Optimize**; **Pass**; **Continue** |
| No outstanding finding or improvement is offered | **Pass** | **Pass**; **Continue** |

For these common cases use the listed recommendation and choice order among applicable actions. For other cases apply the same principles. Use Finish at scope end and state the purpose and next position of Continue. The improvement rows can include selectable O improvements under their separate scope. Preparation owns the corresponding workspace-choice table.

Render one option per applicable action type with consecutive letters and the recommendation at A. In each option name its default IDs, consequences, and effects. Consolidate available M and O remedies under Fix or Optimize while making clear which O items would require explicit selection. Offer Optimize only for a concrete, disclosed outstanding improvement. Recommendations and sole options do not select themselves.

### Interpret what the user selects

Read letters case-insensitively against the latest applicable menu. Clear natural language may select subsets and compound effects. An unambiguous option supplies its disclosed scope, including O items it explicitly selects. Merely mentioning O alternatives leaves them outside bulk M actions. Ask which IDs when several alternatives match. IDs alone specify items without selecting an action.

- **Fix** repairs selected unreasonable findings. Without a clear menu scope, bare Fix covers all displayed pending unreasonable M findings, including earlier groups.
- **Optimize** implements selected optional improvements while preserving supported behavior and contracts. Without a clear menu scope, bare Optimize covers all displayed outstanding optional M improvements, including earlier groups. **Fix and optimize** explicitly selects both remedy sets and is available in natural language.
- **Ignore** records explicitly selected items, their consequences, and the user's acceptance or decline. Clear natural-language retention suffices. Clarify ambiguous items or intent. A retained item ceases to be outstanding while its assessed content and effects remain unchanged. Its judgment stands; the same accepted burden needs no fresh optimization request. Ignore alone neither advances nor waives checks.
- **Pass** prepares and completes applicable delivery, then advances or finishes under Delivery's completion and concurrency rules. Its selection explicitly retains only assessed optional items named in that choice. A request to **deliver** or **only deliver** selects the same delivery while preserving the current review position unless continuation is also selected. Delivery alone needs no routine menu entry. Neither action authorizes PR approval or merging.
- **Continue** advances the fully displayed group without delivery. **Finish** ends the fully displayed review without delivery. Optional items may remain deferred without being declined.

When recording a user's decision about code behavior, apply `rule-code-comment` to decide whether it needs a source comment.

Act on a ready selection without routine reconfirmation. A question, recommendation, or disagreement grants no new authority. Honor an explicit change of request, pause, or stop, and report completed and residual work when stopping. The user can stop or cancel without a menu option.

## Check a selected repair before resuming

Carry the selected findings, supporting paths, verified reasons for corrections, accepted trade-offs, and disclosed effects into the repair. Preserve the fixed comparison, workspace, IDs, groups, saved position, and any pending compound request through the work and interruptions.

At the start of a selected repair, establish the target project's applicable verification process in the workspace being edited. Complete any required initialization or baseline checks before editing, and pause dependent edits if a required prerequisite is unavailable.

Limit edits to the selected remedy and necessary supporting changes. Within that scope, consider whether the verified reason for retaining behavior warrants a comment under the applicable guidance. Retention alone grants no comment-edit authority. Recommend a comment in a read-only review, under an explicit no-edit instruction, or for an unrelated unselected item. If a preservation request could cover either behavior or all edits, clarify it before the affected edit.

When any repair touches a PR file not yet fully reviewed, read [Delivery](references/delivery.md) before determining whole-file Viewed eligibility.

Run required checks on the repaired contents through the project's supported verification methods. Refresh before/after evidence and links. Reuse complete applicable guidance and retain supporting records, including full logs where available. Reuse evidence only while valid for the exact contents, dependencies, and effects; it cannot waive a required check. Pinned PR evidence describes the fixed comparison. Establish unpublished repairs separately.

Independently re-review every changed non-test file, including necessary supporting and unexpected changes, and affected previously reviewed parts. Tests retain their evidence and required-check role. Give the repair its own reply covering every changed non-test file under Report Format, apart from unseen main files and without recounting main progress. A repair or optimization is complete only when checks and affected re-review confirm it. A failed or unavailable required check leaves dependent work incomplete.

A single Fix, Optimize, or Ignore ends at the updated decision. If another effect was explicitly selected, continue its remaining authorized work after any required checks, dedicated repair report, and re-review. For pending delivery, use the decision below.

## Complete a selected delivery

Use [Delivery](references/delivery.md) for inventory, checks and coverage, physical effects, concurrency, and recovery. An explicit preparation request can start that work without authorizing writes. For Pass or only-deliver, preserve the original selection through supplementary review and interruptions. Disclose the concrete plan before execution. Reuse the selection's authority while the scope, destination, and effects remain within it.

Pause writes for any unresolved unreasonable finding in required coverage, including earlier findings whose assessments are reused. Newly disclosed worthwhile optional improvements in that coverage also need a decision. Apply these conditions to selected O work. The earlier Pass neither accepts later findings nor authorizes unselected repairs. Previously retained items stay resolved while their assessed contents and effects remain valid. Unselected O advice stays outside the gate. Use this table while delivery is pending:

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| Required coverage has unresolved unreasonable findings only | **Fix** | **Fix**; **Ignore** |
| Required coverage has unresolved unreasonable findings and optional improvements awaiting a decision | **Fix** | **Fix**; **Optimize**; **Ignore** |
| Only optional improvements in required coverage await a decision | **Optimize** | **Optimize**; **Ignore** |
| Required coverage has no unresolved finding or improvement | Complete the selected delivery | No new choice; finish prerequisites and resume automatically |

Offer only the applicable remedies and retention choices. Fix or Optimize may resolve only some items. After checks, dedicated report, and re-review, use this table for any remaining decisions. Once findings and prerequisites are resolved, complete the original Pass or only-deliver without asking again or substituting Continue/Finish.

Preserve confirmed effects and ask for a concrete decision about changed effects outside existing authority. After applicable commit and publication complete, Pass can start the saved next group read-only while only Viewed remains, following Delivery's version and process rules. Only-deliver stays at the saved position unless continuation was selected. Report confirmed, unknown, and remaining effects, preserving incomplete delivery and its intent for supported resume.

## Worked examples

Consult the example for the decision at hand. The current review's evidence and applicable guide determine judgments and available actions.

| Situation | Example |
| --- | --- |
| Explain additions, modifications, and deletions at different depths, present independent observations, or expand an item on request | [Review group](examples/review-group.md) |
| Judge an added boundary or decide whether uncertainty blocks advancement | [Design judgments](examples/design-judgments.md) |
| Format a repair across supporting files or report a missing required check | [Repair report](examples/repair-report.md) |
| Resume selected delivery after supplementary findings or partial Viewed recording | [Delivery follow-through](examples/delivery-follow-through.md) |
| Present a workspace choice or resolve missing Viewed evidence | [Review preparation](examples/review-preparation.md) |
